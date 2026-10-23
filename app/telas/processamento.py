import os
import time

import streamlit as st

from services import data_service as svc
from state import inicializar_controles_historias, ir_para
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
# Tempo de cada etapa na simulação (segundos). Dá pra trocar com a variável COMMUNITYLAB_DELAY.
ATRASO = float(os.environ.get("COMMUNITYLAB_DELAY", "0.9"))


def _retry():
    st.session_state.proc_status = "retry"


def _desenhar_conteudo(etapas, botoes, topo_area, progresso_area, passos_area, resumo_area, bottom_area):
    ss = st.session_state
    concluidas = etapas.count("concluida")
    em_andamento = "andamento" in etapas
    com_erro = "erro" in etapas
    pct = round((concluidas + (0.5 if em_andamento else 0)) / len(etapas) * 100)
    if concluidas == len(etapas):
        pct = 100
    acao = next((ETAPAS[i][2] for i, e in enumerate(etapas) if e == "andamento"), "")

    if com_erro:
        titulo, sub, selo, tom = "Gravação interrompida", f"{concluidas} de 6 etapas concluídas · aguardando nova tentativa", "Ação necessária", "red"
    elif concluidas == len(etapas):
        titulo, sub, selo, tom = "Análise concluída", "6 de 6 etapas concluídas", "Concluído", "green"
    else:
        titulo, sub, selo, tom = "Analisando suas interações", f"{concluidas} de 6 etapas concluídas · {acao}", "Em andamento", "purple"

    topo_area.markdown(
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">'
        f'<span><b>Lote {esc(ss.lote_id)}</b> <span class="cl-muted">/ {esc(ss.arquivo["nome"])}</span></span>'
        f'<span class="chip chip-{tom}">{selo}</span></div>',
        unsafe_allow_html=True,
    )

    cor = "#B93A32" if com_erro else "#5B3DF5"
    progresso_area.markdown(
        f'<div style="display:flex;justify-content:space-between;font-size:20px;font-weight:600;">'
        f'<span>{titulo}</span><span style="color:{cor};">{pct}%</span></div>'
        f'<div class="cl-progress {"erro" if com_erro else ""}"><div style="width:{pct}%"></div></div>'
        f'<div class="cl-muted">{sub}</div>',
        unsafe_allow_html=True,
    )

    passos = ""
    for (nome, desc, _), estado in zip(ETAPAS, etapas):
        classe, simbolo, rotulo, cor_s = VISUAL[estado]
        passos += (
            f'<div class="cl-step"><div class="ico {classe}">{simbolo}</div>'
            f'<div class="txt"><div class="t">{nome}</div><div class="d">{desc}</div></div>'
            f'<div class="s {cor_s}">{rotulo}</div></div>'
        )
    passos_area.markdown(passos, unsafe_allow_html=True)

    canais = len({i["canal"] for i in ss.interacoes}) if ss.interacoes else 0
    historias_ok = etapas[2] == "concluida"
    if etapas[4] == "concluida":
        situacao = "6 rascunhos gerados · " + ("gravação pendente" if com_erro else "salvos no OCI" if etapas[5] == "concluida" else "gravando")
    else:
        situacao = "Ativos ainda não gerados"

    origem = svc.obter_origem_analise()
    if origem in ("groq", "gemini"):
        nome_provedor = "Groq" if origem == "groq" else "Gemini"
        ambiente_label = f'<span style="color:#047857;font-weight:600;">✓ IA ({nome_provedor})</span>'
    else:
        ambiente_label = '<span style="color:#B45309;font-weight:600;">⚠ Modo demonstração (mock)</span>'

    resumo_area.markdown(
        '<b style="font-size:17px;">Resumo do lote</b><hr style="margin:10px 0;border:none;border-top:1px solid #EEF0F4;">'
        f'<div class="cl-kv"><span>Interações</span><span>{len(ss.interacoes)}</span></div>'
        f'<div class="cl-kv"><span>Canais</span><span>{canais}</span></div>'
        f'<div class="cl-kv"><span>Origem</span><span>{esc(ss.arquivo["origem"])}</span></div>'
        f'<div class="cl-kv"><span>Ambiente</span><span>{ambiente_label}</span></div>'
        '<hr style="margin:10px 0;border:none;border-top:1px solid #EEF0F4;">'
        f'<b>{len(ss.historias) if historias_ok else "–"} histórias identificadas</b><br>'
        f'<span class="cl-muted">{situacao}</span>',
        unsafe_allow_html=True,
    )

    if botoes or com_erro:
        with bottom_area.container():
            if com_erro:
                caixa("red", "<b>Não foi possível salvar no OCI</b><br>O serviço de armazenamento não respondeu a tempo. "
                             "As histórias e os rascunhos foram preservados nesta execução. "
                             "A nova tentativa retoma apenas a gravação, sem duplicar os resultados.")
                st.button("↻ Tentar novamente", on_click=_retry)
            elif concluidas == len(etapas):
                caixa("green", "<b>Análise concluída.</b> As histórias e os rascunhos foram salvos. Agora é a vez do seu time revisar.")
                st.button("Revisar histórias detectadas", type="primary", on_click=ir_para, args=("historias",))
    else:
        bottom_area.markdown(
            '<div class="cl-box box-gray"><b>Análise em andamento</b><br>'
            'A extração usa apenas o conteúdo das mensagens. '
            'Ao concluir, você poderá revisar as histórias e os rascunhos gerados.</div>',
            unsafe_allow_html=True,
        )


