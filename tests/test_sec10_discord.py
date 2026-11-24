from unittest.mock import Mock
import pytest
from src.ingestion import discord_load as d

@pytest.fixture
def importar(monkeypatch):
    monkeypatch.setattr(d, "_cfg", lambda k: {"DISCORD_TOKEN": "fake", "CANAL_ID": "123", "SAL_PSEUDONIMIZACAO": "segredo-ficticio-exclusivo-testes-2026"}.get(k, ""))
    def executar(autores):
        resposta = Mock(status_code=200)
        resposta.json.return_value = [dict(id=str(i+100), author={"id": a}, content="Mensagem de teste", timestamp="2026-01-01T00:00:00Z") for i,a in enumerate(autores)]
        monkeypatch.setattr(d.requests, "get", lambda *a, **kw: resposta)
        return d.buscar_mensagens_discord(sal="segredo-ficticio-exclusivo-testes-2026")
    return executar

def test_colisao_bloqueia_lote_sem_cursor(importar, monkeypatch):
    monkeypatch.setattr(d, "pseudonimizar_autor", lambda *a: "membro_123456")
    validas, _, avisos = importar(["111", "222"])
    assert not validas
    assert any("colisão" in a for a in avisos)
    assert not any(a.startswith(d.MARCADOR_ULTIMO_ID) for a in avisos)
    assert all("111" not in a and "222" not in a for a in avisos)

def test_mesmo_autor_permitido(importar):
    validas, rejeitadas, avisos = importar(["111", "111"])
    assert len(validas) == 2 and not rejeitadas
    assert validas[0]["autor_id"] == validas[1]["autor_id"]
    assert any(a.startswith(d.MARCADOR_ULTIMO_ID) for a in avisos)

@pytest.mark.parametrize("autor", [None, "abc", "0"])
def test_autor_invalido(importar, autor):
    validas, rejeitadas, _ = importar([autor, "111"])
    assert len(validas) == 1 and len(rejeitadas) == 1
    assert "autor" in rejeitadas[0]["motivo"]
