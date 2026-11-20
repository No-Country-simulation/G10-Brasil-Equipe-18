"""Regressão do fluxo Estúdio -> Curadoria e do botão Regenerar.

Cobre dois defeitos achados com análise real do Gemini:
1. A edição feita no Estúdio não chegava na Curadoria (chaves "e:" e "c:").
2. Regenerar quebrava com KeyError 'variacoes' em ativo sem esse campo
   (o Gemini não devolve variacoes, só o mock).

Sem chamada ao Gemini e sem OCI: o conftest.py oculta secrets e credenciais.
"""
import copy
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).parent.parent
APP_PATH = str(RAIZ / "app" / "main.py")

sys.path.insert(0, str(RAIZ / "app"))
from mocks.mock_data import HISTORIAS  # noqa: E402

HID = HISTORIAS[0]["id"]

# Formato real do Gemini: sem "variacoes".
ATIVO_CARD = {
    "id": "card_conquista",
    "nome": "Card de conquista",
    "tipo": "card",
    "campos": {
        "titulo": "Primeira vaga como dev júnior",
        "frase": "O portfólio construído no ONE fez toda a diferença.",
    },
}

ATIVO_POST = {
    "id": "post_linkedin",
    "nome": "Post para LinkedIn",
    "tipo": "texto",
    "campos": {"texto": "Texto original gerado pelo Gemini para o post."},
}


def _abrir(pagina, ativos):
    """Sobe o app, injeta uma história com os ativos dados e abre a página."""
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    assert not at.exception, f"Exceção ao iniciar: {at.exception}"

    historia = copy.deepcopy(HISTORIAS[0])
    historia["ativos"] = ativos

    at.session_state["historias"] = [historia]
    at.session_state["historia_atual"] = historia["id"]
    at.session_state["pagina"] = pagina
    at.run()
    assert not at.exception, f"Exceção ao abrir {pagina}: {at.exception}"
    return at


def _valores(widgets):
    return [w.value for w in widgets]


def _toasts(at):
    return [t.value for t in at.toast]


def _campo(widgets, label):
    achados = [w for w in widgets if w.label == label]
    assert len(achados) == 1, f"Campo '{label}' não encontrado (ou repetido)"
    return achados[0]


def _enviar_para_curadoria(at):
    at.button(key=f"enviar_{HID}").click().run()
    assert not at.exception, f"Exceção ao enviar para curadoria: {at.exception}"
    assert at.session_state["pagina"] == "curadoria"


# ---------- Estúdio -> Curadoria ----------

def test_edicao_do_card_chega_na_curadoria():
    at = _abrir("estudio", [ATIVO_CARD])

    _campo(at.text_input, "Título").input("Título editado no Estúdio").run()
    _campo(at.text_input, "Frase de destaque").input("Frase editada no Estúdio").run()

    _enviar_para_curadoria(at)

    valores = _valores(at.text_input)
    assert "Título editado no Estúdio" in valores, f"Curadoria mostrou: {valores}"
    assert "Frase editada no Estúdio" in valores, f"Curadoria mostrou: {valores}"


def test_edicao_do_post_chega_na_curadoria():
    at = _abrir("estudio", [ATIVO_POST])

    _campo(at.text_area, "Texto do case").input("Post editado no Estúdio").run()

    _enviar_para_curadoria(at)

    valores = _valores(at.text_area)
    assert "Post editado no Estúdio" in valores, f"Curadoria mostrou: {valores}"


def test_envio_sem_edicao_mantem_o_texto_original_na_curadoria():
    at = _abrir("estudio", [ATIVO_CARD])

    _enviar_para_curadoria(at)

    valores = _valores(at.text_input)
    assert ATIVO_CARD["campos"]["titulo"] in valores, f"Curadoria mostrou: {valores}"
    assert ATIVO_CARD["campos"]["frase"] in valores, f"Curadoria mostrou: {valores}"


# ---------- Regenerar sem variacoes ----------

def test_regenerar_no_estudio_sem_variacoes_nao_quebra_e_mantem_o_texto():
    at = _abrir("estudio", [ATIVO_CARD])

    at.button(key=f"regen_estudio_{HID}_{ATIVO_CARD['id']}").click().run()

    assert not at.exception, f"Regenerar quebrou no Estúdio: {at.exception}"
    valores = _valores(at.text_input)
    assert ATIVO_CARD["campos"]["titulo"] in valores
    assert ATIVO_CARD["campos"]["frase"] in valores
    toasts = _toasts(at)
    assert any("Sem novas variações" in t for t in toasts), f"Avisos: {toasts}"
    assert not any("Novo rascunho gerado" in t for t in toasts), f"Avisos: {toasts}"


def test_regenerar_na_curadoria_sem_variacoes_nao_quebra_e_mantem_o_texto():
    at = _abrir("curadoria", [ATIVO_POST])

    botoes = [b for b in at.button if b.label == "↻ Regenerar"]
    assert len(botoes) == 1, "Botão Regenerar não encontrado na Curadoria"
    botoes[0].click().run()

    assert not at.exception, f"Regenerar quebrou na Curadoria: {at.exception}"
    assert ATIVO_POST["campos"]["texto"] in _valores(at.text_area)
    toasts = _toasts(at)
    assert any("Sem novas variações" in t for t in toasts), f"Avisos: {toasts}"
    assert not any("Novo rascunho gerado" in t for t in toasts), f"Avisos: {toasts}"

def test_segundo_envio_leva_a_nova_edicao_para_a_curadoria():
    at = _abrir("estudio", [ATIVO_POST])
    _campo(at.text_area, "Texto do case").input("Primeira edição").run()
    _enviar_para_curadoria(at)
    assert "Primeira edição" in _valores(at.text_area)

    at.sidebar.button(key="nav_estudio").click().run()
    _campo(at.text_area, "Texto do case").input("Segunda edição").run()
    _enviar_para_curadoria(at)

    valores = _valores(at.text_area)
    assert "Segunda edição" in valores, f"Curadoria mostrou: {valores}"
