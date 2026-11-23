"""Rótulo do Ambiente no resumo do lote (Processamento), sem chamar o LLM.

O rótulo fala do provedor que respondeu a análise, nunca da natureza dos dados.
"""
import copy
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "app"))

from mocks.mock_data import HISTORIAS  # noqa: E402
from styles import PROVEDORES_NOMES, nome_provedor  # noqa: E402
from telas.processamento import PROVEDORES_REAIS, rotulo_ambiente  # noqa: E402

APP_PATH = str(RAIZ / "app" / "main.py")

_STREAMLIT = sys.modules["streamlit"]


@pytest.fixture(autouse=True)
def _streamlit_integro():
    # test_oci_storage apaga sys.modules["streamlit"] ao terminar; sem este
    # reparo, o AppTest daqui falha com "DeltaGeneratorSingleton instance
    # already exists".
    sys.modules.setdefault("streamlit", _STREAMLIT)


@pytest.mark.parametrize("provedor, esperado", [
    ("gemini", "Análise real (Gemini)"),
    ("cohere", "Análise real (Cohere)"),
    ("groq", "Análise real (Groq)"),
])
def test_provedor_real_mostra_o_nome_do_provedor(provedor, esperado):
    assert rotulo_ambiente(provedor) == esperado


def test_modo_demonstrativo_continua_demonstracao():
    assert rotulo_ambiente("mock") == "Demonstração"


@pytest.mark.parametrize("origem", ["", None, "erro", "openai", "Gemini", " groq"])
def test_origem_desconhecida_continua_nao_confirmado(origem):
    assert rotulo_ambiente(origem) == "Não confirmado"


def test_rotulos_possiveis_sao_so_os_combinados():
    """Nenhum texto novo sobre a natureza dos dados: isso é dos selos, ainda sem o back."""
    rotulos = {rotulo_ambiente(o) for o in (*PROVEDORES_REAIS, "mock", "erro", "", None)}
    assert rotulos == {
        "Análise real (Gemini)", "Análise real (Cohere)", "Análise real (Groq)",
        "Demonstração", "Não confirmado",
    }
    for rotulo in rotulos:
        assert "fictício" not in rotulo.lower() and "dados reais" not in rotulo.lower()


def test_lista_de_provedores_reais_vem_do_mesmo_lugar_dos_nomes():
    assert set(PROVEDORES_REAIS) == set(PROVEDORES_NOMES)


@pytest.mark.parametrize("origem, esperado", [
    ("gemini", "Gemini"), ("cohere", "Cohere"), ("groq", "Groq"),
    ("outro", "Outro"),  # desconhecido: mesmo comportamento anterior das Histórias
    ("", ""), (None, ""),
])
def test_nome_provedor(origem, esperado):
    assert nome_provedor(origem) == esperado


# ---------- telas ----------

def _abrir(pagina, origem):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    assert not at.exception, at.exception
    at.session_state["historias"] = copy.deepcopy(HISTORIAS)
    at.session_state["proc_origem_analise"] = origem
    at.session_state["proc_status"] = "concluido"
    at.session_state["proc_etapas"] = ["concluida"] * 6
    at.session_state["pagina"] = pagina
    at.session_state["f:rel"] = 0
    at.run()
    assert not at.exception, at.exception
    return at


def _html(at):
    return " ".join(m.value for m in at.markdown)


@pytest.mark.parametrize("origem, esperado", [
    ("gemini", "Análise real (Gemini)"), ("cohere", "Análise real (Cohere)"),
    ("groq", "Análise real (Groq)"), ("mock", "Demonstração"),
])
def test_processamento_mostra_o_ambiente_com_o_provedor(origem, esperado):
    html = _html(_abrir("processamento", origem))
    assert f"<span>Ambiente</span><span>{esperado}</span>" in html


@pytest.mark.parametrize("origem, nome", [("gemini", "Gemini"), ("cohere", "Cohere"), ("groq", "Groq")])
def test_historias_mantem_o_texto_com_o_nome_do_provedor(origem, nome):
    html = _html(_abrir("historias", origem))
    assert "Análise real concluída" in html
    assert f"gerados pela IA ({nome})." in html


def test_historias_mantem_o_aviso_de_resultado_simulado():
    html = _html(_abrir("historias", "mock"))
    assert "Resultado simulado, a análise real falhou" in html
    assert "Análise real concluída" not in html
