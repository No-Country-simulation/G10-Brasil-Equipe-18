"""Regressões de segurança dos adaptadores, sem chamadas externas."""
from unittest.mock import Mock

import pytest
from app.services import llm_provider as lp

SECRET = 'segredo-ficticio-regressao-123'


@pytest.fixture(autouse=True)
def config(monkeypatch):
    monkeypatch.setattr(lp, '_cfg', lambda chave, padrao='': SECRET if chave.endswith('_API_KEY') else padrao)


def test_gemini_chave_somente_no_header(monkeypatch):
    resposta = Mock(status_code=200)
    resposta.json.return_value = {'candidates': [{'content': {'parts': [{'text': '{}'}]}}]}
    post = Mock(return_value=resposta)
    monkeypatch.setattr(lp.requests, 'post', post)
    lp._chamar_gemini('prompt', '{}', 'modelo', 100, 1)
    args, kwargs = post.call_args
    assert SECRET not in args[0]
    assert SECRET not in str(kwargs.get('params', {}))
    assert kwargs['headers']['x-goog-api-key'] == SECRET
    assert SECRET not in str(kwargs['json'])


@pytest.mark.parametrize('adaptador', [lp._chamar_gemini, lp._chamar_cohere, lp._chamar_groq])
def test_erro_http_nao_expoe_corpo(monkeypatch, adaptador):
    resposta = Mock(status_code=503, text=SECRET)
    monkeypatch.setattr(lp.requests, 'post', Mock(return_value=resposta))
    with pytest.raises(lp.ErroProvedor) as erro:
        adaptador('prompt', '{}', 'modelo', 100, 1)
    assert SECRET not in str(erro.value)
    assert '503' in str(erro.value)


def test_fallback_nao_expoe_segredo_em_logs_ou_erro(monkeypatch, caplog):
    post = Mock(side_effect=lp.requests.ConnectionError(SECRET))
    monkeypatch.setattr(lp.requests, 'post', post)
    with pytest.raises(lp.ErroProvedor) as erro:
        lp.LLMProvider().gerar('prompt', {}, natureza_dados='ficticios')
    assert post.call_count == 3
    assert SECRET not in str(erro.value)
    assert SECRET not in caplog.text


@pytest.mark.parametrize('adaptador', [lp._chamar_gemini, lp._chamar_cohere, lp._chamar_groq])
@pytest.mark.parametrize('status, categoria', [(401, 'autenticacao'), (429, 'limite de requisicoes'), (503, 'indisponibilidade')])
def test_classificacao_http_segura(monkeypatch, adaptador, status, categoria):
    monkeypatch.setattr(lp.requests, 'post', Mock(return_value=Mock(status_code=status, text=SECRET)))
    with pytest.raises(lp.ErroProvedor) as erro:
        adaptador('prompt', '{}', 'modelo', 100, 1)
    assert f'HTTP {status}' in str(erro.value)
    assert categoria in str(erro.value)
    assert SECRET not in str(erro.value)
