import json
import pytest
from pathlib import Path
from src import (
    ler_arquivo_bytes,
    pseudonimizar_autor,
    processar_json,
    processar_csv,
    normalizar_texto,
    limpar_e_filtrar_interacoes,
    anonimizar_texto,
    dividir_em_lotes,
    extrair_json_de_texto,
    classificar_interacao,
    gerar_agregacoes,
    avaliar_qualidade,
    carregar_schema,
    validar_interacao,
    validar_ativo,
    validar_historia,
    validar_avaliacao_cqf,
    AtivoGerado,
    AvaliacaoCQF,
    HistoriaDetectada,
    Citacao,
    Interacao,
    calcular_cqf_score,
    validar_integridade_evidencias,
    avaliar_aprovacao_editorial,
    validar_liberacao_publicacao,
    consolidar_decisao_governança,
)



def test_leitura_bytes():
    # Testa utf-8 com acentuação e quebras de linha
    texto_raw = "Linha 1\r\nLinha 2: Acentuação é válida!"
    res, enc, avisos = ler_arquivo_bytes(texto_raw.encode("utf-8"))
    assert "Acentuação é válida!" in res
    assert "\r" not in res
    assert enc == "utf-8-sig"
    assert len(avisos) == 0

def test_pseudonimizacao_autor():
    sal = "segredo123"
    p1 = pseudonimizar_autor("Carlos Silva", sal)
    p2 = pseudonimizar_autor("Carlos Silva", sal)
    p3 = pseudonimizar_autor("Ana Santos", sal)
    
    assert p1.startswith("membro_")
    assert p1 == p2
    assert p1 != p3
    # Se já estiver pseudonimizado, mantém
    assert pseudonimizar_autor("membro_123456", sal) == "membro_123456"

def test_processar_json():
    sal = "teste"
    conteudo = '[{"id": 1, "autor": "User A", "texto": "Mensagem relevante sobre o curso"}]'
    validas, rejeitadas, avisos = processar_json(conteudo, sal)
    assert len(validas) == 1
    assert len(rejeitadas) == 0
    assert validas[0]["id"] == 1
    assert validas[0]["texto"] == "Mensagem relevante sobre o curso"
    assert validas[0]["autor_id"].startswith("membro_")

def test_processar_csv():
    sal = "teste"
    csv_data = "id,autor,texto\n1,Maria,Aprendendo Python no curso!\n"
    validas, rejeitadas, avisos = processar_csv(csv_data, sal)
    assert len(validas) == 1
    assert len(rejeitadas) == 0
    assert validas[0]["id"] == 1
    assert validas[0]["texto"] == "Aprendendo Python no curso!"

def test_limpeza_e_duplicatas():
    # Testa normalização de espaços e caracteres
    assert normalizar_texto("  Texto   com   espaços   duplos \t\n") == "Texto com espaços duplos"

    interacoes = [
        {"id": 1, "autor_id": "membro_001", "texto": "Texto longo o suficiente para passar."},
        {"id": 2, "autor_id": "membro_001", "texto": "Texto longo o suficiente para passar."}, # duplicata
        {"id": 3, "autor_id": "membro_002", "texto": "Curto"}, # rejeitado por tamanho
    ]
    validas, rejeitadas = limpar_e_filtrar_interacoes(interacoes, tamanho_minimo=10)
    assert len(validas) == 1
    assert len(rejeitadas) == 2
    assert validas[0]["id"] == 1

def test_anonimizacao():
    texto = "Meu email é contato@exemplo.com e meu telefone é 11 98888-7777 com CPF 123.456.789-00."
    anonimizado, contagem = anonimizar_texto(texto)
    assert "[EMAIL]" in anonimizado
    assert "[TELEFONE]" in anonimizado
    assert "[CPF]" in anonimizado
    assert contagem["email"] == 1
    assert contagem["telefone"] == 1
    assert contagem["cpf"] == 1

def test_anonimizacao_ner_spacy():
    # Testa NER spaCy: mascara pessoa, preserva cidade e menção
    texto = "Conversei com Mariana Souza em São Paulo sobre o projeto no Discord com @membro_045."
    anonimizado, contagem = anonimizar_texto(texto)
    assert "[NOME]" in anonimizado
    assert "Mariana Souza" not in anonimizado
    assert "São Paulo" in anonimizado
    assert "@membro_045" in anonimizado
    assert contagem["nome"] >= 1

def test_anonimizacao_telefone_ddd_obrigatorio():
    # Telefone com DDD é mascarado
    t1, c1 = anonimizar_texto("Ligue para (11) 98888-7777 ou 21 3222-1234.")
    assert c1["telefone"] == 2
    assert "[TELEFONE]" in t1

    # Sequência de 8 dígitos sem DDD não é confundida com telefone
    t2, c2 = anonimizar_texto("O código do pedido é 12345678 e a data é 20261013.")
    assert c2["telefone"] == 0
    assert "12345678" in t2

def test_dividir_em_lotes():
    itens = [{"id": i} for i in range(12)]
    lotes = dividir_em_lotes(itens, tamanho_lote=5)
    assert len(lotes) == 3
    assert len(lotes[0]) == 5
    assert len(lotes[1]) == 5
    assert len(lotes[2]) == 2

    # Testa validação de tamanho de lote
    with pytest.raises(ValueError):
        dividir_em_lotes(itens, tamanho_lote=0)

def test_extrair_json_de_texto():
    # Bloco markdown com ```json
    markdown_resp = "Aqui está a análise:\n```json\n{\"sentimento\": \"positivo\"}\n```\nObrigado!"
    obj = extrair_json_de_texto(markdown_resp)
    assert obj == {"sentimento": "positivo"}

    # Texto puro com json
    puro = "Resultado: {\"chave\": 123}"
    obj2 = extrair_json_de_texto(puro)
    assert obj2 == {"chave": 123}

