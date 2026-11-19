"""Tela Dashboard - Visão geral do CommunityLab."""
import streamlit as st

from state import contagem_ativos_completa, ir_para, legenda_ativos, resumo_ativos
from styles import cabecalho, md, plural, topbar


def _kpi_card(titulo, valor, descricao, tipo="neutro"):
    """Card de KPI com título, valor grande e descrição."""
    cor_icone = {
        "neutro": "#64748B",
        "sucesso": "#10B981",
        "atencao": "#F59E0B",
    }[tipo]
    
    with st.container(border=True):
        md(f'<div style="min-height:120px;">'
           f'<span class="cl-muted" style="font-size:13px;">{titulo}</span>'
           f'<div style="font-size:36px; font-weight:700; color:{cor_icone}; margin:8px 0;">{valor}</div>'
           f'<span class="cl-muted" style="font-size:13px;">{descricao}</span>'
           f'</div>')


def render():
    ss = st.session_state
    topbar()
    cabecalho(
        "Visão Geral",
        "Dashboard",
        "Acompanhe as interações importadas, histórias detectadas e ativos gerados pela IA.",
    )
    
    # Métricas principais
    contagem = contagem_ativos_completa(ss.historias, ss.status_curadoria, ss.status_ativos)
    total_ativos = contagem["total"]
    num_canais = len({i["canal"] for i in ss.interacoes})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        _kpi_card(
            "Interações importadas",
            len(ss.interacoes),
            f"{plural(num_canais, 'canal', 'canais')} · Lote {ss.lote_id}",
            "neutro"
        )
    
    with col2:
        _kpi_card(
            "Histórias detectadas",
            len(ss.historias),
            f"{len({h['categoria'] for h in ss.historias})} categorias identificadas",
            "sucesso"
        )
    
    with col3:
        _kpi_card(
            "Ativos gerados",
            total_ativos,
            legenda_ativos(contagem),
            "atencao" if (contagem["rascunho"] + contagem["ajustes"]) > 0 else "sucesso"
        )
    
    # Status dos ativos
    st.write("")
    with st.container(border=True):
        md('<div style="font-size:18px; font-weight:600; margin-bottom:12px;">Status dos ativos</div>')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            md(f'<div style="text-align:center;">'
               f'<div style="font-size:28px; font-weight:700; color:#64748B;">{total_ativos}</div>'
               f'<div class="cl-muted">Total gerados</div>'
               f'</div>')
        
        with col2:
            md(f'<div style="text-align:center;">'
               f'<div style="font-size:28px; font-weight:700; color:#F59E0B;">{contagem["rascunho"] + contagem["ajustes"]}</div>'
               f'<div class="cl-muted">Aguardando revisão</div>'
               f'</div>')
        
        with col3:
            md(f'<div style="text-align:center;">'
               f'<div style="font-size:28px; font-weight:700; color:#10B981;">{contagem["aprovado"]}</div>'
               f'<div class="cl-muted">Aprovados</div>'
               f'</div>')
        
        with col4:
            md(f'<div style="text-align:center;">'
               f'<div style="font-size:28px; font-weight:700; color:#DC2626;">{contagem["rejeitado"]}</div>'
               f'<div class="cl-muted">Rejeitados</div>'
               f'</div>')
    
    # Ações rápidas
    st.write("")
    md('<div style="font-size:18px; font-weight:600; margin-bottom:12px;">Ações rápidas</div>')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            md('<div style="padding:8px;">'
               '<div style="font-size:24px; margin-bottom:8px;">📥</div>'
               '<div style="font-weight:600; margin-bottom:4px;">Importar interações</div>'
               '<div class="cl-muted" style="font-size:13px; margin-bottom:12px;">Carregar conversas da comunidade</div>'
               '</div>')
            st.button("→ Ir para Importação", key="goto_import", on_click=ir_para, args=("importacao",), use_container_width=True)
    
    with col2:
        with st.container(border=True):
            md('<div style="padding:8px;">'
               '<div style="font-size:24px; margin-bottom:8px;">💬</div>'
               '<div style="font-weight:600; margin-bottom:4px;">Ver histórias</div>'
               '<div class="cl-muted" style="font-size:13px; margin-bottom:12px;">Explorar os relatos identificados</div>'
               '</div>')
            st.button("→ Ir para Histórias", key="goto_hist", on_click=ir_para, args=("historias",), use_container_width=True)
    
    with col3:
        with st.container(border=True):
            md('<div style="padding:8px;">'
               '<div style="font-size:24px; margin-bottom:8px;">✅</div>'
               '<div style="font-weight:600; margin-bottom:4px;">Revisar ativos</div>'
               '<div class="cl-muted" style="font-size:13px; margin-bottom:12px;">Aprovar ou rejeitar rascunhos</div>'
               '</div>')
            st.button("→ Ir para Curadoria", key="goto_cur", on_click=ir_para, args=("curadoria",), 
                     disabled=(contagem['rascunho'] + contagem['ajustes']) == 0, use_container_width=True)
    
    # Rodapé
    st.write("")
    st.caption(f"Lote demonstrativo {ss.lote_id} · Todos os dados são fictícios · A IA sugere, o time decide")
