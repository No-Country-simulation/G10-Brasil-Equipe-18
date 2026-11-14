"""Regressões para truncamento de resposta sem chamadas externas."""
import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))

from services import llm, llm_provider  # noqa: E402


def test_provedor_usa_limite_de_saida_maior_por_padrao(monkeypatch):
    monkeypatch.setattr(llm_provider, "_cfg", lambda chave, padrao="": padrao)

    provider = llm_provider.LLMProvider()

    assert provider.max_tokens == 8192


def test_limite_de_saida_pode_ser_configurado_por_variavel(monkeypatch):
    monkeypatch.setattr(
        llm_provider,
        "_cfg",
        lambda chave, padrao="": "12288" if chave == "LLM_MAX_OUTPUT_TOKENS" else padrao,
    )

    provider = llm_provider.LLMProvider()

    assert provider.max_tokens == 12288


def test_resposta_truncada_informa_como_aumentar_limite_sem_vazar_conteudo(monkeypatch):
    importlib.reload(llm)
    resposta_parcial = '{"historias": ['

    class ProviderFake:
        def __init__(self, timeout):
            pass

        def gerar(self, prompt, payload):
            return SimpleNamespace(
                texto=resposta_parcial,
                provedor="gemini",
                modelo="gemini-teste",
                finish_reason="MAX_TOKENS",
            )

    monkeypatch.setattr(llm_provider, "LLMProvider", ProviderFake)

    with pytest.raises(llm.ErroAnalise, match="truncada") as erro:
        llm.analisar(
            [{"id": 1, "autor": "membro_001", "canal": "#teste", "texto": "Mensagem de teste."}]
        )

    assert "LLM_MAX_OUTPUT_TOKENS" in str(erro.value)
    assert resposta_parcial not in str(erro.value)
