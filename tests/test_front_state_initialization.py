"""Verifica que a aplicação aguarda a escolha da fonte de dados."""
from streamlit.testing.v1 import AppTest


def test_init_state_nao_carrega_dados_nem_chama_servicos():
    at = AppTest.from_string(
        """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "app"))
import streamlit as st
from services import data_service as svc

def proibido(*args, **kwargs):
    raise AssertionError("a inicialização não deve consultar análise ou OCI")

analisar_original = svc.analisar
listar_original = svc.listar_pacotes
try:
    svc.analisar = proibido
    svc.listar_pacotes = proibido
    import main
    assert st.session_state.pagina == "importacao"
    assert st.session_state.interacoes == []
    assert st.session_state.historias == []
    assert st.session_state.pacotes_oci == []
finally:
    svc.analisar = analisar_original
    svc.listar_pacotes = listar_original
"""
    )

    at.run()

    assert not at.exception


def test_estudio_e_curadoria_mostram_estado_vazio():
    for tela in ("curadoria", "estudio"):
        at = AppTest.from_string(
            f"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "app"))
from state import init_state
from telas import {tela}
init_state()
{tela}.render()
"""
        )
        at.run()
        assert not at.exception
