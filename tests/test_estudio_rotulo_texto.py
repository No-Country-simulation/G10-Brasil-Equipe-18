"""Rótulo do campo de texto no Estúdio, conforme o tipo de ativo.

Ativos de tipo "texto" são o Case de sucesso e o Post para LinkedIn. O campo
só se chama "Texto do case" quando o ativo é um case, a mesma regra da
Curadoria. A chave do campo (e:<historia>:<ativo>:texto) não muda.
Sem chamada ao LLM e sem OCI.
"""
import copy
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).parent.parent
APP_PATH = str(RAIZ / "app" / "main.py")

sys.path.insert(0, str(RAIZ / "app"))
from mocks.mock_data import HISTORIAS  # noqa: E402

POST = {
    "id": "post_linkedin",
    "nome": "Post para LinkedIn",
    "tipo": "texto",
    "campos": {"texto": "Conquista da comunidade: primeira vaga como dev júnior."},
}
CASE = {
    "id": "case",
    "nome": "Case de sucesso",
    "tipo": "texto",
    "campos": {"texto": "Case de Sucesso: transição para tecnologia."},
}


def _abrir_estudio(ativo):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    assert not at.exception, f"Exceção ao iniciar: {at.exception}"
    historia = copy.deepcopy(HISTORIAS[0])
    historia["ativos"] = [copy.deepcopy(ativo)]
    at.session_state["historias"] = [historia]
    at.session_state["historia_atual"] = historia["id"]
    at.session_state["pagina"] = "estudio"
    at.run()
    assert not at.exception, f"Exceção no Estúdio: {at.exception}"
    return at, historia["id"]


def _areas_de_texto(at):
    return [w for w in at.text_area if w.key and w.key.endswith(":texto")]


def test_post_para_linkedin_usa_o_rotulo_texto():
    at, hid = _abrir_estudio(POST)
    areas = _areas_de_texto(at)
    assert len(areas) == 1
    assert areas[0].label == "Texto"
    assert areas[0].value == POST["campos"]["texto"]


def test_case_de_sucesso_continua_com_texto_do_case():
    at, hid = _abrir_estudio(CASE)
    areas = _areas_de_texto(at)
    assert len(areas) == 1
    assert areas[0].label == "Texto do case"


def test_a_chave_do_campo_nao_muda_com_o_rotulo():
    at, hid = _abrir_estudio(POST)
    assert _areas_de_texto(at)[0].key == f"w::e:{hid}:post_linkedin:texto"
