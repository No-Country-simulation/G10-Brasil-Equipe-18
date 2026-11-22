"""Regressões de citações do PR #68; sem API ou OCI."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.testemunhos import preparar_testemunho


def preparar(fonte, evidencia, citacao, origem=41):
    ativo = {
        "campos": {
            "titulo": fonte,
            "descricao": fonte,
            "citacao": citacao,
        }
    }
    return preparar_testemunho(
        ativo,
        fonte,
        [{"texto": evidencia, "id_interacao": origem}],
        41,
    )


@pytest.mark.parametrize(
    "fonte,evidencia,citacao",
    [
        (
            "Consegui minha vaga no primeiro mes.",
            "primeiro mes",
            "primeiro mes.",
        ),
        (
            "Em outubro consegui minha primeira vaga.",
            "consegui minha primeira vaga.",
            "Em outubro consegui minha primeira vaga.",
        ),
        (
            "Consegui minha vaga.",
            "Consegui minha vaga.",
            "Consegui minha vaga",
        ),
        (
            "Em outubro consegui minha primeira vaga.",
            "consegui  minha primeira vaga.",
            "Em outubro consegui minha primeira vaga.",
        ),
    ],
)
def test_aceita_pontuacao_final_e_extensao_literal(
    fonte, evidencia, citacao
):
    ativo, erro = preparar(fonte, evidencia, citacao)

    assert erro == ""
    assert ativo["campos"]["citacao"] == citacao
    assert ativo["interacoes_origem"] == [41]


def test_espacos_da_citacao_sao_recuperados_da_fonte():
    fonte = "Em outubro consegui\nminha primeira vaga."

    ativo, erro = preparar(
        fonte,
        "consegui minha primeira vaga",
        "consegui  minha primeira vaga.",
    )

    assert erro == ""
    assert ativo["campos"]["citacao"] == (
        "consegui\nminha primeira vaga."
    )
    assert ativo["citacoes"][0]["texto"] == ativo["campos"]["citacao"]


@pytest.mark.parametrize(
    "fonte,evidencia,citacao",
    [
        (
            "Ainda não consegui minha vaga.",
            "não consegui minha vaga.",
            "consegui minha vaga.",
        ),
        (
            "Consegui minha vaga e não fui contratado.",
            "Consegui minha vaga e não fui contratado.",
            "Consegui minha vaga",
        ),
        (
            "Em outubro consegui minha vaga.",
            "consegui minha vaga.",
            "Em novembro consegui minha vaga.",
        ),
        (
            "Consegui minha vaga.",
            "Consegui minha vaga.",
            "Consegui, minha vaga.",
        ),
        (
            "Uma conquista.",
            "conquista.",
            "Uma conquista inventada.",
        ),
        (
            "Minha conquista.",
            "Minha conquista.",
            "conquista",
        ),
        (
            "Sem resultados.",
            "",
            "Sem resultados.",
        ),
    ],
)
def test_recusa_corte_invencao_ou_evidencia_vazia(
    fonte, evidencia, citacao
):
    ativo, erro = preparar(fonte, evidencia, citacao)

    assert ativo is None
    assert erro


def test_nao_confunde_palavra_com_sufixo():
    ativo, erro = preparar(
        "Recontratado.",
        "contratado",
        "Recontratado.",
    )

    assert ativo is None
    assert erro


def test_recusa_evidencia_de_outra_interacao():
    ativo, erro = preparar(
        "Consegui minha vaga.",
        "Consegui minha vaga.",
        "Consegui minha vaga.",
        origem=42,
    )

    assert ativo is None
    assert erro


def test_pontuacao_inventada_na_fonte_continua_recusada():
    ativo, erro = preparar(
        "Consegui minha vaga",
        "Consegui minha vaga",
        "Consegui minha vaga.",
    )

    assert ativo is None
    assert erro