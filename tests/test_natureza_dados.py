"""Natureza dos dados declarada: controle na Importação e selo nas Histórias.

O selo mostra só o que a pessoa declarou. Nunca deduz por provedor, origem,
autor ou conteúdo. Sem Gemini e sem OCI: nenhum teste clica em "Importar
interações" (isso dispararia o processamento).
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
from styles import rotulo_natureza  # noqa: E402

NAO_INFORMADA = ("Natureza não informada", "gray")


@pytest.mark.parametrize(
    "valor, esperado",
    [
        ("ficticios", ("Dados fictícios (declarado)", "yellow")),
        ("reais", ("Dados reais (declarado)", "blue")),
        ("nao_informado", NAO_INFORMADA),
        (None, NAO_INFORMADA),
        ("", NAO_INFORMADA),
        ("real", NAO_INFORMADA),
        ("verdadeiro", NAO_INFORMADA),
        # svc.normalizar_natureza_dados ignora caixa e espaços; o pacote grava igual.
        ("  Reais ", ("Dados reais (declarado)", "blue")),
    ],
)
def test_rotulo_por_valor(valor, esperado):
    assert rotulo_natureza(valor) == esperado


def test_nenhum_valor_usa_verde():
    tons = {rotulo_natureza(v)[1] for v in ("ficticios", "reais", "nao_informado", "x")}
    assert "green" not in tons


def _abrir(pagina="importacao"):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    assert not at.exception, at.exception
    at.session_state["pagina"] = pagina
    at.run()
    assert not at.exception, at.exception
    return at


def _carregar_lote(at):
    next(b for b in at.button if b.label == "Carregar JSON").click().run()
    assert not at.exception, at.exception


def _radio(at):
    return next(r for r in at.radio if r.key == "w::natureza_dados")


def _historias(at, natureza, provedor):
    at.session_state["historias"] = [copy.deepcopy(HISTORIAS[0])]
    at.session_state["proc_origem_analise"] = provedor
    at.session_state["dados"] = {**at.session_state["dados"], "natureza_dados": natureza}
    at.session_state["pagina"] = "historias"
    at.run()
    assert not at.exception, at.exception
    return " ".join(m.value for m in at.markdown)


@pytest.mark.parametrize("provedor", ["gemini", "cohere", "mock", ""])
def test_selo_nao_muda_com_o_provedor(provedor):
    html = _historias(_abrir(), "nao_informado", provedor)
    assert "Natureza não informada" in html
    assert "Origem: Real" not in html and "Origem: Simulada" not in html
    assert "mensagem fictícia" not in html


@pytest.mark.parametrize(
    "natureza, texto",
    [
        ("ficticios", "Dados fictícios (declarado)"),
        ("reais", "Dados reais (declarado)"),
        ("nao_informado", "Natureza não informada"),
    ],
)
def test_historias_mostram_o_selo_declarado(natureza, texto):
    html = _historias(_abrir(), natureza, "gemini")
    assert texto in html
    assert sum(t in html for t in ("Dados fictícios", "Dados reais", "Natureza não informada")) == 1


def test_padrao_e_nao_informado_e_opcoes():
    at = _abrir()
    _carregar_lote(at)
    radio = _radio(at)
    assert radio.value == "nao_informado"
    assert list(radio.options) == [
        "Fictícios (exemplo ou teste)",
        "Reais (relatos de pessoas)",
        "Não informado",
    ]


def test_declaracao_sobrevive_a_troca_de_tela():
    at = _abrir()
    _carregar_lote(at)
    _radio(at).set_value("ficticios").run()
    assert at.session_state["dados"]["natureza_dados"] == "ficticios"
    at.session_state["pagina"] = "historias"
    at.run()
    at.session_state["pagina"] = "importacao"
    at.run()
    assert not at.exception, at.exception
    assert at.session_state["dados"]["natureza_dados"] == "ficticios"
    assert _radio(at).value == "ficticios"


def test_lote_novo_volta_para_nao_informado():
    at = _abrir()
    _carregar_lote(at)
    _radio(at).set_value("reais").run()
    assert at.session_state["dados"]["natureza_dados"] == "reais"
    _carregar_lote(at)  # outro lote, sem StreamlitAPIException
    assert at.session_state["dados"]["natureza_dados"] == "nao_informado"
    assert _radio(at).value == "nao_informado"


def test_controle_trava_depois_de_importar_e_destrava_no_lote_novo():
    at = _abrir()
    _carregar_lote(at)
    assert not _radio(at).disabled
    at.session_state["natureza_travada"] = True
    at.run()
    assert _radio(at).disabled
    assert any("Declaração registrada para este lote" in m.value for m in at.markdown)
    _carregar_lote(at)
    assert not _radio(at).disabled


def test_reiniciar_demonstracao_volta_para_nao_informado():
    at = _abrir()
    _carregar_lote(at)
    _radio(at).set_value("reais").run()
    next(b for b in at.sidebar.button if b.label == "Reiniciar demonstração").click().run()
    assert not at.exception, at.exception
    assert at.session_state["dados"].get("natureza_dados", "nao_informado") == "nao_informado"


def test_reenviar_o_mesmo_arquivo_libera_a_declaracao():
    conteudo = (
        b'[{"autor":"Ana","canal":"#geral","tipo":"mensagem",'
        b'"texto":"Consegui minha primeira vaga como dev."}]'
    )
    at = _abrir()
    at.file_uploader[0].set_value(("lote.json", conteudo, "application/json")).run()
    assert not at.exception, at.exception
    lote_1 = at.session_state["lote_id"]
    _radio(at).set_value("reais").run()
    at.session_state["natureza_travada"] = True
    at.run()
    assert _radio(at).disabled

    # Mesmo arquivo, sem esvaziar o campo: continua o mesmo lote e travado.
    at.run()
    assert at.session_state["lote_id"] == lote_1
    assert _radio(at).disabled

    # Campo esvaziado e o mesmo arquivo reenviado: lote novo, declaração liberada.
    at.file_uploader[0].set_value(None).run()
    assert at.session_state["ultimo_upload"] is None
    at.file_uploader[0].set_value(("lote.json", conteudo, "application/json")).run()
    assert not at.exception, at.exception
    assert at.session_state["lote_id"] != lote_1
    assert at.session_state["dados"]["natureza_dados"] == "nao_informado"
    assert not _radio(at).disabled
