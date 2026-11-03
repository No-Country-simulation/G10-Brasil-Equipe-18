"""Testes do estado do lote (app/state.py) - Issue #27."""
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from state import resetar_lote  # noqa: E402

"""Testes do estado do lote (app/state.py) - Issue #27."""
from types import SimpleNamespace

from state import resetar_lote

def test_resetar_lote_limpa_estado_do_lote_anterior():
    ss = SimpleNamespace()
    resetar_lote(ss)
    ss.historias = [{"id": "h1"}]
    ss.proc_origem_analise = "mock"
    ss.proc_erro_oci = "falha antiga"
    lote_antigo = ss.lote_id

    resetar_lote(ss)

    assert ss.historias == []
    assert ss.proc_origem_analise == ""
    assert ss.proc_erro_oci == ""
    assert ss.lote_id != lote_antigo


