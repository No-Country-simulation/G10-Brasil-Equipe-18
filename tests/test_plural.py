"""Testes para a função plural em app/styles.py."""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))

from state import legenda_ativos  # noqa: E402
from styles import plural  # noqa: E402


def test_plural_singular_um():
    """1 deve retornar a forma singular."""
    assert plural(1, "canal", "canais") == "1 canal"


def test_plural_plural_dois():
    """2 deve retornar a forma plural."""
    assert plural(2, "canal", "canais") == "2 canais"


def test_plural_zero():
    """0 deve retornar a forma plural."""
    assert plural(0, "canal", "canais") == "0 canais"


def test_legenda_zero_aprovados():
    """Quando não há aprovados, a legenda não deve mencionar aprovados."""
    contagem = {
        "total": 5,
        "rascunho": 5,
        "ajustes": 0,
        "aprovado": 0,
        "rejeitado": 0,
    }
    resultado = legenda_ativos(contagem)
    assert "aprovado" not in resultado
    assert "5 rascunhos aguardando" in resultado


def test_legenda_um_aprovado():
    """1 aprovado deve usar a forma singular."""
    contagem = {
        "total": 6,
        "rascunho": 5,
        "ajustes": 0,
        "aprovado": 1,
        "rejeitado": 0,
    }
    resultado = legenda_ativos(contagem)
    assert "1 aprovado" in resultado
    assert "5 rascunhos aguardando" in resultado


def test_legenda_dois_aprovados():
    """2 aprovados deve usar a forma plural."""
    contagem = {
        "total": 7,
        "rascunho": 5,
        "ajustes": 0,
        "aprovado": 2,
        "rejeitado": 0,
    }
    resultado = legenda_ativos(contagem)
    assert "2 aprovados" in resultado


def test_legenda_um_rascunho_aguardando():
    """1 rascunho deve usar a forma singular."""
    contagem = {
        "total": 1,
        "rascunho": 1,
        "ajustes": 0,
        "aprovado": 0,
        "rejeitado": 0,
    }
    resultado = legenda_ativos(contagem)
    assert "1 rascunho aguardando" in resultado


def test_legenda_zero_rascunhos_aguardando():
    """0 rascunhos deve usar a forma plural."""
    contagem = {
        "total": 5,
        "rascunho": 0,
        "ajustes": 0,
        "aprovado": 5,
        "rejeitado": 0,
    }
    resultado = legenda_ativos(contagem)
    assert "0 rascunhos aguardando" in resultado


def test_legenda_sem_numero_repetido():
    """A legenda não deve conter números repetidos (ex: "1 1 aprovado")."""
    contagens = [
        {"total": 1, "rascunho": 0, "ajustes": 0, "aprovado": 1, "rejeitado": 0},
        {"total": 2, "rascunho": 0, "ajustes": 0, "aprovado": 2, "rejeitado": 0},
        {"total": 10, "rascunho": 5, "ajustes": 0, "aprovado": 5, "rejeitado": 0},
        {"total": 15, "rascunho": 10, "ajustes": 5, "aprovado": 0, "rejeitado": 0},
    ]
    
    # Regex para detectar número repetido (ex: "1 1" ou "5 5")
    padrao_duplicado = re.compile(r"\b(\d+) \1\b")
    
    for contagem in contagens:
        resultado = legenda_ativos(contagem)
        match = padrao_duplicado.search(resultado)
        assert match is None, f"Número duplicado encontrado em: {resultado}"
