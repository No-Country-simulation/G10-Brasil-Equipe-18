# CommunityLab Acceptance Test Plan (CATP)   

**Versão:** 1.1  
**Projeto:** CommunityLab — Hackathon ONE G10  
**Equipe:** 18  
**Responsável funcional:** Marcus — Project Manager  
**Status:** Planejamento revisado — testes ainda não executados

## 1. Objetivo

Estabelecer um plano estruturado de testes de aceitação para verificar se o MVP do CommunityLab atende aos requisitos funcionais, mantém a fidelidade das informações e executa corretamente o fluxo integrado de processamento.

O CATP complementa o CommunityLab Quality Framework (CQF v1.0), sem substituí-lo.

A implementação declarada de uma funcionalidade não equivale à aprovação de seu teste de aceitação.

## 2. Escopo dos testes

O plano contempla:

- Importação de interações em CSV e JSON.
- Validação e tratamento de dados.
- Análise de sentimentos e extração de tópicos.
- Identificação de histórias de sucesso relevantes.
- Rastreabilidade das evidências por trecho literal e ID da interação original.
- Geração de depoimentos estruturados.
- Geração de casos de sucesso sem fatos inventados.
- Navegação e funcionalidades da interface Streamlit.
- Revisão e curadoria humana com controles independentes.
- Aplicação das regras RG-01, RG-02 e RG-03.
- Integração e persistência na OCI Object Storage, incluindo idempotência.
- Identificação de dados fictícios no modo demonstração.
- Controles de qualidade definidos pelo CQF, conforme decisão de escopo do MVP.

## 3. Matriz de testes de aceitação

Todos os testes possuem status inicial **Não executado**.

| ID | Funcionalidade | Resultado esperado | Status |
|---|---|---|---|
| CATP-001 | Importação CSV | Arquivo válido processado corretamente | Não executado |
| CATP-002 | Importação JSON | Dados válidos importados corretamente | Não executado |
| CATP-003 | Dados inválidos | Erro tratado e informado ao usuário | Não executado |
| CATP-004 | Análise de sentimentos | Resultado associado à interação original | Não executado |
| CATP-005 | Extração de tópicos | Tópicos identificados e rastreáveis | Não executado |
| CATP-006 | Detecção de histórias | Histórias relevantes identificadas sem substituir resultados vazios por histórias fictícias | Não executado |
| CATP-007 | Rastreabilidade | Evidência literal vinculada ao ID da interação original | Não executado |
| CATP-008 | Geração de depoimentos | Depoimento estruturado e fiel à fonte | Não executado |
| CATP-009 | Geração de casos de sucesso | Caso estruturado sem fatos inventados | Não executado |
| CATP-010 | Curadoria humana | Controles independentes validados pelos subcasos CATP-010a a CATP-010d | Não executado |
| CATP-010a | Validação factual | Estados Pendente, Validada, Insuficiente e Contradição registrados corretamente | Não executado |
| CATP-010b | Curadoria editorial | Estados Rascunho, Ajustes, Aprovado e Rejeitado registrados corretamente | Não executado |
| CATP-010c | Autorização de publicação | Estados Não registrada e Registrada independentes da aprovação editorial | Não executado |
| CATP-010d | Indicador RG-03 | Liberação para publicação depende de todos os requisitos aplicáveis | Não executado |
| CATP-011 | Persistência OCI | Resultado armazenado e recuperável, sem duplicidade ao regravar o mesmo lote | Não executado |
| CATP-012 | CQF — Pontuação | Cálculo conforme CQF v1.0, caso integrado ao MVP | Não executado |
| CATP-013 | CQF — Contradições | Contradição não resolvida impede aprovação, caso a regra esteja integrada | Não executado |
| CATP-014 | Autorização | Divulgação impedida sem autorização apropriada | Não executado |
| CATP-015 | Fluxo completo | Processamento integrado executado com sucesso | Não executado |
| CATP-016 | Navegação Streamlit | Navegação funcional entre os seis módulos previstos | Não executado |
| CATP-017 | Estúdio — evidências e conteúdo | Fontes e conteúdo gerado exibidos lado a lado | Não executado |
| CATP-018 | Estúdio — regeneração RG-01 | Regeneração preserva fatos e não inventa informações | Não executado |
| CATP-019 | Curadoria — controles | Três controles independentes funcionam corretamente | Não executado |
| CATP-020 | Contradição RG-02 | Interface bloqueia aprovação diante de contradição não resolvida | Não executado |
| CATP-021 | Indicador RG-03 | Indicador de liberação corresponde às condições efetivas de publicação | Não executado |
| CATP-022 | Solicitação de ajustes | Observações editoriais registradas e vinculadas ao conteúdo | Não executado |
| CATP-023 | Modo demonstração | Dados fictícios e resultados simulados identificados explicitamente | Não executado |

