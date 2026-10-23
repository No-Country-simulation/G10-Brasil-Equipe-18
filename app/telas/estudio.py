"""Tela Estúdio de Conteúdo - Evidências + Edição de rascunhos."""
import streamlit as st

from state import campo, definir, historia_por_id, ir_para, valor
from styles import avatar, cabecalho, chip, destacar, esc, md, topbar


def _chave(hid, aid, nome_campo):
    return f"e:{hid}:{aid}:{nome_campo}"


def _regenerar(hid, aid):
    from services import data_service as svc
    ss = st.session_state
    h = historia_por_id(hid)
    n = ss.regen.get(f"{hid}:{aid}", 0) + 1
    ss.regen[f"{hid}:{aid}"] = n
    for nome_campo, texto in svc.regenerar(h, aid, n).items():
        definir(_chave(hid, aid, nome_campo), texto)
    # Resetar validação factual para "pendente" ao regenerar (requisito do review)
    chave = f"{hid}:{aid}"
    ss.validacao_factual[chave] = "pendente"
    ss.toast = "Novo rascunho gerado. Revise antes de enviar para curadoria."


def _alternar_copia():
    st.session_state.mostrar_copia = not st.session_state.mostrar_copia


def _enviar_curadoria(hid):
    ss = st.session_state
    ss.historia_atual = hid
    ss.mostrar_copia = False
    ss.toast = "Enviado para curadoria. Revise e aprove ou rejeite."
    ir_para("curadoria")


def _coluna_evidencias(h):
    """Coluna esquerda: fatos e evidências originais."""
    with st.container(border=True):
        md('<div style="font-size:18px; font-weight:600; margin-bottom:12px;">Fatos e evidências originais</div>')
        
        # Mensagem original com destaques
        md('<b style="font-size:14px;">Mensagem original</b>')
        md(f'<div class="cl-quote" style="margin:8px 0 12px 0;">"{destacar(h["mensagem_original"], h["destaques"])}"</div>')
        
        # Metadados
        md(f'<div class="cl-kv"><span>Canal</span><span>{esc(h["canal"])}</span></div>')
        md(f'<div class="cl-kv"><span>Autor</span><span>{esc(h["autor"])}</span></div>')
        md(f'<div class="cl-kv"><span>Lote</span><span>{esc(st.session_state.lote_id)}</span></div>')
        md(chip("Mensagem fictícia"))
        
        st.divider()
        
        # Fatos extraídos
        md('<b style="font-size:14px; margin-top:12px;">Fatos extraídos</b>')
        fatos_html = ""
        for f in h["fatos"]:
            fatos_html += (
                f'<div style="margin:10px 0;">'
                f'<span style="color:#10B981;">✓</span> {esc(f)}<br>'
                f'<span class="cl-muted" style="margin-left:18px; font-size:12px;">Vem da mensagem original</span>'
                f'</div>'
            )
        md(fatos_html)


