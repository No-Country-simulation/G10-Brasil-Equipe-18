"""Estado da aplicação (st.session_state) e helpers.

Obs.: o Streamlit apaga o estado de widgets que não aparecem numa execução
(por exemplo ao trocar de tela). Por isso os valores editáveis ficam em
st.session_state.dados e os widgets só os espelham (ver campo()).
"""
import copy

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


def init_state():
    ss = st.session_state
    if ss.get("_iniciado"):
        return
    ss._iniciado = True
    ss.pagina = "dashboard"
    ss.dados = {}
    ss.interacoes = copy.deepcopy(m.INTERACOES)
    ss.arquivo = {"nome": m.ARQUIVO_DEMO, "tamanho": m.ARQUIVO_DEMO_TAMANHO, "origem": "Arquivo JSON"}
    ss.lote_id = m.LOTE_ID
    ss.ultimo_upload = None
    ss.historias = svc.analisar(ss.interacoes)
    ss.proc_status = "novo"  # novo | retry | erro | concluido
    ss.proc_etapas = ["pendente"] * 6
    ss.historia_atual = None
    # Controles da Curadoria (3 dimensões independentes)
    ss.validacao_factual = {}  # "hist:ativo" -> pendente | validada | insuficiente | contradicao
    ss.status_curadoria = {}  # "hist:ativo" -> rascunho | ajustes | aprovado | rejeitado
    ss.autorizacao = {}  # "hist:ativo" -> nao_registrada | registrada
    ss.observacoes = {}  # "hist:ativo" -> texto de observação
    ss.motivos = {}  # "hist:ativo" -> texto de motivo de rejeição
    # Legado (manter compatibilidade)
    ss.status_ativos = {}  # "hist:ativo" -> rascunho | aprovado | rejeitado (legado)
    ss.regen = {}
    ss.pacotes_oci = svc.listar_pacotes()
    ss.toast = None
    ss.mostrar_copia = False
    inicializar_controles_historias(ss.historias)


def inicializar_controles_historias(historias):
    """Garante que todas as histórias e ativos possuam controles de curadoria inicializados."""
    ss = st.session_state
    if "status_ativos" not in ss:
        ss.status_ativos = {}
    if "validacao_factual" not in ss:
        ss.validacao_factual = {}
    if "status_curadoria" not in ss:
        ss.status_curadoria = {}
    if "autorizacao" not in ss:
        ss.autorizacao = {}
    for h in historias or []:
        for a in h.get("ativos", []):
            chave = f"{h['id']}:{a['id']}"
            if chave not in ss.status_ativos:
                ss.status_ativos[chave] = "rascunho"
            if chave not in ss.validacao_factual:
                ss.validacao_factual[chave] = "pendente"
            if chave not in ss.status_curadoria:
                ss.status_curadoria[chave] = "rascunho"
            if chave not in ss.autorizacao:
                ss.autorizacao[chave] = "nao_registrada"


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
