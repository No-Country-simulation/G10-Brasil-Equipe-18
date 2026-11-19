"""Casos gerados para a conferência de citação.

A regra está no docstring de `app/services/conferencia_citacao.py`. Aqui a
gente não escreve caso à mão: a gente constrói o caso a partir da mensagem
original, então sabe a resposta certa sem perguntar ao código.

Famílias cobertas (positivas e negativas):
- marcador no meio, no fim e no início da citação
- citação sem marcador (literal)
- uma letra trocada, duas palavras invertidas, palavra removida
- marcador do tipo errado
- lacuna longa demais e lacuna cruzando fim de frase
- âncora repetida no original (positiva e negativa)
- citação que pertence a outra interação

Seed fixa: o corpus é o mesmo em toda execução, e um caso novo que quebre
aparece com o número dele para virar teste nomeado.
"""
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "app"))

from services.conferencia_citacao import (  # noqa: E402
    MAX_PALAVRAS_MARCADOR,
    MOTIVO_ANONIMIZADO,
    MOTIVO_LITERAL,
    conferir_citacao,
)

SEMENTE = 20261119
TOTAL_POR_FAMILIA = 200

DADOS = {
    "[NOME]": ["Ana", "Ana Paula", "Joao Silva", "Maria de Souza", "Lu"],
    "[EMAIL]": ["ana@exemplo.com", "joao.silva@teste.org", "contato@time.dev"],
    "[CPF]": ["123.456.789-09", "987.654.321-00", "111.222.333-44"],
    "[TELEFONE]": ["(13) 99876-5432", "(11) 3456-7890", "(21) 98765-4321"],
}
OUTRO_TIPO = {
    "[NOME]": "[EMAIL]",
    "[EMAIL]": "[CPF]",
    "[CPF]": "[TELEFONE]",
    "[TELEFONE]": "[NOME]",
}
PREFIXOS = ["Falei com ", "Conversei com ", "Segue o contato: ", "Ontem eu e ",
            "Quem me indicou foi ", "O time inteiro viu: "]
SUFIXOS = [" ontem no grupo.", " e ela me indicou a vaga.", " confirmado.",
           " no canal support.", " depois da aula."]


def _lixo(rng):
    return f"zzqx{rng.randint(10, 99)}"


def _troca_letra(rng, texto):
    """Troca uma letra de uma palavra por outra, sem criar palavra do original."""
    palavras = texto.split()
    for indice in rng.sample(range(len(palavras)), len(palavras)):
        palavra = palavras[indice]
        if len(palavra) > 2 and palavra.isalpha():
            letra = rng.choice("abcdefghij")
            trocada = palavra[:-1] + letra
            if trocada != palavra:
                palavras[indice] = trocada
                return " ".join(palavras)
    return texto + " " + _lixo(rng)


def _inverte_palavras(rng, texto):
    palavras = texto.split()
    if len(palavras) < 2:
        return texto + " " + _lixo(rng)
    a, b = rng.sample(range(len(palavras)), 2)
    palavras[a], palavras[b] = palavras[b], palavras[a]
    return " ".join(palavras)


