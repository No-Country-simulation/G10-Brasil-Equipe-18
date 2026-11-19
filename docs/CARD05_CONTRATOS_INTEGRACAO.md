# Card 05 — Contratos de integração do CommunityLab
Versão 0.1 • 18/11/2026 • Proposta para revisão técnica

## Estado e alcance
Documento preparado para Marcus, com base nos arquivos consultados da main em 18/11. Define uma proposta de compatibilidade, exemplos sintéticos e verificações de contrato. Não implementa adaptadores, não altera schemas e não comprova geração por LLM, persistência OCI ou aceite do MVP. A decisão editorial do case em texto único foi delegada por Marcus; sua integração continua pendente.

Revisão: Jaqueline (análise/geração), Tissiany (interface), Luciene (persistência). Confirmar a manutenção dos contratos anteriormente atribuídos à Ketlyn, preservando seus créditos.

## 1. Três representações distintas
1. Entrada simplificada do app: lista de mensagens ou objeto com interacoes.
2. Contratos canônicos em schemas/ e src/modelos.py.
3. História/ativo de apresentação consumidos pelo Streamlit e presentes no pacote do lote.

Um formato não deve ser validado diretamente contra o schema de outro. Manter os schemas existentes como referência canônica e propor adaptadores explícitos, sem afirmar que já existem.

## 2. Entrada atualmente aceita pelo app
| Campo | Comportamento observado |
|---|---|
| autor, canal, texto | Obrigatórios na rotina de ingestão; valores convertidos em string e aparados. Não enviar nomes reais nos exemplos. |
| tipo | Opcional, padrão mensagem; categoria da história é definida depois. |
| id | Inteiro positivo preservado; ausência usa posição a partir de 1. Duplicidade efetiva bloqueia lote. |
| _id_efetivo | Campo interno calculado antes de filtros; não deve ser informado como identificador canônico externo. |
| Outros campos | Não preservados pelo dicionário mínimo de normalização. |

Upload usa UTF-8 (aceita BOM), CSV com csv.DictReader e JSON com json.loads. Uma lista JSON vazia é rejeitada na ingestão; uma análise sem histórias é resultado diferente e pode ser válida.

### Divergências concretas a corrigir ou formalizar
- CSV retorna strings. Um id textual como 701 não é convertido para inteiro pelo caminho consultado; pode virar a posição. Não anunciar equivalência de IDs CSV/JSON antes de decidir conversão.
- bool é subclasse de int em Python: True satisfaz a condição atual isinstance(id, int) and id >= 1. O comentário do código diz que booleanos são inválidos, mas o código observado aceita True. O schema JSON de interação rejeita booleano como integer. Registrar a correção/teste, sem contar como implementada por este documento.
- Checar comportamento de null e tipos complexos nos campos textuais; str(None) pode passar como texto em vez de representar ausência.
- Schema canônico de interação exige versao_schema, id, autor_id, data, origem e texto; não admite canal/tipo de mensagem soltos. Não enviar diretamente o JSON canônico ao importador simplificado.
- Data ausente na entrada simplificada não deve ser inventada como data de publicação. Separar horário de importação; decidir a política para entradas sem data antes de converter ao schema canônico.

## 3. Identificadores e vínculos
- ID da interação: único dentro do lote; identidade completa = lote + id.
- ID da história: único dentro do lote e ligado a interacoes_origem.
- ID canônico do ativo: ativo_001, ativo_002 etc., único dentro do lote.
- id local do front: chave estável do formato dentro da história, como testemunho_estruturado ou case_sucesso.
- A chave de aplicação atual usa história/ativo; ao persistir decisões incluir também o lote para evitar colisões entre sessões.
- Conversões devem preservar o vínculo entre cada história e sua interação, inclusive quando duas histórias estão no mesmo lote.

## 4. Mapeamento proposto para os dois formatos

### 4.1 Visão geral dos tipos

| Aspecto | Testemunho | Case |
|---|---|---|
| tipo canônico (editorial) | testemunho_estruturado | case_sucesso |
| tipo do front (formulário) | testemunho | texto |
| campos no front | titulo, descricao, citacao | texto |
| titulo canônico | Título editorial, opcional no schema | Título editorial, opcional no schema |
| texto canônico | Descrição + duas quebras + citação entre aspas | Narrativa em texto único |
| vínculo | interacoes_origem e evidências conferidas | interacoes_origem e evidências conferidas |

