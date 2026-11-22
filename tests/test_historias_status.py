"""Chip de status de cada história na tela Histórias.

História sem ativos (por exemplo, quando nenhum formato passou na conferência
da fonte) não pode aparecer como "Rejeitado": ninguém tomou essa decisão. Sem
chamada ao Gemini e sem OCI.
"""
import copy
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).parent.parent
APP_PATH = str(RAIZ / "app" / "main.py")

sys.path.insert(0, str(RAIZ / "app"))
from mocks.mock_data import HISTORIAS  # noqa: E402


def _abrir_historias(ativos, status_curadoria=None):
    """Sobe o app com uma história de ativos dados e abre a tela Histórias."""
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    assert not at.exception, f"Exceção ao iniciar: {at.exception}"

    historia = copy.deepcopy(HISTORIAS[0])
    historia["ativos"] = ativos

    at.session_state["historias"] = [historia]
    at.session_state["pagina"] = "historias"
    at.session_state["f:rel"] = 0
    if status_curadoria:
        at.session_state["status_curadoria"] = {
            f"{historia['id']}:{a['id']}": status_curadoria for a in ativos
        }
    at.run()
    assert not at.exception, f"Exceção em Histórias: {at.exception}"
    return at, historia


def _cartao(at):
    """HTML do rodapé do cartão (contagem de ativos e chip de status)."""
    return " ".join(m.value for m in at.markdown if "ativos gerados" in m.value)


def test_historia_sem_ativos_mostra_chip_neutro_e_nao_rejeitado():
    at, _ = _abrir_historias([])
    html = _cartao(at)
    assert "0 ativos gerados" in html
    assert "Sem ativos gerados" in html
    assert "chip-gray" in html
    assert "Rejeitado" not in html
    assert "chip-red" not in html


def test_historia_com_ativos_em_rascunho_segue_pendente():
    ativos = copy.deepcopy(HISTORIAS[0]["ativos"])
    at, _ = _abrir_historias(ativos)
    html = _cartao(at)
    assert "Revisão humana pendente" in html
    assert "Sem ativos gerados" not in html


def test_historia_com_todos_ativos_rejeitados_segue_rejeitada():
    ativos = copy.deepcopy(HISTORIAS[0]["ativos"])
    at, _ = _abrir_historias(ativos, status_curadoria="rejeitado")
    html = _cartao(at)
    assert "Rejeitado" in html
    assert "chip-red" in html
    assert "Sem ativos gerados" not in html


def test_historia_com_ativos_aprovados_segue_concluida():
    ativos = copy.deepcopy(HISTORIAS[0]["ativos"])
    at, _ = _abrir_historias(ativos, status_curadoria="aprovado")
    html = _cartao(at)
    assert "Revisão concluída" in html
    assert "Sem ativos gerados" not in html