def test_agregacao():
    interacoes = [
        {
            "id": 1,
            "analise": {
                "sentimento": "positivo",
                "relevancia": "alta",
                "tipo_insight": "conquista",
                "topicos": ["carreira", "tecnologia"]
            }
        },
        {
            "id": 2,
            "analise": {
                "sentimento": "negativo",
                "relevancia": "baixa",
                "tipo_insight": "duvida",
                "topicos": ["carreira"]
            }
        }
    ]
    resumo = gerar_agregacoes(interacoes)
    assert resumo["total"] == 2
    assert resumo["por_sentimento"]["positivo"] == 1
    assert resumo["por_sentimento"]["negativo"] == 1
    assert resumo["por_relevancia"]["alta"] == 1
    assert resumo["ranking_topicos"][0]["topico"] == "carreira"
    assert resumo["ranking_topicos"][0]["total"] == 2

def test_validacao_schemas():
    base_dir = Path(__file__).parent.parent
    schema_interacao = carregar_schema(str(base_dir / "schemas/interacao_schema.json"))
    schema_ativo = carregar_schema(str(base_dir / "schemas/ativo_gerado_schema.json"))

    interacao_valida = {
        "versao_schema": "1.0",
        "id": 1,
        "autor_id": "membro_001",
        "data": "2026-10-15T10:00:00Z",
        "origem": "discord",
        "texto": "Mensagem válida de teste",
        "status_revisao": "pendente"
    }
    valido, erros = validar_interacao(interacao_valida, schema_interacao)
    assert valido, f"Erros: {erros}"

    ativo_valido = {
        "versao_schema": "1.0",
        "id_ativo": "ativo_001",
        "tipo": "post_linkedin",
        "texto": "Texto do post de divulgação",
        "interacoes_origem": [1],
        "status_revisao": "pendente",
        "criado_em": "2026-10-15T10:00:00Z"
    }
    valido_ativo, erros_ativo = validar_ativo(ativo_valido, schema_ativo)
    assert valido_ativo, f"Erros: {erros_ativo}"

def test_interacao_schema_versao_obrigatoria():
    base_dir = Path(__file__).parent.parent
    schema_interacao = carregar_schema(str(base_dir / "schemas/interacao_schema.json"))

    # Interação sem versao_schema deve falhar
    interacao_invalida = {
        "id": 1,
        "autor_id": "membro_001",
        "data": "2026-10-15T10:00:00Z",
        "origem": "discord",
        "texto": "Mensagem sem versão de schema",
    }
    valido, erros = validar_interacao(interacao_invalida, schema_interacao)
    assert not valido
    assert any("versao_schema" in e for e in erros)

def test_ingestion_fallback_data_dinamica():
    # Item sem data deve receber timestamp ISO atual gerado dinamicamente
    itens, _, _ = processar_json('[{"texto": "Sem data explícita"}]', sal="teste")
    assert len(itens) == 1
    data_gerada = itens[0]["data"]
    assert "T" in data_gerada
    assert data_gerada != "2026-10-13T00:00:00Z"

def test_classificar_interacao_sucesso():
    base_dir = Path(__file__).parent.parent
    schema_interacao = carregar_schema(str(base_dir / "schemas/interacao_schema.json"))
    
    interacao = {
        "versao_schema": "1.0",
        "id": 1,
        "autor_id": "membro_001",
        "data": "2026-10-15T10:00:00Z",
        "origem": "discord",
        "texto": "Consegui meu primeiro emprego como dev!",
        "status_revisao": "pendente"
    }

    # Mock de LLM retornando JSON válido
    def llm_fake(prompt: str) -> str:
        return """
        Aqui está a resposta:
        ```json
        {
            "sentimento": "positivo",
            "relevancia": "alta",
            "topicos": ["carreira"],
            "tipo_insight": "conquista",
            "justificativa": "Relato de contratação",
            "confianca": 0.95
        }
        ```
        """

    res, status, avisos = classificar_interacao(
        interacao=interacao,
        schema_interacao=schema_interacao,
        funcao_chamar_llm=llm_fake,
        prompt_template="Analise: {{texto}}",
        max_tentativas=2,
        limiar_confianca=0.6
    )

    assert status == "sucesso"
    assert "analise" in res
    assert res["analise"]["sentimento"] == "positivo"
    assert res["analise"]["tipo_insight"] == "conquista"
    assert len(avisos) == 0

def test_classificar_interacao_retry_e_recuperacao():
    base_dir = Path(__file__).parent.parent
    schema_interacao = carregar_schema(str(base_dir / "schemas/interacao_schema.json"))
    
    interacao = {
        "versao_schema": "1.0",
        "id": 2,
        "autor_id": "membro_002",
        "data": "2026-10-15T10:00:00Z",
        "origem": "discord",
        "texto": "Qual a melhor linguagem?",
        "status_revisao": "pendente"
    }

    tentativas = 0
    def llm_com_falha_inicial(prompt: str) -> str:
        nonlocal tentativas
        tentativas += 1
        if tentativas == 1:
            return "Resposta quebrada que não contém JSON"
        return '{"sentimento": "neutro", "relevancia": "media", "topicos": ["tecnologia"], "tipo_insight": "duvida", "confianca": 0.8}'

    res, status, avisos = classificar_interacao(
        interacao=interacao,
        schema_interacao=schema_interacao,
        funcao_chamar_llm=llm_com_falha_inicial,
        prompt_template="Analise: {{texto}}",
        max_tentativas=2
    )

    assert status == "sucesso"
    assert tentativas == 2
    assert res["analise"]["sentimento"] == "neutro"
    assert any("Tentativa 1 falhou" in a for a in avisos)

def test_classificar_interacao_tentativas_esgotadas():
    base_dir = Path(__file__).parent.parent
    schema_interacao = carregar_schema(str(base_dir / "schemas/interacao_schema.json"))
    
    interacao = {
        "versao_schema": "1.0",
        "id": 3,
        "autor_id": "membro_003",
        "data": "2026-10-15T10:00:00Z",
        "origem": "discord",
        "texto": "Mensagem qualquer",
        "status_revisao": "pendente"
    }

    def llm_sempre_invalido(prompt: str) -> str:
        return "Não sei a resposta"

    res, status, avisos = classificar_interacao(
        interacao=interacao,
        schema_interacao=schema_interacao,
        funcao_chamar_llm=llm_sempre_invalido,
        prompt_template="{{texto}}",
        max_tentativas=2
    )

    assert status == "sem_analise"
    assert "analise" not in res
    assert any("Esgotadas as tentativas" in a for a in avisos)

