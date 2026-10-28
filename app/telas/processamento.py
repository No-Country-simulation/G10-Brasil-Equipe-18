
import os
import time

import streamlit as st

from services import data_service as svc
from state import ir_para
from styles import caixa, cabecalho, esc, md, topbar


ETAPAS = [
    ("Limpeza dos dados", "Normalização dos campos e remoção de duplicatas.", "limpando os dados"),
    ("Análise de sentimento e tópicos", "Classificação das mensagens e dos temas da comunidade.", "analisando sentimento e tópicos"),
    ("Detecção de histórias", "Identificação de relatos com potencial de marketing.", "detectando histórias"),
    ("Extração de fatos e citações", "Separação de evidências e trechos das mensagens de origem.", "extraindo fatos e citações"),
    ("Geração de ativos", "Criação de rascunhos para revisão humana.", "gerando rascunhos"),
    ("Salvando no OCI", "Armazenamento das histórias, evidências e rascunhos.", "salvando no OCI"),
]

VISUAL = {
    "concluida": ("ico-ok", "✓", "Concluída", "s-ok"),
    "andamento": ("ico-run", "◔", "Em andamento", "s-run"),
    "pendente": ("ico-pen", "", "Pendente", "s-pen"),
    "erro": ("ico-err", "!", "Erro", "s-err"),
}

ATRASO = float(os.environ.get("COMMUNITYLAB_DELAY", "0.9"))


def _retry():
    st.session_state.proc_status = "retry"


def _pacotes_confirmados(pacotes):
    return (
        isinstance(pacotes, list)
        and bool(pacotes)
        and all(
            isinstance(p, dict)
            and p.get("status") == "salvo"
            and p.get("persistencia") == "real"
            for p in pacotes
        )
    )


def _motivo_falha(pacotes):
    if not isinstance(pacotes, list) or not pacotes:
        return "Nenhum pacote foi confirmado pelo serviço de armazenamento."
    motivos = [
        str(p.get("motivo"))
        for p in pacotes
        if isinstance(p, dict)
        and (p.get("status") != "salvo" or p.get("persistencia") != "real")
        and p.get("motivo")
    ]
    return "; ".join(dict.fromkeys(motivos)) or "Nem todos os pacotes foram confirmados no OCI."


def _desenhar(etapas, botoes):
    ss = st.session_state
    concluidas = etapas.count("concluida")
    em_andamento = "andamento" in etapas
    com_erro = "erro" in etapas
    pct = round((concluidas + (0.5 if em_andamento else 0)) / len(etapas) * 100)
    acao = next((ETAPAS[i][2] for i, e in enumerate(etapas) if e == "andamento"), "")
    pacotes = ss.get("pacotes_oci", [])
    persistido = etapas[5] == "concluida" and _pacotes_confirmados(pacotes)
    origem = ss.get("proc_origem_analise", "")
    demonstrativo = origem == "mock"
    erro_analise = ss.get("proc_erro_etapa") == "analise"

    if com_erro:
        titulo, sub, selo, tom = (
            "Processamento interrompido",
            f"{concluidas} de 6 etapas concluídas · ação necessária",
            "Ação necessária", "red",
        )
    elif persistido and concluidas == len(etapas):
        titulo, sub, selo, tom = "Processamento concluído", "6 de 6 etapas concluídas", "Concluído", "green"
    else:
        titulo, sub, selo, tom = (
            "Analisando suas interações",
            f"{concluidas} de 6 etapas concluídas · {acao}",
            "Em andamento", "purple",
        )

    md(
        '<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<span><b>Lote {esc(ss.lote_id)}</b> <span class="cl-muted">/ {esc(ss.arquivo["nome"])}</span></span>'
        f'<span class="chip chip-{tom}">{selo}</span></div>'
    )
    esq, dir_ = st.columns([2.1, 1])
    with esq:
        with st.container(border=True):
            cor = "#B93A32" if com_erro else "#5B3DF5"
            classe_erro = "erro" if com_erro else ""
            md(
                '<div style="display:flex;justify-content:space-between;font-size:20px;font-weight:600;">'
                f'<span>{titulo}</span><span style="color:{cor};">{pct}%</span></div>'
                f'<div class="cl-progress {classe_erro}"><div style="width:{pct}%"></div></div>'
                f'<div class="cl-muted">{sub}</div>'
            )
            passos = ""
            for (nome, desc, _), estado in zip(ETAPAS, etapas):
                classe, simbolo, rotulo, cor_s = VISUAL[estado]
                passos += (
                    f'<div class="cl-step"><div class="ico {classe}">{simbolo}</div>'
                    f'<div class="txt"><div class="t">{nome}</div><div class="d">{desc}</div></div>'
                    f'<div class="s {cor_s}">{rotulo}</div></div>'
                )
            md(passos)
    with dir_:
        with st.container(border=True):
            canais = len({i["canal"] for i in ss.interacoes})
            historias_ok = etapas[4] == "concluida"
            historias = ss.get("historias", []) if historias_ok else []
            quantidade_ativos = sum(
                len(h.get("ativos", [])) for h in historias if isinstance(h, dict)
            )
            if historias_ok:
                if persistido:
                    situacao = f"{quantidade_ativos} rascunhos · salvos no OCI"
                elif com_erro:
                    situacao = f"{quantidade_ativos} rascunhos · gravação não confirmada"
                else:
                    situacao = f"{quantidade_ativos} rascunhos · aguardando gravação"
            else:
                situacao = "Ativos ainda não gerados"
            ambiente = "Demonstração" if demonstrativo else "Análise real" if origem == "gemini" else "Não confirmado"
            md(
                '<b style="font-size:17px;">Resumo do lote</b>'
                '<hr style="margin:10px 0;border:none;border-top:1px solid #EEF0F4;">'
                f'<div class="cl-kv"><span>Interações</span><span>{len(ss.interacoes)}</span></div>'
                f'<div class="cl-kv"><span>Canais</span><span>{canais}</span></div>'
                f'<div class="cl-kv"><span>Origem</span><span>{esc(ss.arquivo["origem"])}</span></div>'
                f'<div class="cl-kv"><span>Ambiente</span><span>{ambiente}</span></div>'
                '<hr style="margin:10px 0;border:none;border-top:1px solid #EEF0F4;">'
                f'<b>{len(historias) if historias_ok else "–"} histórias identificadas</b><br>'
                f'<span class="cl-muted">{situacao}</span>'
            )
        with st.container(border=True):
            md(
                '<b>O próximo passo é revisar</b><br><span class="cl-muted">'
                'As mensagens originais serão preservadas. Os ativos gerados são rascunhos '
                'e não serão publicados automaticamente.</span>'
            )

    if demonstrativo and etapas[4] == "concluida":
        caixa(
            "gray",
            "<b>Dados demonstrativos.</b><br>A análise real não foi concluída. "
            "As histórias apresentadas são exemplos e não devem ser tratadas como "
            "resultados extraídos das interações importadas.",
        )

    if com_erro:
        if erro_analise:
            caixa("red", "<b>Falha na análise.</b><br>" + esc(ss.get("proc_erro_analise", "Erro desconhecido.")))
        else:
            motivo = ss.get("proc_erro_oci", "") or _motivo_falha(pacotes)
            caixa(
                "red",
                "<b>Gravação no OCI não confirmada.</b><br>" + esc(motivo)
                + "<br>Os resultados permanecem disponíveis nesta sessão. "
                "Uma nova tentativa não repetirá a análise.",
            )
            if botoes:
                st.button("↻ Tentar novamente", on_click=_retry, key="retry_oci")
    elif persistido and concluidas == len(etapas):
        caixa(
            "green",
            "<b>Processamento concluído.</b> Os pacotes foram confirmados no OCI. "
            "Agora o time pode revisar os resultados.",
        )
        if botoes:
            st.button("Revisar histórias detectadas", type="primary", on_click=ir_para, args=("historias",))
    else:
        caixa(
            "gray",
            "<b>Análise em andamento</b><br>A extração usa o conteúdo das mensagens. "
            "Ao concluir, será possível revisar as histórias e os rascunhos.",
        )
    st.caption("Os ativos são rascunhos sujeitos à revisão humana. Nenhum conteúdo será publicado automaticamente.")


