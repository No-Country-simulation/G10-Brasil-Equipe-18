"""Dados FICTÍCIOS usados só pelo front enquanto o back não existe.

Nada aqui representa pessoas ou depoimentos reais.
Quando o back estiver pronto, o ideal é que o front deixe de importar
este arquivo e passe a usar apenas services/data_service.py.
"""

BUCKET = "communitylab-ativos-marketing"
LOTE_ID = "DEMO-001"
ARQUIVO_DEMO = "one_comunidade_demo.json"
ARQUIVO_DEMO_TAMANHO = "2,4 KB"

INTERACOES = [
    {"autor": "Marina Costa", "canal": "#conquistas", "tipo": "mensagem",
     "texto": "Consegui minha primeira vaga como dev júnior! O portfólio que construí no ONE fez a diferença."},
    {"autor": "Lucas Almeida", "canal": "#projetos", "tipo": "mensagem",
     "texto": "Nosso projeto de controle financeiro foi destaque no desafio. Fizemos tudo em equipe!"},
    {"autor": "Camila Santos", "canal": "#carreira", "tipo": "mensagem",
     "texto": "Depois de 10 anos no varejo, concluí a formação e comecei minha transição para tecnologia."},
    {"autor": "Rafael Lima", "canal": "#geral", "tipo": "mensagem",
     "texto": "Alguém sabe qual é o horário da próxima mentoria?"},
    {"autor": "Beatriz Nunes", "canal": "#geral", "tipo": "mensagem",
     "texto": "Bom dia, pessoal! Começando a semana com bastante energia."},
    {"autor": "Pedro Alves", "canal": "#projetos", "tipo": "mensagem",
     "texto": "Alguém tem um exemplo de como organizar as pastas do projeto?"},
]