def test_classificar_interacao_baixa_confianca():
    base_dir = Path(__file__).parent.parent
    schema_interacao = carregar_schema(str(base_dir / "schemas/interacao_schema.json"))
    
    interacao = {
        "versao_schema": "1.0",
        "id": 4,
        "autor_id": "membro_004",
        "data": "2026-10-15T10:00:00Z",
        "origem": "discord",
        "texto": "Dúvida confusa",
        "status_revisao": "pendente"
    }

    def llm_baixa_confianca(prompt: str) -> str:
        return '{"sentimento": "neutro", "relevancia": "baixa", "topicos": ["outro"], "tipo_insight": "duvida", "confianca": 0.4}'

    res, status, avisos = classificar_interacao(
        interacao=interacao,
        schema_interacao=schema_interacao,
        funcao_chamar_llm=llm_baixa_confianca,
        prompt_template="{{texto}}",
        limiar_confianca=0.6
    )

    assert status == "sucesso"
    assert res["status_revisao"] == "pendente"
    assert any("Baixa confiança" in a for a in avisos)

def test_avaliar_qualidade():
    referencia = [
        {
            "id": 1,
            "analise": {
                "sentimento": "positivo",
                "relevancia": "alta",
                "tipo_insight": "conquista",
                "topicos": ["carreira", "tecnologia"]
            }
        },
        {
            "id": 2,
            "analise": {
                "sentimento": "neutro",
                "relevancia": "media",
                "tipo_insight": "duvida",
                "topicos": ["estudos"]
            }
        }
    ]

    # Pipeline com 100% acerto no id 1, e erro de sentimento no id 2
    pipeline = [
        {
            "id": 1,
            "status_revisao": "pendente",
            "analise": {
                "sentimento": "positivo",
                "relevancia": "alta",
                "tipo_insight": "conquista",
                "topicos": ["tecnologia", "carreira"],
                "confianca": 0.9
            }
        },
        {
            "id": 2,
            "status_revisao": "pendente",
            "analise": {
                "sentimento": "negativo", # erro de sentimento
                "relevancia": "media",
                "tipo_insight": "duvida",
                "topicos": ["estudos"],
                "confianca": 0.5 # < 0.6 -> revisão prioritária
            }
        },
        {
            "id": 3,
            "status_revisao": "pendente"
            # sem analise
        }
    ]

    metricas = avaliar_qualidade(pipeline, referencia)
    assert metricas["total_comparados"] == 2
    assert metricas["acuracia"]["sentimento"] == 0.5
    assert metricas["acuracia"]["relevancia"] == 1.0
    assert metricas["acuracia"]["tipo_insight"] == 1.0
    assert metricas["acuracia"]["topicos"] == 1.0
    assert metricas["sem_analise"] == 1
    assert 2 in metricas["revisao_prioritaria"]

def test_ingestao_deteccao_colisao(monkeypatch):
    # Caso 1: autores iguais geram o mesmo autor_id sem aviso de colisão
    conteudo_sem_colisao = json.dumps([
        {"id": 1, "autor": "Carlos Silva", "texto": "Primeira mensagem válida"},
        {"id": 2, "autor": "Carlos Silva", "texto": "Segunda mensagem do mesmo autor"}
    ])
    itens, _, avisos_sem_colisao = processar_json(conteudo_sem_colisao, sal="sal_teste")
    assert len(itens) == 2
    assert not any("Detectada colisão" in a for a in avisos_sem_colisao)

    # Caso 2: autores distintos forçados ao mesmo autor_id geram aviso de colisão
    conteudo_com_colisao = json.dumps([
        {"id": 1, "autor": "Carlos Silva", "texto": "Mensagem da primeira pessoa"},
        {"id": 2, "autor": "Ana Santos", "texto": "Mensagem da segunda pessoa"}
    ])
    monkeypatch.setattr("src.ingestion.ingestion.pseudonimizar_autor", lambda autor, sal: "membro_777777")
    monkeypatch.setattr("src.ingestion.pseudonimizar_autor", lambda autor, sal: "membro_777777")
    
    itens_col, _, avisos_colisao = processar_json(conteudo_com_colisao, sal="sal_teste")
    assert len(itens_col) == 2
    assert any("Detectada colisão de pseudonimização" in a for a in avisos_colisao)
    assert any("membro_777777" in a for a in avisos_colisao)

def test_leitura_cp1252_latin1_e_replace():
    # Testa cp1252 com caractere específico (símbolo de euro €, mapeado para byte 0x80)
    texto_cp1252 = "Preço em euros: 50 €".encode("cp1252")
    res_cp, enc_cp, avisos_cp = ler_arquivo_bytes(texto_cp1252)
    assert "Preço em euros: 50" in res_cp
    assert enc_cp == "cp1252"

    # Testa fallback para latin-1 com byte 0x81 (indefinido em cp1252 e inválido em utf-8)
    bytes_latin1 = b"In\x81valido"
    res_lat, enc_lat, avisos_lat = ler_arquivo_bytes(bytes_latin1)
    assert "In" in res_lat
    assert enc_lat == "latin-1"

def test_processar_csv_delimitador_ponto_e_virgula():
    sal = "teste"
    csv_data = "id;autor;texto\n10;Carlos;Mensagem separada por ponto e virgula\n"
    validas, rejeitadas, avisos = processar_csv(csv_data, sal)
    assert len(validas) == 1
    assert len(rejeitadas) == 0
    assert validas[0]["id"] == 10
    assert validas[0]["texto"] == "Mensagem separada por ponto e virgula"

