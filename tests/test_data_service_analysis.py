"""Garante que falha de análise não troca mensagens reais por histórias fictícias."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from services import data_service as svc
from services import llm


def test_analisar_propaga_falha_em_vez_de_devolver_historias_de_mock(monkeypatch):
    def falhar(interacoes):
        raise RuntimeError("provedor indisponível (simulado)")

    monkeypatch.setattr(llm, "analisar", falhar)

    interacoes = [
        {
            "id": 123456789,
            "autor": "membro_123456",
            "canal": "discord-112233",
            "tipo": "mensagem",
            "texto": "Consegui meu primeiro emprego depois do curso.",
        }
    ]

    with pytest.raises(RuntimeError, match="Análise real falhou"):
        svc.analisar(interacoes)

    assert svc.ORIGEM_ANALISE == "erro"
    assert "provedor indisponível (simulado)" in svc.ULTIMO_ERRO


def test_processamento_usa_interacoes_discord_e_nao_mostra_historias_mockadas():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_string(
        """
import os
import sys
from pathlib import Path
os.environ["COMMUNITYLAB_DELAY"] = "0"
sys.path.insert(0, str(Path.cwd() / "app"))
import streamlit as st
from services import data_service as svc
from services import llm
from state import init_state
from telas import processamento
original_analisar = llm.analisar
original_listar = svc.listar_pacotes
recebidas = []
def falhar(itens):
    recebidas.extend(itens)
    raise RuntimeError("provedor indisponível (simulado)")
try:
    svc.listar_pacotes = lambda: []
    llm.analisar = falhar
    init_state()
    st.session_state.interacoes = [{
        "id": 123456789,
        "autor": "membro_123456",
        "canal": "discord-112233",
        "tipo": "mensagem",
        "texto": "Consegui meu primeiro emprego depois do curso.",
        "_id_efetivo": 123456789,
    }]
    st.session_state.arquivo = {"nome": "Discord", "tamanho": "1 mensagem", "origem": "Discord"}
    st.session_state.proc_status = "novo"
    processamento.render()
    assert recebidas == st.session_state.interacoes
    assert st.session_state.proc_status == "erro"
    assert st.session_state.proc_erro_etapa == "analise"
    assert st.session_state.historias == []
finally:
    llm.analisar = original_analisar
    svc.listar_pacotes = original_listar
"""
    )

    at.run()

    assert not at.exception
