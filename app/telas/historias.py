import streamlit as st

from state import CATEGORIA_TODAS, campo, definir, ir_para, resumo_ativos
from styles import avatar, caixa, cabecalho, chip, esc, md, topbar


def _kpi(coluna, rotulo, numero, legenda):
    with coluna:
        with st.container(border=True):
            md(f'<span class="cl-muted">{esc(rotulo)}</span><div class="cl-big">{numero}</div>'
               f'<span class="cl-muted">{esc(legenda)}</span>')


def _limpar_filtros():
    definir("f:cat", CATEGORIA_TODAS)
    definir("f:rel", 70)


def _revisar(hid):
    ss = st.session_state
    ss.historia_atual = hid
    ss.mostrar_copia = False
    ir_para("estudio")


def _status_da_historia(h):
    ss = st.session_state
    estados = [ss.status_ativos.get(f"{h['id']}:{a['id']}", "rascunho") for a in h["ativos"]]
    if "rascunho" in estados:
        return chip("Revisão humana pendente", "yellow")
    if all(e == "rejeitado" for e in estados):
        return chip("Rejeitado", "red")
    return chip("Revisão concluída", "green")


def render():
    ss = st.session_state
    topbar()
    cabecalho("Etapa 3 de 4 · Revisar", "Histórias detectadas",
              "Explore os relatos identificados e revise os ativos antes de qualquer publicação.")
    historias = ss.historias
    if not historias:
        caixa("gray", "<b>Nenhuma história detectada ainda</b><br>"
                      "Carregue suas conversas e inicie o processamento na tela de Importação.")
        st.button("→ Ir para Importação", type="primary", on_click=ir_para, args=("importacao",))
        return

    contagem = resumo_ativos()
    total_ativos = sum(contagem.values())
    categorias = sorted({h["categoria"] for h in historias})

    c1, c2, c3 = st.columns(3)
    _kpi(c1, "Interações analisadas", len(ss.interacoes), f"{len({i['canal'] for i in ss.interacoes})} canais no lote {ss.lote_id}")
    _kpi(c2, "Histórias detectadas", len(historias), f"{len(categorias)} categorias identificadas")
    _kpi(c3, "Ativos gerados", total_ativos, f"{contagem['rascunho']} rascunhos aguardando revisão humana")

    origem_analise = ss.get("proc_origem_analise", "")
    
    if origem_analise == "mock":
        caixa("yellow", "⚠️ <b>Resultado simulado, a análise real falhou</b><br>"
                        "As histórias e rascunhos abaixo foram gerados a partir do fallback mock "
                        "porque a análise real não estava disponível ou falhou.")
    elif origem_analise == "gemini":
        caixa("green", "✓ <b>Análise real concluída</b><br>"
                       "As histórias e rascunhos abaixo foram identificados e gerados pela IA (Gemini). "
                       "A decisão final de publicação é sempre do seu time.")
    else:
        caixa("yellow", "<b>Rascunhos, não publicações</b><br>As mensagens são a fonte; os ativos são sugestões da IA. "
                        "Valide os fatos e a autorização de uso antes de aprovar.")

    with st.container(border=True):
        f1, f2, f3 = st.columns([2, 3, 1])
        with f1:
            cat = campo(st.selectbox, "Categoria", "f:cat", CATEGORIA_TODAS, options=[CATEGORIA_TODAS] + categorias)
        with f2:
            rel = campo(st.slider, "Relevância mínima", "f:rel", 70, min_value=0, max_value=100)
        with f3:
            st.write("")
            st.button("Limpar filtros", on_click=_limpar_filtros)

    filtradas = [h for h in historias if (cat == CATEGORIA_TODAS or h["categoria"] == cat) and h["relevancia"] >= rel]
    filtradas.sort(key=lambda h: h["relevancia"], reverse=True)
    md(f'<div style="display:flex;justify-content:space-between;margin-top:8px;"><b>{len(filtradas)} histórias encontradas</b>'
       f'<span class="cl-muted">Maior relevância primeiro · Lote {esc(ss.lote_id)}</span></div>')

    if not filtradas:
        caixa("gray", "Nenhuma história com esses filtros. Tente diminuir a relevância mínima ou clique em <b>Limpar filtros</b>.")

    for h in filtradas:
        with st.container(border=True):
            topo, rel_col = st.columns([4, 1])
            with topo:
                md(f'{avatar(h["iniciais"])}<b>{esc(h["autor"])}</b><br>'
                   f'<span class="cl-muted" style="margin-left:46px;">{esc(h["canal"])} · {esc(h["origem"])}</span>')
            with rel_col:
                md(f'<div style="text-align:right;"><span class="cl-muted">Relevância</span> '
                   f'<span style="font-size:22px;">{h["relevancia"]}</span> <span class="cl-muted">/ 100</span></div>')
            # TODO(Jaqueline): Quando o backend fornecer campo de origem individual por história (ex.: h.get("origem_analise")), usar o valor individual.
            origem_lote = ss.get("proc_origem_analise", "")
            if origem_lote == "gemini":
                selo_origem = chip("Origem: Real", "green")
            elif origem_lote == "mock":
                selo_origem = chip("Origem: Simulada", "yellow")
            else:
                selo_origem = ""
            chips = chip(h["categoria"]) + chip(f'Sentimento {h["sentimento"].lower()}', "green")
            if selo_origem:
                chips += selo_origem
            md(chips)
            msg_ficticia = " · mensagem fictícia" if origem_lote == "mock" else ""
            md(f'<div class="cl-quote"><small>Trecho original{msg_ficticia}</small>"{esc(h["mensagem_original"])}"</div>')
            rodape, botao = st.columns([4, 1])
            with rodape:
                md(f'<b>{len(h["ativos"])} ativos gerados</b> &nbsp;{_status_da_historia(h)}<br>'
                   f'<span class="cl-muted">{" · ".join(esc(a["nome"]) for a in h["ativos"])}</span>')
            with botao:
                st.button("→ Ver no Estúdio", key=f"rev_{h['id']}", on_click=_revisar, args=(h["id"],))

    aprov = contagem["aprovado"]
    texto = "Nenhum ativo aprovado ou publicado" if aprov == 0 else f"{aprov} ativo(s) aprovado(s) · nenhum publicado"
    md(f'<div style="display:flex;justify-content:space-between;margin-top:6px;" class="cl-muted">'
       f'<span>Exibindo {len(filtradas)} de {len(historias)} histórias</span><span>{texto}</span></div>')
