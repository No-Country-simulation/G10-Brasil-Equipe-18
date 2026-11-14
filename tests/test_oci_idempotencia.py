"""Regravar o mesmo lote nao pode criar objetos novos (CATP-011).

A garantia vem do caminho ser deterministico: mesmo lote, mesmo nome de
arquivo, mesmo objeto. A segunda gravacao sobrescreve em vez de duplicar.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services import data_service as svc  # noqa: E402
from services import oci_storage  # noqa: E402

LOTE = "LOTE-20261110T120000Z-IDEM0001"


def test_regravar_o_mesmo_lote_reusa_os_mesmos_objetos(monkeypatch):
    chamadas = []

    def duble(caminho, dados):
        chamadas.append(caminho)
        return {
            "caminho": caminho,
            "tamanho": "1,0 KB",
            "salvo_em": "2026-11-10T12:00:00+00:00",
        }

    monkeypatch.setattr(oci_storage, "disponivel", lambda: True)
    monkeypatch.setattr(oci_storage, "salvar_objeto", duble)

    historias = [{"id": 1, "citacoes": [{"id_interacao": 1, "texto": "mensagem"}]}]
    manifesto = svc.pacotes_do_lote(LOTE)

    primeira = svc.salvar_no_oci(manifesto, LOTE, historias)
    segunda = svc.salvar_no_oci(manifesto, LOTE, historias)

    # Duas gravacoes de dois arquivos = quatro chamadas...
    assert len(chamadas) == 4
    # ...mas apenas dois objetos distintos: a segunda sobrescreve a primeira.
    assert len(set(chamadas)) == 2
    assert all(p["status"] == "salvo" for p in primeira + segunda)
