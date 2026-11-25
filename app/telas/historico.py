"""Tela Histórico - Consulta e recuperação de registros persistidos no OCI."""
import json
import os

import streamlit as st

from mocks import mock_data as m
from services import data_service as svc
from state import campo, definir, ir_para, resetar_lote, valor
from styles import caixa, cabecalho, chip, esc, md, topbar

# Modo demonstração: lê diretamente da variável de ambiente (evita import pesado de src/)
_modo_demo_str = os.getenv("MODO_DEMONSTRACAO", "").lower()
MODO_DEMONSTRACAO: bool = _modo_demo_str in ("1", "true", "sim")

try:
    _dialogo = st.dialog
except AttributeError:  # pragma: no cover
    _dialogo = st.experimental_dialog

FILTROS = ["Todos", "Salvos", "Com erro"]
ESTADOS_DEMO = ["Normal", "Vazio", "Carregando", "Erro de conexão"]


def deve_exibir_erro(motivo_erro: str, modo_demo: bool) -> bool:
    """Decide se um erro de armazenamento deve ser exibido ao usuário.
    
    Regras:
    - Erro de credencial: exibe apenas se modo_demo=False
    - Erro operacional (rede, permissão, etc.): sempre exibe
    
    Args:
        motivo_erro: Mensagem de erro retornada pelo armazenamento
        modo_demo: True se o sistema está em modo demonstração
    
    Returns:
        True se o erro deve ser exibido, False caso contrário
    """
    if not motivo_erro:
        return False
    
    eh_erro_credencial = "credencial" in motivo_erro.lower()
    
    # Erro de credencial só aparece fora do modo demo
    if eh_erro_credencial:
        return not modo_demo
    
    # Erros operacionais sempre aparecem
    return True


@_dialogo("Visualizar JSON", width="large")
def _dialogo_json(caminho):
    dados = svc.conteudo_pacote(caminho)
    if dados is None:
        st.caption(caminho)
        caixa("red", "<b>Não foi possível ler este objeto</b><br>"
                     "O arquivo não existe no bucket ou a leitura falhou. "
                     "Nenhum conteúdo fictício é exibido.")
        st.caption("Os ativos são rascunhos e aguardam revisão humana.")
        return
    conteudo = json.dumps(dados, ensure_ascii=False, indent=2)
    st.caption(f"{caminho} · Salvo com sucesso")
    st.code(conteudo, language="json")
    st.download_button("⬇ Baixar", data=conteudo, file_name=caminho.split("/")[-1], mime="application/json", key="dl_dialogo")
    st.caption("Os ativos são rascunhos e aguardam revisão humana.")


def aplicar_lote_recuperado(ss, lote):
    """Troca o lote da sessão pelo lote recuperado do bucket.

    Não analisa nada: só preenche o estado com o que veio do pacote. Deve rodar
    num callback (on_click), antes de os widgets serem desenhados.
    """
    resetar_lote(ss)
    # resetar_lote não limpa estas chaves; sem isso sobrariam interações do lote anterior.
    ss.interacoes = []
    ss.ultimo_upload = None
    ss.avisos_discord = []
    ss.rejeitadas_discord = []

    ss.lote_id = lote["lote_id"]
    ss.historias = lote["historias"]
    ss.arquivo = {"nome": f"Lote {lote['lote_id']} reaberto do Histórico", "tamanho": "", "origem": "Histórico (OCI)"}
    ss.proc_status = "concluido"
    ss.proc_etapas = ["concluida"] * 6
    ss.proc_origem_analise = lote.get("origem_analise") or ""
    ss.pacotes_oci = list(lote["pacotes"])
    ss.dados["natureza_dados"] = lote["natureza_dados"]
    ss["w::natureza_dados"] = lote["natureza_dados"]  # o widget da Importação espelha este valor
    ss.natureza_travada = True

    for chave, decisao in lote["decisoes"].items():
        status = decisao["status_curadoria"]
        ss.validacao_factual[chave] = decisao["validacao_factual"]
        ss.status_curadoria[chave] = status
        ss.autorizacao[chave] = decisao["autorizacao"]
        # O parecer volta para o campo do status gravado (observação ou motivo).
        campo_parecer = svc.campo_do_parecer(status)
        if decisao["parecer"] and campo_parecer == "observacoes":
            ss.observacoes[chave] = decisao["parecer"]
        elif decisao["parecer"] and campo_parecer == "motivos":
            ss.motivos[chave] = decisao["parecer"]


def _reabrir_lote(caminho):
    """Callback do botão: se a leitura falhar, a sessão atual fica como estava."""
    ss = st.session_state
    lote = svc.recuperar_lote(caminho)
    if not lote.get("ok"):
        ss.erro_reabertura = lote.get("motivo") or "Não foi possível reabrir o lote."
        return
    aplicar_lote_recuperado(ss, lote)
    ss.erro_reabertura = ""
    ss.aviso_reabertura = " ".join(lote["avisos"])
    ss.toast = f"Lote {lote['lote_id']} reaberto. Nenhuma análise foi repetida."
    ir_para("curadoria")


