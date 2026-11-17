from src.preprocessing import anonimizacao


def test_fallback_preserva_foi_no_inicio_da_frase(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    texto = "Consegui minha primeira vaga. Foi uma conquista importante."

    resultado, _ = anonimizacao.anonimizar_texto(texto)

    assert resultado == texto


def test_fallback_mascara_nome_proprio(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)

    resultado, _ = anonimizacao.anonimizar_texto("Conversei com Mariana ontem.")

    assert resultado == "Conversei com [NOME] ontem."