# tipo do ativo: "texto" (um campo de texto) ou "testemunho" (título + descrição + citação)
# Cada historia tem duas partes:
# - campos que as telas leem (autor, canal, categoria, sentimento, relevancia,
#   mensagem_original, destaques, fatos, ativos);
# - campos do contrato de historia (tipo, resumo, resultados, topicos,
#   tipo_insight, justificativa, confianca, citacoes).
# Os valores seguem o guia de rotulagem e o schemas/historia_detectada.json.
HISTORIAS = [
    {
        "id": "hist-001",
        "autor": "Marina Costa",
        "iniciais": "MC",
        "canal": "#conquistas",
        "origem": "Mensagem da comunidade",
        "categoria": "Conquista profissional",
        "sentimento": "positivo",
        "relevancia": 90,
        "relevancia_nivel": "alta",
        "tipo_insight": "conquista",
        "topicos": [
            "carreira",
            "estudos"
        ],
        "justificativa": "Resultado concreto: primeira vaga como desenvolvedora júnior, com o portfólio da formação como diferencial.",
        "confianca": 0.92,
        "tipo": "conquista_profissional",
        "resumo": "Participante do Programa ONE conquista a primeira vaga como desenvolvedora júnior, com o portfólio construído durante a formação como diferencial.",
        "resultados": [
            "Primeira vaga como desenvolvedora júnior"
        ],
        "mensagem_original": "Consegui minha primeira vaga como dev júnior! O portfólio que construí no ONE fez a diferença.",
        "citacoes": [
            {
                "texto": "Consegui minha primeira vaga como dev júnior!",
                "id_interacao": 1
            },
            {
                "texto": "O portfólio que construí no ONE fez a diferença.",
                "id_interacao": 1
            }
        ],
        "interacoes_origem": [
            1
        ],
        "destaques": [
            "Consegui minha primeira vaga como dev júnior!",
            "O portfólio que construí no ONE fez a diferença."
        ],
        "fatos": [
            "Conquista: primeira vaga como dev júnior",
            "Origem: portfólio construído no ONE"
        ],
        "ativos": [
            {
                "id": "testemunho",
                "nome": "Testemunho estruturado",
                "tipo": "testemunho",
                "campos": {
                    "titulo": "Da comunidade para o mercado: primeira vaga tech",
                    "descricao": "Marina Costa conquistou sua primeira posição como desenvolvedora júnior após participar do Programa ONE. O diferencial foi o portfólio construído durante a formação, que mostrou suas habilidades práticas aos recrutadores.",
                    "citacao": "O portfólio que construí no ONE fez a diferença."
                },
                "variacoes": [
                    {
                        "titulo": "Primeira vaga como dev júnior conquistada",
                        "descricao": "Participante do Programa ONE, Marina Costa conseguiu sua primeira vaga como desenvolvedora júnior. O portfólio desenvolvido durante o programa foi decisivo no processo seletivo.",
                        "citacao": "Consegui minha primeira vaga como dev júnior! O portfólio que construí no ONE fez a diferença."
                    }
                ]
            },
            {
                "id": "post_linkedin",
                "nome": "Post para LinkedIn",
                "tipo": "texto",
                "campos": {
                    "texto": "Primeira vaga como dev júnior conquistada. O portfólio feito durante a formação foi o que abriu a porta."
                }
            }
        ]
    },
    {
        "id": "hist-002",
        "autor": "Camila Santos",
        "iniciais": "CS",
        "canal": "#carreira",
        "origem": "Mensagem da comunidade",
        "categoria": "Superação",
        "sentimento": "positivo",
        "relevancia": 70,
        "relevancia_nivel": "media",
        "tipo_insight": "historia",
        "topicos": [
            "carreira"
        ],
        "justificativa": "Relato de percurso: dez anos no varejo e o início da transição para tecnologia depois da formação.",
        "confianca": 0.86,
        "tipo": "superacao",
        "resumo": "Depois de dez anos no varejo, participante conclui a formação e começa a transição de carreira para a área de tecnologia.",
        "resultados": [
            "Início da transição para tecnologia"
        ],
        "mensagem_original": "Depois de 10 anos no varejo, concluí a formação e comecei minha transição para tecnologia.",
        "citacoes": [
            {
                "texto": "Depois de 10 anos no varejo",
                "id_interacao": 3
            },
            {
                "texto": "comecei minha transição para tecnologia",
                "id_interacao": 3
            }
        ],
        "interacoes_origem": [
            3
        ],
        "destaques": [
            "Depois de 10 anos no varejo",
            "comecei minha transição para tecnologia"
        ],
        "fatos": [
            "Percurso: dez anos no varejo",
            "Processo: concluiu a formação",
            "Resultado: início da transição para tecnologia"
        ],
        "ativos": [
            {
                "id": "case_sucesso",
                "nome": "Case de sucesso",
                "tipo": "texto",
                "campos": {
                    "titulo": "Dez anos no varejo até a transição para tecnologia",
                    "texto": "Camila Santos passou dez anos no varejo antes de concluir a formação e começar a transição de carreira para tecnologia."
                }
            }
        ]
    },
    {
        "id": "hist-003",
        "autor": "Lucas Almeida",
        "iniciais": "LA",
        "canal": "#projetos",
        "origem": "Mensagem da comunidade",
        "categoria": "Projeto de destaque",
        "sentimento": "positivo",
        "relevancia": 90,
        "relevancia_nivel": "alta",
        "tipo_insight": "conquista",
        "topicos": [
            "tecnologia",
            "comunidade"
        ],
        "justificativa": "Entrega concreta: projeto em equipe destacado no desafio da comunidade.",
        "confianca": 0.9,
        "tipo": "projeto_destaque",
        "resumo": "Projeto de controle financeiro feito em equipe é destacado no desafio da comunidade.",
        "resultados": [
            "Destaque no desafio da comunidade"
        ],
        "mensagem_original": "Nosso projeto de controle financeiro foi destaque no desafio. Fizemos tudo em equipe!",
        "citacoes": [
            {
                "texto": "Nosso projeto de controle financeiro foi destaque no desafio.",
                "id_interacao": 2
            },
            {
                "texto": "Fizemos tudo em equipe!",
                "id_interacao": 2
            }
        ],
        "interacoes_origem": [
            2
        ],
        "destaques": [
            "Nosso projeto de controle financeiro foi destaque no desafio.",
            "Fizemos tudo em equipe!"
        ],
        "fatos": [
            "Projeto: controle financeiro",
            "Resultado: destaque no desafio",
            "Formato: trabalho em equipe"
        ],
        "ativos": [
            {
                "id": "testemunho",
                "nome": "Testemunho estruturado",
                "tipo": "testemunho",
                "campos": {
                    "titulo": "Projeto em equipe destacado no desafio",
                    "descricao": "O projeto de controle financeiro de Lucas Almeida e da equipe foi destaque no desafio da comunidade.",
                    "citacao": "Nosso projeto de controle financeiro foi destaque no desafio."
                }
            }
        ]
    }
]

PACOTES_OCI = [
    {"caminho": "ativos/demo-001/pacote-distribuicao.json", "lote": "DEMO-001",
     "data": "15/10/2026 14:32", "tamanho": "2,4 KB", "status": "salvo"},
    {"caminho": "ativos/demo-001/evidencias.json", "lote": "DEMO-001",
     "data": "15/10/2026 14:32", "tamanho": "1,1 KB", "status": "salvo"},
    {"caminho": "ativos/demo-002/pacote-distribuicao.json", "lote": "DEMO-002",
     "data": None, "tamanho": None, "status": "falhou"},
]