def _gera_casos():
    rng = random.Random(SEMENTE)
    casos = []

    def novo(familia, trecho, original, esperado, motivo=None):
        casos.append({"familia": familia, "trecho": trecho, "original": original,
                      "esperado": esperado, "motivo": motivo})

    for _ in range(TOTAL_POR_FAMILIA):
        marcador = rng.choice(list(DADOS))
        pii = rng.choice(DADOS[marcador])
        prefixo = rng.choice(PREFIXOS)
        sufixo = rng.choice(SUFIXOS)
        original = prefixo + pii + sufixo

        # 1. marcador no meio
        novo("marcador no meio", prefixo + marcador + sufixo, original, True,
             MOTIVO_ANONIMIZADO)
        # 2. marcador no fim da citação
        novo("marcador no fim", prefixo + marcador, original, True,
             MOTIVO_ANONIMIZADO)
        # 3. marcador no início da citação
        novo("marcador no início", marcador + sufixo, original, True,
             MOTIVO_ANONIMIZADO)
        # 4. literal, sem marcador
        novo("literal", sufixo.strip(), original, True, MOTIVO_LITERAL)
        novo("literal no começo", prefixo.strip(), original, True, MOTIVO_LITERAL)

        # 5. letra trocada no texto literal
        novo("letra trocada", _troca_letra(rng, prefixo) + marcador + sufixo,
             original, False)
        # 6. palavras invertidas
        novo("palavras invertidas", _inverte_palavras(rng, prefixo) + marcador + sufixo,
             original, False)
        # 7. marcador do tipo errado
        novo("tipo errado", prefixo + OUTRO_TIPO[marcador] + sufixo, original, False)
        # 8. lacuna longa demais
        longo = "muito tempo depois de tudo isso passou "
        novo("lacuna longa", prefixo + marcador + sufixo, prefixo + longo + sufixo, False)
        # 9. lacuna cruzando fim de frase
        novo("fim de frase", prefixo + marcador + sufixo,
             prefixo + "Ana. Paula" + sufixo, False)
        # 10. outra interação
        novo("outra interação", prefixo + marcador + sufixo,
             "Organizei meus estudos com as dicas da comunidade.", False)
        # 11. recorte no meio da palavra (não é citação)
        novo("recorte no meio da palavra", "lei com " + marcador + sufixo,
             "Falei com " + pii + sufixo, False)
        # 12. espaço duplo: é formato, confere
        novo("espaço duplo", prefixo + " " + marcador + sufixo, original, True,
             MOTIVO_ANONIMIZADO)
        # 13. reticência no fim da citação: é formato, confere
        novo("reticência final", prefixo + marcador + "...", original, True,
             MOTIVO_ANONIMIZADO)
        # 14. caixa diferente: o texto está diferente, não confere
        novo("caixa diferente",
             prefixo[:1].lower() + prefixo[1:] + marcador + sufixo, original, False)
        # 15. nome mascarado com pontuação no original
        nome_pontuado = rng.choice(["Ana (Aninha)", "Ana, Paula", "Ana P.", "Ana-Clara"])
        novo("nome com pontuação", prefixo + "[NOME]" + sufixo,
             prefixo + nome_pontuado + sufixo, True, MOTIVO_ANONIMIZADO)

    # 11. âncora repetida — negativa (o conteúdo do meio não pode ser pulado)
    novo("âncora repetida", "Falei com [NOME] ontem e [EMAIL].",
         "Falei com Ana ontem e 123. Outra ontem e x@exemplo.com.", False)
    # 12. âncora repetida — positiva
    novo("âncora repetida ok", "Falei com [NOME] ontem e [EMAIL].",
         "Falei com Ana ontem e x@exemplo.com.", True, MOTIVO_ANONIMIZADO)
    # 13. âncora repetida com troca no trecho depois da segunda âncora
    for _ in range(TOTAL_POR_FAMILIA):
        pii = rng.choice(DADOS["[NOME]"])
        email = rng.choice(DADOS["[EMAIL]"])
        original = f"Falei com {pii} ontem e {rng.randint(10, 99)}. Outra ontem e {email}."
        novo("âncora repetida com lixo", "Falei com [NOME] ontem e [EMAIL].",
             original, False)

    return casos


CASOS = _gera_casos()


@pytest.mark.parametrize("caso", CASOS, ids=[f"{i:04d}-{c['familia']}"
                                             for i, c in enumerate(CASOS)])
def test_casos_gerados(caso):
    confere, motivo = conferir_citacao(caso["trecho"], caso["original"])
    assert confere is caso["esperado"], (
        f"[{caso['familia']}] esperado {caso['esperado']}, veio {confere} "
        f"({motivo})\n  citação: {caso['trecho']!r}\n  original: {caso['original']!r}"
    )
    if caso["motivo"]:
        assert motivo == caso["motivo"], (
            f"[{caso['familia']}] motivo {motivo!r}, esperado {caso['motivo']!r}"
        )


def test_corpus_tem_todas_as_familias():
    familias = {caso["familia"] for caso in CASOS}
    esperadas = {
        "marcador no meio", "marcador no fim", "marcador no início", "literal",
        "literal no começo", "letra trocada", "palavras invertidas", "tipo errado",
        "lacuna longa", "fim de frase", "outra interação", "âncora repetida",
        "âncora repetida ok", "âncora repetida com lixo",
    }
    assert esperadas <= familias, f"faltando: {sorted(esperadas - familias)}"


def test_limite_de_palavras_do_nome_e_o_declarado():
    """O limite do marcador de nome é o valor publicado no código."""
    seis_palavras = "Ana Paula de Souza Lima Costa"
    assert len(seis_palavras.split()) > MAX_PALAVRAS_MARCADOR
    confere, _ = conferir_citacao("Falei com [NOME] ontem.",
                                 f"Falei com {seis_palavras} ontem.")
    assert confere is False
