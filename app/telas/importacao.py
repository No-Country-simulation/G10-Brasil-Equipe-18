"""Tela Importação - Upload de interações da comunidade."""
import json
from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st

from services import data_service as svc
from state import CANAL_TODOS, campo, definir, ir_para, valor
from styles import cabecalho, chip, esc, md, topbar


def render():
    topbar()
    cabecalho(
        "Etapa 1 de 4 · Importar",
        "Importação",
        "Carregue conversas da comunidade para identificar histórias com potencial de marketing.",
    )
    with st.container(border=True):
        aba_upload, aba_json, aba_discord = st.tabs(
            ["⬆️ Upload de arquivo", "{ } Colar JSON", "💬 Discord"]
        )
        with aba_upload:
            _upload()
        with aba_json:
            _colar_json()
        with aba_discord:
            _discord()
    _avisos_discord()
    _previa()
    _rodape()


def _estrutura_dados():
    md(
        '<b>Estrutura dos dados</b><br><span class="cl-muted">Cada interação deve conter os campos:</span><br>'
        + "".join(chip(c) for c in ("autor", "canal", "tipo", "texto"))
        + '<br><span class="cl-muted">Use mensagens de origem. Os ativos de marketing serão gerados em uma etapa posterior.</span>'
    )


def _novo_id_lote():
    instante = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"LOTE-{instante}-{uuid4().hex.upper()}"


def _novo_lote(interacoes, nome, tamanho, origem):
    ss = st.session_state
    ss.lote_id = _novo_id_lote()
    ss.interacoes = interacoes
    ss.historias = []
    ss.historia_atual = None
    ss.pacotes_oci = []
    ss.arquivo = {"nome": nome, "tamanho": tamanho, "origem": origem}
    ss.proc_status = "novo"
    ss.avisos_discord = []
    ss.rejeitadas_discord = []
    definir("f:canal", CANAL_TODOS)


def _normalizar_interacoes_discord(interacoes):
    """Adapta mensagens Discord ao contrato usado pelas telas do front."""
    itens = []
    for item in interacoes:
        id_discord = str(item.get("id_discord", ""))
        id_interacao = int(id_discord) if id_discord.isdigit() else item.get("id")
        itens.append(
            {
                "id": id_interacao,
                "autor": item.get("autor_id") or "membro_desconhecido",
                "canal": item.get("canal", "Discord"),
                "tipo": item.get("tipo") or "mensagem",
                "texto": item.get("texto", ""),
            }
        )
    return svc.interacoes_de_json(json.dumps(itens, ensure_ascii=False))


def _discord():
    canal_id = campo(
        st.text_input,
        "ID do canal Discord",
        "discord_canal_id",
        "",
        placeholder="Usa CANAL_ID das configurações se ficar vazio",
    )
    st.caption(
        "O token do bot deve estar em DISCORD_TOKEN no ambiente ou em st.secrets; "
        "não o cole nesta tela."
    )
    limite = st.slider(
        "Quantidade de mensagens",
        min_value=10,
        max_value=100,
        value=50,
        step=10,
        key="discord_limite",
    )
    if st.button("Buscar mensagens do Discord", type="primary", key="buscar_discord"):
        _buscar_discord((canal_id or "").strip() or None, limite)


def _buscar_discord(canal_id, limite):
    ss = st.session_state
    ss.avisos_discord = []
    ss.rejeitadas_discord = []
    try:
        after_id = svc.carregar_cursor_discord()
        interacoes, rejeitadas, avisos = svc.buscar_mensagens_discord(
            canal_id=canal_id,
            after_id=after_id,
            limite=limite,
        )
    except Exception as erro:
        st.error(f"Não foi possível consultar o Discord ou o cursor no OCI: {erro}")
        return

    ss.rejeitadas_discord = rejeitadas
    if not interacoes:
        ss.avisos_discord = [
            aviso for aviso in avisos
            if svc.after_id_discord([aviso]) is None
        ]
        if not avisos and not rejeitadas:
            st.info("Não há mensagens novas neste canal.")
        elif rejeitadas:
            st.warning(
                "A consulta não encontrou mensagens válidas para importar. "
                "O cursor não será avançado."
            )
        return

    try:
        normalizadas = _normalizar_interacoes_discord(interacoes)
    except ValueError as erro:
        ss.avisos_discord = [
            aviso for aviso in avisos
            if svc.after_id_discord([aviso]) is None
        ]
        st.error(f"As mensagens do Discord não puderam ser preparadas: {erro}")
        return

    canal = canal_id or interacoes[0].get("canal", "Discord")
    quantidade = len(normalizadas)
    nome = f"Discord · {canal}"
    tamanho = f"{quantidade} mensagem" + ("s" if quantidade != 1 else "")
    _novo_lote(normalizadas, nome, tamanho, "Discord")
    ss.avisos_discord = avisos
    ss.rejeitadas_discord = rejeitadas
    ss.discord_canal_id = canal
    st.success(f"{quantidade} mensagens do Discord carregadas para revisão.")


