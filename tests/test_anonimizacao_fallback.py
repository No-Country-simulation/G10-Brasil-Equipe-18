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


def test_fallback_preserva_palavras_no_inicio_de_frase(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    texto = "Concluí o módulo. Usei os exemplos. Com isso, avancei."

    resultado, _ = anonimizacao.anonimizar_texto(texto)

    assert resultado == texto


def test_fallback_mascara_nome_composto_com_um_unico_marcador(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    texto = "Fizemos tudo em dupla com a Renata Moura."

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == "Fizemos tudo em dupla com a [NOME]."
    assert contagem["nome"] == 1


def test_fallback_mascara_nome_composto_no_inicio_da_frase(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    texto = "Renata Moura compartilhou a solução com a equipe."

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == "[NOME] compartilhou a solução com a equipe."
    assert contagem["nome"] == 1


def test_fallback_mascara_nome_composto_em_caixa_alta_com_contexto(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    texto = "Trabalhei com a RENATA MOURA no projeto."

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == "Trabalhei com a [NOME] no projeto."
    assert contagem["nome"] == 1


def test_fallback_mascara_nome_de_local_em_contexto_pessoal(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    texto = "Conversei com Paulo ontem."

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == "Conversei com [NOME] ontem."
    assert contagem["nome"] == 1


def test_fallback_mascara_nome_no_inicio_com_indicio_de_pessoa(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    texto = "Paulo me ajudou a aprender SQL."

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == "[NOME] me ajudou a aprender SQL."
    assert contagem["nome"] == 1


def test_fallback_preserva_local_e_termo_tecnico_em_frase_inicial(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    texto = "São Paulo usa Power BI. Foi útil."

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == texto
    assert contagem["nome"] == 0


def test_fallback_preserva_marcadores_pseudonimizados(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    texto = "Falei com [NOME] e recebi [EMAIL]."

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == texto
    assert contagem["nome"] == 0


def test_fallback_nao_junta_nome_e_produto_separados_por_virgula(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    texto = "Conversei com Bianca, Oracle Cloud foi usado no projeto."

    resultado, contagem = anonimizacao.anonimizar_texto(texto)

    assert resultado == "Conversei com [NOME], Oracle Cloud foi usado no projeto."
    assert contagem["nome"] == 1


def test_fallback_preserva_produtos_com_nomes_compostos(monkeypatch):
    monkeypatch.setattr(anonimizacao, "_obter_nlp", lambda: None)
    casos = [
        "Subimos tudo com a Oracle Cloud.",
        "Automatizei com o GitHub Actions.",
        "Faça o painel com o Power BI.",
    ]

    for texto in casos:
        resultado, contagem = anonimizacao.anonimizar_texto(texto)
        assert resultado == texto
        assert contagem["nome"] == 0
