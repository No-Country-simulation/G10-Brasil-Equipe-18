"""Tela Importação - Upload de interações da comunidade."""
import json

import streamlit as st

from mocks import mock_data as m
from services import data_service as svc
from state import CANAL_TODOS, campo, definir, ir_para, resetar_lote, valor
from styles import cabecalho, chip, esc, md, topbar


def render():
    topbar()
    cabecalho(
        "Etapa 1 de 4 · Importar",
        "Importação",
        "Carregue conversas da comunidade para identificar histórias com potencial de marketing.",
    )
    with st.container(border=True):
        aba_upload, aba_json = st.tabs(["⬆️ Upload de arquivo", "{ } Colar JSON"])
        with aba_upload:
            _upload()
        with aba_json:
            _colar_json()
    _previa()
    _rodape()


def _estrutura_dados():
    md(
        '<b>Estrutura dos dados</b><br><span class="cl-muted">Cada interação deve conter os campos:</span><br>'
        + "".join(chip(c) for c in ("autor", "canal", "tipo", "texto"))
        + '<br><span class="cl-muted">Use mensagens de origem. Os ativos de marketing serão gerados em uma etapa posterior.</span>'
    )


def _novo_lote(interacoes, nome, tamanho, origem):
    ss = st.session_state
    resetar_lote(ss)
    ss.interacoes = interacoes
    ss.arquivo = {"nome": nome, "tamanho": tamanho, "origem": origem}
    ss.proc_status = "novo"
    definir("f:canal", CANAL_TODOS)


def _upload():
    ss = st.session_state
    esq, dir_ = st.columns([2.4, 1])
    with esq:
        arquivo = st.file_uploader("Selecione um arquivo CSV ou JSON", type=["csv", "json"])
        if arquivo is not None:
            marca = (arquivo.name, arquivo.size)
            if ss.ultimo_upload != marca:
                try:
                    itens = svc.parse_interacoes(arquivo.name, arquivo.getvalue())
                    tamanho = f"{arquivo.size / 1024:.1f} KB".replace(".", ",")
                    origem = "Arquivo CSV" if arquivo.name.lower().endswith(".csv") else "Arquivo JSON"
                    _novo_lote(itens, arquivo.name, tamanho, origem)
                    ss.ultimo_upload = marca
                except ValueError as erro:
                    st.error(str(erro))
        md(
            '<div style="border:1px solid #E2E8F0;border-radius:10px;padding:12px 14px;background:#fff;">'
            f'📄 <b>{esc(ss.arquivo["nome"])}</b><br>'
            f'<span class="cl-muted">{esc(ss.arquivo["tamanho"])} · arquivo lido</span></div>'
        )
    with dir_:
        _estrutura_dados()


def _carregar_json():
    texto = valor("json_texto")
    try:
        itens = svc.interacoes_de_json(texto)
    except ValueError:
        return
    _novo_lote(itens, "json_colado.json", f"{len(texto.encode('utf-8')) / 1024:.1f} KB".replace(".", ","), "JSON colado")
    st.session_state.toast = "JSON carregado."


def _colar_json():
    padrao = json.dumps(m.INTERACOES, ensure_ascii=False, indent=2)
    esq, dir_ = st.columns([2.4, 1])
    with esq:
        texto = campo(st.text_area, "Cole um array de interações em JSON", "json_texto", padrao, height=220)
        valido = False
        try:
            n = len(svc.interacoes_de_json(texto))
            valido = True
            md(f'<span style="color:#047857;">✓ JSON válido · {n} interações reconhecidas</span>')
        except ValueError as erro:
            st.error(str(erro))
        st.button("Carregar JSON", disabled=not valido, on_click=_carregar_json)
    with dir_:
        _estrutura_dados()


def _tabela_html(linhas):
    corpo = "".join(
        f'<tr><td class="mut">{esc(str(i.get("_id_efetivo", idx)))}</td>'
        f'<td><b>{esc(i["autor"])}</b></td><td class="mut">{esc(i["canal"])}</td>'
        f'<td class="mut">{esc(i["tipo"])}</td><td>{esc(i["texto"])}</td></tr>'
        for idx, i in enumerate(linhas, start=1)
    )
    return (
        '<table class="cl-table"><thead><tr><th>ID</th><th>autor</th><th>canal</th><th>tipo</th><th>texto</th></tr></thead>'
        f"<tbody>{corpo}</tbody></table>"
    )


def _previa():
    ss = st.session_state
    interacoes = ss.interacoes
    canais = sorted({i["canal"] for i in interacoes})
    opcoes = [CANAL_TODOS] + canais
    if valor("f:canal", CANAL_TODOS) not in opcoes:
        definir("f:canal", CANAL_TODOS)
    
    # Mostrar avisos de IDs inválidos (regra B)
    avisos = svc.avisos_validacao_ids()
    if avisos:
        with st.expander("⚠️ Avisos sobre IDs das interações", expanded=True):
            for aviso in avisos:
                st.warning(aviso, icon="⚠️")
    
    with st.container(border=True):
        esq, dir_ = st.columns([3, 1])
        with esq:
            md(
                f'<span style="font-size:20px;font-weight:600;">Prévia das interações</span> &nbsp;{chip(f"{len(interacoes)} carregadas", "green")}'
                f'<br><span class="cl-muted">Lote demonstrativo · {len(canais)} canais · mensagens fictícias</span>'
            )
        with dir_:
            escolhido = campo(st.selectbox, "Filtrar por canal", "f:canal", CANAL_TODOS, options=opcoes)
        linhas = interacoes if escolhido == CANAL_TODOS else [i for i in interacoes if i["canal"] == escolhido]
        md(_tabela_html(linhas))
        st.caption(f"Exibindo {len(linhas)} de {len(interacoes)} interações · Lote {ss.lote_id}")


def _analisar():
    ss = st.session_state
    ss.proc_status = "novo"
    ir_para("processamento")


def _rodape():
    n = len(st.session_state.interacoes)
    esq, dir_ = st.columns([3, 1])
    with esq:
        md(
            f'<b>{n} interações prontas para análise</b><br>'
            '<span class="cl-muted">Exemplo fictício. Não representa depoimentos reais do Programa ONE.</span>'
        )
    with dir_:
        st.button("📥 Importar interações", type="primary", on_click=_analisar, disabled=n == 0)
