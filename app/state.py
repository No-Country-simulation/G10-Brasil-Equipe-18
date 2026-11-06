"""Estado da aplicação (st.session_state) e helpers.

Obs.: o Streamlit apaga o estado de widgets que não aparecem numa execução
(por exemplo ao trocar de tela). Por isso os valores editáveis ficam em
st.session_state.dados e os widgets só os espelham (ver campo()).
"""
import copy
import uuid

import streamlit as st

from mocks import mock_data as m
from services import data_service as svc

MENU = [
    ("dashboard", "📊  Dashboard"),
    ("importacao", "📥  Importação"),
    ("historias", "💬  Histórias"),
    ("estudio", "✨  Estúdio de Conteúdo"),
    ("curadoria", "✅  Curadoria"),
    ("historico", "🗄️  Histórico"),
]
CATEGORIA_TODAS = "Todas as categorias"
CANAL_TODOS = "Todos os canais"


def _gerar_lote_id():
    """Gera um ID de lote único para cada importação."""
    return "LOTE-" + uuid.uuid4().hex[:6].upper()


def resetar_lote(ss=None):
    """Limpa todo o estado ligado ao lote atual e gera um novo lote_id.

    Deve ser chamada a cada nova importação (via _novo_lote em importacao.py)
    e também pode ser chamada por reiniciar() quando necessário.
    """
    if ss is None:
        ss = st.session_state
    ss.lote_id = _gerar_lote_id()
    ss.historias = []
    ss.proc_status = "novo"        # novo | retry | erro | concluido
    ss.proc_etapas = ["pendente"] * 6
    ss.historia_atual = None
    ss.proc_origem_analise = ""    # "gemini" | "mock" | ""
    ss.proc_erro_oci = ""          # motivo da falha OCI (quando houver)
    ss.proc_erro_analise = ""      # mensagem de erro da análise (quando houver)
    ss.proc_erro_etapa = ""        # etapa onde ocorreu erro
    # Controles de curadoria — limpos para não herdar dados do lote anterior
    ss.validacao_factual = {}
    ss.status_curadoria = {}
    ss.autorizacao = {}
    ss.observacoes = {}
    ss.motivos = {}
    ss.status_ativos = {}          # legado — manter compatibilidade
    ss.regen = {}
    ss.pacotes_oci = []


def init_state():
    ss = st.session_state
    if ss.get("_iniciado"):
        return
    ss._iniciado = True
    ss.pagina = "dashboard"
    ss.dados = {}
    ss.interacoes = copy.deepcopy(m.INTERACOES)
    ss.arquivo = {"nome": m.ARQUIVO_DEMO, "tamanho": m.ARQUIVO_DEMO_TAMANHO, "origem": "Arquivo JSON"}
    ss.ultimo_upload = None
    ss.toast = None
    ss.mostrar_copia = False
    # Inicializa o lote com estado neutro (sem rodar análise no boot — Issue #27)
    resetar_lote(ss)
    # Mantém o lote_id demo para a primeira carga
    ss.lote_id = m.LOTE_ID


def reiniciar():
    st.session_state.clear()


def ir_para(pagina):
    st.session_state.pagina = pagina


def campo(widget, label, chave, padrao, **kwargs):
    """Cria um widget cujo valor sobrevive à troca de tela."""
    ss = st.session_state
    wkey = f"w::{chave}"
    if chave not in ss.dados:
        ss.dados[chave] = padrao
    if wkey not in ss:
        ss[wkey] = ss.dados[chave]

    def _sincronizar():
        ss.dados[chave] = ss[wkey]

    return widget(label, key=wkey, on_change=_sincronizar, **kwargs)


def definir(chave, valor):
    """Altera um valor guardado e o widget que o espelha (use antes do widget ou em callbacks)."""
    ss = st.session_state
    ss.dados[chave] = valor
    ss[f"w::{chave}"] = valor


def valor(chave, padrao=None):
    return st.session_state.dados.get(chave, padrao)


def historia_por_id(hid):
    for h in st.session_state.historias:
        if h["id"] == hid:
            return h
    return None


def resumo_ativos():
    """Conta ativos por status em todas as histórias."""
    contagem = {"rascunho": 0, "aprovado": 0, "rejeitado": 0}
    for status in st.session_state.status_ativos.values():
        contagem[status] += 1
    return contagem
