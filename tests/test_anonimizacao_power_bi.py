"""Regressão do falso positivo de anonimização no caso Power BI."""
from types import SimpleNamespace

import pytest

from src.preprocessing import anonimizacao


@pytest.mark.parametrize("caminho", ["fallback", "spacy"])
def test_power_bi_nao_e_mascarado_como_nome(monkeypatch, caminho):
    texto = "Criei um painel em Power BI para analisar os resultados."

    if caminho == "fallback":
        monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    else:
        inicio = texto.index("Power BI")
        entidade = SimpleNamespace(
            label_="PER",
            text="Power BI",
            start_char=inicio,
            end_char=inicio + len("Power BI"),
            root=SimpleNamespace(pos_="PROPN"),
        )
        monkeypatch.setattr(
            anonimizacao,
            "_obter_nlp",
            lambda: lambda _: SimpleNamespace(ents=[entidade]),
        )

    anonimizado, contagem = anonimizacao.anonimizar_texto(texto)

    assert anonimizado == texto
    assert contagem["nome"] == 0
