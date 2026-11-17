"""Regressão do Estúdio de Conteúdo para o tipo de ativo "card".

O Gemini devolve o Card de conquista com tipo "card" e os campos titulo e
frase (sem "texto" e sem "variacoes"). O mock usa "testemunho", por isso a
suíte antiga não cobria esse formato. Sem chamada ao Gemini e sem OCI: o
conftest.py oculta secrets e credenciais.
"""
import copy
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).parent.parent
APP_PATH = str(RAIZ / "app" / "main.py")

# main.py importa "state", "styles" etc. a partir de app/, então o mesmo
# diretório precisa estar no path para importar o mock de historias.
sys.path.insert(0, str(RAIZ / "app"))
from mocks.mock_data import HISTORIAS  # noqa: E402

TITULO = "Primeira vaga como dev júnior"
FRASE = "O portfólio construído no ONE fez toda a diferença."

ATIVO_CARD = {
    "id": "card_conquista",
    "nome": "Card de conquista",
    "tipo": "card",
    "campos": {"titulo": TITULO, "frase": FRASE},
}

ATIVO_DESCONHECIDO = {
    "id": "ativo_novo",
    "nome": "Ativo novo",
    "tipo": "formato_que_nao_existe",
    "campos": {"qualquer": "valor"},
}


def _abrir_estudio(ativos):
    """Sobe o app, injeta uma história com os ativos dados e abre o Estúdio."""
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    assert not at.exception, f"Exceção ao iniciar: {at.exception}"

    historia = copy.deepcopy(HISTORIAS[0])
    historia["ativos"] = ativos

    at.session_state["historias"] = [historia]
    at.session_state["historia_atual"] = historia["id"]
    at.session_state["pagina"] = "estudio"
    at.run()
    return at


def _por_label(widgets, label):
    return [w for w in widgets if w.label == label]


def test_estudio_abre_card_com_titulo_e_frase():
    """Card no formato do Gemini abre sem exceção e mostra título e frase."""
    at = _abrir_estudio([ATIVO_CARD])

    assert not at.exception, f"Exceção no Estúdio com ativo card: {at.exception}"

    titulos = _por_label(at.text_input, "Título")
    frases = _por_label(at.text_input, "Frase de destaque")
    assert len(titulos) == 1, "Campo Título do card não apareceu"
    assert len(frases) == 1, "Campo Frase de destaque do card não apareceu"
    assert titulos[0].value == TITULO
    assert frases[0].value == FRASE

    # O card não deve cair no formulário de texto
    assert not _por_label(at.text_area, "Texto do case")


def test_estudio_avisa_tipo_desconhecido_sem_quebrar():
    """Tipo de ativo desconhecido mostra aviso em vez de exceção."""
    at = _abrir_estudio([ATIVO_DESCONHECIDO])

    assert not at.exception, f"Exceção no Estúdio com tipo desconhecido: {at.exception}"
    avisos = [w.value for w in at.warning]
    assert any("não suportado" in a for a in avisos), f"Aviso não apareceu: {avisos}"
    assert not _por_label(at.text_area, "Texto do case")
