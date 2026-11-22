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
    {"id": 1, "autor": "Marina Costa", "canal": "#conquistas", "tipo": "mensagem",
     "texto": "Consegui minha primeira vaga como dev júnior! O portfólio que construí no ONE fez a diferença."},
    {"id": 2, "autor": "Lucas Almeida", "canal": "#projetos", "tipo": "mensagem",
     "texto": "Nosso projeto de controle financeiro foi destaque no desafio. Fizemos tudo em equipe!"},
    {"id": 3, "autor": "Camila Santos", "canal": "#carreira", "tipo": "mensagem",
     "texto": "Depois de 10 anos no varejo, concluí a formação e comecei minha transição para tecnologia."},
    {"id": 4, "autor": "Rafael Lima", "canal": "#geral", "tipo": "mensagem",
     "texto": "Alguém sabe qual é o horário da próxima mentoria?"},
    {"id": 5, "autor": "Beatriz Nunes", "canal": "#geral", "tipo": "mensagem",
     "texto": "Bom dia, pessoal! Começando a semana com bastante energia."},
    {"id": 6, "autor": "Pedro Alves", "canal": "#projetos", "tipo": "mensagem",
     "texto": "Alguém tem um exemplo de como organizar as pastas do projeto?"},
]

# tipo do ativo: "texto" (um campo de texto) ou "testemunho" (título + descrição + citação)
HISTORIAS = [
    {
        "id": "hist-001",
        "autor": "Marina Costa",
        "iniciais": "MC",
        "canal": "#conquistas",
        "origem": "Mensagem da comunidade",
        "categoria": "Conquista profissional",
        "sentimento": "Positivo",
        "relevancia": 96,
        "mensagem_original": "Consegui minha primeira vaga como dev júnior! O portfólio que construí no ONE fez a diferença.",
        "citacoes": [
            {"texto": "primeira vaga como dev júnior!", "id_interacao": 1},
            {"texto": "O portfólio que construí no ONE fez a diferença.", "id_interacao": 1}
        ],
        "interacoes_origem": [1],
        "destaques": ["primeira vaga como dev júnior!", "O portfólio que construí no ONE fez a diferença."],
        "fatos": ["Conquista: primeira vaga como dev júnior", "Origem: portfólio construído no ONE"],
        "ativos": [
            {"id": "testemunho", "nome": "Testemunho estruturado", "tipo": "testemunho",
             "campos": {
                 "titulo": "Da comunidade para o mercado: primeira vaga tech",
                 "descricao": "Marina Costa conquistou sua primeira posição como desenvolvedora júnior após participar do Programa ONE. O diferencial foi o portfólio construído durante a formação, que demonstrou suas habilidades práticas aos recrutadores.",
                 "citacao": "O portfólio que construí no ONE fez a diferença."
             },
             "variacoes": [{
                 "titulo": "Primeira vaga como dev júnior conquistada",
                 "descricao": "Participante do Programa ONE, Marina Costa conseguiu sua primeira vaga como desenvolvedora júnior. O portfólio desenvolvido durante o programa foi decisivo no processo seletivo.",
                 "citacao": "Consegui minha primeira vaga como dev júnior! O portfólio que construí no ONE fez a diferença."
             }],
             "fontes": [
                 {"afirmacao": "Marina conquistou primeira vaga como dev júnior", "fato": "Conquista: primeira vaga como dev júnior", "trecho": "primeira vaga como dev júnior!"},
                 {"afirmacao": "Portfólio construído no ONE foi decisivo", "fato": "Origem: portfólio construído no ONE", "trecho": "O portfólio que construí no ONE fez a diferença."}
             ]},
            {"id": "case", "nome": "Case de sucesso", "tipo": "texto",
             "campos": {"texto": "Case de Sucesso: Transição para Tecnologia\n\n"
                                 "Marina Costa ingressou no mercado tech conquistando sua primeira vaga como desenvolvedora júnior. "
                                 "O diferencial competitivo veio do portfólio prático construído durante o Programa ONE, "
                                 "que demonstrou suas habilidades técnicas aos recrutadores.\n\n"
                                 "Resultado: Primeira colocação profissional na área de tecnologia."},
             "variacoes": [{"texto": "História de Sucesso: Primeira Vaga Tech\n\n"
                                     "Participante: Marina Costa\n"
                                     "Conquista: Primeira vaga como desenvolvedora júnior\n"
                                     "Fator decisivo: Portfólio construído no Programa ONE\n\n"
                                     "Marina ingressou no mercado de tecnologia após concluir a formação. "
                                     "O portfólio desenvolvido durante o programa foi destacado como diferencial no processo seletivo."}],
             "fontes": [
                 {"afirmacao": "Marina conquistou primeira vaga como dev júnior", "fato": "Conquista: primeira vaga como dev júnior", "trecho": "primeira vaga como dev júnior!"},
                 {"afirmacao": "Portfólio foi o diferencial", "fato": "Origem: portfólio construído no ONE", "trecho": "O portfólio que construí no ONE fez a diferença."}
             ]},
        ],
    },
    {
        "id": "hist-002",
        "autor": "Lucas Almeida",
        "iniciais": "LA",
        "canal": "#projetos",
        "origem": "Mensagem da comunidade",
        "categoria": "Projeto de destaque",
        "sentimento": "Positivo",
        "relevancia": 89,
        "mensagem_original": "Nosso projeto de controle financeiro foi destaque no desafio. Fizemos tudo em equipe!",
        "citacoes": [
            {"texto": "projeto de controle financeiro foi destaque no desafio.", "id_interacao": 2},
            {"texto": "Fizemos tudo em equipe!", "id_interacao": 2}
        ],
        "interacoes_origem": [2],
        "destaques": ["projeto de controle financeiro foi destaque no desafio.", "Fizemos tudo em equipe!"],
        "fatos": ["Projeto: controle financeiro", "Reconhecimento: destaque no desafio", "Trabalho em equipe"],
        "ativos": [
            {"id": "testemunho", "nome": "Testemunho estruturado", "tipo": "testemunho",
             "campos": {
                 "titulo": "Projeto colaborativo reconhecido no desafio",
                 "descricao": "Lucas Almeida e sua equipe desenvolveram um sistema de controle financeiro que foi destacado no desafio do Programa ONE. O projeto demonstrou não apenas competências técnicas, mas também habilidades de trabalho em equipe.",
                 "citacao": "Nosso projeto de controle financeiro foi destaque no desafio. Fizemos tudo em equipe!"
             },
             "variacoes": [{
                 "titulo": "Equipe conquista destaque com projeto financeiro",
                 "descricao": "O time de Lucas Almeida foi reconhecido no desafio do Programa ONE com um projeto de controle financeiro. A iniciativa destacou-se pela qualidade técnica e pela colaboração entre os participantes.",
                 "citacao": "Fizemos tudo em equipe!"
             }],
             "fontes": [
                 {"afirmacao": "Projeto de controle financeiro foi destaque", "fato": "Projeto: controle financeiro", "trecho": "projeto de controle financeiro foi destaque no desafio."},
                 {"afirmacao": "Desenvolvido em equipe", "fato": "Trabalho em equipe", "trecho": "Fizemos tudo em equipe!"}
             ]},
            {"id": "case", "nome": "Case de sucesso", "tipo": "texto",
             "campos": {"texto": "Case de Sucesso: Projeto Colaborativo em Destaque\n\n"
                                 "Equipe liderada por Lucas Almeida desenvolveu um sistema de controle financeiro "
                                 "que foi reconhecido como destaque no desafio do Programa ONE. "
                                 "O projeto demonstrou competências técnicas sólidas e excelente capacidade de colaboração.\n\n"
                                 "Resultado: Reconhecimento oficial no desafio e validação das habilidades de trabalho em equipe."},
             "variacoes": [{"texto": "História de Sucesso: Destaque em Projeto de Equipe\n\n"
                                     "Equipe: Lucas Almeida e colaboradores\n"
                                     "Projeto: Sistema de controle financeiro\n"
                                     "Reconhecimento: Destaque no desafio do Programa ONE\n\n"
                                     "O projeto foi desenvolvido de forma colaborativa e destacou-se pela qualidade técnica. "
                                     "A iniciativa evidenciou tanto as competências individuais quanto a capacidade de trabalho em equipe."}],
             "fontes": [
                 {"afirmacao": "Projeto foi destaque no desafio", "fato": "Reconhecimento: destaque no desafio", "trecho": "projeto de controle financeiro foi destaque no desafio."},
                 {"afirmacao": "Trabalho realizado em equipe", "fato": "Trabalho em equipe", "trecho": "Fizemos tudo em equipe!"}
             ]},
        ],
    },
    {
        "id": "hist-003",
        "autor": "Camila Santos",
        "iniciais": "CS",
        "canal": "#carreira",
        "origem": "Mensagem da comunidade",
        "categoria": "Superação e transição de carreira",
        "sentimento": "Positivo",
        "relevancia": 84,
        "mensagem_original": "Depois de 10 anos no varejo, concluí a formação e comecei minha transição para tecnologia.",
        "citacoes": [
            {"texto": "Depois de 10 anos no varejo,", "id_interacao": 3},
            {"texto": "concluí a formação", "id_interacao": 3},
            {"texto": "comecei minha transição para tecnologia.", "id_interacao": 3}
        ],
        "interacoes_origem": [3],
        "destaques": ["Depois de 10 anos no varejo,", "concluí a formação", "comecei minha transição para tecnologia."],
        "fatos": ["Trajetória: 10 anos no varejo", "Marco: formação concluída", "Mudança: início da transição para tecnologia"],
        "ativos": [
            {"id": "testemunho", "nome": "Testemunho estruturado", "tipo": "testemunho",
             "campos": {
                 "titulo": "Transição de carreira: do varejo para a tecnologia",
                 "descricao": "Após uma década de experiência no varejo, Camila Santos concluiu a formação no Programa ONE e iniciou sua transição para a área de tecnologia. A trajetória exemplifica que mudanças de carreira são possíveis em qualquer momento da vida profissional.",
                 "citacao": "Depois de 10 anos no varejo, concluí a formação e comecei minha transição para tecnologia."
             },
             "variacoes": [{
                 "titulo": "Recomeço profissional na tecnologia",
                 "descricao": "Camila Santos decidiu mudar de carreira após 10 anos no setor de varejo. Concluiu a formação no Programa ONE e deu início à sua jornada na área tech, demonstrando que nunca é tarde para recomeçar.",
                 "citacao": "concluí a formação e comecei minha transição para tecnologia."
             }],
             "fontes": [
                 {"afirmacao": "Camila trabalhou 10 anos no varejo", "fato": "Trajetória: 10 anos no varejo", "trecho": "Depois de 10 anos no varejo,"},
                 {"afirmacao": "Concluiu a formação no programa", "fato": "Marco: formação concluída", "trecho": "concluí a formação"},
                 {"afirmacao": "Iniciou transição para tecnologia", "fato": "Mudança: início da transição para tecnologia", "trecho": "comecei minha transição para tecnologia."}
             ]},
            {"id": "case", "nome": "Case de sucesso", "tipo": "texto",
             "campos": {"texto": "Case de Sucesso: Transição de Carreira para Tecnologia\n\n"
                                 "Camila Santos construiu 10 anos de experiência no setor de varejo antes de decidir mudar de área. "
                                 "Após concluir a formação no Programa ONE, iniciou sua transição para o mercado de tecnologia.\n\n"
                                 "Resultado: Transição de carreira bem-sucedida, demonstrando que mudanças profissionais "
                                 "são viáveis com dedicação e formação adequada."},
             "variacoes": [{"texto": "História de Sucesso: Nova Carreira em Tech\n\n"
                                     "Participante: Camila Santos\n"
                                     "Trajetória anterior: 10 anos no varejo\n"
                                     "Mudança: Transição para tecnologia após formação\n\n"
                                     "Camila decidiu recomeçar profissionalmente na área tech. "
                                     "Concluiu a formação no Programa ONE e iniciou sua nova trajetória, "
                                     "provando que é possível mudar de carreira em qualquer etapa da vida profissional."}],
             "fontes": [
                 {"afirmacao": "Experiência de 10 anos no varejo", "fato": "Trajetória: 10 anos no varejo", "trecho": "Depois de 10 anos no varejo,"},
                 {"afirmacao": "Formação concluída", "fato": "Marco: formação concluída", "trecho": "concluí a formação"},
                 {"afirmacao": "Transição iniciada", "fato": "Mudança: início da transição para tecnologia", "trecho": "comecei minha transição para tecnologia."}
             ]},
        ],
    },
]

PACOTES_OCI = [
    {"caminho": "ativos/demo-001/pacote-distribuicao.json", "lote": "DEMO-001",
     "data": "15/10/2026 14:32", "tamanho": "2,4 KB", "status": "salvo"},
    {"caminho": "ativos/demo-001/evidencias.json", "lote": "DEMO-001",
     "data": "15/10/2026 14:32", "tamanho": "1,1 KB", "status": "salvo"},
    {"caminho": "ativos/demo-002/pacote-distribuicao.json", "lote": "DEMO-002",
     "data": None, "tamanho": None, "status": "falhou"},
]