@_dialogo("Reabrir este lote?")
def _dialogo_reabrir(caminho, lote):
    ss = st.session_state
    st.write(f"O lote atual da sessão ({ss.lote_id}) será substituído pelo lote {lote}.")
    if ss.get("erro_curadoria"):
        caixa("red", "<b>Há decisões que não foram gravadas no bucket.</b><br>"
                     "Se você continuar, elas serão perdidas.")
    else:
        st.caption("As decisões já gravadas no bucket não são apagadas.")
    c1, c2 = st.columns(2)
    if c1.button("Cancelar", key="reabrir_cancelar"):
        st.rerun()
    if c2.button("Reabrir lote", type="primary", key="reabrir_confirmar",
                 on_click=_reabrir_lote, args=(caminho,)):
        st.rerun()


def _tentar_de_novo(indice):
    ss = st.session_state
    ss.pacotes_oci[indice] = svc.reenviar_pacote(ss.pacotes_oci[indice])
    ss.toast = "Pacote salvo no OCI."


def _reconectar():
    definir("demo_estado_oci", "Normal")


def _metricas(bucket, lotes, legenda_lotes, ultima, legenda_ultima, skeleton=False):
    c1, c2, c3 = st.columns(3)
    itens = [(c1, "Bucket", bucket, "Object Storage"), (c2, "Lotes salvos", lotes, legenda_lotes),
             (c3, "Última gravação", ultima, legenda_ultima)]
    for coluna, rotulo, grande, legenda in itens:
        with coluna:
            with st.container(border=True):
                if skeleton:
                    md(f'<span class="cl-muted">{rotulo}</span><div class="cl-skel" style="width:70%;height:26px;"></div>'
                       '<span class="cl-muted">Consultando o bucket...</span>')
                else:
                    md(f'<span class="cl-muted">{rotulo}</span><div class="cl-big" style="font-size:22px;">{esc(grande)}</div>'
                       f'<span class="cl-muted">{esc(legenda)}</span>')


def _tabela(pacotes):
    ss = st.session_state
    filtro = campo(st.radio, "Filtro", "f:oci", "Todos", options=FILTROS, horizontal=True, label_visibility="collapsed")
    if filtro == "Salvos":
        visiveis = [(i, p) for i, p in enumerate(pacotes) if p["status"] == "salvo"]
    elif filtro == "Com erro":
        visiveis = [(i, p) for i, p in enumerate(pacotes) if p["status"] == "falhou"]
    else:
        visiveis = list(enumerate(pacotes))
    larguras = [2.8, 1.0, 1.3, 0.8, 1.5, 4.2]
    cab = st.columns(larguras)
    for col, titulo in zip(cab, ["Caminho do objeto", "Lote", "Data", "Tamanho", "Status", "Ações"]):
        col.markdown(f'<span class="cl-muted">{titulo}</span>', unsafe_allow_html=True)
    for i, p in visiveis:
        st.divider()
        c = st.columns(larguras)
        c[0].markdown(f'📄 {p["caminho"]}')
        c[1].markdown(f'<span class="cl-muted">{p["lote"]}</span>', unsafe_allow_html=True)
        c[2].markdown(f'<span class="cl-muted">{p["data"] or "Não salvo"}</span>', unsafe_allow_html=True)
        c[3].markdown(f'<span class="cl-muted">{p["tamanho"] or "–"}</span>', unsafe_allow_html=True)
        if p["status"] == "salvo":
            c[4].markdown(chip("Salvo com sucesso", "green"), unsafe_allow_html=True)
            a1, a2, a3 = c[5].columns(3)
            if a1.button("</> Ver JSON", key=f"ver_{p['caminho']}"):
                _dialogo_json(p["caminho"])
            if "evidencia" not in p["caminho"]:  # só o pacote principal carrega as histórias
                if ss.historias:
                    if a3.button("↺ Reabrir", key=f"reabrir_{p['caminho']}"):
                        _dialogo_reabrir(p["caminho"], p["lote"])
                else:
                    a3.button("↺ Reabrir", key=f"reabrir_{p['caminho']}",
                              on_click=_reabrir_lote, args=(p["caminho"],))
            # Não lê o objeto durante a renderização: uma leitura por linha deixava a
            # tela lenta. O diálogo lê só no clique e já traz o botão de baixar.
            if a2.button("⬇ Baixar", key=f"dl_{p['caminho']}"):
                _dialogo_json(p["caminho"])
        else:
            c[4].markdown(chip("Falhou", "red"), unsafe_allow_html=True)
            c[5].button("↻ Tentar novamente", key=f"retry_{p['caminho']}", on_click=_tentar_de_novo, args=(i,))
    if not visiveis:
        st.caption("Nenhum pacote neste filtro.")
    st.divider()
    salvos = [p for p in pacotes if p["status"] == "salvo"]
    lotes = {p["lote"] for p in salvos}
    erros = len(pacotes) - len(salvos)
    st.caption(f"{len(pacotes)} objetos · {len(lotes)} lote salvo · {erros} objeto com erro")


