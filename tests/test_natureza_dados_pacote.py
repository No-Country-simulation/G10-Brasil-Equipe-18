"""Natureza dos dados no pacote do lote.

A declaracao vem da importacao (ficticios, reais ou nao_informado). O pacote
grava o que foi declarado; ausente ou invalida, grava o padrao `nao_informado`,
para o selo nunca deduzir a natureza do autor, do texto ou do provedor.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services import data_service as svc  # noqa: E402
from services import oci_storage  # noqa: E402

LOTE = "LOTE-20261120T200000Z-NATUREZA1"


def _gravar(monkeypatch, **kwargs):
    """Grava o lote e devolve o conteudo do pacote-distribuicao.json."""
    conteudos = {}

    def duble(caminho, dados):
        conteudos[caminho] = dados
        return {
            "caminho": caminho,
            "tamanho": "1,0 KB",
            "salvo_em": "2026-11-20T20:00:00+00:00",
        }

    monkeypatch.setattr(oci_storage, "disponivel", lambda: True)
    monkeypatch.setattr(oci_storage, "salvar_objeto", duble)

    historias = [{"id": "hist-001", "citacoes": [{"id_interacao": 1, "texto": "mensagem"}]}]
    svc.salvar_no_oci(svc.pacotes_do_lote(LOTE), LOTE, historias, **kwargs)

    caminho = next(c for c in conteudos if c.endswith("pacote-distribuicao.json"))
    dados = conteudos[caminho]
    if isinstance(dados, (bytes, bytearray)):
        dados = dados.decode("utf-8")
    return json.loads(dados) if isinstance(dados, str) else dados


def test_sem_declaracao_grava_nao_informado(monkeypatch):
    pacote = _gravar(monkeypatch)
    assert pacote["natureza_dados"] == "nao_informado"


def test_natureza_declarada_e_preservada(monkeypatch):
    assert _gravar(monkeypatch, natureza_dados="ficticios")["natureza_dados"] == "ficticios"
    assert _gravar(monkeypatch, natureza_dados="reais")["natureza_dados"] == "reais"


def test_valor_fora_da_lista_cai_no_padrao(monkeypatch):
    assert _gravar(monkeypatch, natureza_dados="fictício")["natureza_dados"] == "nao_informado"
    assert _gravar(monkeypatch, natureza_dados="outra coisa")["natureza_dados"] == "nao_informado"
    assert _gravar(monkeypatch, natureza_dados=None)["natureza_dados"] == "nao_informado"


def test_pacote_sobe_para_a_versao_1_1(monkeypatch):
    """Campo novo no envelope: formato mudou, versao acompanha."""
    pacote = _gravar(monkeypatch)
    assert pacote["versao_schema"] == "1.1"
    assert "natureza_dados" in pacote


def test_normalizar_aceita_caixa_alta_e_espacos():
    assert svc.normalizar_natureza_dados("  FICTICIOS  ") == "ficticios"
    assert svc.normalizar_natureza_dados("Reais") == "reais"
    assert svc.normalizar_natureza_dados("") == "nao_informado"
