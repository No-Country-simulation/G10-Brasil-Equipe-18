"""CSS e pequenos helpers de HTML (chips, cards, topbar)."""
import html as _html

import streamlit as st

# Tokens de cor - Identidade visual CommunityLab
AZUL_MARINHO = "#101B32"      # Sidebar e navegação
VIOLETA = "#7C3AED"           # Cor primária, ações de IA
CIANO = "#22D3EE"             # Detalhes tecnológicos (só sobre escuro)
BRANCO_NEUTRO = "#F8FAFC"     # Fundo da área de trabalho
VERDE = "#10B981"             # Sucesso (fundos e ícones)
VERDE_TEXTO = "#047857"       # Verde para texto sobre fundo claro
TEXTO_PRINCIPAL = "#0F172A"   # Texto principal
TEXTO_SECUNDARIO = "#64748B"  # Texto secundário
BORDA_SUAVE = "#E2E8F0"       # Bordas de cards

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Reset e base */
.stApp {font-family:'Inter',sans-serif; color:#0F172A;}
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}
.block-container {padding-top:1.4rem; max-width:1240px;}

/* Sidebar - Azul-marinho */
section[data-testid="stSidebar"] {
    background-color:#101B32 !important;
    border-right:1px solid #1e2a42;
}
section[data-testid="stSidebar"] * {color:#F8FAFC;}
section[data-testid="stSidebar"] .cl-muted {color:#94A3B8 !important;}

/* Botões da sidebar - 3 estados */
section[data-testid="stSidebar"] .stButton > button {
    width:100%; 
    justify-content:flex-start; 
    text-align:left;
    background-color:transparent;
    color:#F8FAFC;
    border:1px solid transparent;
    border-radius:8px;
    transition:all 0.2s ease;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color:rgba(124,58,237,0.15);
    border-color:#7C3AED;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background-color:#7C3AED;
    color:#FFFFFF;
    font-weight:600;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background-color:#6D28D9;
}

/* Logo e slogan */
.cl-logo {font-size:24px; font-weight:700; margin-bottom:8px; color:#F8FAFC;}
.cl-slogan {
    font-size:13px; 
    color:#94A3B8; 
    font-weight:400; 
    margin-bottom:20px;
    font-style:italic;
}
.cl-ws {
    border:1px solid rgba(226,232,240,0.2); 
    border-radius:10px; 
    padding:12px; 
    margin-bottom:14px; 
    font-size:14px;
    background:rgba(248,250,252,0.05);
}
.cl-ws small {color:#94A3B8; font-size:12px;}

.cl-label {font-size:11px; letter-spacing:.05em; color:#94A3B8; margin:10px 0 6px; text-transform:uppercase;}

.cl-humana {
    background:rgba(248,250,252,0.08); 
    border-radius:10px; 
    padding:12px; 
    font-size:13px; 
    color:#CBD5E1;
    border:1px solid rgba(226,232,240,0.1);
}
.cl-humana b {color:#F8FAFC;}

.cl-topbar {display:flex; justify-content:space-between; align-items:center; padding-bottom:12px; border-bottom:1px solid #E2E8F0; margin-bottom:18px; color:#64748B; font-size:14px;}
.cl-topbar b {color:#0F172A; font-weight:500;}

.cl-etapa {font-size:12px; letter-spacing:.05em; color:#64748B; text-transform:uppercase; margin-top:6px;}
.cl-titulo {font-size:34px; font-weight:600; color:#0F172A; margin:2px 0 4px;}
.cl-sub {color:#64748B; font-size:16px; margin-bottom:16px;}

/* Chips */
.chip {display:inline-block; padding:3px 10px; border-radius:6px; font-size:12px; font-weight:500; margin-right:6px;}
.chip-gray {background:#EEF0F4; color:#475569;}
.chip-green {background:#DCFCE7; color:#047857;}
.chip-yellow {background:#FFF3D6; color:#92400E;}
.chip-red {background:#FEE2E2; color:#991B1B;}
.chip-purple {background:#F3E8FF; color:#7C3AED;}
.chip-blue {background:#DBEAFE; color:#1E40AF;}

.avatar {display:inline-flex; width:36px; height:36px; border-radius:50%; background:#E2E8F0; color:#475569; align-items:center; justify-content:center; font-size:12px; font-weight:600; margin-right:10px; vertical-align:middle;}

.cl-quote {background:#F8FAFC; border-radius:8px; padding:12px 14px; font-size:14px; color:#0F172A; border:1px solid #E2E8F0;}
.cl-quote small {display:block; font-size:10.5px; letter-spacing:.05em; color:#64748B; text-transform:uppercase; margin-bottom:4px;}

mark {background:#DDD6FE; color:inherit; padding:1px 2px; border-radius:3px;}

.cl-muted {color:#64748B; font-size:13px;}
.cl-big {font-size:26px; font-weight:600; color:#0F172A;}

.cl-kv {display:flex; justify-content:space-between; font-size:14px; padding:6px 0;}
.cl-kv span:first-child {color:#64748B;}

.cl-table {width:100%; border-collapse:collapse; font-size:14px;}
.cl-table th {text-align:left; color:#64748B; font-weight:500; font-size:12.5px; background:#F8FAFC; padding:10px 12px;}
.cl-table td {padding:14px 12px; border-top:1px solid #E2E8F0; vertical-align:top;}
.cl-table td.mut {color:#64748B;}

.cl-progress {height:8px; background:#E2E8F0; border-radius:8px; overflow:hidden; margin:10px 0 8px;}
.cl-progress > div {height:100%; background:#7C3AED;}
.cl-progress.erro > div {background:#DC2626;}

.cl-step {display:flex; align-items:center; gap:14px; padding:14px 0; border-top:1px solid #E2E8F0;}
.cl-step .ico {width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:14px; flex:none;}
.ico-ok {background:#DCFCE7; color:#047857;}
.ico-run {background:#F3E8FF; color:#7C3AED;}
.ico-pen {border:1px dashed #CBD5E1; color:#94A3B8;}
.ico-err {background:#FEE2E2; color:#DC2626;}
.cl-step .txt {flex:1;}
.cl-step .t {font-weight:500; font-size:15px;}
.cl-step .d {font-size:13px; color:#64748B;}
.cl-step .s {font-size:13px;}
.s-ok {color:#047857;} .s-run {color:#7C3AED;} .s-pen {color:#94A3B8;} .s-err {color:#DC2626;}

.cl-box {border-radius:10px; padding:14px 16px; font-size:14px; margin:10px 0;}
.box-yellow {background:#FFFBEB; color:#92400E; border:1px solid #FEF3C7;}
.box-red {background:#FEE2E2; color:#991B1B; border:1px solid #FECACA;}
.box-gray {background:#F8FAFC; color:#475569; border:1px solid #E2E8F0;}
.box-green {background:#DCFCE7; color:#047857; border:1px solid #BBF7D0;}

.cl-cardativo {background:#F3E8FF; border-radius:10px; padding:24px; margin-bottom:12px;}
.cl-cardativo .one {font-size:22px; font-weight:700; color:#7C3AED;}
.cl-cardativo .one small {font-size:11px; font-weight:400; margin-left:8px;}
.cl-cardativo .tit {font-size:24px; font-weight:600; margin:10px 0 6px; color:#0F172A;}
.cl-cardativo .aut {color:#7C3AED; font-weight:600;}

.cl-skel {height:14px; border-radius:6px; background:linear-gradient(90deg,#E2E8F0 25%,#F8FAFC 37%,#E2E8F0 63%); background-size:400% 100%; animation:sk 1.4s ease infinite; margin:8px 0;}
@keyframes sk {0% {background-position:100% 50%;} 100% {background-position:0 50%;}}
"""


def compactar(s):
    """Junta as linhas do HTML para o Markdown não tratar recuo como bloco de código."""
    return "".join(linha.strip() for linha in s.splitlines())


def md(s):
    st.markdown(compactar(s), unsafe_allow_html=True)


def injetar_css():
    st.markdown("<style>" + compactar(_CSS) + "</style>", unsafe_allow_html=True)


def esc(texto):
    return _html.escape(str(texto))


def plural(n, singular, plural_):
    """Ex.: plural(1, "canal", "canais") -> "1 canal"."""
    return f"{n} {singular if n == 1 else plural_}"


def chip(texto, tom="gray"):
    return f'<span class="chip chip-{tom}">{esc(texto)}</span>'


def rotulo_natureza(valor):
    """(texto, tom) do selo da natureza DECLARADA dos dados do lote.

    Só reflete o que a pessoa declarou na Importação: nunca deduz por autor,
    conteúdo, origem ou provedor. Valor ausente ou inválido vira "não informada".
    Nenhum valor usa verde, para o selo não parecer validação.
    """
    from services import data_service as svc

    natureza = svc.normalizar_natureza_dados(valor)
    if natureza == "ficticios":
        return "Dados fictícios (declarado)", "yellow"
    if natureza == "reais":
        return "Dados reais (declarado)", "blue"
    return "Natureza não informada", "gray"


def avatar(iniciais):
    return f'<span class="avatar">{esc(iniciais)}</span>'


def topbar():
    md(
        '<div class="cl-topbar"><span>Espaço de trabalho &nbsp;›&nbsp; <b>Programa ONE</b></span>'
        '<span class="chip chip-gray">Dados demonstrativos</span></div>'
    )


def cabecalho(etapa, titulo, subtitulo, extra=""):
    md(
        f'<div class="cl-etapa">{esc(etapa)}</div>'
        f'<div class="cl-titulo">{esc(titulo)} {extra}</div>'
        f'<div class="cl-sub">{esc(subtitulo)}</div>'
    )


def caixa(tom, conteudo_html):
    md(f'<div class="cl-box box-{tom}">{conteudo_html}</div>')


def destacar(texto, trechos):
    """Escapa o texto e marca os trechos usados nos rascunhos."""
    saida = esc(texto)
    for trecho in trechos:
        saida = saida.replace(esc(trecho), f"<mark>{esc(trecho)}</mark>")
    return saida


def conferencia_html(confere, motivo):
    """Resultado da conferência de UMA citação: rótulo + motivo, em HTML.

    confere: True, False ou None (não deu para conferir). Os dois True têm
    rótulo e cor diferentes. O azul avisa que a parte mascarada não é
    conferida, para não parecer aprovação. None nunca fica verde.
    """
    from services import data_service as svc

    if confere is None:
        return f'<span class="cl-muted" style="font-size:12px;">{esc(motivo)}</span>'
    if confere and motivo == svc.MOTIVO_LITERAL:
        return chip("Trecho literal conferido", "green")
    if confere:
        return chip("Compatível com anonimização · a parte mascarada não é conferida", "blue")
    return (
        f'{chip("⚠ Não confere", "yellow")}'
        f'<span class="cl-muted" style="font-size:12px;">{esc(motivo)}</span>'
    )


def conferencia_da_citacao_editada(texto, historia, interacoes):
    """Resultado logo abaixo do campo "Citação" editável (Estúdio e Curadoria).

    Recalculado a cada rerun, portanto a cada edição. Texto vazio não mostra nada.
    """
    from services import data_service as svc

    if not (texto or "").strip():
        return
    confere, motivo, id_int = svc.conferencia_da_citacao_do_ativo(texto, historia, interacoes)
    origem = f"interação nº {id_int}" if id_int else ""
    md(
        f'<div class="cl-muted" style="font-size:12px; margin:-8px 0 8px 0;">'
        f'Conferência da citação {("(" + origem + ") ") if origem else ""}→ '
        f'{conferencia_html(confere, motivo)}</div>'
    )


def evidencias_citadas(historia, interacoes_do_lote, modo_demonstracao=True):
    """Componente compartilhado: exibe evidências citadas com conferência por citação.

    Cada citação é conferida contra o texto da interação do seu id_interacao
    (services.data_service.conferencia_da_citacao).
    Regra C: NUNCA fica verde sem interação de origem.
    Regra D: Em modo demonstração, rotula como "Exemplo de demonstração".

    Retorna: HTML das evidências.
    """
    from services import data_service as svc

    citacoes = historia.get("citacoes", [])
    if not citacoes:
        return '<span class="cl-muted">Nenhuma evidência citada registrada.</span>'

    html_partes = []
    if not interacoes_do_lote:
        # Lote reaberto do Histórico: o pacote não guarda a mensagem original.
        html_partes.append(
            '<div class="cl-muted" style="font-size:12px;">Conferência indisponível: '
            'a mensagem original não é guardada no pacote.</div>'
        )
    for citacao in citacoes:
        trecho = citacao.get("texto", "")
        confere, motivo, id_int = svc.conferencia_da_citacao(citacao, interacoes_do_lote)

        if id_int:
            id_display = f'interação nº <b>{id_int}</b>'
        else:
            id_display = '<span class="cl-muted">ID não informado</span>'
        # Sem ID, o motivo "ID não informado" já está no id_display.
        selo = "" if (confere is None and not id_int) else conferencia_html(confere, motivo)

        rotulo_demo = f' {chip("Exemplo de demonstração", "gray")}' if modo_demonstracao else ""

        html_partes.append(
            f'<div style="margin:10px 0; padding:10px; background:#F8FAFC; border-radius:6px; border:1px solid #E2E8F0;">'
            f'<div style="font-size:13px; color:#0F172A; margin-bottom:4px;">"{esc(trecho)}"</div>'
            f'<div class="cl-muted" style="font-size:12px;">→ {id_display} {selo}{rotulo_demo}</div>'
            f'</div>'
        )

    return "".join(html_partes)
