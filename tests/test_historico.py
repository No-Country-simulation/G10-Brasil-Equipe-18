"""Testes para app/telas/historico.py.

Testa a função deve_exibir_erro() que decide se um erro de armazenamento
deve ser mostrado ao usuário em função do MODO_DEMONSTRACAO.
"""
import sys
from pathlib import Path

import pytest

# Adiciona app/ ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from telas.historico import deve_exibir_erro


def test_erro_credencial_modo_demo_desligado():
    """Caso (a): MODO_DEMONSTRACAO=False + erro credencial → EXIBE."""
    assert deve_exibir_erro("Credencial da OCI nao encontrada", modo_demo=False)
    assert deve_exibir_erro("credencial invalida", modo_demo=False)
    assert deve_exibir_erro("Falha na CREDENCIAL", modo_demo=False)


def test_erro_credencial_modo_demo_ligado():
    """Caso (b): MODO_DEMONSTRACAO=True + erro credencial → OCULTA."""
    assert not deve_exibir_erro("Credencial da OCI nao encontrada", modo_demo=True)
    assert not deve_exibir_erro("credencial invalida", modo_demo=True)
    assert not deve_exibir_erro("Falha na CREDENCIAL", modo_demo=True)


def test_erro_operacional_modo_demo_desligado():
    """Caso (c): MODO_DEMONSTRACAO=False + erro operacional → EXIBE."""
    assert deve_exibir_erro("Falha de rede: timeout", modo_demo=False)
    assert deve_exibir_erro("Permissão negada no bucket", modo_demo=False)
    assert deve_exibir_erro("SDK da OCI nao instalado", modo_demo=False)


def test_erro_operacional_modo_demo_ligado():
    """Caso (d): MODO_DEMONSTRACAO=True + erro operacional → EXIBE."""
    assert deve_exibir_erro("Falha de rede: timeout", modo_demo=True)
    assert deve_exibir_erro("Permissão negada no bucket", modo_demo=True)
    assert deve_exibir_erro("SDK da OCI nao instalado", modo_demo=True)


def test_sem_erro_nao_exibe():
    """Caso (e): Sem erro → não exibe."""
    assert not deve_exibir_erro("", modo_demo=False)
    assert not deve_exibir_erro("", modo_demo=True)


def test_matriz_completa():
    """Matriz de decisão completa: todos os cenários em uma tabela."""
    casos = [
        # (motivo_erro, modo_demo, esperado_exibir, descricao)
        ("Credencial da OCI nao encontrada", False, True, "Credencial + Demo OFF"),
        ("Credencial da OCI nao encontrada", True, False, "Credencial + Demo ON"),
        ("Falha de rede: timeout", False, True, "Operacional + Demo OFF"),
        ("Falha de rede: timeout", True, True, "Operacional + Demo ON"),
        ("", False, False, "Sem erro + Demo OFF"),
        ("", True, False, "Sem erro + Demo ON"),
    ]
    
    for motivo, modo_demo, esperado, descricao in casos:
        resultado = deve_exibir_erro(motivo, modo_demo)
        assert resultado == esperado, f"Falhou: {descricao} (esperado={esperado}, obtido={resultado})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
