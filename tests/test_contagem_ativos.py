"""Testes para a contagem completa de ativos (Tarefa 1)."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))

from state import contagem_ativos_completa  # noqa: E402


def test_contagem_sem_status_registrado():
    """3 histórias x 2 ativos sem nenhum status deve dar 6 gerados, 6 aguardando, 0 aprovados."""
    historias = [
        {"id": "h1", "ativos": [{"id": "a1"}, {"id": "a2"}]},
        {"id": "h2", "ativos": [{"id": "a3"}, {"id": "a4"}]},
        {"id": "h3", "ativos": [{"id": "a5"}, {"id": "a6"}]},
    ]
    status_dict = {}
    
    resultado = contagem_ativos_completa(historias, status_dict)
    
    assert resultado["total"] == 6
    assert resultado["rascunho"] == 6
    assert resultado["ajustes"] == 0
    assert resultado["aprovado"] == 0
    assert resultado["rejeitado"] == 0


def test_contagem_com_dois_aprovados():
    """Com 2 aprovados, deve ter 4 aguardando (rascunho)."""
    historias = [
        {"id": "h1", "ativos": [{"id": "a1"}, {"id": "a2"}]},
        {"id": "h2", "ativos": [{"id": "a3"}, {"id": "a4"}]},
        {"id": "h3", "ativos": [{"id": "a5"}, {"id": "a6"}]},
    ]
    status_dict = {
        "h1:a1": "aprovado",
        "h2:a3": "aprovado",
    }
    
    resultado = contagem_ativos_completa(historias, status_dict)
    
    assert resultado["total"] == 6
    assert resultado["rascunho"] == 4
    assert resultado["ajustes"] == 0
    assert resultado["aprovado"] == 2
    assert resultado["rejeitado"] == 0


def test_contagem_com_ajustes():
    """Inclui um caso com ajustes solicitados."""
    historias = [
        {"id": "h1", "ativos": [{"id": "a1"}, {"id": "a2"}]},
        {"id": "h2", "ativos": [{"id": "a3"}, {"id": "a4"}]},
    ]
    status_dict = {
        "h1:a1": "aprovado",
        "h1:a2": "ajustes",
        "h2:a3": "rascunho",
        # h2:a4 não tem status registrado, conta como rascunho
    }
    
    resultado = contagem_ativos_completa(historias, status_dict)
    
    assert resultado["total"] == 4
    assert resultado["rascunho"] == 2  # a3 (explícito) + a4 (sem status)
    assert resultado["ajustes"] == 1
    assert resultado["aprovado"] == 1
    assert resultado["rejeitado"] == 0


def test_contagem_com_rejeitado():
    """Inclui um caso com rejeitado."""
    historias = [
        {"id": "h1", "ativos": [{"id": "a1"}, {"id": "a2"}, {"id": "a3"}]},
        {"id": "h2", "ativos": [{"id": "a4"}]},
    ]
    status_dict = {
        "h1:a1": "aprovado",
        "h1:a2": "rejeitado",
        "h1:a3": "ajustes",
        "h2:a4": "rascunho",
    }
    
    resultado = contagem_ativos_completa(historias, status_dict)
    
    assert resultado["total"] == 4
    assert resultado["rascunho"] == 1
    assert resultado["ajustes"] == 1
    assert resultado["aprovado"] == 1
    assert resultado["rejeitado"] == 1


def test_contagem_historias_sem_ativos():
    """História sem ativos não deve quebrar."""
    historias = [
        {"id": "h1", "ativos": []},
        {"id": "h2", "ativos": [{"id": "a1"}]},
    ]
    status_dict = {"h2:a1": "aprovado"}
    
    resultado = contagem_ativos_completa(historias, status_dict)
    
    assert resultado["total"] == 1
    assert resultado["rascunho"] == 0
    assert resultado["aprovado"] == 1


def test_contagem_todos_aprovados():
    """Todos aprovados: rascunho deve ser 0."""
    historias = [
        {"id": "h1", "ativos": [{"id": "a1"}, {"id": "a2"}]},
    ]
    status_dict = {
        "h1:a1": "aprovado",
        "h1:a2": "aprovado",
    }
    
    resultado = contagem_ativos_completa(historias, status_dict)
    
    assert resultado["total"] == 2
    assert resultado["rascunho"] == 0
    assert resultado["aprovado"] == 2