def render():
    ss = st.session_state
    topbar()
    cabecalho(
        "Etapa 2 de 4 · Analisar", "Processamento",
        "Acompanhe a análise das interações e a preparação dos rascunhos para o seu time.",
    )

    if ss.proc_status not in ("novo", "retry"):
        _desenhar(ss.proc_etapas, botoes=True)
        return

    retry = ss.proc_status == "retry"
    etapas = ["concluida"] * 5 + ["pendente"] if retry else ["pendente"] * 6
    area = st.empty()

    if not retry:
        ss.proc_erro_oci = ""
        ss.proc_erro_analise = ""
        ss.proc_erro_etapa = ""
        ss.proc_origem_analise = ""

        # A primeira etapa é uma preparação visual. A análise real acontece
        # enquanto as etapas 2 a 5 permanecem em andamento.
        etapas[0] = "andamento"
        with area.container():
            _desenhar(etapas, botoes=False)
        time.sleep(ATRASO)
        etapas[0] = "concluida"

        etapas[1] = "andamento"
        with area.container():
            _desenhar(etapas, botoes=False)
        try:
            historias = svc.analisar(ss.interacoes)
            origem = svc.ORIGEM_ANALISE
        except Exception as erro:
            etapas[1] = "erro"
            ss.proc_status = "erro"
            ss.proc_erro_etapa = "analise"
            ss.proc_erro_analise = str(erro)
            ss.proc_etapas = etapas
            with area.container():
                _desenhar(etapas, botoes=True)
            return

        # O serviço devolve uma análise completa (ou um fallback demonstrativo).
        # Não atribuímos conclusão a etapas subsequentes antes desse retorno.
        ss.historias = historias
        ss.proc_origem_analise = origem
        etapas[1] = "concluida"
        for i in range(2, 5):
            etapas[i] = "andamento"
            with area.container():
                _desenhar(etapas, botoes=False)
            time.sleep(ATRASO)
            etapas[i] = "concluida"

    etapas[5] = "andamento"
    with area.container():
        _desenhar(etapas, botoes=False)

    try:
        if ss.get("dados", {}).get("demo_erro_oci"):
            raise RuntimeError("Falha demonstrativa de gravação no OCI.")
        pacotes = svc.salvar_no_oci(ss.pacotes_oci, ss.lote_id, ss.historias)
        ss.pacotes_oci = pacotes
        if _pacotes_confirmados(pacotes):
            etapas[5] = "concluida"
            ss.proc_status = "concluido"
            ss.proc_erro_oci = ""
        else:
            etapas[5] = "erro"
            ss.proc_status = "erro"
            ss.proc_erro_oci = _motivo_falha(pacotes)
    except Exception as erro:
        etapas[5] = "erro"
        ss.proc_status = "erro"
        ss.proc_erro_oci = str(erro)

    ss.proc_etapas = etapas
    with area.container():
        _desenhar(etapas, botoes=True)