### 4.2 Tabela campo a campo — Testemunho Estruturado

| Campo | Representação Front | Representação Canônica | Origem do dado | Critério de teste | Decisão |
|-------|---------------------|------------------------|----------------|-------------------|---------|
| **id** | `testemunho_estruturado` (chave local) | `ativo_001` (ID único do lote) | Gerado pela aplicação | ID único dentro do lote, sem colisão | Aprovado - IDs separados por contexto |
| **tipo** | `testemunho` (tipo de formulário) | `testemunho_estruturado` (tipo editorial) | Normalizado pela aplicação | Validação contra schema canônico | **Post LinkedIn e Card mantêm seus tipos editoriais próprios** |
| **nome** | `"Testemunho estruturado"` (rótulo UI) | Não presente no schema canônico | Interface do usuário | Exibição no Estúdio/Curadoria | Aprovado - apenas para apresentação |
| **titulo** | `campos.titulo` (editável; o formulário do Estúdio e da Curadoria lê o campo diretamente, então a projeção do front deve trazê-lo) | `titulo` (string, **opcional**: fora de `required` em `schemas/ativo_gerado_schema.json` e `Optional[str]` em `src/modelos.py`; máx. 200) | Gerado por LLM, editável no Estúdio | Preservação após edição; ativo canônico sem `titulo` continua válido | Aprovado - opcional no canônico; quando presente, igual a `campos.titulo` |
| **descricao** | `campos.descricao` (editável) | Parte de `texto` (antes das aspas) | Gerado por LLM, editável no Estúdio | Ida: compor `texto`. Volta: ler do envelope (ver 4.6) | **Pendente** - adaptador não implementado |
| **citacao** | `campos.citacao` (editável) | Parte de `texto` (entre aspas) | Gerado por LLM, editável no Estúdio | Ida: compor `texto`. Volta: ler do envelope (ver 4.6) | **Pendente** - adaptador não implementado |
| **texto** | Não editável diretamente | Composição: `descricao + "\n\n\"" + citacao + "\""` | Derivado dos campos estruturados | Formato com duas quebras + aspas | Aprovado - regra de composição definida |
| **interacoes_origem** | Não editável (metadado exibido) | `interacoes_origem` (array de int) | Vínculo estabelecido na análise | Rastreabilidade completa | Aprovado - vínculo preservado |
| **status_revisao** | Não presente (usa controles separados) | `status_revisao: "pendente"` | Iniciado pela aplicação | Mapeamento: rascunho/ajustes → pendente | **Pendente** - envelope deve preservar estados detalhados |
| **criado_em** | Não exibido | `criado_em` (ISO 8601 UTC) | Timestamp real da geração | Data de criação, não da interação | Aprovado - instante UTC real |
| **modelo_llm** | Não exibido | `modelo_llm` (opcional) | Provedor efetivamente usado | Rastreabilidade técnica | Aprovado - quando disponível |
| **versao_schema** | Não presente | `"1.0"` | Aplicação | Validação de compatibilidade | Aprovado - fixo em 1.0 |
| **oci_object_path** | Não presente | Omitido (opcional no schema) | Não usado atualmente | Padrão `ativos/AAAA-MM-DD/...` se presente | Aprovado - omissão permitida |

### 4.3 Tabela campo a campo — Case de Sucesso