def test_processar_e_exportar_dataframe_pandas():
    import pandas as pd
    from src import processar_dataframe, interacoes_para_dataframe

    dados = pd.DataFrame([
        {"id": 1, "autor": "Beatriz", "texto": "Adorando o curso de dados!"},
        {"id": 2, "autor": "Beatriz", "texto": ""}, # deve ser rejeitada
        {"id": 3, "autor": "Lucas", "texto": "Excelente mentoria hoje."}
    ])

    validas, rejeitadas, avisos = processar_dataframe(dados, sal="segredo")
    assert len(validas) == 2
    assert len(rejeitadas) == 1
    assert validas[0]["autor_id"].startswith("membro_")

    # Testa conversão para DataFrame de volta
    df_result = interacoes_para_dataframe(validas)
    assert isinstance(df_result, pd.DataFrame)
    assert len(df_result) == 2
    assert "autor_id" in df_result.columns
    assert "texto" in df_result.columns

def test_modelos_pydantic_validacao():
    from src import (
        Interacao,
        AnaliseInteracao,
        Citacao,
        HistoriaDetectada,
        AtivoGerado,
        LoteInteracoes,
    )

    interacao = Interacao(
        id=1,
        autor_id="membro_123456",
        data="2026-10-15T10:00:00Z",
        texto="Texto da mensagem de teste",
        analise=AnaliseInteracao(
            sentimento="positivo",
            relevancia="alta",
            topicos=["carreira"],
            tipo_insight="conquista",
            confianca=0.9
        )
    )
    assert interacao.id == 1
    assert interacao.analise is not None
    assert interacao.analise.sentimento == "positivo"
    assert interacao.versao_schema == "1.0"

    citacao = Citacao(texto="Fui contratado!", id_interacao=1)
    historia = HistoriaDetectada(
        id_historia="historia_001",
        tipo="conquista_profissional",
        resumo="Contratação de novo dev",
        interacoes_origem=[1],
        fatos=["Foi contratado"],
        citacoes=[citacao]
    )
    assert historia.id_historia == "historia_001"
    assert historia.versao_schema == "1.1"

    ativo = AtivoGerado(
        id_ativo="ativo_001",
        tipo="post_linkedin",
        texto="Texto do post",
        interacoes_origem=[1]
    )
    assert ativo.versao_schema == "1.0"

    lote = LoteInteracoes(interacoes=[interacao])
    assert len(lote.interacoes) == 1

def test_cpf_valido_vs_sequencia_numerica():
    # Sequência de 11 dígitos que NÃO é CPF válido não é mascarada
    t1, c1 = anonimizar_texto("O código do pedido é 99988877766 e o outro é 12345678901.")
    assert c1["cpf"] == 0
    assert "99988877766" in t1

    # CPF formatado é mascarado
    t2, c2 = anonimizar_texto("Meu CPF é 123.456.789-00.")
    assert c2["cpf"] == 1
    assert "[CPF]" in t2

def test_ativo_gerado_schema_versao_obrigatoria():
    base_dir = Path(__file__).parent.parent
    schema_ativo = carregar_schema(str(base_dir / "schemas/ativo_gerado_schema.json"))

    ativo_sem_versao = {
        "id_ativo": "ativo_001",
        "tipo": "post_linkedin",
        "texto": "Post",
        "interacoes_origem": [1],
        "status_revisao": "pendente",
        "criado_em": "2026-10-15T10:00:00Z"
    }
    valido, erros = validar_ativo(ativo_sem_versao, schema_ativo)
    assert not valido
    assert any("versao_schema" in e for e in erros)

def test_modulos_src_pipeline():
    # Testa os submódulos de src criados conforme o README
    import src.ingestion
    import src.preprocessing
    import src.analysis
    import src.detection
    import src.extraction
    import src.generation
    import src.orchestration
    import src.storage

    assert hasattr(src.ingestion, "ler_arquivo_bytes")
    assert hasattr(src.preprocessing, "anonimizar_texto")
    assert hasattr(src.analysis, "classificar_interacao")
    assert hasattr(src.detection, "filtrar_candidatos_historia")
    assert hasattr(src.generation, "AtivoGerado")
    assert hasattr(src.orchestration, "dividir_em_lotes")
    assert hasattr(src.storage, "carregar_schema")


def test_ativo_gerado_novos_tipos_cqf():
    base_dir = Path(__file__).parent.parent
    schema_ativo = carregar_schema(str(base_dir / "schemas/ativo_gerado_schema.json"))

    for tipo in ["testemunho_estruturado", "case_sucesso", "card_conquista"]:
        ativo_dict = {
            "versao_schema": "1.0",
            "id_ativo": "ativo_101",
            "tipo": tipo,
            "titulo": "História de Sucesso",
            "texto": "Texto do testemunho com evidências rastreáveis.",
            "interacoes_origem": [1, 2],
            "status_revisao": "pendente",
            "criado_em": "2026-10-20T10:00:00Z",
            "id_avaliacao_cqf": "cqf_001",
        }
        valido, erros = validar_ativo(ativo_dict, schema_ativo)
        assert valido, f"Falha para tipo {tipo}: {erros}"

        # Teste com Pydantic
        modelo = AtivoGerado.model_validate(ativo_dict)
        assert modelo.tipo == tipo
        assert modelo.id_avaliacao_cqf == "cqf_001"


def test_avaliacao_cqf_schema_e_modelo():
    base_dir = Path(__file__).parent.parent
    schema_cqf = carregar_schema(str(base_dir / "schemas/avaliacao_cqf_schema.json"))

    dado_cqf = {
        "versao_schema": "1.0",
        "id_avaliacao": "cqf_001",
        "id_historia": "historia_001",
        "id_ativo": "ativo_001",
        "versao_framework": "1.0",
        "nota_relevancia": 5.0,
        "nota_completude": 4.0,
        "nota_clareza_impacto": 5.0,
        "nota_evidencias": 4.0,
        "cqf_score": 89.0,
        "classificacao_editorial": "alta_prioridade",
        "status_validacao_factual": "conforme",
        "status_curadoria": "aprovado",
        "status_autorizacao_publicacao": "autorizada",
        "decisao_editorial": "aprovado",
        "responsavel_avaliacao": "Marcus - PM",
        "data_avaliacao": "2026-10-20T11:00:00Z",
        "observacoes": "Relato aprovado com evidências validadas."
    }

    valido, erros = validar_avaliacao_cqf(dado_cqf, schema_cqf)
    assert valido, f"Erros no schema CQF: {erros}"

    # Validação Pydantic
    obj = AvaliacaoCQF.model_validate(dado_cqf)
    assert obj.cqf_score == 89.0
    assert obj.nota_relevancia == 5.0

    # Teste de nota inválida (> 5.0) no Pydantic
    dado_invalido = dado_cqf.copy()
    dado_invalido["nota_relevancia"] = 6.0
    try:
        AvaliacaoCQF.model_validate(dado_invalido)
        assert False, "Deveria ter falhado com nota_relevancia > 5.0"
    except Exception:
        pass

    # Teste de nota inválida no JSON Schema
    valido_invalido, erros_invalido = validar_avaliacao_cqf(dado_invalido, schema_cqf)
    assert not valido_invalido


