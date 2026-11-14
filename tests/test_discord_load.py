"""Testes da ingestão via API REST do Discord (tudo mockado, sem rede)."""
import re
import pytest
from unittest.mock import patch, MagicMock
from requests import RequestException

from src.ingestion.discord_load import buscar_mensagens_discord

MODULO = "src.ingestion.discord_load"


def _resposta(status=200, json=None, text="", headers=None):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = [] if json is None else json
    r.text = text
    r.headers = headers or {}
    return r


@pytest.fixture(autouse=True)
def credenciais():
    cfg = {"DISCORD_TOKEN": "token_fake", "CANAL_ID": "112233"}
    with patch(f"{MODULO}._cfg", side_effect=lambda c: cfg.get(c, "")):
        yield


@pytest.fixture
def mock_get():
    with patch(f"{MODULO}.requests.get") as m:
        m.return_value = _resposta()
        yield m


@pytest.fixture
def mensagens_api():
    return [
        {"id": "1234567890", "content": "Fui contratado depois do curso!",
         "author": {"id": "999", "username": "membro_comunidade", "global_name": "Dev Comunidade"},
         "timestamp": "2026-11-05T10:00:00.000Z"},
        {"id": "1234567891", "content": "",
         "author": {"id": "888", "username": "bot_discord"},
         "timestamp": "2026-11-05T09:59:00.000Z"},
    ]


# ---------- configuração ----------

@pytest.mark.parametrize("faltando,msg", [
    ("DISCORD_TOKEN", "DISCORD_TOKEN não configurado."),
    ("CANAL_ID", "CANAL_ID não configurado."),
])
def test_credenciais_ausentes(mock_get, faltando, msg):
    cfg = {"DISCORD_TOKEN": "t", "CANAL_ID": "c", faltando: ""}
    with patch(f"{MODULO}._cfg", side_effect=lambda c: cfg[c]):
        validas, rejeitadas, avisos = buscar_mensagens_discord()
    assert validas == [] and rejeitadas == []
    assert msg in avisos
    mock_get.assert_not_called()


# ---------- requisição ----------

def test_requisicao_http_correta(mock_get):
    buscar_mensagens_discord(limite=50)
    args, kwargs = mock_get.call_args
    assert args[0].endswith("/channels/112233/messages")
    assert kwargs["headers"]["Authorization"] == "Bot token_fake"
    assert kwargs["params"] == {"limit": 50}      # sem 'after'
    assert kwargs["timeout"] == 15


def test_limite_padrao_de_cinquenta_mensagens(mock_get):
    buscar_mensagens_discord()
    assert mock_get.call_args.kwargs["params"]["limit"] == 50


def test_after_id_repassado(mock_get):
    buscar_mensagens_discord(after_id="99887766")
    assert mock_get.call_args.kwargs["params"]["after"] == "99887766"


@pytest.mark.parametrize("pedido,enviado", [(500, 100), (101, 100), (10, 10), (0, 1), (-5, 1)])
def test_limite_ajustado(mock_get, pedido, enviado):
    buscar_mensagens_discord(limite=pedido)
    assert mock_get.call_args.kwargs["params"]["limit"] == enviado


# ---------- conversão ----------

def test_sucesso_basico(mock_get, mensagens_api):
    mock_get.return_value = _resposta(json=mensagens_api)
    validas, rejeitadas, avisos = buscar_mensagens_discord()

    assert len(validas) == 1
    assert validas[0]["id_discord"] == "1234567890"
    assert validas[0]["origem"] == "discord"
    assert validas[0]["texto"] == "Fui contratado depois do curso!"
    assert len(rejeitadas) == 1
    assert "vazia" in rejeitadas[0]["motivo"].lower()


def test_lista_vazia_nao_gera_ultimo_id(mock_get):
    validas, rejeitadas, avisos = buscar_mensagens_discord()
    assert validas == [] and rejeitadas == []
    assert not any("ultimo_id" in a for a in avisos)


# ---------- erros ----------

