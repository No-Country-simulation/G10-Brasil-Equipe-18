"""Testes para a função plural em app/styles.py."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))

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
