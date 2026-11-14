"""Testes do vocabulário fechado da análise (llm.py).

Rodam sem chamar o modelo: a normalização recebe um retorno simulado, então
o resultado é reproduzível e não custa token.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))

from services import llm  # noqa: E402

TEXTO = (
    "Depois de 8 meses de estudo no programa ONE, recebi minha proposta "
    "e fui contratada como Desenvolvedora Junior."
)

INTERACOES = [
    {
        "id": 1,
        "autor": "membro_000101",
        "canal": "#conquistas",
        "tipo": "mensagem",
        "texto": TEXTO,
    }
]


def historia(**mudancas):
    base = {
        "id": "hist-001",
        "indice_interacao": 1,
        "autor": "membro_000101",
        "canal": "#conquistas",
        "sentimento": "positivo",
        "relevancia": "alta",
        "topicos": ["carreira"],
        "tipo_insight": "conquista",
        "justificativa": "Relato de vaga conquistada.",
        "confianca": 0.9,
        "tipo": "conquista_profissional",
        "resumo": "Membro contratado como desenvolvedora junior apos 8 meses de estudo.",
        "resultados": ["Contratacao como Desenvolvedora Junior"],
        "mensagem_original": TEXTO,
        "destaques": ["fui contratada como Desenvolvedora Junior"],
        "fatos": [
            "Estudou 8 meses no programa ONE",
            "Foi contratada como Desenvolvedora Junior",
        ],
        "ativos": [
            {
                "id": "post_linkedin",
                "nome": "Post para LinkedIn",
                "tipo": "texto",
                "campos": {"texto": "Post gerado a partir da historia."},
            }
        ],
    }
    base.update(mudancas)
    return base


def test_historia_valida_entra_com_os_campos_do_contrato():
    saida = llm._normalizar([historia()], INTERACOES)

    assert len(saida) == 1
    item = saida[0]
    assert item["sentimento"] == "positivo"
    assert item["tipo_insight"] == "conquista"
    assert item["topicos"] == ["carreira"]
    assert item["tipo"] == "conquista_profissional"
    assert item["confianca"] == 0.9
    assert item["resumo"].startswith("Membro contratado")
    assert item["resultados"] == ["Contratacao como Desenvolvedora Junior"]
    assert llm.ULTIMAS_RECUSADAS == []


def test_categoria_e_nota_derivadas_para_a_tela():
    item = llm._normalizar([historia()], INTERACOES)[0]

    assert item["categoria"] == "Conquista profissional"
    assert item["relevancia"] == 90
    assert item["relevancia_nivel"] == "alta"


def test_sentimento_em_caixa_alta_e_aceito_com_aviso():
    item = llm._normalizar([historia(sentimento="Positivo")], INTERACOES)[0]

    assert item["sentimento"] == "positivo"
    assert any("sentimento" in aviso for aviso in llm.ULTIMOS_AVISOS)


def test_sentimento_fora_da_lista_e_recusado():
    saida = llm._normalizar([historia(sentimento="feliz")], INTERACOES)

    assert saida == []
    assert "sentimento fora da lista fechada" in llm.ULTIMAS_RECUSADAS[0]["motivo"]


def test_relevancia_numerica_e_recusada():
    saida = llm._normalizar([historia(relevancia=85)], INTERACOES)

    assert saida == []
    assert "relevancia fora da lista fechada" in llm.ULTIMAS_RECUSADAS[0]["motivo"]


def test_tipo_insight_inventado_e_recusado():
    saida = llm._normalizar([historia(tipo_insight="elogio")], INTERACOES)

    assert saida == []
    assert "tipo_insight fora da lista fechada" in llm.ULTIMAS_RECUSADAS[0]["motivo"]


def test_tipo_de_historia_no_vocabulario_errado_e_recusado():
    saida = llm._normalizar([historia(tipo="conquista")], INTERACOES)

    assert saida == []
    assert "tipo fora da lista fechada" in llm.ULTIMAS_RECUSADAS[0]["motivo"]


def test_topico_fora_da_lista_e_recusado():
    saida = llm._normalizar([historia(topicos=["clima"])], INTERACOES)

    assert saida == []
    assert "topico fora da lista fechada" in llm.ULTIMAS_RECUSADAS[0]["motivo"]


def test_historia_sem_topico_e_recusada():
    saida = llm._normalizar([historia(topicos=[])], INTERACOES)

    assert saida == []
    assert "Sem topico" in llm.ULTIMAS_RECUSADAS[0]["motivo"]


def test_topico_repetido_e_aceito_com_aviso():
    item = llm._normalizar([historia(topicos=["carreira", "Carreira"])], INTERACOES)[0]

    assert item["topicos"] == ["carreira"]
    assert any("repetido" in aviso for aviso in llm.ULTIMOS_AVISOS)


def test_citacao_que_nao_existe_no_texto_recusa_a_historia():
    saida = llm._normalizar([historia(destaques=["ganhei tres promocoes"])], INTERACOES)

    assert saida == []
    assert "Sem citacao literal" in llm.ULTIMAS_RECUSADAS[0]["motivo"]


def test_historia_sem_fato_e_recusada():
    saida = llm._normalizar([historia(fatos=[])], INTERACOES)

    assert saida == []
    assert "Sem fato extraido" in llm.ULTIMAS_RECUSADAS[0]["motivo"]


def test_historia_sem_resumo_e_recusada():
    saida = llm._normalizar([historia(resumo="")], INTERACOES)

    assert saida == []
    assert "Sem resumo" in llm.ULTIMAS_RECUSADAS[0]["motivo"]


def test_historia_sem_ativo_e_recusada():
    saida = llm._normalizar([historia(ativos=[])], INTERACOES)

    assert saida == []
    assert "Sem ativo gerado" in llm.ULTIMAS_RECUSADAS[0]["motivo"]


def test_confianca_invalida_vira_none_com_aviso():
    item = llm._normalizar([historia(confianca="alta")], INTERACOES)[0]

    assert item["confianca"] is None
    assert any("confianca" in aviso for aviso in llm.ULTIMOS_AVISOS)


def test_lote_sem_historia_devolve_lista_vazia_sem_recusa():
    saida = llm._normalizar([], INTERACOES)

    assert saida == []
    assert llm.ULTIMAS_RECUSADAS == []


def test_recusa_guarda_identificador_e_motivo():
    llm._normalizar([historia(id="hist-042", sentimento="feliz")], INTERACOES)

    recusa = llm.ULTIMAS_RECUSADAS[0]
    assert recusa["id"] == "hist-042"
    assert recusa["motivo"]


def test_historia_ambigua_registra_os_outros_tipos():
    item = llm._normalizar(
        [
            historia(
                tipo="superacao",
                tipos_alternativos=["conquista_profissional"],
            )
        ],
        INTERACOES,
    )[0]

    assert item["tipo"] == "superacao"
    assert item["tipos_alternativos"] == ["conquista_profissional"]
    assert llm.ULTIMAS_AMBIGUIDADES == [
        {
            "id": "hist-001",
            "tipo": "superacao",
            "alternativos": ["conquista_profissional"],
        }
    ]


def test_tipo_alternativo_fora_da_lista_e_ignorado_com_aviso():
    item = llm._normalizar(
        [historia(tipo="superacao", tipos_alternativos=["carreira"])],
        INTERACOES,
    )[0]

    assert item["tipos_alternativos"] == []
    assert any("tipos_alternativos" in aviso for aviso in llm.ULTIMOS_AVISOS)


def test_tipo_alternativo_repetido_ou_igual_ao_escolhido_e_descartado():
    item = llm._normalizar(
        [
            historia(
                tipo="superacao",
                tipos_alternativos=["superacao", "conquista_profissional", "Conquista profissional"],
            )
        ],
        INTERACOES,
    )[0]

    assert item["tipos_alternativos"] == ["conquista_profissional"]


def test_historia_sem_ambiguidade_nao_registra_nada():
    item = llm._normalizar([historia()], INTERACOES)[0]

    assert item["tipos_alternativos"] == []
    assert llm.ULTIMAS_AMBIGUIDADES == []


def test_maximo_de_historias_fica_nomeado():
    assert llm.MAXIMO_HISTORIAS == 3


def test_prompt_carregado_do_arquivo_externo():
    arquivo_prompt = Path(llm.__file__).with_name("prompt_analise.txt")
    assert llm.PROMPT == arquivo_prompt.read_text(encoding="utf-8")


def test_prompt_tem_as_listas_fechadas_do_guia():
    assert "positivo | neutro | negativo" in llm.PROMPT
    assert "alta | media | baixa" in llm.PROMPT
    assert "carreira, estudos, tecnologia, ferramentas, comunidade, eventos, outro" in llm.PROMPT
    assert "conquista_profissional" in llm.PROMPT
    assert "até 3 interações" in llm.PROMPT.format(maximo=llm.MAXIMO_HISTORIAS)