@pytest.mark.parametrize("status,trecho", [
    (401, "inválido"), (403, "sem acesso"), (500, "HTTP 500"),
])
def test_erros_http(mock_get, status, trecho):
    mock_get.return_value = _resposta(status=status, text="Erro interno")
    validas, rejeitadas, avisos = buscar_mensagens_discord()
    assert validas == [] and rejeitadas == []
    assert any(trecho in a for a in avisos)


def test_excecao_de_conexao(mock_get):
    mock_get.side_effect = RequestException("Timeout")
    validas, _, avisos = buscar_mensagens_discord()
    assert validas == []
    assert any("Erro de conexão" in a for a in avisos)


# ---------- privacidade ----------

def test_autor_pseudonimizado(mock_get, mensagens_api):
    mock_get.return_value = _resposta(json=mensagens_api)
    validas, _, _ = buscar_mensagens_discord()
    assert re.fullmatch(r"membro_\d{3,}", validas[0]["autor_id"])
    assert "Dev Comunidade" not in str(validas)


def test_rejeitadas_sem_dados_pessoais(mock_get, mensagens_api):
    mock_get.return_value = _resposta(json=mensagens_api)
    _, rejeitadas, _ = buscar_mensagens_discord()
    assert "bot_discord" not in str(rejeitadas)


def test_mencao_anonimizada(mock_get):
    msg = {"id": "1", "content": "valeu <@123456789>!", "author": {"id": "9"},
           "timestamp": "2026-11-05T10:00:00.000Z"}
    mock_get.return_value = _resposta(json=[msg])
    validas, _, _ = buscar_mensagens_discord()
    assert "123456789" not in validas[0]["texto"]


# ---------- robustez ----------

def test_json_invalido_nao_quebra(mock_get):
    r = _resposta()
    r.json.side_effect = ValueError("não é JSON")
    mock_get.return_value = r
    validas, _, avisos = buscar_mensagens_discord()
    assert validas == [] and avisos


def test_rate_limit_com_retry_after(mock_get):
    mock_get.return_value = _resposta(status=429, text="rate limited",
                                      headers={"Retry-After": "2"})
    _, _, avisos = buscar_mensagens_discord()
    assert any("2" in a and "segundos" in a.lower() for a in avisos)


def test_ordem_cronologica(mock_get):
    novas = [
        {"id": "2", "content": "segunda", "author": {"id": "1"}, "timestamp": "2026-11-05T10:01:00Z"},
        {"id": "1", "content": "primeira", "author": {"id": "1"}, "timestamp": "2026-11-05T10:00:00Z"},
    ]
    mock_get.return_value = _resposta(json=novas)
    validas, _, _ = buscar_mensagens_discord()
    assert [v["texto"] for v in validas] == ["primeira", "segunda"]

def test_resposta_nao_lista(mock_get):
    # Testa quando a API retorna um objeto JSON que não é lista (ex: erro de payload)
    mock_get.return_value = _resposta(json={"message": "Unauthorized"})
    validas, rejeitadas, avisos = buscar_mensagens_discord()
    assert validas == [] and rejeitadas == []
    assert any("formato inesperado" in a for a in avisos)

def test_timestamp_invalido(mock_get):
    # Testa mensagem com timestamp que quebra o fromisoformat
    msg = {
        "id": "123",
        "content": "teste",
        "author": {"id": "1"},
        "timestamp": "data-malformada"
    }
    mock_get.return_value = _resposta(json=[msg])
    validas, rejeitadas, _ = buscar_mensagens_discord()
    assert validas == []
    assert len(rejeitadas) == 1
    assert "Timestamp" in rejeitadas[0]["motivo"]


def test_tipo_mensagem_invalido(mock_get):
    # Testa mensagem de sistema (ex: tipo 6 - usuário entrou no servidor)
    msg = {
        "id": "123",
        "content": "entrou no canal",
        "author": {"id": "1"},
        "type": 6,
        "timestamp": "2026-11-05T10:00:00.000Z"
    }
    mock_get.return_value = _resposta(json=[msg])
    validas, rejeitadas, _ = buscar_mensagens_discord()
    assert validas == []
    assert len(rejeitadas) == 1
    assert "sistema" in rejeitadas[0]["motivo"].lower()

