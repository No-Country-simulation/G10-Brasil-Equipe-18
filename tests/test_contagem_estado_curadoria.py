"""Contadores leem o estado editorial atual (status_curadoria).

Revisão do PR #51: as telas liam status_ativos, mas _solicitar_ajustes()
grava só status_curadoria. Os testes chamam a função real da Curadoria,
sem mock do estado, e conferem o que os contadores mostram.
"""
import sys
from pathlib import Path

import pytest
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))

from state import contagem_ativos_completa, estado_editorial, legenda_ativos  # noqa: E402
from telas import curadoria  # noqa: E402

HISTORIAS = [{"id": "h1", "ativos": [{"id": "a1"}]}]


@pytest.fixture
def ss():
    """session_state em modo bare, com os dicionários que init_state() cria."""
    estado = st.session_state
    for nome in ("status_curadoria", "status_ativos", "observacoes"):
        estado[nome] = {}
    yield estado
    for nome in ("status_curadoria", "status_ativos", "observacoes", "toast"):
        if nome in estado:
            del estado[nome]


def test_solicitar_ajustes_reflete_em_aguardando_revisao(ss):
    """Rascunho -> _solicitar_ajustes() real -> contador mostra 1 em ajustes."""
    ss.status_curadoria["h1:a1"] = "rascunho"

    curadoria._solicitar_ajustes("h1", "a1", "Incluir a data da conquista.")

    assert ss.status_curadoria["h1:a1"] == "ajustes"
    assert "h1:a1" not in ss.status_ativos  # o legado não é atualizado

    contagem = contagem_ativos_completa(HISTORIAS, ss.status_curadoria, ss.status_ativos)
    assert contagem["ajustes"] == 1
    assert contagem["rascunho"] == 0
    assert contagem["rascunho"] + contagem["ajustes"] == 1
    assert legenda_ativos(contagem).startswith("1 rascunho aguardando revisão humana")


def test_estado_atual_tem_prioridade_sobre_legado(ss):
    """Se os dois existem e divergem, vale status_curadoria."""
    ss.status_curadoria["h1:a1"] = "ajustes"
    ss.status_ativos["h1:a1"] = "aprovado"

    assert estado_editorial("h1:a1", ss.status_curadoria, ss.status_ativos) == "ajustes"
    contagem = contagem_ativos_completa(HISTORIAS, ss.status_curadoria, ss.status_ativos)
    assert contagem["aprovado"] == 0
    assert contagem["ajustes"] == 1


def test_legado_so_status_ativos_preenchido():
    """Sessão legada: sem status_curadoria, os contadores usam status_ativos."""
    historias = [{"id": "h1", "ativos": [{"id": "a1"}, {"id": "a2"}, {"id": "a3"}]}]
    legado = {"h1:a1": "aprovado", "h1:a2": "rejeitado"}

    contagem = contagem_ativos_completa(historias, {}, legado)

    assert contagem == {"total": 3, "rascunho": 1, "ajustes": 0, "aprovado": 1, "rejeitado": 1}
    assert estado_editorial("h1:a3", {}, legado) == "rascunho"
