import sys
from pathlib import Path
from unittest.mock import Mock
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from services import llm_provider as lp

@pytest.fixture
def setup(monkeypatch):
    p = lp.LLMProvider()
    calls = {n: Mock(return_value=lp.RespostaProvedor("ok")) for n in ("gemini", "cohere", "groq")}
    monkeypatch.setattr(p, "_ordem", lambda: [(n, f, n) for n, f in calls.items()])
    return p, calls

@pytest.mark.parametrize("natureza,lista", [("nao_informado", "gemini"), ("reais", ""), ("reais", "gemini,invalido")])
def test_bloqueio(setup, monkeypatch, natureza, lista):
    p, calls = setup
    monkeypatch.setattr(lp, "_cfg", lambda *a: lista)
    with pytest.raises(lp.ErroProvedor):
        p.gerar("p", {}, natureza_dados=natureza)
    assert not any(f.called for f in calls.values())

def test_fallback_restrito(setup, monkeypatch):
    p, calls = setup
    monkeypatch.setattr(lp, "_cfg", lambda *a: "gemini,groq")
    calls["gemini"].side_effect = lp.ErroProvedor("falha")
    assert p.gerar("p", {}, natureza_dados="reais").provedor == "groq"
    calls["cohere"].assert_not_called()

def test_ficticio(setup, monkeypatch):
    p, calls = setup
    monkeypatch.setattr(lp, "_cfg", lambda *a: "")
    assert p.gerar("p", {}, natureza_dados="ficticios").provedor == "gemini"

def test_callable_sem_natureza(setup):
    p, calls = setup
    with pytest.raises(lp.ErroProvedor):
        p.como_callable()("p")
    assert not any(f.called for f in calls.values())

def test_disponibilidade(setup, monkeypatch):
    p, calls = setup
    monkeypatch.setattr(lp, "_cfg", lambda k, *a: "groq" if k == "LLM_PROVEDORES_DADOS_REAIS" else "chave")
    assert p.provedor_disponivel(natureza_dados="reais") == "groq"