| Campo | Representação Front | Representação Canônica | Origem do dado | Critério de teste | Decisão |
|-------|---------------------|------------------------|----------------|-------------------|---------|
| **id** | `case_sucesso` (chave local) | `ativo_002` (ID único do lote) | Gerado pela aplicação | ID único dentro do lote, sem colisão | Aprovado - IDs separados por contexto |
| **tipo** | `texto` (tipo de formulário) | `case_sucesso` (tipo editorial) | Normalizado pela aplicação | Validação contra schema canônico | **Post LinkedIn e Card mantêm seus tipos editoriais próprios** |
| **nome** | `"Case de sucesso"` (rótulo UI) | Não presente no schema canônico | Interface do usuário | Exibição no Estúdio/Curadoria | Aprovado - apenas para apresentação |
| **titulo** | Não presente no formulário atual | `titulo` (string, opcional no schema) | Pode ser gerado por LLM | **Decidir se será metadado ou incorporado ao texto** | **Pendente de decisão** - evitar duplicação |
| **texto** | `campos.texto` (editável) | `texto` (string, obrigatório) | Gerado por LLM, editável no Estúdio | Preservação após edição | Aprovado - narrativa em texto único |
| **interacoes_origem** | Não editável (metadado exibido) | `interacoes_origem` (array de int) | Vínculo estabelecido na análise | Rastreabilidade completa | Aprovado - vínculo preservado |
| **status_revisao** | Não presente (usa controles separados) | `status_revisao: "pendente"` | Iniciado pela aplicação | Mapeamento: rascunho/ajustes → pendente | **Pendente** - envelope deve preservar estados detalhados |
| **criado_em** | Não exibido | `criado_em` (ISO 8601 UTC) | Timestamp real da geração | Data de criação, não da interação | Aprovado - instante UTC real |
| **modelo_llm** | Não exibido | `modelo_llm` (opcional) | Provedor efetivamente usado | Rastreabilidade técnica | Aprovado - quando disponível |
| **versao_schema** | Não presente | `"1.0"` | Aplicação | Validação de compatibilidade | Aprovado - fixo em 1.0 |
| **oci_object_path** | Não presente | Omitido (opcional no schema) | Não usado atualmente | Padrão `ativos/AAAA-MM-DD/...` se presente | Aprovado - omissão permitida |

### 4.4 Post LinkedIn e Card de Conquista

**Decisão do Marcus (comentário de 18/11/2026):**
> Post LinkedIn e Card de conquista seguem como tipos editoriais próprios; formato de tela não deve mudar essa classificação.

| Tipo de ativo | Tipo editorial canônico | Tipo de formulário front | Observação |
|---------------|-------------------------|--------------------------|------------|
| Post para LinkedIn | `post_linkedin` | `texto` ou `card` (a definir) | Formato de tela não altera classificação editorial |
| Card de conquista | `card_conquista` | `card` | Preserva estrutura visual específica |

**Proposta de mapeamento, ainda não adaptador implementado.** Preservar dados estruturados de título/descrição/citação no envelope de apresentação; não tentar recuperar campos perdidos dividindo texto livre. Ao salvar edições, atualizar também a projeção canônica. No case, o formulário atual só edita texto: conferir se o título será exibido como metadado ou incorporado ao conteúdo sem duplicação. Não declarar essa decisão de interface concluída.

O schema canônico de ativo tem additionalProperties=false. Não acrescentar campos, id_historia, lote ou estados próprios ao objeto AtivoGerado sem revisão versionada. Esses dados podem ficar num envelope explicitamente separado.

### 4.5 Campos opcionais de revisão e CQF — destino

Os três campos existem no schema canônico (`schemas/ativo_gerado_schema.json`) e em `AtivoGerado` (`src/modelos.py`), valem para Testemunho e Case e são opcionais. Hoje nenhum código do app os preenche nem grava, e o envelope proposto no #49 (`envelope_proposto.json`) não os inclui. Por isso o destino fica pendente.

| Campo | Definição no contrato | Onde é gravado hoje | Para onde vai | Decisão |
|-------|-----------------------|---------------------|---------------|---------|
| **revisor** | string; "quem aprovou ou rejeitou" | Em nenhum lugar: a Curadoria não registra o responsável pela decisão | Não definido | **Pendente** |
| **observacao_revisor** | string, máx. 500 | Não é gravado no ativo. A Curadoria guarda a observação de ajustes e o motivo de rejeição só na sessão (`observacoes` e `motivos`), e o envelope do #49 tem `parecer` em `curadoria`; a relação entre esses campos não está decidida | Não definido | **Pendente** |
| **id_avaliacao_cqf** | string no padrão `cqf_NNN`; liga o ativo a uma avaliação CQF (`schemas/avaliacao_cqf_schema.json`) | Em nenhum lugar no app; aparece só nos exemplos `data/samples/cenarios_cqf.json` e nos testes | Não definido | **Pendente** |

Até a decisão, omitir os três campos do objeto canônico (não usar `null`, porque o schema exige string quando a propriedade está presente).

### 4.6 Volta ao formulário depende do envelope

A volta do canônico para o formulário do front (por exemplo, ao recuperar um ativo no Histórico) depende dos campos estruturados preservados no envelope de curadoria: `historias[].ativos[].campos` com `titulo`, `descricao` e `citacao` no testemunho e `texto` no case. O formulário é reconstruído a partir desses campos, sem divisão de texto livre: o adaptador não deve separar o `texto` canônico em descrição e citação procurando quebras de linha ou aspas. Se o envelope não trouxer os campos estruturados, a volta é tratada como dado incompleto e não como texto a ser fatiado.