def test_cqf_score_casos_positivos_validacao():
    # CQF-001: Conquista profissional (R=5, C=4, I=5, E=4) -> 89.0 (Alta)
    res_001 = calcular_cqf_score(relevancia=5, completude=4, clareza_impacto=5, evidencias=4)
    assert res_001["cqf_score"] == 89.0
    assert res_001["classificacao_editorial"] == "alta_prioridade"

    # CQF-002: Projeto de destaque (R=4, C=4, I=4, E=3) -> 74.0 (Média)
    res_002 = calcular_cqf_score(relevancia=4, completude=4, clareza_impacto=4, evidencias=3)
    assert res_002["cqf_score"] == 74.0
    assert res_002["classificacao_editorial"] == "prioridade_media"

    # CQF-003: Superação (R=5, C=5, I=5, E=4) -> 94.0 (Alta)
    res_003 = calcular_cqf_score(relevancia=5, completude=5, clareza_impacto=5, evidencias=4)
    assert res_003["cqf_score"] == 94.0
    assert res_003["classificacao_editorial"] == "alta_prioridade"


def test_cqf_score_casos_negativos_validacao():
    # CQF-NEG-001: Evidências insuficientes (R=2, C=1, I=2, E=1) -> 29.0 (Baixa)
    res_neg_001 = calcular_cqf_score(relevancia=2, completude=1, clareza_impacto=2, evidencias=1)
    assert res_neg_001["cqf_score"] == 29.0
    assert res_neg_001["classificacao_editorial"] == "baixa_prioridade"

    # CQF-NEG-002: Informações contraditórias (R=4, C=2, I=2, E=1) -> 44.0 (Baixa)
    res_neg_002 = calcular_cqf_score(relevancia=4, completude=2, clareza_impacto=2, evidencias=1)
    assert res_neg_002["cqf_score"] == 44.0
    assert res_neg_002["classificacao_editorial"] == "baixa_prioridade"

    # CQF-NEG-003: Ausência de autorização (R=5, C=5, I=5, E=4) -> 94.0 (Alta pontuação editorial)
    res_neg_003 = calcular_cqf_score(relevancia=5, completude=5, clareza_impacto=5, evidencias=4)
    assert res_neg_003["cqf_score"] == 94.0


def test_cqf_score_validacao_limites():
    # Nota negativa
    with pytest.raises(ValueError):
        calcular_cqf_score(relevancia=-1, completude=3, clareza_impacto=3, evidencias=3)

    # Nota acima de 5
    with pytest.raises(ValueError):
        calcular_cqf_score(relevancia=3, completude=5.5, clareza_impacto=3, evidencias=3)


def test_regra_rg01_integridade_evidencias():
    interacoes = [
        Interacao(
            id=1,
            autor_id="membro_001",
            data="2026-10-15T10:00:00Z",
            texto="Consegui minha primeira vaga como desenvolvedora júnior após 6 meses de estudo."
        )
    ]

    # Citação literal presente -> Válido
    historia_valida = HistoriaDetectada(
        id_historia="historia_001",
        tipo="conquista_profissional",
        resumo="Conquista de vaga",
        interacoes_origem=[1],
        fatos=["Foi contratada como desenvolvedora júnior"],
        resultados=["Primeira vaga em tech"],
        citacoes=[
            Citacao(
                texto="Consegui minha primeira vaga como desenvolvedora júnior",
                id_interacao=1
            )
        ],
        autorizacao_divulgacao="autorizada",
        status_revisao="aprovado"
    )
    valido, erros = validar_integridade_evidencias(historia_valida, interacoes)
    assert valido
    assert len(erros) == 0

    # Citação inventada/alterada (violação RG-01) -> Inválido
    historia_inventada = HistoriaDetectada(
        id_historia="historia_002",
        tipo="conquista_profissional",
        resumo="Conquista com alucinação",
        interacoes_origem=[1],
        fatos=["Fato inventado"],
        citacoes=[
            Citacao(
                texto="Recebi um salário de 10 mil reais logo no primeiro mês",
                id_interacao=1
            )
        ],
        autorizacao_divulgacao="autorizada",
        status_revisao="aprovado"
    )
    valido_inv, erros_inv = validar_integridade_evidencias(historia_inventada, interacoes)
    assert not valido_inv
    assert any("RG-01 Violação" in e for e in erros_inv)


def test_regra_rg02_consistencia_factual_bloqueio():
    # Contradição detectada bloqueia aprovação editorial
    pode_aprovar, msg = avaliar_aprovacao_editorial(
        status_validacao_factual="contradicao_detectada",
        status_curadoria="aprovado"
    )
    assert not pode_aprovar
    assert "Bloqueio RG-02" in msg

    # Evidências insuficientes não devem ser aprovadas diretamente
    pode_aprovar_insuf, msg_insuf = avaliar_aprovacao_editorial(
        status_validacao_factual="evidencias_insuficientes",
        status_curadoria="aprovado"
    )
    assert not pode_aprovar_insuf


def test_regra_rg03_trava_publicacao():
    # CQF-NEG-003: Score 94, curadoria aprovada, mas autorização pendente -> BLOQUEADO
    pode_publicar, msg = validar_liberacao_publicacao(
        status_curadoria="aprovado",
        status_autorizacao="pendente",
        cqf_score=94.0
    )
    assert not pode_publicar
    assert "Bloqueio RG-03" in msg

    # Autorizada -> LIBERADO
    pode_publicar_ok, msg_ok = validar_liberacao_publicacao(
        status_curadoria="aprovado",
        status_autorizacao="autorizada",
        cqf_score=94.0
    )
    assert pode_publicar_ok
    assert "Liberado" in msg_ok


