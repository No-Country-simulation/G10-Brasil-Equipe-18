"""Valida o payload de análise sem chamar provedores externos."""
import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))

from services import llm, llm_provider  # noqa: E402
from src.preprocessing import anonimizacao  # noqa: E402


@pytest.fixture
def chamada_llm(monkeypatch):
    importlib.reload(llm)
    recebidos = []

    class ProvedorFalso:
        def __init__(self, timeout):
            pass

        def gerar(self, prompt, payload):
            assert isinstance(payload, str)
            recebidos.extend(json.loads(payload))
            return SimpleNamespace(
                texto='{"historias": []}',
                provedor="teste",
                modelo="modelo-falso",
                finish_reason="STOP",
            )

    monkeypatch.setattr(llm_provider, "LLMProvider", ProvedorFalso)
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    return recebidos


INTERACAO = {
    "id": 1,
    "autor": "Marina Costa",
    "canal": "#conquistas",
    "tipo": "mensagem",
    "texto": (
        "Consegui minha primeira vaga. Meu e-mail é marina@example.com, "
        "telefone (11) 98888-7777 e CPF 123.456.789-00."
    ),
}


def test_payload_preserva_id_e_campos_de_entrada(chamada_llm):
    llm.analisar([INTERACAO])

    assert chamada_llm[0]["id"] == 1
    assert chamada_llm[0]["autor"] == "Marina Costa"
    assert chamada_llm[0]["canal"] == "#conquistas"
    assert chamada_llm[0]["tipo"] == "mensagem"


def test_payload_anonimiza_pii_do_texto_antes_de_enviar(chamada_llm):
    llm.analisar([INTERACAO])

    texto_enviado = chamada_llm[0]["texto"]
    assert "marina@example.com" not in texto_enviado
    assert "(11) 98888-7777" not in texto_enviado
    assert "123.456.789-00" not in texto_enviado
    assert "[EMAIL]" in texto_enviado
    assert "[TELEFONE]" in texto_enviado
    assert "[CPF]" in texto_enviado