## 5. Metadados e governança
| Campo canônico | Quem preenche |
|---|---|
| versao_schema | Aplicação, versão 1.0 |
| id_ativo | Aplicação, alocação determinística sem colisão no lote |
| tipo | Aplicação normaliza o formato editorial permitido |
| texto/titulo | Conteúdo gerado e depois revisável, conforme a fonte |
| interacoes_origem | Fonte do lote, validada pelo aplicativo |
| criado_em | Aplicação, instante real UTC da criação, não data inventada do relato |
| status_revisao | Aplicação, começa pendente |
| modelo_llm | Provedor/modelo efetivamente utilizado quando conhecido |

Nunca pedir que o modelo declare um conteúdo aprovado, validado ou autorizado.

Mapeamento editorial proposto: rascunho e ajustes → pendente; aprovado → aprovado; rejeitado → rejeitado. Como o schema perde a distinção ajustes/rascunho, o envelope de curadoria deve conservar o estado detalhado e o parecer.

Validação factual, decisão editorial e autorização são independentes. No app atual: pendente/validada/insuficiente/contradicao; rascunho/ajustes/aprovado/rejeitado; nao_registrada/registrada. Preservar separadamente essas dimensões; um status editorial aprovado não libera publicação sozinho.

## 6. Pacote do lote e OCI
O caminho observado em salvar_no_oci contém versao_schema, lote, gerado_em, origem_analise, historias e evidencias. Ativos atuais estão dentro das histórias no formato de apresentação. Isso não é um documento AtivoGerado canônico.

O OCI usa organização por lote. A propriedade opcional oci_object_path do schema de ativo exige ativos/AAAA-MM-DD/arquivo.json. Os dois conceitos não são equivalentes:
- não preencher essa propriedade com um caminho que viole o padrão;
- documentar a localização do pacote no envelope;
- decidir se a propriedade do ativo continua omitida ou se o contrato será versionado para outro padrão.

Omissão da propriedade é permitida pelo schema e foi usada nos exemplos. Não usar null: o schema exige string quando a propriedade está presente.

Persistência das decisões ainda precisa de implementação/validação nos Cards 19/21. Este documento propõe o envelope, não afirma que ele seja lido pelo Histórico atual.

## 7. Exemplos e como validar
Em data/samples/card05/:
- entrada_app.json e entrada_app.csv: duas mensagens fictícias equivalentes para os IDs 1 e 2.
- interacoes_canonicas.json: mesmos relatos com datas sintéticas explícitas e campos do schema canônico; não é entrada direta do app.
- ativos_canonicos.json: um testemunho e um case validados contra o schema atual.
- envelope_proposto.json: preserva histórias, projeções do front, vínculos e controles humanos. Não importar como pacote real já suportado.

Dados inventados exclusivamente para demonstração; textos editoriais redigidos manualmente para a especificação, sem chamada a LLM. Nenhuma autorização real, gravação OCI ou processamento real está implícito.

Executar:
python -m pip install jsonschema
python scripts/validar_exemplos_card05.py

O validador checa schemas reais do repositório, citações e vínculos, projeções propostas e três rejeições essenciais. As verificações isoladas de ingestão, descritas no relatório, usaram as funções da main com importações externas removidas; não são um teste E2E do Streamlit.

## 8. Pendências e condição de conclusão
1. Jaqueline/Tissiany validarem o mapeamento editorial/formulário, representação do título do case e fonte dos IDs.
2. Definir a compatibilidade da entrada canônica versus simplificada, incluindo IDs CSV, booleanos e datas ausentes.
3. Decidir o envelope de persistência e o caminho OCI, com Luciene.
4. Implementar/testar adaptadores e demonstrar exemplos de ida/volta sem perder campos ou trocar origens.
5. Registrar revisão técnica e referências de PR/commit no Card 05.

A implementação completa dos geradores é dos Cards 13/14; decisões persistidas, dos Cards 19/21; homologação E2E, do Card 23. Schema-validade não prova fidelidade semântica.

## 9. Fontes
Os SHAs de conteúdo consultados constam de fontes_consultadas.json. Eles identificam blobs de arquivos, não o SHA do deploy da VM nem o commit de uma rodada histórica.
