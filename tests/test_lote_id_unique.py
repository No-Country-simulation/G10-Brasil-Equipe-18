"""Os lotes importados precisam de chaves OCI distintas."""
import re
import sys
from pathlib import Path
from types import SimpleNamespace

importacao_path = str(Path(__file__).resolve().parents[1] / "app")
sys.path.insert(0, importacao_path)

from services import oci_storage  # noqa: E402
from telas import importacao  # noqa: E402


def test_cada_novo_lote_recebe_id_unico_e_chave_oci_estavel(monkeypatch):
    sessao = SimpleNamespace()
    monkeypatch.setattr(importacao, "st", SimpleNamespace(session_state=sessao))
    monkeypatch.setattr(importacao, "definir", lambda *args: None)

    interacoes = [{"id": 1, "autor": "membro_001", "canal": "Discord", "texto": "Mensagem."}]
    importacao._novo_lote(interacoes, "Discord", "1 mensagem", "Discord")
    primeiro_id = sessao.lote_id
    primeiro_caminho = oci_storage.caminho_do_lote(
        primeiro_id, f"lote_{primeiro_id}.json"
    )

    importacao._novo_lote(interacoes, "Discord", "1 mensagem", "Discord")
    segundo_id = sessao.lote_id
    segundo_caminho = oci_storage.caminho_do_lote(
        segundo_id, f"lote_{segundo_id}.json"
    )

    assert primeiro_id != segundo_id
    assert re.fullmatch(r"LOTE-\d{8}T\d{6}Z-[A-F0-9]{32}", primeiro_id)
    assert re.fullmatch(r"LOTE-\d{8}T\d{6}Z-[A-F0-9]{32}", segundo_id)
    assert primeiro_caminho != segundo_caminho
    assert oci_storage.caminho_do_lote(primeiro_id, f"lote_{primeiro_id}.json") == primeiro_caminho