def render():
    ss = st.session_state
    topbar()
    cabecalho("Etapa 2 de 4 · Analisar", "Processamento", "Acompanhe a análise das interações e a preparação dos rascunhos para o seu time.")

    topo_area = st.empty()
    esq, dir_ = st.columns([2.1, 1])
    with esq:
        with st.container(border=True):
            progresso_area = st.empty()
            passos_area = st.empty()
    with dir_:
        with st.container(border=True):
            resumo_area = st.empty()
        with st.container(border=True):
            md(
                '<b>O próximo passo é revisar</b><br><span class="cl-muted">As mensagens originais serão preservadas. '
                "Os ativos gerados são rascunhos e não serão publicados automaticamente.</span>"
            )
    bottom_area = st.empty()
    st.caption("Execução demonstrativa com mensagens fictícias. Nenhum conteúdo será publicado.")

    if ss.proc_status in ("novo", "retry"):
        inicio = 0 if ss.proc_status == "novo" else 5
        etapas = ["concluida"] * inicio + ["pendente"] * (6 - inicio)
        terminou = True

        for i in range(inicio, 6):
            etapas[i] = "andamento"
            _desenhar_conteudo(etapas, False, topo_area, progresso_area, passos_area, resumo_area, bottom_area)

            # Etapa 1 (index 0): limpeza e filtragem real de ruídos e duplicatas (src.preprocessing.limpeza)
            if i == 0 and ss.proc_status == "novo":
                try:
                    interacoes_limpas, rejeitadas = svc.limpar_interacoes_lote(ss.interacoes)
                    if interacoes_limpas:
                        ss.interacoes = interacoes_limpas
                        ss.dados["interacoes_rejeitadas"] = len(rejeitadas)
                except Exception as _e_limp:
                    print(f"[processamento] limpeza falhou: {_e_limp}", flush=True)

            # Etapa 2 (index 1): classificação de sentimentos e tópicos (src.analysis.classificacao)
            elif i == 1 and ss.proc_status == "novo":
                try:
                    ss.interacoes_analisadas = svc.classificar_interacoes_lote(ss.interacoes)
                except Exception as _e_cls:
                    print(f"[processamento] classificacao falhou: {_e_cls}", flush=True)

            # Etapa 3 (index 2): detecção de histórias e ativos com LLM
            elif i == 2 and ss.proc_status == "novo":
                try:
                    ss.historias = svc.analisar(ss.interacoes)
                    inicializar_controles_historias(ss.historias)
                except Exception as _e_analise:
                    print(f"[processamento] analisar falhou: {_e_analise}", flush=True)
                    ss.historias = []
            else:
                time.sleep(ATRASO)

            if i == 5 and ss.get("dados", {}).get("demo_erro_oci"):
                etapas[i] = "erro"
                ss.proc_status = "erro"
                terminou = False
                break
            etapas[i] = "concluida"

        if terminou:
            ss.proc_status = "concluido"
            if not ss.historias:
                ss.historias = svc.analisar(ss.interacoes)
                inicializar_controles_historias(ss.historias)
            ss.pacotes_oci = svc.salvar_no_oci(ss.pacotes_oci, ss.lote_id)
        ss.proc_etapas = etapas
        _desenhar_conteudo(etapas, True, topo_area, progresso_area, passos_area, resumo_area, bottom_area)
    else:
        _desenhar_conteudo(ss.proc_etapas, True, topo_area, progresso_area, passos_area, resumo_area, bottom_area)
