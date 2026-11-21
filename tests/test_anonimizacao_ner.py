"""Regressões para falsos positivos do NER com spaCy disponível."""
import pytest

from src.preprocessing import anonimizacao


class _Token:
    def __init__(self, pos):
        self.pos_ = pos


class _Entidade:
    def __init__(self, texto, inicio, pos, label="PER"):
        self.label_ = label
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
        for definicao in self.entidades_por_texto:
            trecho, pos = definicao[:2]
            label = definicao[2] if len(definicao) > 2 else "PER"
            inicio = texto.index(trecho)
            entidades.append(_Entidade(trecho, inicio, pos, label))
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


def test_ner_preserva_termo_tecnico_apos_verbo_de_estudo(monkeypatch):
    texto = "júnior! Estudei SQL e Power BI"
    monkeypatch.setattr(
        anonimizacao,
        "_obter_nlp",
        lambda: _NLPFalso([("Estudei SQL", "PROPN"), ("Power BI", "PROPN")]),
    )

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == texto
    assert contagem["nome"] == 0


def test_ner_mascara_nome_composto_rotulado_como_loc_em_contexto_pessoal(monkeypatch):
    texto = "Fizemos tudo em dupla com a Renata Moura."
    monkeypatch.setattr(
        anonimizacao,
        "_obter_nlp",
        lambda: _NLPFalso([("Renata Moura", "PROPN", "LOC")]),
    )

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == "Fizemos tudo em dupla com a [NOME]."
    assert contagem["nome"] == 1


@pytest.mark.parametrize(
    ("texto", "local"),
    [
        ("Visitamos São Paulo no evento.", "São Paulo"),
        ("Visitamos Curitiba no evento.", "Curitiba"),
        ("Visitamos Florianópolis no evento.", "Florianópolis"),
    ],
)
def test_ner_preserva_loc_sem_contexto_de_pessoa(monkeypatch, texto, local):
    monkeypatch.setattr(
        anonimizacao,
        "_obter_nlp",
        lambda: _NLPFalso([(local, "PROPN", "LOC")]),
    )

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == texto
    assert contagem["nome"] == 0


def test_modelo_real_mascara_nome_loc_e_preserva_estudei_sql(monkeypatch):
    import spacy

    try:
        nlp = spacy.load("pt_core_news_sm")
    except OSError:
        pytest.skip("modelo pt_core_news_sm não instalado")

    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: nlp)

    texto_nome = "Fizemos tudo em dupla com a Renata Moura"
    nome_anonimizado, _ = anonimizacao.anonimizar_texto(texto_nome)
    texto_per = "Conversei com Renata Medeiros ontem"
    per_anonimizado, _ = anonimizacao.anonimizar_texto(texto_per)
    texto_tecnico = "júnior! Estudei SQL e Power BI"
    tecnico_anonimizado, contagem = anonimizacao.anonimizar_texto(texto_tecnico)

    assert nome_anonimizado == "Fizemos tudo em dupla com a [NOME]"
    assert per_anonimizado == "Conversei com [NOME] ontem"
    assert tecnico_anonimizado == texto_tecnico
    assert contagem["nome"] == 0
