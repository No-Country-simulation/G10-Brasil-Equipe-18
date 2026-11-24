"""Aviso logo abaixo do "Texto do case" quando o texto sai da mensagem original.

A regra é a do preparar_case: cada parágrafo precisa ser um trecho literal da
fonte, na ordem. A fonte é h["mensagem_original"]. O aviso só informa: não
bloqueia nada. O Post para LinkedIn não recebe o aviso. Sem LLM e sem OCI.
"""
import copy
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).parent.parent
APP_PATH = str(RAIZ / "app" / "main.py")

sys.path.insert(0, str(RAIZ / "app"))
from mocks.mock_data import HISTORIAS  # noqa: E402
from services import data_service as svc  # noqa: E402

FONTE = HISTORIAS[0]["mensagem_original"]
P1 = "Consegui minha primeira vaga como dev júnior!"
P2 = "O portfólio que construí no ONE fez a diferença."
INVENTADO = "Essa é uma conquista incrível."
CASE = {"id": "case_sucesso", "nome": "Case de sucesso", "tipo": "texto", "campos": {"texto": P1}}
POST = {"id": "post_linkedin", "nome": "Post para LinkedIn", "tipo": "texto",
        "campos": {"texto": "Conquista da comunidade: primeira vaga como dev júnior."}}


# ---- Função pura ----

def test_fonte_confere_com_a_fonte_inteira():
    assert svc.conferencia_do_texto_case(FONTE, FONTE) == (True, svc.MOTIVO_CASE_LITERAL)


def test_dois_paragrafos_literais_na_ordem_conferem():
    assert svc.conferencia_do_texto_case(f"{P1}\n\n{P2}", FONTE)[0] is True


def test_paragrafo_inventado_nao_confere():
    confere, motivo = svc.conferencia_do_texto_case(f"{P1}\n\n{INVENTADO}", FONTE)
    assert (confere, motivo) == (False, svc.MOTIVO_CASE_FORA_DA_FONTE)


def test_paragrafos_literais_fora_de_ordem_nao_conferem():
    assert svc.conferencia_do_texto_case(f"{P2}\n\n{P1}", FONTE)[0] is False


@pytest.mark.parametrize("fonte", [None, "", "   "])
def test_fonte_indisponivel_e_neutra_nunca_verdadeira(fonte):
    assert svc.conferencia_do_texto_case(P1, fonte) == (None, svc.MOTIVO_INDISPONIVEL)


@pytest.mark.parametrize("texto", [None, "", "   ", "\n\n  \t"])
def test_texto_vazio_com_fonte_nao_confere(texto):
    resultado = svc.conferencia_do_texto_case(texto, FONTE)
    assert resultado[0] is not True
    assert resultado == (None, svc.MOTIVO_CASE_TEXTO_VAZIO)


# ---- Componente ----

def test_texto_vazio_nao_mostra_nada():
    assert "Conferência do texto" not in _html_do_componente("  ", {"mensagem_original": FONTE})


def test_componente_verde_amarelo_e_neutro():
    historia = {"mensagem_original": FONTE}
    verde = _html_do_componente(P1, historia)
    assert "chip-green" in verde and "chip-yellow" not in verde
    amarelo = _html_do_componente(INVENTADO, historia)
    assert "chip-yellow" in amarelo and "chip-green" not in amarelo
    assert "Fontes deste conteúdo" in amarelo
    neutro = _html_do_componente(P1, {})
    assert "chip-green" not in neutro and "chip-yellow" not in neutro
    assert svc.MOTIVO_INDISPONIVEL in neutro


def _html_do_componente(texto, historia):
    import styles
    saida = []
    original = styles.md
    styles.md = saida.append
    try:
        styles.conferencia_do_texto_case_editado(texto, historia)
    finally:
        styles.md = original
    return "".join(saida)


# ---- Telas (AppTest) ----

def _abrir(pagina, ativo):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    assert not at.exception, f"Exceção ao iniciar: {at.exception}"
    historia = copy.deepcopy(HISTORIAS[0])
    historia["ativos"] = [copy.deepcopy(ativo)]
    at.session_state["historias"] = [historia]
    at.session_state["historia_atual"] = historia["id"]
    at.session_state["pagina"] = pagina
    at.run()
    assert not at.exception, f"Exceção em {pagina}: {at.exception}"
    return at


def _area(at):
    return next(w for w in at.text_area if w.label in ("Texto do case", "Texto"))


def _avisos(at):
    return [m.value for m in at.markdown if "Conferência do texto" in m.value]


@pytest.mark.parametrize("pagina", ["estudio", "curadoria"])
def test_case_mostra_verde_e_muda_ao_editar(pagina):
    at = _abrir(pagina, CASE)
    (aviso,) = _avisos(at)
    assert "chip-green" in aviso
    _area(at).set_value(f"{P1}\n\n{INVENTADO}").run()
    assert not at.exception
    (aviso,) = _avisos(at)
    assert "chip-yellow" in aviso and "chip-green" not in aviso
    _area(at).set_value(P1).run()
    (aviso,) = _avisos(at)
    assert "chip-green" in aviso


@pytest.mark.parametrize("pagina", ["estudio", "curadoria"])
def test_post_para_linkedin_nao_mostra_o_aviso(pagina):
    at = _abrir(pagina, POST)
    assert _avisos(at) == []
    _area(at).set_value(INVENTADO).run()
    assert _avisos(at) == []


def test_lote_reaberto_sem_interacoes_usa_mensagem_original_como_fonte():
    at = _abrir("estudio", CASE)
    assert list(at.session_state["interacoes"]) == []
    (aviso,) = _avisos(at)
    assert "chip-green" in aviso
