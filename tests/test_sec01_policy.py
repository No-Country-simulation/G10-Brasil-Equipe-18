import pytest
from src.config import resolver_sal_pseudonimizacao
from src.ingestion import discord_load

@pytest.mark.parametrize("sal", ["", " ", "communitylab_default_salt"])
def test_sal_publico_rejeitado(sal):
    with pytest.raises(ValueError):
        resolver_sal_pseudonimizacao(sal=sal)
    assert resolver_sal_pseudonimizacao(sal=sal, permitir_publico=True) == "communitylab_default_salt"

def test_sal_configurado(monkeypatch):
    monkeypatch.setenv("SAL_PSEUDONIMIZACAO", "segredo-de-teste")
    assert resolver_sal_pseudonimizacao() == "segredo-de-teste"

def test_discord_bloqueado_antes_da_rede(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "token-teste")
    monkeypatch.setenv("CANAL_ID", "123")
    def proibido(*args, **kwargs):
        pytest.fail("Consulta externa indevida")
    monkeypatch.setattr(discord_load.requests, "get", proibido)
    itens, rejeitadas, avisos = discord_load.buscar_mensagens_discord(sal="communitylab_default_salt")
    assert not itens and not rejeitadas
    assert any("SAL_PSEUDONIMIZACAO" in aviso for aviso in avisos)