def test_consolidar_decisao_governança():
    # Caso negativo 1: evidências insuficientes
    d1 = consolidar_decisao_governança(29.0, "evidencias_insuficientes", "pendente", "pendente")
    assert d1 == "solicitar_informacoes"

    # Caso negativo 2: contradição
    d2 = consolidar_decisao_governança(44.0, "contradicao_detectada", "pendente", "pendente")
    assert d2 == "bloqueado_contradicao"

    # Caso negativo 3: score alto aprovado mas sem autorização
    d3 = consolidar_decisao_governança(94.0, "conforme", "aprovado", "pendente")
    assert d3 == "bloqueado_sem_autorizacao"

    # Caso positivo: aprovado e autorizado
    d_ok = consolidar_decisao_governança(94.0, "conforme", "aprovado", "autorizada")
    assert d_ok == "aprovado"


def test_cenarios_cqf_json_validacao_completa():
    base_dir = Path(__file__).parent.parent
    arquivo_cqf = base_dir / "data/samples/cenarios_cqf.json"
    assert arquivo_cqf.exists(), "Arquivo data/samples/cenarios_cqf.json não encontrado"

    dados = json.loads(arquivo_cqf.read_text(encoding="utf-8"))
    cenarios = dados.get("cenarios", [])
    assert len(cenarios) == 6, f"Esperados 6 cenários CQF, encontrados: {len(cenarios)}"

    schema_interacao = carregar_schema(str(base_dir / "schemas/interacao_schema.json"))
    schema_historia = carregar_schema(str(base_dir / "schemas/historia_detectada.json"))
    schema_cqf = carregar_schema(str(base_dir / "schemas/avaliacao_cqf_schema.json"))
    schema_ativo = carregar_schema(str(base_dir / "schemas/ativo_gerado_schema.json"))

    scores_esperados = {
        "CQF-001": 89.0,
        "CQF-002": 74.0,
        "CQF-003": 94.0,
        "CQF-NEG-001": 29.0,
        "CQF-NEG-002": 44.0,
        "CQF-NEG-003": 94.0,
    }

    for c in cenarios:
        caso_id = c["id_caso"]
        interacao = c["interacao"]
        historia = c["historia"]
        avaliacao = c["avaliacao_cqf"]

        # 1. Validação de schemas
        val_i, err_i = validar_interacao(interacao, schema_interacao)
        assert val_i, f"[{caso_id}] Erro no schema de interação: {err_i}"

        val_h, err_h = validar_historia(historia, schema_historia)
        assert val_h, f"[{caso_id}] Erro no schema de história: {err_h}"

        val_cqf, err_cqf = validar_avaliacao_cqf(avaliacao, schema_cqf)
        assert val_cqf, f"[{caso_id}] Erro no schema CQF: {err_cqf}"

        if "ativo" in c:
            val_a, err_a = validar_ativo(c["ativo"], schema_ativo)
            assert val_a, f"[{caso_id}] Erro no schema de ativo: {err_a}"

        # 2. Recálculo e conferência matemática do score
        calc = calcular_cqf_score(
            relevancia=avaliacao["nota_relevancia"],
            completude=avaliacao["nota_completude"],
            clareza_impacto=avaliacao["nota_clareza_impacto"],
            evidencias=avaliacao["nota_evidencias"],
        )
        assert calc["cqf_score"] == scores_esperados[caso_id], (
            f"[{caso_id}] Score recalculado {calc['cqf_score']} != esperado {scores_esperados[caso_id]}"
        )
        assert calc["classificacao_editorial"] == avaliacao["classificacao_editorial"]

        # 3. Integridade das evidências (RG-01)
        val_ev, err_ev = validar_integridade_evidencias(historia, [interacao])
        assert val_ev, f"[{caso_id}] Falha de integridade das evidências: {err_ev}"


def test_ativo_gerado_card_conquista_validacao_completa():
    """Valida especificamente o contrato do ativo 'card_conquista' utilizado pelo Front-end."""
    base_dir = Path(__file__).parent.parent
    schema_ativo = carregar_schema(str(base_dir / "schemas/ativo_gerado_schema.json"))

    # 1. Ativo válido com tipo card_conquista compatível com READMEFrontend.md
    ativo_card = {
        "versao_schema": "1.0",
        "id_ativo": "ativo_501",
        "tipo": "card_conquista",
        "titulo": "Marina Costa · Nova Desenvolvedora Júnior",
        "texto": "Consegui minha primeira vaga como desenvolvedora júnior após 6 meses de estudo.",
        "interacoes_origem": [1],
        "status_revisao": "pendente",
        "criado_em": "2026-10-22T12:00:00Z",
        "id_avaliacao_cqf": "cqf_001",
    }

    # Validação via JSON Schema Draft 2020-12
    valido, erros = validar_ativo(ativo_card, schema_ativo)
    assert valido, f"Erro na validação do schema para card_conquista: {erros}"

    # Validação via Modelo Pydantic v2
    modelo = AtivoGerado.model_validate(ativo_card)
    assert modelo.tipo == "card_conquista"
    assert modelo.id_ativo == "ativo_501"
    assert modelo.titulo == "Marina Costa · Nova Desenvolvedora Júnior"
    assert modelo.interacoes_origem == [1]

    # 2. Preservação dos tipos já existentes (garantir que nenhum formato existente foi quebrado)
    todos_os_tipos = [
        "testemunho_estruturado",
        "case_sucesso",
        "post_linkedin",
        "resumo_newsletter",
        "card_conquista",
    ]
    for tipo_item in todos_os_tipos:
        dados_tipo = {
            "versao_schema": "1.0",
            "id_ativo": "ativo_999",
            "tipo": tipo_item,
            "texto": f"Exemplo de conteúdo para o tipo {tipo_item}",
            "interacoes_origem": [10],
            "status_revisao": "aprovado",
            "criado_em": "2026-10-22T12:00:00Z",
        }
        ok, errs = validar_ativo(dados_tipo, schema_ativo)
        assert ok, f"Tipo {tipo_item} deveria ser válido, mas falhou: {errs}"
        m = AtivoGerado.model_validate(dados_tipo)
        assert m.tipo == tipo_item

    # 3. Rejeição de tipos não autorizados
    ativo_invalido = ativo_card.copy()
    ativo_invalido["tipo"] = "tipo_inexistente"
    valido_inv, erros_inv = validar_ativo(ativo_invalido, schema_ativo)
    assert not valido_inv
    assert any("tipo" in e for e in erros_inv)

    with pytest.raises(Exception):
        AtivoGerado.model_validate(ativo_invalido)