def _avisos_discord():
    ss = st.session_state
    avisos = [
        aviso for aviso in ss.get("avisos_discord", [])
        if svc.after_id_discord([aviso]) is None
    ]
    if avisos:
        with st.expander("Avisos da importação do Discord", expanded=True):
            for aviso in avisos:
                st.warning(aviso)

    rejeitadas = ss.get("rejeitadas_discord", [])
    if rejeitadas:
        with st.expander(f"Mensagens descartadas ({len(rejeitadas)})"):
            for item in rejeitadas:
                st.write(f"Mensagem {item.get('posicao')}: {item.get('motivo')}")


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
        arquivo_status = (
            "carregado com sucesso"
            if ss.arquivo.get("origem") in ("Arquivo CSV", "Arquivo JSON")
            else "Aguardando seleção de arquivo"
        )
        md(
            '<div style="border:1px solid #E2E8F0;border-radius:10px;padding:12px 14px;background:#fff;">'
            f'📄 <b>{esc(ss.arquivo["nome"])}</b><br>'
            f'<span class="cl-muted">{esc(ss.arquivo["tamanho"])} · {arquivo_status}</span></div>'
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
    padrao = svc.interacoes_demo_json()
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
    
    origem = ss.arquivo.get("origem", "")
    if not interacoes:
        detalhe = "Nenhuma fonte carregada. Escolha uma aba acima para importar dados."
    elif origem == "Discord":
        detalhe = f"{esc(origem)} · {len(canais)} canais"
    else:
        detalhe = f"Lote demonstrativo · {len(canais)} canais · mensagens fictícias"
    with st.container(border=True):
        esq, dir_ = st.columns([3, 1])
        with esq:
            md(
                f'<span style="font-size:20px;font-weight:600;">Prévia das interações</span> &nbsp;{chip(f"{len(interacoes)} carregadas", "green")}'
                f'<br><span class="cl-muted">{detalhe}</span>'
            )
        with dir_:
            escolhido = campo(st.selectbox, "Filtrar por canal", "f:canal", CANAL_TODOS, options=opcoes)
        linhas = interacoes if escolhido == CANAL_TODOS else [i for i in interacoes if i["canal"] == escolhido]
        md(_tabela_html(linhas))
        resumo = (
            f"Exibindo {len(linhas)} de {len(interacoes)} interações · Lote {ss.lote_id}"
            if interacoes
            else "Nenhuma interação carregada."
        )
        st.caption(resumo)


def _analisar():
    ss = st.session_state
    ss.proc_status = "novo"
    ir_para("processamento")


def _rodape():
    ss = st.session_state
    n = len(ss.interacoes)
    origem = ss.arquivo.get("origem")
    if not n:
        nota = "Escolha uma fonte nas abas acima para carregar interações."
    elif origem == "Discord":
        nota = (
            "Mensagens importadas do Discord. Autores pseudonimizados; "
            "revise as evidências antes de usar qualquer conteúdo."
        )
    else:
        nota = "Exemplo fictício. Não representa depoimentos reais do Programa ONE."
    esq, dir_ = st.columns([3, 1])
    with esq:
        md(
            f'<b>{n} interações prontas para análise</b><br>'
            f'<span class="cl-muted">{nota}</span>'
        )
    with dir_:
        st.button("📥 Importar interações", type="primary", on_click=_analisar, disabled=n == 0)
