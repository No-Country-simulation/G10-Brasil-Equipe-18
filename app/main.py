"""CommunityLab · front em Streamlit.

Rodar (na raiz do repositório): streamlit run app/main.py
"""

import sys
from pathlib import Path

# Garante a raiz do projeto no sys.path para imports de 'src'.
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st

from state import MENU, campo, init_state, ir_para, reiniciar
from styles import injetar_css, md
from telas import curadoria, dashboard, estudio, historias, historico, importacao, processamento


CSS_TUBO = """
<style>
.cl-tubo {
    position: relative;
    display: inline-block;
    line-height: 1;
}

.cl-bolha {
    position: absolute;
    top: 12%;
    left: 76%;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #5CE17B;
    pointer-events: none;
    opacity: 0;
    animation: cl-borbulhar 2.8s ease-out infinite;
}

.cl-bolha:nth-of-type(2) {
    animation-delay: 0.25s;
}

.cl-bolha:nth-of-type(3) {
    animation-delay: 0.5s;
}

@keyframes cl-borbulhar {
    0% {
        opacity: 0;
        transform: translate(0, 0) scale(0.6);
    }
    12% {
        opacity: 1;
    }
    48%, 100% {
        opacity: 0;
        transform: translate(4px, -16px) scale(1.2);
    }
}

@media (prefers-reduced-motion: reduce) {
    .cl-bolha {
        animation: none;
    }
}
</style>
"""

st.set_page_config(page_title="CommunityLab", page_icon="🧪", layout="wide")
injetar_css()
st.markdown(CSS_TUBO, unsafe_allow_html=True)
init_state()

ss = st.session_state
TELAS = {
    "dashboard": dashboard.render,
    "importacao": importacao.render,
    "processamento": processamento.render,
    "historias": historias.render,
    "estudio": estudio.render,
    "curadoria": curadoria.render,
    "historico": historico.render,
}

with st.sidebar:
    md(
        '<div class="cl-logo">'
        '<span class="cl-tubo" aria-hidden="true">🧪'
        '<span class="cl-bolha"></span>'
        '<span class="cl-bolha"></span>'
        '<span class="cl-bolha"></span>'
        '</span> CommunityLab'
        '</div>'
    )
    md('<div class="cl-slogan">Histórias reais. Impacto inteligente.</div>')
    md('<div class="cl-ws"><b>Programa ONE</b><br><small>Oracle Next Education + Alura</small></div>')
    md('<div class="cl-label">ESPAÇO DE TRABALHO</div>')

    ativo = "importacao" if ss.pagina == "processamento" else ss.pagina
    for chave, rotulo in MENU:
        st.button(
            rotulo,
            key=f"nav_{chave}",
            type="primary" if chave == ativo else "secondary",
            on_click=ir_para,
            args=(chave,),
        )

    st.write("")
    md('<div class="cl-humana"><b>A decisão é humana.</b><br>A IA sugere histórias e rascunhos. Seu time revisa antes de publicar.</div>')
    md('<div class="cl-muted" style="margin-top:12px;"><b>CM</b> &nbsp;Comunidade e Marketing<br>Ambiente demonstrativo</div>')

    with st.expander("⚙️ Modo demonstração"):
        campo(st.checkbox, "Simular erro ao salvar no OCI", "demo_erro_oci", False)
        campo(
            st.selectbox,
            "Estado da tela Histórico",
            "demo_estado_oci",
            "Normal",
            options=historico.ESTADOS_DEMO,
        )
        st.button("Reiniciar demonstração", on_click=reiniciar)

if ss.get("toast"):
    st.toast(ss.toast)
    ss.toast = None

TELAS[ss.pagina]()