def test_regra_rg01_normalizacao_espacos():
    """Valida que a regra RG-01 normaliza múltiplos espaços e quebras de linha entre citação e texto original."""
    interacoes = [
        Interacao(
            id=1,
            autor_id="membro_001",
            data="2026-10-15T10:00:00Z",
            # Texto original com quebra de linha e múltiplos espaços
            texto="Consegui minha primeira vaga como\n   desenvolvedora júnior   após 6 meses de estudo."
        )
    ]

    # Citação com espaçamento padronizado em espaço simples
    historia_com_espaco_normalizado = HistoriaDetectada(
        id_historia="historia_001",
        tipo="conquista_profissional",
        resumo="Conquista de vaga",
        interacoes_origem=[1],
        fatos=["Foi contratada como desenvolvedora júnior"],
        resultados=["Primeira vaga em tech"],
        citacoes=[
            Citacao(
                texto="Consegui minha primeira vaga como desenvolvedora júnior",
                id_interacao=1
            )
        ],
        autorizacao_divulgacao="autorizada",
        status_revisao="aprovado"
    )

    valido, erros = validar_integridade_evidencias(historia_com_espaco_normalizado, interacoes)
    assert valido, f"RG-01 deveria aceitar citação com espaços normalizados, mas falhou: {erros}"
    assert len(erros) == 0


def test_data_service_regenerar_validacao_rg01():
    """Valida que data_service.regenerar aplica a regra RG-01 e descarta variações com citações alucinadas."""
    from app.services.data_service import regenerar

    historia = {
        "id": "hist_001",
        "interacoes_origem": ["int_001"],
        "mensagem_original": "Consegui minha primeira vaga como dev júnior! O portfólio fez a diferença.",
        "ativos": [
            {
                "id": "testemunho",
                "campos": {
                    "titulo": "Primeira vaga",
                    "citacao": "O portfólio fez a diferença."
                },
                "variacoes": [
                    {
                        "titulo": "Variação Válida",
                        "citacao": "Consegui minha primeira vaga como dev júnior!"
                    },
                    {
                        "titulo": "Variação Alucinada",
                        "citacao": "Fui contratado para ganhar 100 mil dólares por mês."
                    }
                ]
            }
        ]
    }

    # Vez 0 -> campos base (válido)
    res0 = regenerar(historia, "testemunho", 0)
    assert res0["titulo"] == "Primeira vaga"
    assert res0["citacao"] == "O portfólio fez a diferença."

    # Vez 1 -> variação 1 (válida pela RG-01)
    res1 = regenerar(historia, "testemunho", 1)
    assert res1["titulo"] == "Variação Válida"
    assert res1["citacao"] == "Consegui minha primeira vaga como dev júnior!"

    # Vez 2 -> variação 2 (alucinada: viola RG-01 e aciona fallback seguro da versão base)
    res2 = regenerar(historia, "testemunho", 2)
    assert res2["titulo"] == "Primeira vaga"
    assert res2["citacao"] == "O portfólio fez a diferença."


def test_parse_interacoes_csv_virgula_e_ponto_e_virgula():
    """Valida suporte a arquivos CSV delimitados por vírgula (,) e por ponto e vírgula (;)."""
    from app.services.data_service import parse_interacoes

    csv_virgula = (
        'autor,canal,tipo,texto\n'
        '"Marina Costa","#conquistas",mensagem,"Consegui minha primeira vaga!"\n'
    )
    itens_v = parse_interacoes("teste_virgula.csv", csv_virgula)
    assert len(itens_v) == 1
    assert itens_v[0]["autor"] == "Marina Costa"
    assert itens_v[0]["canal"] == "#conquistas"
    assert itens_v[0]["texto"] == "Consegui minha primeira vaga!"

    csv_ponto_virgula = (
        'autor;canal;tipo;texto\n'
        'Carlos Silva;#geral;mensagem;Estudando todos os dias.\n'
    )
    itens_pv = parse_interacoes("teste_ponto_virgula.csv", csv_ponto_virgula)
    assert len(itens_pv) == 1
    assert itens_pv[0]["autor"] == "Carlos Silva"
    assert itens_pv[0]["canal"] == "#geral"
    assert itens_pv[0]["texto"] == "Estudando todos os dias."


def test_curto_prazo_r02_validacao_rg01_id_flexivel():
    """R-02: Testa correspondência de IDs flexível entre int e str (ex: 'int_001' vs 1)."""
    interacoes = [
        {"id": "int_001", "texto": "Depois de 6 meses de estudo, fui aprovado no processo seletivo!"}
    ]
    historia = {
        "id": "hist-001",
        "interacoes_origem": ["int_001"],
        "citacoes": [
            {"id_interacao": "int_001", "texto": "fui aprovado no processo seletivo!"}
        ]
    }
    valido, erros = validar_integridade_evidencias(historia, interacoes)
    assert valido is True
    assert len(erros) == 0

    # Com id numérico na citação e int_XXX na origem
    historia_num = {
        "id": "hist-001",
        "interacoes_origem": [1],
        "citacoes": [
            {"id_interacao": 1, "texto": "fui aprovado no processo seletivo!"}
        ]
    }
    valido_num, erros_num = validar_integridade_evidencias(historia_num, interacoes)
    assert valido_num is True


