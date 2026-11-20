"""Testes da conferência de citação.

Cobrem os quatro tipos de dado pessoal mascarados, os dois motivos de sucesso
(literal e com anonimização), a rejeição de citação alterada, de citação de
outra interação e de marcador cobrindo conteúdo incompatível com o seu tipo,
e um guarda-corpo: se a anonimização passar a produzir um marcador que a
conferência não conhece, o último teste quebra em vez de o defeito voltar em
silêncio.
"""
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "app"))

from services.conferencia_citacao import (  # noqa: E402
    MARCADORES,
    MOTIVO_ANONIMIZADO,
    MOTIVO_LITERAL,
    conferir_citacao,
)

ORIGINAL = "Conversei com Joao Silva ontem e ele me indicou a vaga."


@pytest.mark.parametrize(
    "caso, trecho, original, esperado",
    [
        ("nome mascarado",
         "Conversei com [NOME] ontem e ele me indicou a vaga.", ORIGINAL, True),
        ("nome de quatro partes",
         "Quem me indicou foi [NOME], do time de dados.",
         "Quem me indicou foi Ana Paula de Souza, do time de dados.", True),
        ("e-mail mascarado",
         "Meu contato e [EMAIL], me chama la.",
         "Meu contato e maria@exemplo.com, me chama la.", True),
        ("CPF mascarado",
         "Meu CPF e [CPF], confere ai.",
         "Meu CPF e 123.456.789-09, confere ai.", True),
        ("telefone mascarado",
         "Liga no [TELEFONE] depois das 18h.",
         "Liga no (13) 99876-5432 depois das 18h.", True),
        ("sem marcador, literal",
         "primeira vaga como dev junior",
         "Consegui minha primeira vaga como dev junior!", True),
        ("sem marcador, alterado",
         "primeira vaga como dev pleno",
         "Consegui minha primeira vaga como dev junior!", False),
        ("citação alterada fora do marcador",
         "Conversei com [NOME] ontem e ele me indicou o emprego.", ORIGINAL, False),
        ("citação de outra interação",
         "Organizei meus estudos com as dicas.",
         "Consegui minha primeira vaga como dev junior!", False),
        ("marcador cobrindo meia frase",
         "Comecei [NOME] fim.",
         "Comecei a estudar muito tempo depois, no fim.", False),
        ("marcador atravessando fim de frase",
         "Consegui a vaga [NOME] hoje eu recomendo.",
         "Consegui a vaga. Muito tempo depois, hoje eu recomendo.", False),
        ("citação só com marcador", "[NOME]", "Joao Silva deu a dica.", False),
        ("citação vazia", "", ORIGINAL, False),
        ("mensagem original ausente", "[NOME] ontem", "", False),
        ("marcador de e-mail cobrindo nome",
         "Meu contato e [EMAIL], me chama la.",
         "Meu contato e Joao Silva, me chama la.", False),
        ("marcador de CPF cobrindo e-mail",
         "Meu CPF e [CPF], confere ai.",
         "Meu CPF e maria@exemplo.com, confere ai.", False),
        ("marcador de nome cobrindo numero",
         "Falei com [NOME] ontem.",
         "Falei com 2024 ontem.", False),
        ("marcador de telefone cobrindo palavra",
         "Liga no [TELEFONE] depois das 18h.",
         "Liga no suporte depois das 18h.", False),
        ("citação terminando em e-mail",
         "Meu contato e [EMAIL]",
         "Meu contato e maria@exemplo.com, me chama la.", True),
        ("citação terminando em CPF",
         "Meu CPF e [CPF]",
         "Meu CPF e 123.456.789-09, confere ai.", True),
        ("citação terminando em telefone",
         "Liga no [TELEFONE]",
         "Liga no (13) 99876-5432 depois das 18h.", True),
        ("citação terminando em marcador, com ponto final",
         "Meu contato e [EMAIL].",
         "Meu contato e maria@exemplo.com.", True),
        ("citação terminando em nome",
         "Quem me indicou foi [NOME]",
         "Quem me indicou foi Ana Paula de Souza, do time de dados.", True),
        ("final aceita dado diferente do citado, porque não compara o dado real",
         "Meu contato e [EMAIL]",
         "Meu contato e outro@exemplo.org, me chama la.", True),
        ("final com tipo errado",
         "Meu contato e [EMAIL]",
         "Meu contato e Joao Silva, me chama la.", False),
        ("marcadores consecutivos, ambos compatíveis",
         "Contato [NOME] [EMAIL] confirmado.",
         "Contato Ana ana@exemplo.com confirmado.", True),
        ("marcadores consecutivos, segundo incompatível",
         "Contato [NOME] [EMAIL] confirmado.",
         "Contato Ana telefone incorreto.", False),
        ("marcadores consecutivos, resto alterado",
         "Contato [NOME] [EMAIL] confirmado.",
         "Contato Ana ana@exemplo.com cancelado.", False),
        ("âncora repetida não pode pular conteúdo",
         "Falei com [NOME] ontem e [EMAIL].",
         "Falei com Ana ontem e 123. Outra ontem e x@exemplo.com.", False),
        ("âncora repetida com o resto batendo",
         "Falei com [NOME] ontem e [EMAIL].",
         "Falei com Ana ontem e x@exemplo.com.", True),
    ],
)
def test_conferencia(caso, trecho, original, esperado):
    confere, motivo = conferir_citacao(trecho, original)
    assert confere is esperado, f"{caso}: esperado {esperado}, veio {confere} ({motivo})"
    if not esperado:
        assert motivo, f"{caso}: reprovou sem motivo"


