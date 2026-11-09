"""Testes offline dos provedores de LLM; nenhuma chamada externa."""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services import llm_provider


def test_ordem_de_fallback_deixa_groq_por_ultimo():
    provider = llm_provider.LLMProvider()

    assert [nome for nome, _, _ in provider._ordem()] == ["gemini", "cohere", "groq"]


def test_cohere_envia_requisicao_v2_e_normaliza_resposta(monkeypatch):
    resposta_http = SimpleNamespace(
        status_code=200,
        text="",
        json=lambda: {
            "message": {"content": [{"type": "text", "text": '{"historias": []}'}]},
            "finish_reason": "COMPLETE",
        },
    )
    post = Mock(return_value=resposta_http)
    monkeypatch.setattr(llm_provider, "_cfg", lambda chave, padrao="": "chave-teste")
    monkeypatch.setattr(llm_provider.requests, "post", post)

    resultado = llm_provider._chamar_cohere(
        "prompt de sistema", "payload json", "modelo-teste", 1024, 12
    )

    assert resultado.texto == '{"historias": []}'
    assert resultado.finish_reason == "COMPLETE"
    args, kwargs = post.call_args
    assert args[0] == llm_provider.COHERE_ENDPOINT
    assert kwargs["headers"]["Authorization"] == "Bearer chave-teste"
    assert kwargs["json"]["model"] == "modelo-teste"
    assert kwargs["json"]["messages"] == [
        {"role": "system", "content": "prompt de sistema"},
        {"role": "user", "content": "payload json"},
    ]
    assert kwargs["json"]["max_tokens"] == 1024
    assert kwargs["timeout"] == 12


def test_cohere_falha_com_erro_controlado_em_status_nao_200(monkeypatch):
    resposta_http = SimpleNamespace(status_code=503, text="indisponível")
    monkeypatch.setattr(llm_provider, "_cfg", lambda chave, padrao="": "chave-teste")
    monkeypatch.setattr(llm_provider.requests, "post", Mock(return_value=resposta_http))

    try:
        llm_provider._chamar_cohere("prompt", "payload", "modelo", 100, 1)
    except llm_provider.ErroProvedor as erro:
        assert "Cohere 503" in str(erro)
    else:
        raise AssertionError("Esperava ErroProvedor para resposta HTTP não 200")


def test_disponibilidade_prioriza_cohere_sobre_groq(monkeypatch):
    monkeypatch.setattr(
        llm_provider,
        "_cfg",
        lambda chave, padrao="": "chave-teste" if chave in {"COHERE_API_KEY", "GROQ_API_KEY"} else "",
    )
    provider = llm_provider.LLMProvider()

    assert provider.provedor_disponivel() == "cohere"


def test_provider_tenta_cohere_antes_de_groq(monkeypatch):
    provider = llm_provider.LLMProvider()
    chamadas = []

    def falha_gemini(*args):
        chamadas.append("gemini")
        raise llm_provider.ErroProvedor("Gemini indisponível")

    def sucesso_cohere(*args):
        chamadas.append("cohere")
        return llm_provider.RespostaProvedor("resposta cohere", "COMPLETE")

    def nao_deve_chamar_groq(*args):
        chamadas.append("groq")
        raise AssertionError("Groq deveria permanecer como último fallback")

    monkeypatch.setattr(
        provider,
        "_ordem",
        lambda: [
            ("gemini", falha_gemini, "gemini-teste"),
            ("cohere", sucesso_cohere, "cohere-teste"),
            ("groq", nao_deve_chamar_groq, "groq-teste"),
        ],
    )

    resultado = provider.gerar("prompt", {})

    assert resultado.provedor == "cohere"
    assert resultado.fallback_usado is True
    assert chamadas == ["gemini", "cohere"]


def test_erro_de_rede_no_provedor_tenta_o_proximo(monkeypatch):
    provider = llm_provider.LLMProvider()
    chamadas = []

    def timeout_gemini(*args):
        chamadas.append("gemini")
        raise llm_provider.requests.Timeout("timeout simulado")

    def sucesso_cohere(*args):
        chamadas.append("cohere")
        return llm_provider.RespostaProvedor("resposta cohere", "COMPLETE")

    monkeypatch.setattr(
        provider,
        "_ordem",
        lambda: [
            ("gemini", timeout_gemini, "gemini-teste"),
            ("cohere", sucesso_cohere, "cohere-teste"),
            ("groq", lambda *args: None, "groq-teste"),
        ],
    )

    resultado = provider.gerar("prompt", {})

    assert resultado.provedor == "cohere"
    assert chamadas == ["gemini", "cohere"]
