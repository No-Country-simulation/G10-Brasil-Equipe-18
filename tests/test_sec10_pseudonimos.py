import json
import re
import hashlib
import hmac
import pytest
from src.ingestion import ingestion as ing


def test_hmac_formato_e_determinismo():
    esperado = int.from_bytes(hmac.new(b"sal-teste", b"autor-teste", hashlib.sha256).digest(), "big") % 10**20
    resultado = ing.pseudonimizar_autor("autor-teste", "sal-teste")
    assert resultado == f"membro_{esperado:020d}"
    assert re.fullmatch(r"membro_[0-9]{20}", resultado)
    assert resultado == ing.pseudonimizar_autor("autor-teste", "sal-teste")


def test_sais_distintos():
    assert ing.pseudonimizar_autor("autor-teste", "a") != ing.pseudonimizar_autor("autor-teste", "b")


@pytest.mark.parametrize("autor", ["membro_001", "membro_123456", "membro_12345678901234567890"])
def test_preserva_legado_e_idempotencia(autor):
    assert ing.pseudonimizar_autor(autor, "sal-teste") == autor


@pytest.mark.parametrize("formato", ["json", "csv", "dataframe"])
def test_colisao_bloqueia_lote(monkeypatch, formato):
    monkeypatch.setattr(ing, "pseudonimizar_autor", lambda autor, sal: "membro_777777")
    dados = [{"autor": "A", "texto": "Mensagem um"}, {"autor": "B", "texto": "Mensagem dois"}]
    if formato == "json":
        validas, rejeitadas, avisos = ing.processar_json(json.dumps(dados), "sal")
    elif formato == "csv":
        validas, rejeitadas, avisos = ing.processar_csv("autor,texto\nA,Mensagem um\nB,Mensagem dois\n", "sal")
    else:
        import pandas as pd
        validas, rejeitadas, avisos = ing.processar_dataframe(pd.DataFrame(dados), "sal")
    assert validas == []
    assert rejeitadas
    assert any("colisão" in aviso for aviso in avisos)
