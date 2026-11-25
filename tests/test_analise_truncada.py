"""Resposta truncada pelo limite de saída não é JSON inválido.

O que estes testes garantem:
- resposta cortada no limite (`finish_reason=MAX_TOKENS`) vira um erro próprio,
  com mensagem que fala de truncamento e não de JSON inválido;
- JSON realmente inválido continua sendo recusado com a mensagem de JSON;
- a camada de dados expõe o tipo da falha, para a tela dizer o certo.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "app"))

from services import data_service as svc  # noqa: E402
from services import llm  # noqa: E402
from services import llm_provider  # noqa: E402
from services.llm_provider import ResultadoLLM  # noqa: E402

INTERACOES = [
    {
        "autor": "membro_teste",
        "canal": "canal-teste",
        "tipo": "mensagem",
        "texto": "Consegui minha primeira vaga como analista de dados depois de um ano estudando.",
    }
]


def _provider_falso(texto, finish_reason):
    class ProviderFalso:
        def __init__(self, *args, **kwargs):
            pass

        def gerar(self, prompt, payload, *, natureza_dados):
            return ResultadoLLM(
                texto=texto,
                provedor="gemini",
                modelo="gemini-3-flash-preview",
                finish_reason=finish_reason,
            )

    return ProviderFalso


def test_resposta_truncada_tem_erro_proprio(monkeypatch):
    resposta = '{"historias": [{"id": "hist-001", "segredo": "nao registrar",'
    monkeypatch.setattr(
        llm_provider,
        "LLMProvider",
        _provider_falso(resposta, "MAX_TOKENS"),
    )

    with pytest.raises(llm.ErroRespostaTruncada) as erro:
        llm.analisar(INTERACOES, natureza_dados="ficticios")

    mensagem = str(erro.value)
    assert "truncada" in mensagem.lower()
    assert "JSON inválido" not in mensagem
    assert "provedor=gemini" in mensagem and "finish_reason=MAX_TOKENS" in mensagem
    assert resposta not in mensagem
    assert "nao registrar" not in mensagem
    # É subclasse do erro de análise: quem já tratava a falha continua tratando.
    assert isinstance(erro.value, llm.ErroAnalise)


def test_json_invalido_sem_truncamento_mantem_a_mensagem(monkeypatch):
    monkeypatch.setattr(
        llm_provider,
        "LLMProvider",
        _provider_falso('{"historias": [{"id": "hist-001",', "STOP"),
    )

    with pytest.raises(llm.ErroAnalise) as erro:
        llm.analisar(INTERACOES, natureza_dados="ficticios")

    assert not isinstance(erro.value, llm.ErroRespostaTruncada)
    assert "JSON inválido" in str(erro.value)


def test_camada_de_dados_marca_a_falha_como_truncada(monkeypatch):
    monkeypatch.setattr(
        llm_provider,
        "LLMProvider",
        _provider_falso('{"historias": [', "MAX_TOKENS"),
    )

    with pytest.raises(RuntimeError):
        svc.analisar(INTERACOES, natureza_dados="ficticios")

    assert svc.ULTIMO_ERRO_TRUNCADO is True
    assert svc.ORIGEM_ANALISE == "erro"
