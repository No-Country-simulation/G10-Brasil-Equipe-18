"""Regressões para falsos positivos do NER com spaCy disponível."""
from src.preprocessing import anonimizacao


class _Token:
    def __init__(self, pos):
        self.pos_ = pos


class _Entidade:
    label_ = "PER"

    def __init__(self, texto, inicio, pos):
        self.text = texto
        self.start_char = inicio
        self.end_char = inicio + len(texto)
        self.root = _Token(pos)


class _Documento:
    def __init__(self, entidades):
        self.ents = entidades


class _NLPFalso:
    def __init__(self, entidades_por_texto):
        self.entidades_por_texto = entidades_por_texto

    def __call__(self, texto):
        entidades = []
        for trecho, pos in self.entidades_por_texto:
            inicio = texto.index(trecho)
            entidades.append(_Entidade(trecho, inicio, pos))
        return _Documento(entidades)


def test_ner_preserva_sigla_tecnica_classificada_como_pessoa(monkeypatch):
    texto = "Terminei o módulo de APIs do curso ontem."
    monkeypatch.setattr(
        anonimizacao,
        "_obter_nlp",
        lambda: _NLPFalso([("APIs", "PROPN")]),
    )

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == texto
    assert contagem["nome"] == 0


def test_ner_preserva_palavra_funcional_classificada_como_pessoa(monkeypatch):
    texto = "Com as dicas daqui, consegui organizar meus estudos."
    monkeypatch.setattr(
        anonimizacao,
        "_obter_nlp",
        lambda: _NLPFalso([("Com", "ADP")]),
    )

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == texto
    assert contagem["nome"] == 0


def test_ner_mantem_mascaramento_de_nome_proprio(monkeypatch):
    texto = "Conversei com Mariana ontem."
    monkeypatch.setattr(
        anonimizacao,
        "_obter_nlp",
        lambda: _NLPFalso([("Mariana", "PROPN")]),
    )

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == "Conversei com [NOME] ontem."
    assert contagem["nome"] == 1


def test_ner_mascara_nome_proprio_em_caixa_alta(monkeypatch):
    texto = "Conversei com MARIA ontem."
    monkeypatch.setattr(
        anonimizacao,
        "_obter_nlp",
        lambda: _NLPFalso([("MARIA", "PROPN")]),
    )

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == "Conversei com [NOME] ontem."
    assert contagem["nome"] == 1
