"""Data do Histórico no fuso de São Paulo.

O bucket grava em UTC; a tela mostrava o horário UTC sem avisar. Estes testes
fixam a conversão e garantem que texto inválido não levanta erro.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "app"))

from services.data_service import _data_br  # noqa: E402


def test_converte_utc_para_sao_paulo():
    assert _data_br("2026-10-22T04:05:54+00:00") == "22/10/2026 01:05"


def test_aceita_sufixo_z():
    assert _data_br("2026-10-22T04:05:54Z") == "22/10/2026 01:05"


def test_mantem_quando_ja_vem_com_offset_local():
    assert _data_br("2026-10-22T01:05:54-03:00") == "22/10/2026 01:05"


def test_sem_fuso_e_tratado_como_utc():
    assert _data_br("2026-10-22T04:05:54") == "22/10/2026 01:05"


def test_virada_de_dia():
    """23h UTC do dia 21 é 20h do dia 21 em São Paulo; 02h UTC é 23h do dia anterior."""
    assert _data_br("2026-10-22T02:30:00+00:00") == "21/10/2026 23:30"


def test_texto_vazio_devolve_vazio():
    assert _data_br("") == ""
    assert _data_br(None) == ""


def test_texto_invalido_nao_quebra():
    assert _data_br("sem data") == "sem data"
