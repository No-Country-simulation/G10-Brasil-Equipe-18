"""Regression test for PII in metadata sent to LLM providers."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from services import llm, llm_provider
from src.preprocessing import anonimizacao


def test_metadata_pii_not_sent_to_provider(monkeypatch):
    captured = []

    class FakeProvider:
        def __init__(self, timeout):
            pass

        def gerar(self, prompt, payload, *, natureza_dados):
            captured.extend(json.loads(payload))
            return SimpleNamespace(texto='{"historias": []}', provedor="teste",
                                   modelo="fake", finish_reason="STOP")

    monkeypatch.setattr(llm_provider, "LLMProvider", FakeProvider)
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    item = {"id": 1, "autor": "membro_123456", "canal": "marina@example.com",
            "tipo": "123.456.789-00", "texto": "Consegui minha primeira vaga."}
    before = dict(item)
    llm.analisar([item], natureza_dados="ficticios")
    assert len(captured) == 1
    assert "marina@example.com" not in captured[0]["canal"]
    assert "123.456.789-00" not in captured[0]["tipo"]
    assert item == before