def _coluna_conteudo(h):
    """Coluna direita: conteúdo gerado pela IA."""
    hid = h["id"]
    
    with st.container(border=True):
        md('<div style="font-size:18px; font-weight:600; margin-bottom:12px;">Conteúdo gerado pela IA</div>')
        
        # Abas por tipo de ativo
        nomes = [a["nome"] for a in h["ativos"]]
        escolhido = campo(st.radio, "Tipo de ativo", f"aba_estudio:{hid}", nomes[0], options=nomes,
                          horizontal=True, label_visibility="collapsed")
        
        ativo = next(a for a in h["ativos"] if a["nome"] == escolhido)
        aid = ativo["id"]
        
        # Selo "Gerado por IA"
        md(f'<div style="text-align:right; margin-bottom:8px;">{chip("Gerado por IA", "purple")}</div>')
        
        # Conteúdo editável
        if ativo["tipo"] == "testemunho":
            campo(st.text_input, "Título", _chave(hid, aid, "titulo"), ativo["campos"].get("titulo", ""))
            campo(st.text_area, "Descrição", _chave(hid, aid, "descricao"), ativo["campos"].get("descricao", ""), height=120)
            campo(st.text_area, "Citação", _chave(hid, aid, "citacao"), ativo["campos"].get("citacao", ""), height=60)
            
            # Contador de caracteres
            titulo = valor(_chave(hid, aid, "titulo"), "")
            descricao = valor(_chave(hid, aid, "descricao"), "")
            citacao = valor(_chave(hid, aid, "citacao"), "")
            total = len(titulo) + len(descricao) + len(citacao)
            st.caption(f"{total} caracteres no total")
            
            copiavel = f"{titulo}\n\n{descricao}\n\n\"{citacao}\""
        elif ativo["tipo"] == "card":
            campo(st.text_input, "Título do card", _chave(hid, aid, "titulo"), ativo["campos"].get("titulo", ""))
            campo(st.text_area, "Frase", _chave(hid, aid, "frase"), ativo["campos"].get("frase", ""), height=80)
            
            titulo = valor(_chave(hid, aid, "titulo"), "")
            frase = valor(_chave(hid, aid, "frase"), "")
            st.caption(f"{len(titulo) + len(frase)} caracteres no total")
            
            copiavel = f"{titulo}\n\n{frase}"
        else:  # texto / post_linkedin / qualquer outro
            # Pega o primeiro campo de texto disponível
            texto_inicial = (
                ativo["campos"].get("texto")
                or next(iter(ativo["campos"].values()), "")
            )
            campo(st.text_area, "Texto", _chave(hid, aid, "texto"), texto_inicial, height=300)
            texto = valor(_chave(hid, aid, "texto"), "")
            st.caption(f"{len(texto)} caracteres")
            copiavel = texto

        
        st.divider()
        
        # Fontes do conteúdo
        md('<b style="font-size:14px; margin-top:12px;">Fontes deste conteúdo</b>')
        if "fontes" in ativo:
            fontes_html = ""
            for fonte in ativo["fontes"]:
                fontes_html += (
                    f'<div style="margin:10px 0; padding:10px; background:#F8FAFC; border-radius:6px; border:1px solid #E2E8F0;">'
                    f'<div style="font-weight:500; margin-bottom:4px;">{esc(fonte["afirmacao"])}</div>'
                    f'<div class="cl-muted" style="font-size:12px; margin-bottom:4px;">→ Baseado em: {esc(fonte["fato"])}</div>'
                    f'<div class="cl-muted" style="font-size:12px;">→ Trecho: "<mark>{esc(fonte["trecho"])}</mark>"</div>'
                    f'</div>'
                )
            md(fontes_html)
        else:
            st.caption("Rastreabilidade não disponível para este tipo de ativo.")
        
        # Botões de ação
        st.write("")
        col1, col2, col3, col4 = st.columns([1.2, 1.2, 2, 2])
        col1.button("↻ Regenerar", key=f"regen_estudio_{hid}_{aid}", on_click=_regenerar, args=(hid, aid), 
                   use_container_width=True)
        col2.button("Copiar", key=f"copy_estudio_{hid}_{aid}", on_click=_alternar_copia, use_container_width=True)
        col4.button("→ Enviar para curadoria", key=f"enviar_{hid}", on_click=_enviar_curadoria, args=(hid,),
                   type="primary", use_container_width=True)
        
        if st.session_state.mostrar_copia:
            st.code(copiavel, language=None)
            st.caption("Use o ícone no canto do bloco para copiar.")


def render():
    ss = st.session_state
    
    # Se não há história selecionada, pega a primeira
    hid = ss.get("historia_atual") or ss.historias[0]["id"]
    h = historia_por_id(hid)
    
    if not h:
        st.error("História não encontrada.")
        st.button("← Voltar para histórias", on_click=ir_para, args=("historias",))
        return
    
    topbar()
    cabecalho(
        "Etapa 3 de 4 · Revisar",
        "Estúdio de Conteúdo",
        "Visualize as evidências originais e edite os rascunhos gerados pela IA antes de enviar para curadoria.",
    )
    
    st.button("← Voltar para histórias", on_click=ir_para, args=("historias",))
    
    # Cabeçalho da história
    with st.container(border=True):
        esq, dir_ = st.columns([3, 1])
        with esq:
            md(f'{avatar(h["iniciais"])}<b>{esc(h["autor"])}</b><br>'
               f'<span class="cl-muted" style="margin-left:46px;">{esc(h["canal"])} · {esc(h["origem"])}</span>')
        with dir_:
            md(f'<div style="text-align:right;">'
               f'<span class="cl-muted">Relevância</span> '
               f'<span style="font-size:22px; font-weight:600;">{h["relevancia"]}</span>'
               f'<span class="cl-muted"> / 100</span></div>')
        
        sentimento = h["sentimento"].lower()
        md(f'<div style="margin-left:46px; margin-top:8px;">'
           f'{chip(h["categoria"])}{chip("Sentimento " + sentimento, "green")}</div>')
    
    # Duas colunas: evidências à esquerda, conteúdo à direita
    esq, dir_ = st.columns([1, 1])
    
    with esq:
        _coluna_evidencias(h)
    
    with dir_:
        _coluna_conteudo(h)
    
    # Aviso
    st.caption("O Estúdio serve para LER evidências e EDITAR rascunhos. A decisão de aprovar ou rejeitar acontece na Curadoria.")
