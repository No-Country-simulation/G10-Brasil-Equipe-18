"""Diagnóstico do JSON inválido do LLM sem chamadas aos provedores."""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from services import llm, llm_provider


def test_provider_preserva_finish_reason_sem_chamada_externa(monkeypatch):
    texto = '{"historias": ['
    saida = SimpleNamespace(texto=texto, finish_reason="MAX_TOKENS")
    provider = llm_provider.LLMProvider()
    monkeypatch.setattr(
        provider,
        "_ordem",
        lambda: [("gemini", lambda *args: saida, "gemini-teste")],
    )

    resultado = provider.gerar("prompt", {})

    assert resultado.texto == texto
    assert resultado.finish_reason == "MAX_TOKENS"




def test_adaptador_gemini_extrai_finish_reason_sem_rede(monkeypatch):
    resposta = SimpleNamespace(
        status_code=200,
        json=lambda: {
            "candidates": [
                {
                    "content": {"parts": [{"text": "{\"historias\": ["}]},
                    "finishReason": "MAX_TOKENS",
                }
            ]
        },
    )
    monkeypatch.setattr(llm_provider, "_cfg", lambda chave, padrao="": "chave-simulada")
    monkeypatch.setattr(llm_provider.requests, "post", lambda *args, **kwargs: resposta)

    saida = llm_provider._chamar_gemini("prompt", "[]", "gemini-teste", 10, 1)

    assert saida.texto == '{"historias": ['
    assert saida.finish_reason == "MAX_TOKENS"


def test_erro_json_inclui_metadados_sem_expor_resposta_ou_payload(monkeypatch):
    resposta_invalida = '{"segredo_da_mensagem":"não registrar",'

    class ProviderFake:
        def __init__(self, timeout):
            pass

        def gerar(self, prompt, payload):
            return SimpleNamespace(
                texto=resposta_invalida,
                provedor="gemini",
                modelo="gemini-teste",
                fallback_usado=False,
                erro_primario="",
                finish_reason="MAX_TOKENS",
            )

    monkeypatch.setattr(llm_provider, "LLMProvider", ProviderFake)
    interacoes = [
        {
            "id": 123,
            "autor": "membro_123456",
            "canal": "discord-112233",
            "tipo": "mensagem",
            "texto": "texto privado de teste",
        }
    ]

    with pytest.raises(llm.ErroAnalise) as erro:
        llm.analisar(interacoes)

    mensagem = str(erro.value)
    assert "provedor=gemini" in mensagem
    assert "modelo=gemini-teste" in mensagem
    assert "finish_reason=MAX_TOKENS" in mensagem
    assert f"resposta_chars={len(resposta_invalida)}" in mensagem
    assert "linha=1" in mensagem and "coluna=" in mensagem
    assert resposta_invalida not in mensagem
    assert "texto privado de teste" not in mensagem