### 3.1. CATP-007 — Rastreabilidade das evidências

**Objetivo:** garantir que toda evidência apresentada no conteúdo gerado seja verificável.

**Procedimento:**

1. Selecionar uma interação com ID conhecido.
2. Executar a análise e acessar o conteúdo gerado.
3. Identificar os trechos apresentados como evidências.
4. Comparar cada trecho com a mensagem original.
5. Verificar o vínculo entre a evidência e o ID da interação de origem.

**Critérios de aceitação:**

- A evidência deve corresponder literalmente ao texto original.
- O ID da interação de origem deve estar disponível para verificação.
- A evidência não poderá ser atribuída a outra interação.
- Trechos alterados ou sem origem verificável não serão aceitos.

**Evidências necessárias:** ID da interação, mensagem original, trecho citado e registro do vínculo.

### 3.2. CATP-010 — Curadoria humana

A curadoria possui três controles independentes e um indicador de liberação.

**CATP-010a — Validação factual**

Verificar os estados:

- Pendente
- Validada
- Insuficiente
- Contradição

Confirmar que alterações de estado sejam registradas corretamente.

**CATP-010b — Curadoria editorial**

Verificar os estados:

- Rascunho
- Ajustes
- Aprovado
- Rejeitado

Confirmar que a decisão editorial seja independente da autorização de publicação.

**CATP-010c — Autorização de publicação**

Verificar os estados:

- Não registrada
- Registrada

A aprovação editorial não poderá gerar autorização automaticamente.

**CATP-010d — Indicador de liberação (RG-03)**

O indicador **Liberado para publicação** deverá refletir os requisitos aplicáveis de validação factual, aprovação editorial e autorização.

O CATP-010 somente será considerado aprovado quando seus quatro subcasos aplicáveis forem aprovados.

### 3.3. CATP-011 — Persistência e idempotência OCI

**Objetivo:** garantir armazenamento, recuperação e prevenção de duplicidades no OCI Object Storage.

**Procedimento:**

1. Preparar um lote com identificador único.
2. Executar sua primeira gravação no bucket.
3. Confirmar o armazenamento e a recuperação do objeto.
4. Repetir a gravação utilizando o mesmo identificador e os mesmos dados.
5. Consultar os objetos e a contagem de lotes após a repetição.
6. Comparar os resultados das duas operações.

**Critérios de aceitação:**

- O objeto deve ser armazenado e recuperável.
- O reprocessamento do mesmo lote não deve criar duplicidades.
- A contagem de lotes não deve aumentar indevidamente.
- A operação deve preservar a identidade lógica do lote.

**Evidências necessárias:** ID do lote, chave do objeto, registros das duas operações e comparação da listagem do bucket.

### 3.4. Regras de negócio e testes de interface

**RG-01 — CATP-018**

A regeneração de conteúdo deve preservar a fidelidade à interação original. Nomes, números, fatos e resultados não sustentados pelas evidências constituem falha.

**RG-02 — CATP-013 e CATP-020**

O CATP-013 verifica a regra funcional de contradição. O CATP-020 verifica se a interface impede a aprovação enquanto existir contradição não resolvida.

**RG-03 — CATP-010d e CATP-021**

O CATP-010d verifica a lógica de liberação. O CATP-021 verifica a apresentação correta do indicador na interface.

**CATP-014 — Autorização**

A autorização de publicação deve permanecer independente da aprovação editorial. A ausência de autorização impede a divulgação, mesmo quando o conteúdo estiver editorialmente aprovado.

**CATP-023 — Modo demonstração**

Os dados fictícios devem estar claramente identificados. Resultados simulados não poderão ser apresentados como resultados reais de análises ou integrações.

### 3.5. Status de implementação e aplicabilidade

As informações abaixo foram apresentadas durante a revisão do frontend e deverão ser confirmadas por execução.

| Casos | Situação informada | Validação |
|---|---|---|
| CATP-007 | Fontes apresentadas no Estúdio | Não executado |
| CATP-008 e CATP-009 | Ativos com fontes implementados no frontend | Não executado |
| CATP-010 | Controles independentes de curadoria implementados | Não executado |
| CATP-013 | Bloqueio de contradição implementado | Não executado |
| CATP-014 | Autorização independente implementada | Não executado |
| CATP-012 | Pontuação CQF não implementada no frontend | Pendente de decisão de escopo |