def test_curto_prazo_f03_pydantic_historia_e_interacao():
    """F-03/M-01: Garante que HistoriaDetectada aceita 'hist-001' e Interacao aceita id int ou str."""
    cit = Citacao(texto="Consegui meu estágio!", id_interacao="int_001")
    hist = HistoriaDetectada(
        id_historia="hist-001",
        tipo="conquista_profissional",
        resumo="Aluno conquistou seu estágio",
        interacoes_origem=["int_001"],
        fatos=["Entrou no estágio"],
        citacoes=[cit]
    )
    assert hist.id_historia == "hist-001"
    assert hist.citacoes[0].id_interacao == "int_001"


def test_curto_prazo_i01_i02_pseudonimizacao_na_ingestao():
    """I-01/I-02: Verifica que _normalizar gera autor_id no padrão membro_XXXXXX."""
    from app.services.data_service import parse_interacoes
    conteudo = json.dumps([
        {"autor": "Ana Maria", "canal": "#carreira", "tipo": "mensagem", "texto": "Comecei hoje no curso!"}
    ])
    itens = parse_interacoes("lote.json", conteudo)
    assert len(itens) == 1
    assert itens[0]["autor"] == "Ana Maria"
    assert itens[0]["autor_id"].startswith("membro_")
    assert len(itens[0]["autor_id"]) >= 13


def test_curto_prazo_f04_origem_analise_e_c01_cqf_dinamico():
    """F-04 e C-01/C-02: Verifica isolamento de estado e cálculo dinâmico das dimensões CQF."""
    from app.services.data_service import (
        obter_origem_analise,
        _definir_origem_analise,
        _enriquecer_historias_com_cqf,
    )
    _definir_origem_analise("gemini", "")
    assert obter_origem_analise() == "gemini"

    # Enriquecimento com dimensões CQF dinâmicas
    interacoes = [
        {"id": "int_001", "texto": "Após transição de carreira, fui contratado como desenvolvedor com salário 40% maior!"}
    ]
    historias = [
        {
            "id": "hist-001",
            "relevancia": 95.0,
            "mensagem_original": "Após transição de carreira, fui contratado como desenvolvedor com salário 40% maior!",
            "fatos": ["Fez transição de carreira", "Foi contratado como dev"],
            "destaques": ["fui contratado como desenvolvedor"]
        }
    ]
    enriquecidas = _enriquecer_historias_com_cqf(historias, interacoes)
    h = enriquecidas[0]
    assert h["cqf_score"] > 80.0
    assert h["cqf_classificacao"] == "alta_prioridade"
    # Dimensões dinâmicas calculadas
    assert "clareza_impacto" in h["cqf_dimensoes"]
    assert "evidencias" in h["cqf_dimensoes"]
    assert h["cqf_dimensoes"]["clareza_impacto"] >= 4.0
    assert h["cqf_dimensoes"]["evidencias"] >= 4.0


def test_rg01_resiliencia_reticencias_llm():
    """Verifica que o validador RG-01 aceita citações do LLM com reticências (...) no final."""
    interacao = {"id": 1, "texto": "Nosso projeto de controle financeiro foi destaque no desafio. Fizemos tudo em equipe!"}
    historia = {
        "interacoes_origem": [1],
        "citacoes": [
            {"id_interacao": 1, "texto": "projeto de controle financeiro foi desta..."},
            {"id_interacao": 1, "texto": "Fizemos tudo em equipe!..."}
        ]
    }
    valido, erros = validar_integridade_evidencias(historia, [interacao])
    assert valido
    assert len(erros) == 0


def test_pipeline_limpeza_e_classificacao_lote():
    """Verifica que as funções de limpeza e classificação enriquecem o lote com sucesso."""
    from app.services.data_service import limpar_interacoes_lote, classificar_interacoes_lote
    lote = [
        {"id": 1, "autor": "Carlos", "canal": "#geral", "texto": "Curto"},  # < 10 caracteres -> rejeitado
        {"id": 2, "autor": "Marina", "canal": "#conquistas", "texto": "Consegui minha primeira vaga como dev júnior!"},
        {"id": 3, "autor": "Marina", "canal": "#conquistas", "texto": "Consegui minha primeira vaga como dev júnior!"},  # duplicata
    ]
    validas, rejeitadas = limpar_interacoes_lote(lote)
    assert len(validas) == 1
    assert len(rejeitadas) == 2
    assert validas[0]["id"] == 2

    classificadas = classificar_interacoes_lote(validas)
    assert len(classificadas) == 1
    assert "analise" in classificadas[0]
    assert classificadas[0]["analise"]["sentimento"] == "positivo"
    assert classificadas[0]["analise"]["tipo_insight"] == "conquista"


def test_salvar_no_oci_com_auditoria_cqf(tmp_path):
    """Verifica que salvar_no_oci grava pacotes e cria trilha formal de auditoria CQF."""
    from app.services import data_service as svc
    import app.services.data_service as ds_mod
    original_oci_dir = ds_mod._OCI_DIR
    ds_mod._OCI_DIR = tmp_path

    try:
        pacotes = [{"id": "DEMO-TESTE", "status": "salvo"}]
        historias = [
            {
                "id": "hist-001",
                "cqf_score": 92.5,
                "cqf_classificacao": "alta_prioridade",
                "avaliacao_cqf": {
                    "id_avaliacao": "cqf_001",
                    "id_historia": "hist-001",
                    "cqf_score": 92.5,
                    "classificacao_editorial": "alta_prioridade"
                }
            }
        ]
        svc.salvar_no_oci(pacotes, "LOTE-UNIT-001", historias=historias)
        
        # Verifica se o pacote de ativos foi gravado
        ativos_salvos = list(tmp_path.glob("ativos/*/*.json"))
        assert len(ativos_salvos) == 1

        # Verifica se a auditoria CQF foi persistida
        auditorias = list(tmp_path.glob("auditorias/*/*.json"))
        assert len(auditorias) == 1
        with open(auditorias[0], "r", encoding="utf-8") as f:
            dados_auditoria = json.load(f)
            assert dados_auditoria["lote_id"] == "LOTE-UNIT-001"
            assert len(dados_auditoria["avaliacoes"]) == 1
            assert dados_auditoria["avaliacoes"][0]["id_avaliacao"] == "cqf_001"
    finally:
        ds_mod._OCI_DIR = original_oci_dir