def lote_mais_recente(pacotes):
    """Pacote gravado mais recentemente, ou None quando nao ha nenhum."""
    return max(pacotes, key=lambda p: p.get("salvo_em") or "") if pacotes else None


def render():
    ss = st.session_state
    estado = valor("demo_estado_oci", "Normal")
    topbar()
    cabecalho("Etapa 4 de 4 · Armazenamento", "Histórico",
              "Pacotes de histórias, evidências e rascunhos salvos no seu bucket.", extra=chip("OCI Always Free", "green"))

    # Fonte principal e o bucket: recarregar a pagina nao pode esconder o que
    # ja foi gravado. A sessao serve de apoio quando o bucket esta vazio.
    pacotes = svc.listar_pacotes()
    if not pacotes:
        pacotes = ss.pacotes_oci
    vistos = set()
    unicos = []
    for pacote in pacotes:
        chave = pacote.get("caminho")
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(pacote)
    pacotes = unicos
    if ss.get("erro_reabertura"):
        caixa("red", f"<b>Não foi possível reabrir o lote</b><br>{esc(ss.erro_reabertura)}<br>"
                     "O lote que estava aberto na sessão foi mantido.")
    motivo_erro = svc.erro_armazenamento()
    # Em modo demonstração (MODO_DEMONSTRACAO), oculta erro de credencial
    # Fora do modo demonstração, mostra erro de credencial explicitamente
    if deve_exibir_erro(motivo_erro, MODO_DEMONSTRACAO):
        caixa("red", f"<b>Falha ao consultar o bucket</b><br>{motivo_erro}")
    if estado == "Erro de conexão":
        c1, c2 = st.columns([4, 1])
        with c1:
            caixa("red", "<b>Não foi possível consultar o bucket</b><br>Verifique a conexão com a OCI e tente novamente. Os dados atuais não estão disponíveis.")
        with c2:
            st.button("↻ Tentar novamente", on_click=_reconectar)
        _metricas(svc.bucket_atual() or "indisponível", "Indisponível", "Não foi possível atualizar", "Não consultada", "Sem dados atuais do bucket")
        with st.container(border=True):
            md('<b style="font-size:18px;">Pacotes salvos</b>')
            md('<div style="text-align:center;padding:40px 0;">☁️<br><b>Os pacotes não puderam ser carregados</b><br>'
               '<span class="cl-muted">A lista será exibida quando a conexão com o bucket for restabelecida.</span></div>')
    elif estado == "Carregando":
        _metricas("", "", "", "", "", skeleton=True)
        with st.container(border=True):
            md('<b style="font-size:18px;">Pacotes salvos</b>' + '<div class="cl-skel"></div>' * 6
               + '<span class="cl-muted">Consultando pacotes no Object Storage...</span>')
    elif estado == "Vazio" or not pacotes:
        _metricas(svc.bucket_atual() or "indisponível", "0", "Nenhum lote processado", "Nenhuma gravação", "Aguardando o primeiro lote")
        with st.container(border=True):
            md('<b style="font-size:18px;">Pacotes salvos</b>')
            md('<div style="text-align:center;padding:30px 0;">📂<br><b>Nenhum pacote salvo ainda</b><br>'
               '<span class="cl-muted">Processe um lote na Importação para guardar seus primeiros pacotes.</span></div>')
            st.button("→ Ir para Importação", type="primary", on_click=ir_para, args=("importacao",))
    else:
        salvos = [p for p in pacotes if p["status"] == "salvo"]
        lotes = {p["lote"] for p in salvos}
        ultima = (lote_mais_recente(salvos) or {}).get("data")
        lote_recente = (lote_mais_recente(salvos) or {}).get("lote")
        _metricas(svc.bucket_atual() or "indisponível", str(len(lotes)), f"{len(salvos)} objetos no bucket", ultima or "Nenhuma gravação",
                  f"Lote {lote_recente}" if lote_recente else "Aguardando o primeiro lote")
        with st.container(border=True):
            md('<b style="font-size:18px;">Pacotes salvos</b>')
            _tabela(pacotes)
    caixa("gray", "ⓘ Os pacotes guardam as histórias, os trechos citados e os rascunhos, não as mensagens originais. Nada é publicado automaticamente.")
