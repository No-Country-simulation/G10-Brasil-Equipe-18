"""Rótulo do Ambiente no resumo do lote (Processamento), sem chamar o LLM."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from telas.processamento import PROVEDORES_REAIS, rotulo_ambiente


@pytest.mark.parametrize("provedor", ["gemini", "cohere", "groq"])
def test_provedor_real_vira_analise_real(provedor):
    assert rotulo_ambiente(provedor) == "Análise real"


def test_modo_demonstrativo_continua_demonstracao():
    assert rotulo_ambiente("mock") == "Demonstração"


@pytest.mark.parametrize("origem", ["", None, "erro", "openai", "Gemini", " groq"])
def test_origem_desconhecida_continua_nao_confirmado(origem):
    assert rotulo_ambiente(origem) == "Não confirmado"


def test_rotulos_possiveis_sao_so_os_tres_combinados():
    """Nenhum texto novo sobre a natureza dos dados: isso é dos selos, ainda sem o back."""
    rotulos = {rotulo_ambiente(o) for o in (*PROVEDORES_REAIS, "mock", "erro", "", None)}
    assert rotulos == {"Análise real", "Demonstração", "Não confirmado"}