**CATP-012:** manter o caso planejado até decisão formal da equipe sobre sua inclusão no MVP inicial ou transferência para fase posterior.

**Referências para execução do frontend:**

- Branch: `feat/frontend-streamlit`
- Instruções: `COMO_RODAR.md`
- Especificações: `CLAUDE.md` e `READMEFrontend.md`

O funcionamento com dados fictícios não comprova a integração real com LLM e OCI.

## 4. Procedimento de execução

Cada teste deverá registrar:

- Identificador do teste.
- Data de execução.
- Responsável pela execução.
- Ambiente utilizado.
- Branch, versão e commit do sistema testado.
- Dados de entrada.
- Pré-condições e procedimento executado.
- Resultado esperado.
- Resultado observado.
- Status de implementação: disponível, parcial, não implementado ou não verificado.
- Aplicabilidade ao escopo aprovado.
- Status de execução: aprovado, reprovado, bloqueado ou não executado.
- Evidências de execução.
- Referência ao defeito identificado, quando aplicável.
- Resultado do reteste após eventual correção.

A ausência de implementação não deve ser confundida com aprovação ou reprovação de um teste não executado.

Casos não aplicáveis exigem justificativa e decisão formal de escopo.

## 5. Critérios de aceitação

Um teste somente poderá ser considerado aprovado quando o comportamento observado corresponder ao resultado esperado e houver evidência suficiente para sustentar a decisão.

A documentação de um caso de teste não equivale à sua execução.

Para conteúdos derivados de interações, deverão ser verificados:

- Fidelidade aos fatos presentes na fonte.
- Correspondência literal das citações utilizadas como evidência.
- Vínculo ao ID da interação original.
- Ausência de informações inventadas.
- Independência dos controles de curadoria e autorização.

Uma análise válida sem histórias relevantes não poderá apresentar histórias fictícias como resultado real.

Falhas relevantes deverão ser registradas, corrigidas e submetidas a novo teste.

## 6. Responsabilidades

**Marcus — Project Manager:** planejamento funcional, coordenação dos testes de aceitação, consolidação dos resultados, acompanhamento das pendências e encaminhamento das decisões de escopo.

**Equipe técnica:** apoio à preparação do ambiente, execução dos testes pertinentes, análise de falhas, fornecimento de evidências e correções, conforme distribuição acordada.

Cada execução deverá identificar o responsável e o commit efetivamente validado.

## 7. Integração com o CQF

O CQF avalia a qualidade editorial e estabelece controles de governança sobre histórias e conteúdos.

O CATP verifica se as funcionalidades implementadas atendem aos comportamentos esperados.

Os seis cenários documentados em `CQF_VALIDATION_REPORT.md` poderão ser utilizados como referências para testes de aceitação, com adaptações aos formatos reais de entrada e saída do MVP.

**CATP-012 — Pontuação CQF**

A implementação do CQF Score 0–100 permanece pendente de decisão de escopo.

Até deliberação da equipe:

- O teste permanece documentado.
- O status de execução permanece Não executado.
- A aplicabilidade permanece pendente.
- Não se presume implementação ou aprovação.

Caso o CQF Score seja transferido para uma fase posterior, a decisão deverá ser registrada formalmente.

A validação da regra de contradição não depende da implementação da pontuação numérica.

## 8. Critério de encerramento

A execução do CATP será considerada encerrada quando:

- Os testes aplicáveis ao escopo aprovado forem executados.
- Os resultados estiverem documentados.
- As evidências forem rastreáveis aos dados e ao commit testado.
- As falhas impeditivas forem resolvidas e retestadas ou formalmente tratadas.
- Os testes bloqueados e não aplicáveis possuírem justificativas documentadas.
- As decisões pendentes de escopo estiverem registradas.

A decisão final de aceite dependerá da avaliação conjunta dos responsáveis pelo projeto.

---

**Documento de planejamento funcional — CATP v1.1.**

**Histórico de versões:**

- **v1.0:** matriz inicial de 15 casos de teste e critérios gerais de aceitação.
- **v1.1:** detalhamento da curadoria humana, inclusão dos testes de interface Streamlit, rastreabilidade por ID e evidência literal, idempotência OCI, regras RG-01 a RG-03 e padronização das evidências de execução.
