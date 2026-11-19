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
| Aspecto | Testemunho | Case |
|---|---|---|
| tipo canônico (editorial) | testemunho_estruturado | case_sucesso |
| tipo do front (formulário) | testemunho | texto |
| campos no front | titulo, descricao, citacao | texto |
| titulo canônico | Título editorial | Título editorial, opcional no schema |
| texto canônico | Descrição + duas quebras + citação entre aspas | Narrativa em texto único |
| vínculo | interacoes_origem e evidências conferidas | interacoes_origem e evidências conferidas |

**Proposta de mapeamento, ainda não adaptador implementado.** Preservar dados estruturados de título/descrição/citação no envelope de apresentação; não tentar recuperar campos perdidos dividindo texto livre. Ao salvar edições, atualizar também a projeção canônica. No case, o formulário atual só edita texto: conferir se o título será exibido como metadado ou incorporado ao conteúdo sem duplicação. Não declarar essa decisão de interface concluída.

O schema canônico de ativo tem additionalProperties=false. Não acrescentar campos, id_historia, lote ou estados próprios ao objeto AtivoGerado sem revisão versionada. Esses dados podem ficar num envelope explicitamente separado.

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
