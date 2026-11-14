"""Verifica que o progresso é persistido antes da análise longa."""
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from telas import processamento  # noqa: E402


def test_progresso_e_status_sao_persistidos_antes_da_analise():
    sessao = SimpleNamespace(
        proc_status="novo",
        proc_etapas=["pendente"] * len(processamento.ETAPAS),
    )
    etapas = ["concluida", "andamento", "pendente", "pendente", "pendente", "pendente"]

    processamento._persistir_progresso(sessao, etapas, status="processando")

    assert sessao.proc_status == "processando"
    assert sessao.proc_etapas == etapas
    etapas[1] = "concluida"
    assert sessao.proc_etapas[1] == "andamento"
