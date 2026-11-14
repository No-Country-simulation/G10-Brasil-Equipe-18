"""O lote novo precisa montar o manifesto do que vai gravar no OCI (Issue #27, item 3).

Hoje estes testes falham: a lista de pacotes a gravar nasce vazia e nada a repoe.
Depois da correcao, os dois passam.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services import data_service as svc  # noqa: E402
from services import oci_storage  # noqa: E402

LOTE = "LOTE-20261110T120000Z-ABCD1234"


def test_manifesto_do_lote_tem_os_dois_arquivos():
    manifesto = svc.pacotes_do_lote(LOTE)

    caminhos = [p["caminho"] for p in manifesto]

    assert len(manifesto) == 2
    assert any(c.endswith("pacote-distribuicao.json") for c in caminhos)
    assert any(c.endswith("evidencias.json") for c in caminhos)


def test_gravacao_do_lote_novo_grava_dois_objetos(monkeypatch):
    gravados = {}

    def duble(caminho, dados):
        gravados[caminho] = dados
        return {
            "caminho": caminho,
            "tamanho": "1,0 KB",
            "salvo_em": "2026-11-10T12:00:00+00:00",
        }

    monkeypatch.setattr(oci_storage, "disponivel", lambda: True)
    monkeypatch.setattr(oci_storage, "salvar_objeto", duble)

    historias = [
        {
            "id": 1,
            "titulo": "Historia de teste",
            "citacoes": [{"id_interacao": 1, "texto": "mensagem original"}],
        }
    ]

    resultado = svc.salvar_no_oci(svc.pacotes_do_lote(LOTE), LOTE, historias)

    assert len(gravados) == 2
    assert all(
        p["status"] == "salvo" and p["persistencia"] == "real" for p in resultado
    )

    pacote = gravados[oci_storage.caminho_do_pacote(LOTE)]
    assert pacote["historias"] == historias
    assert pacote["lote"] == LOTE