def test_sucesso_literal_tem_motivo_proprio():
    confere, motivo = conferir_citacao(
        "primeira vaga como dev junior",
        "Consegui minha primeira vaga como dev junior!",
    )
    assert confere is True
    assert motivo == MOTIVO_LITERAL


def test_sucesso_com_marcador_tem_motivo_proprio():
    confere, motivo = conferir_citacao(
        "Conversei com [NOME] ontem e ele me indicou a vaga.", ORIGINAL
    )
    assert confere is True
    assert motivo == MOTIVO_ANONIMIZADO


def test_motivos_de_sucesso_sao_distintos():
    """A interface não pode apresentar os dois casos com o mesmo texto."""
    assert MOTIVO_LITERAL != MOTIVO_ANONIMIZADO
    assert "literal" in MOTIVO_LITERAL
    assert "anonimização" in MOTIVO_ANONIMIZADO


def test_motivo_aponta_tipo_incompativel():
    _, motivo = conferir_citacao(
        "Meu contato e [EMAIL], me chama la.",
        "Meu contato e Joao Silva, me chama la.",
    )
    assert "incompatível com o tipo" in motivo


def test_motivo_distingue_alterado_de_ausente():
    _, motivo_sem_marcador = conferir_citacao("primeira vaga como dev pleno",
                                              "primeira vaga como dev junior")
    _, motivo_com_marcador = conferir_citacao("Conversei com [NOME] ontem e ele me indicou o emprego.",
                                              ORIGINAL)
    assert "não encontrado" in motivo_sem_marcador
    assert "alterado" in motivo_com_marcador


def test_marcadores_conhecidos_cobrem_o_que_a_anonimizacao_produz():
    """Guarda-corpo: um marcador novo na anonimização tem que aparecer aqui."""
    from src.preprocessing import anonimizacao

    texto = (
        "Sou o Joao Silva, meu e-mail e joao@exemplo.com, "
        "meu CPF e 123.456.789-09 e meu telefone e (13) 99876-5432."
    )
    anonimizado, _ = anonimizar_texto_seguro(anonimizacao, texto)
    produzidos = set(re.findall(r"\[[A-ZÇÃÕ]+\]", anonimizado))

    desconhecidos = produzidos - set(MARCADORES)
    assert not desconhecidos, (
        f"a anonimização produziu marcadores que a conferência não conhece: "
        f"{sorted(desconhecidos)}. Atualizar MARCADORES em conferencia_citacao.py"
    )


def anonimizar_texto_seguro(modulo, texto):
    """Anonimiza sem depender do modelo spaCy (usa o fallback)."""
    original = modulo._obter_nlp
    modulo._obter_nlp = lambda: None
    try:
        return modulo.anonimizar_texto(texto)
    finally:
        modulo._obter_nlp = original
