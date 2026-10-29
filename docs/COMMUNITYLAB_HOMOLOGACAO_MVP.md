
# CommunityLab — Relatório de Homologação e Aceite do MVP

**Projeto:** CommunityLab — Detector Inteligente de Histórias de Sucesso e Testemunhos  
**Hackathon:** ONE G10 — Equipe 18  
**Documento:** `COMMUNITYLAB_HOMOLOGACAO_MVP.md`  
**Versão:** 0.4 — Consolidação dos PRs #26 e #28 e esclarecimentos da Issue #27  
**Data de preparação:** 26/10/2026  
**Última atualização:** 29/10/2026  
**Referência funcional:** `docs/CATP_TEST_PLAN.md` — CATP v1.1  
**Referência de gestão:** Card 23 — Testes Integrados e Demonstração  
**Responsável funcional e consolidação:** Marcus — Project Manager  
**Responsável principal pelos testes integrados:** Ketlyn Barbosa  
**Apoio técnico:** Tissiany Delmiro, Jaqueline de Lira e Luciene Godoy  

**STATUS GERAL: HOMOLOGAÇÃO PENDENTE — SEM ACEITE DO MVP**

> **Regra de evidência:** nenhuma implementação declarada, integração de commit, teste unitário informado ou demonstração simulada constitui, isoladamente, aprovação de um caso de aceitação. A aprovação exige execução, observação e evidências vinculadas ao código efetivamente testado.

> **Nota da versão 0.4:** esta atualização preserva os registros históricos dos PRs #26 e #28, distingue a sessão Streamlit associada ao commit `9fcb06e` do teste direto posterior do Gemini, incorpora os esclarecimentos técnicos da Jaqueline na Issue #27 e corrige a atribuição da responsabilidade OCI. Não constitui aceite do MVP.

---

## 1. Objetivo e escopo

Consolidar o planejamento, a execução, os resultados e as evidências da homologação integrada do MVP CommunityLab.

O escopo compreende:

- Importação de arquivos CSV e JSON.
- Preparação e processamento das interações.
- Análise por inteligência artificial.
- Identificação de sentimentos, tópicos e relevância.
- Detecção de histórias de sucesso.
- Rastreabilidade de fontes, autores e evidências.
- Geração de depoimentos estruturados.
- Geração de cases de sucesso.
- Curadoria humana.
- Controles de validação factual, aprovação editorial e autorização.
- Persistência e recuperação real na OCI Object Storage.
- Tratamento de falhas e consistência entre lotes.
- Demonstração integrada do MVP.

### 1.1 Critérios essenciais

A homologação deve comprovar:

1. Fidelidade às informações de origem.
2. Identificação de evidências literais e IDs.
3. Ausência de fatos inventados.
4. Três histórias demonstrativas: conquista profissional, projeto de destaque e superação.
5. Dois formatos principais de ativo: depoimento estruturado e case de sucesso.
6. Curadoria humana.
7. Independência entre aprovação editorial e autorização.
8. Persistência e recuperação real na OCI.
9. Tratamento adequado de erros.
10. Ausência de defeitos críticos impeditivos.

Posts para LinkedIn são complementares. O painel analítico é opcional conforme o Card 23.

A pontuação CQF 0–100, prevista no CATP-012, permanece **pendente de decisão formal de escopo**.

### 1.2 Objetivo da atualização de 29/10/2026

Preservar a distinção entre:

- Funcionalidade visualmente apresentada.
- Funcionalidade efetivamente executada.
- Análise real pelo Gemini.
- Conteúdo demonstrativo ou mock.
- Persistência real na OCI.
- Mensagem de sucesso apresentada pela interface.
- Teste técnico isolado.
- Teste integrado de aceitação.

Os resultados preliminares não autorizam aprovação automática dos casos CATP.

---

## 2. Identificação do ambiente de homologação

### 2.1 Sessão local preliminar — Streamlit

| Campo | Registro |
|---|---|
| Identificador | PRELIM-20261029-01 |
| Data | 29/10/2026 |
| Executor | Marcus — Project Manager |
| Ambiente | Windows, VS Code, Python `.venv` |
| Aplicação | Streamlit local |
| URL | `http://localhost:8501` |
| Branch | `docs/homologacao-mvp` |
| Commit de referência | `9fcb06e` |
| SHA completo | A confirmar na execução formal |
| Arquivo utilizado | `data/samples/teste_importacao_catp001.csv` |
| Resultado | Verificação preliminar; homologação não concluída |
| Defeito relacionado | Issue #27 |

**Esclarecimento importante:** conforme análise posterior da Jaqueline, o commit `9fcb06e`, de 26/10/2026, antecede os merges dos PRs #20 e #21.

Naquele código, `app/telas/processamento.py` ainda não continha os elementos `persistencia` e `_pacotes_confirmados`, posteriormente presentes na `main`.

Portanto, os comportamentos observados nessa sessão devem ser tratados como **evidência histórica daquele código**, sem generalização automática para a versão posterior da `main`.

### 2.2 Integrações registradas em 28/10/2026

**PR #20 — Persistência OCI e status do processamento**

- Integração registrada na `main`.
- Merge de referência: `a05ae6b`.
- Revisão técnica informou testes de gravação real, falha simulada e reenvio.
- A evidência técnica relatada não substitui homologação integrada.

**PR #21 — Credenciais OCI via Streamlit Secrets**

- Desenvolvido por Tissiany.
- Integração registrada na `main`.
- Merge de referência: `2b65357`.
- Permite configuração de credenciais OCI via Streamlit Secrets.
- A configuração e a execução integrada ainda precisam ser comprovadas no ambiente de homologação.

**Pendência:** comportamento com bucket OCI vazio, cuja correção ainda não foi confirmada.

### 2.3 Arquivo CSV utilizado

Arquivo: `data/samples/teste_importacao_catp001.csv`

```csv
autor,canal,tipo,texto
membro_001,#conquistas-e-vagas,depoimento,Conquistei minha primeira vaga na área de IA!
membro_002,#duvidas-langgraph,pergunta_tecnica,Como estruturar nós condicionais no LangGraph?
```

Observações da sessão histórica:

- Duas interações disponíveis.
- Dois canais distintos.
- Prévia das interações apresentada.
- Falha de chamada Gemini observada.
- Fallback mock acionado.
- Histórias demonstrativas exibidas com autores diferentes dos registros importados.
- Persistência real não comprovada.

### 2.4 Teste direto posterior do Gemini — 29/10/2026

Conforme comentário técnico de Jaqueline de Lira na Issue #27:

| Campo | Registro |
|---|---|
| Data | 29/10/2026 |
| Horário informado | 12h45 |
| Executora | Jaqueline de Lira |
| Referência de código | `main`, com `2b65357` citado na análise |
| Tipo | Script local de teste direto do serviço |
| Modelo | `gemini-3.5-flash-lite` |
| Arquivo | `data/samples/teste_recuperacao.json` |
| Entradas | 3 interações |
| Histórias geradas | 3 |
| Autores | Ana Ribeiro, Bruno Sales e Carla Nunes |
| Correspondência com entradas | Informada como correta |
| Fallback mock | Não acionado nessa execução |
| Tempo aproximado | 21,9 segundos |
| Streamlit | Não testado nessa execução |
| Persistência OCI | Não testada nessa execução |

**Conclusão técnica:** o teste direto constitui evidência positiva de funcionamento do Gemini naquele ambiente e naquela execução.

Não comprova:

- Execução integrada pelo Streamlit.
- Persistência OCI.
- Recuperação dos objetos.
- Tratamento de erros 503 e timeout.
- Reinicialização de estado entre lotes.
- Homologação do MVP.

### 2.5 Diagnósticos adicionais informados na Issue #27

**Gemini e tratamento de falhas**

O caminho utilizado pela aplicação ainda não possuía mecanismo comprovado de novas tentativas ou modelo secundário.

Falhas 503/timeout podiam levar diretamente ao fallback mock.

A implementação de tentativas adicionais, segundo modelo e controle de tempo foi proposta, mas não há confirmação de conclusão nesta versão.

**Estado entre lotes**

Jaqueline informou que `_novo_lote` reinicializa:

- Interações.
- Arquivo.
- `proc_status`.

Entretanto, não reinicializa adequadamente:

- Histórias.
- Curadoria.

A correção e o reteste permanecem pendentes.

**OCI e bucket vazio**

O catálogo depende da listagem de pacotes no bucket.

Com o bucket vazio, pode ocorrer erro mesmo quando existem histórias disponíveis.

O problema foi diagnosticado, mas sua correção não foi confirmada.

**Responsabilidade OCI**

Jaqueline retificou a atribuição anterior e informou que a frente de persistência OCI voltou à sua responsabilidade.

A colaboração com Luciene deve ser alinhada entre as integrantes.

---

## 3. Estados e critérios de classificação

### 3.1 Implementação

- Disponível.
- Parcial.
- Não implementada.
- Não verificada.

### 3.2 Aplicabilidade

- Aplicável.
- Não aplicável, com justificativa e decisão formal.
- Pendente de decisão.

### 3.3 Execução

- Não executado.
- Aprovado.
- Reprovado.
- Bloqueado.

### 3.4 Evidências

São aceitas evidências como:

- Capturas de tela.
- Logs sanitizados.
- Arquivos de saída.
- IDs de interação.
- Chaves de objetos OCI não sensíveis.
- Relatórios técnicos.
- Links para commits e PRs.
- Registros de execução com ambiente identificado.

### 3.5 Regra de aprovação

Um caso somente poderá ser aprovado quando:

1. O ambiente estiver identificado.
2. O commit testado estiver registrado.
3. A entrada utilizada estiver documentada.
4. O resultado esperado estiver definido.
5. O resultado observado corresponder ao esperado.
6. As evidências forem suficientes e rastreáveis.

Verificações preliminares não substituem testes formais.

---

## 4. Matriz mestre de aceitação — CATP v1.1

| ID | Funcionalidade | Execução formal | Evidência ou pendência |
|---|---|---|---|
| CATP-001 | Importação CSV | Não executado | Prévia de duas interações verificada no teste histórico |
| CATP-002 | Importação JSON | Não executado | Pendente |
| CATP-003 | Dados inválidos | Não executado | Tratamento de erros pendente |
| CATP-004 | Sentimentos | Não executado | Rastreabilidade pendente |
| CATP-005 | Tópicos | Não executado | Rastreabilidade pendente |
| CATP-006 | Histórias | Não executado | Fallback mock histórico; teste Gemini direto posterior positivo |
| CATP-007 | Rastreabilidade | Não executado | Divergência histórica; autores preservados no teste direto posterior |
| CATP-008 | Depoimentos | Não executado | Pendente |
| CATP-009 | Cases | Não executado | Pendente |
| CATP-010 | Curadoria humana | Não executado | Quatro subcasos pendentes |
| CATP-010a | Validação factual | Não executado | Pendente |
| CATP-010b | Curadoria editorial | Não executado | Pendente |
| CATP-010c | Autorização | Não executado | Independência dos controles pendente |
| CATP-010d | Indicador RG-03 | Não executado | Pendente |
| CATP-011 | OCI e idempotência | Não executado | Persistência integrada não comprovada |
| CATP-012 | CQF Score 0–100 | Não executado | Aplicabilidade pendente de decisão |
| CATP-013 | CQF contradições | Não executado | Aplicabilidade a confirmar |
| CATP-014 | Autorização | Não executado | Bloqueio de divulgação pendente |
| CATP-015 | Fluxo completo | Não executado | Gemini–Streamlit–OCI não homologado |
| CATP-016 | Navegação Streamlit | Não executado | Verificação parcial; PR #29 em revisão |
| CATP-017 | Estúdio | Não executado | Pendente |
| CATP-018 | Regeneração RG-01 | Não executado | Fidelidade factual pendente |
| CATP-019 | Controles de curadoria | Não executado | Independência dos controles pendente |
| CATP-020 | Contradição RG-02 | Não executado | Bloqueio de aprovação pendente |
| CATP-021 | Indicador RG-03 | Não executado | Pendente |
| CATP-022 | Ajustes editoriais | Não executado | Pendente |
| CATP-023 | Modo demonstração | Não executado | Identificação explícita de mock pendente |

**Nota:** CATP-010 é agregador e depende dos quatro subcasos aplicáveis.

A matriz contém 23 casos principais e quatro subcasos adicionais.

### 4.1 Síntese das verificações preliminares

| Caso | Observação | Conclusão |
|---|---|---|
| CATP-001 | Prévia CSV exibida | Verificação parcial |
| CATP-006 | Mock após falha Gemini no teste histórico | Requer reteste na versão atual |
| CATP-007 | Autores divergentes no teste histórico | Rastreabilidade integrada pendente |
| CATP-011 | Salvamento visual sem confirmação OCI | Não verificado |
| CATP-015 | Conclusão visual apesar da falha histórica | Requer reteste |
| CATP-016 | Navegação parcialmente observada | Verificação parcial |
| CATP-023 | Mock apresentado no fluxo histórico | Requer reteste |

O teste direto posterior do Gemini demonstra funcionamento específico do serviço, mas não altera automaticamente os estados formais da matriz.

### 4.2 Resultados demonstrativos históricos

O CSV continha os autores `membro_001` e `membro_002`.

A sessão histórica apresentou histórias associadas a:

- Marina Costa.
- Lucas Almeida.
- Camila Santos.

Esses autores não correspondiam às entradas utilizadas.

A observação permanece registrada como evidência histórica do commit `9fcb06e`.

**Não se conclui que a mesma divergência ocorra na `main` posterior.**

---

## 5. Registro dos seis cenários de homologação integrada

A equipe informou a existência de seis arquivos de teste preparados para execução.

Os nomes, conteúdos e resultados completos ainda precisam ser formalmente associados aos cenários.

| Cenário | Arquivo | Objetivo | Execução | Evidência |
|---|---|---|---|---|
| HINT-01 | A preencher | A mapear | Não executado | Pendente |
| HINT-02 | A preencher | A mapear | Não executado | Pendente |
| HINT-03 | A preencher | A mapear | Não executado | Pendente |
| HINT-04 | A preencher | A mapear | Não executado | Pendente |
| HINT-05 | A preencher | A mapear | Não executado | Pendente |
| HINT-06 | A preencher | A mapear | Não executado | Pendente |

### 5.1 Casos negativos obrigatórios

Verificar, quando aplicável:

- Citação inexistente.
- ID duplicado.
- ID inválido.
- Evidência sem origem identificável.
- Dados insuficientes.
- Contradição não resolvida.
- Falha de Gemini.
- Timeout.
- Falha de persistência.
- Bucket OCI vazio.
- Novo lote após processamento anterior.

Quando não for possível conferir a origem de uma evidência, utilizar a indicação neutra **“Conferência indisponível”**, conforme orientação técnica registrada.

### 5.2 Execução local preliminar — PRELIM-20261029-01

**Responsável:** Marcus — Project Manager  
**Ambiente:** Streamlit local  
**Commit de referência:** `9fcb06e`  
**Arquivo:** `data/samples/teste_importacao_catp001.csv`  
**Tipo:** Verificação funcional preliminar.

**Passos observados:**

1. Disponibilização de CSV com duas interações.
2. Visualização da prévia.
3. Acionamento da importação e do processamento.
4. Exibição de progresso visual.
5. Apresentação de histórias e ativos.
6. Inspeção das mensagens do terminal.

**Resultado observado:**

- Prévia apresentada.
- Falha Gemini observada.
- Fallback mock acionado.
- Histórias demonstrativas sem correspondência com os autores do CSV.
- Indicação visual de conclusão sem comprovação de persistência real.

**Conclusão:** fluxo integrado não homologado nessa sessão.

**Limitação:** os resultados correspondem ao código histórico identificado e não comprovam o comportamento da `main` posterior.

**Defeito relacionado:** Issue #27.

### 5.3 Registro individual para testes formais

```text
ID do teste / cenário:
Data:
Responsável:
Ambiente:
Branch:
SHA completo:
Arquivo de entrada:
Versão do arquivo:
ID do lote:
Pré-condições:
Passos executados:
Resultado esperado:
Resultado observado:
Estado da implementação:
Aplicabilidade:
Resultado formal:
Evidências:
Defeito vinculado:
Gravidade:
Responsável pelo tratamento:
Reteste:
Conclusão:
```

---

## 6. Três demonstrações obrigatórias

| ID | História | Verificações mínimas | Execução |
|---|---|---|---|
| DEMO-01 | Conquista profissional | Entrada, análise, evidências, depoimento, case, curadoria e OCI | Não executado |
| DEMO-02 | Projeto de destaque | Participação, resultados comprovados, dois ativos, curadoria e OCI | Não executado |
| DEMO-03 | Superação | Fidelidade aos fatos, dois ativos, curadoria e OCI | Não executado |

### 6.1 Condições de aprovação

Cada demonstração deverá:

1. Utilizar entradas identificadas.
2. Preservar autores e fontes.
3. Apresentar evidências verificáveis.
4. Produzir depoimento estruturado.
5. Produzir case de sucesso.
6. Permitir curadoria humana.
7. Comprovar persistência e recuperação real.
8. Não inventar informações.

### 6.2 Restrição da sessão preliminar

As três histórias demonstrativas apresentadas após a importação do CSV de duas interações não constituem comprovação das três demonstrações obrigatórias.

Da mesma forma, as três histórias geradas no teste direto posterior do Gemini não comprovam, isoladamente, os fluxos completos de demonstração.

---

## 7. Controles transversais de qualidade e curadoria

### 7.1 RG-01 — Fidelidade factual

A regeneração não poderá alterar:

- Nomes.
- Números.
- Resultados.
- Fatos.
- Evidências.

Alterações somente poderão ocorrer quando sustentadas pelas fontes.

### 7.2 RG-02 — Contradições

Contradições não resolvidas devem impedir a aprovação quando o controle for aplicável.

A regra deve ser testada na lógica e na interface.

### 7.3 RG-03 — Liberação para publicação

A liberação deve depender de:

1. Validação factual.
2. Aprovação editorial.
3. Autorização apropriada.

Esses controles são independentes.

### 7.4 Rastreabilidade

- Citações literais.
- IDs de origem verificáveis.
- Autores correspondentes às entradas.
- Ausência de atribuição indevida.
- Separação entre resultados reais e demonstrativos.

### 7.5 Riscos adicionais

**Fallback mock:** conteúdo demonstrativo não pode ser apresentado como análise real.

**Estado entre lotes:** uma nova importação deve reinicializar histórias, curadoria e referências do lote anterior.

**Mensagens de sucesso:** progresso visual não substitui confirmação real de processamento e armazenamento.

**Tratamento de falhas:** erros precisam ser identificáveis e permitir diagnóstico.

**Teste isolado:** resultado positivo do serviço Gemini não equivale a aprovação do pipeline completo.

---

## 8. Comprovação da OCI Object Storage

| Controle | Evidência necessária | Situação |
|---|---|---|
| Conectividade | Região e bucket configurados | Não verificado |
| Gravação | Chave de objeto e confirmação real | Não verificado |
| Recuperação | Objeto recuperado com integridade | Não verificado |
| Idempotência | Ausência de duplicidade indevida | Não verificado |
| Histórias e ativos | Conteúdo efetivamente persistido | Não verificado |
| Curadoria | Decisões persistidas e recuperadas | Não verificado |
| Falha controlada | Erro não apresentado como sucesso | Não verificado |
| Bucket vazio | Tratamento correto do catálogo | Não verificado |
| Segurança | Logs sem credenciais e segredos | Não verificado |

### 8.1 Histórico técnico

O PR #20 registrou correções de persistência e status do processamento, posteriormente integradas à `main`.

A revisão técnica relatou testes de gravação real.

Entretanto, essas informações não comprovam a execução integrada do fluxo completo no ambiente de homologação.

### 8.2 Diagnóstico do bucket vazio

Segundo Jaqueline, o catálogo de arquivos depende de `listar_pacotes`.

Quando o bucket está vazio, a aplicação pode apresentar erro mesmo havendo histórias disponíveis.

**Situação:** diagnóstico registrado; correção e reteste ainda não comprovados.

### 8.3 Responsabilidade técnica

**Responsável de referência pela frente OCI:** Jaqueline de Lira.

A atribuição foi esclarecida em comentário posterior na Issue #27.

Luciene Godoy poderá colaborar nas atividades de integração e orquestração, conforme alinhamento entre as integrantes.

### 8.4 Critérios para reteste OCI

O reteste deverá comprovar:

1. Credenciais válidas em ambiente autorizado.
2. Bucket e região corretos.
3. Gravação real.
4. Recuperação real.
5. Integridade dos dados.
6. Correspondência com o lote.
7. Idempotência.
8. Persistência da curadoria.
9. Tratamento de falhas.
10. Comportamento com bucket vazio.
11. Mensagens de interface consistentes.
12. Ausência de exposição de credenciais.

**Status:** pendente de execução integrada e evidências.

---

## 9. Defeitos, riscos e impedimentos

### 9.1 Issue #27

**Título:** Corrigir inconsistências na análise Gemini, fallback mock e persistência OCI.

**Data:** 29/10/2026  
**Prioridade:** Urgente  
**Situação:** Aberta  
**Reteste:** Pendente

**Referência:** https://github.com/No-Country-simulation/G10-Brasil-Equipe-18/issues/27

### 9.2 Impedimentos históricos incorporados do PR #26

#### IMP-001 — Gemini não configurado no ambiente local

O terminal indicou ausência de `GEMINI_API_KEY` em uma execução anterior, com fallback mock.

**Situação:** impedimento histórico; o teste direto posterior confirmou execução real do Gemini em outro contexto, sem comprovar a configuração integrada do Streamlit.

#### IMP-002 — Histórias demonstrativas após importação CSV

Duas interações foram importadas, mas três histórias fictícias foram apresentadas.

**Situação:** observação histórica associada ao commit `9fcb06e`. Requer reteste na versão atual.

#### IMP-003 — Persistência OCI e confirmação visual

A sessão local não comprovou gravação real.

O PR #20 registrou correções e testes técnicos posteriormente.

**Situação:** integração informada; homologação do fluxo completo pendente.

#### IMP-004 — Fluxo integrado de ponta a ponta

Importação CSV observada, porém análise real e persistência não comprovadas na sessão.

**Situação:** pendente de reteste integrado.

#### IMP-005 — Bucket OCI vazio

Problema relatado no catálogo de pacotes.

**Situação:** correção ainda não confirmada. Responsabilidade técnica de referência: Jaqueline.

### 9.3 Diagnóstico atualizado da Issue #27

**Defeito 1 — Tratamento de falhas Gemini**

Falhas 503/timeout podem acionar fallback mock sem tentativas adicionais ou modelo secundário.

**Defeito 2 — Mensagens de conclusão**

O fluxo precisa distinguir conclusão visual de processamento efetivamente confirmado.

**Defeito 3 — Persistência OCI**

A gravação e recuperação precisam ser comprovadas antes de informar sucesso.

**Defeito 4 — Estado entre lotes**

Histórias e curadoria não são adequadamente reinicializadas em `_novo_lote`, conforme análise técnica da Jaqueline.

**Defeito 5 — Correspondência entre entrada e saída**

A divergência foi observada na sessão histórica. O teste direto posterior do Gemini apresentou correspondência correta dos autores.

**Defeito 6 — Bucket vazio**

O catálogo pode falhar quando não existem objetos no bucket.

### 9.4 Critérios mínimos de correção

- Identificar explicitamente resultados reais e demonstrativos.
- Não informar análise real concluída quando a chamada Gemini falhar.
- Implementar e testar recuperação de falhas 503/timeout.
- Verificar modelo secundário conforme solução adotada.
- Evitar substituição silenciosa por conteúdo fictício.
- Confirmar persistência real antes de informar sucesso.
- Tratar bucket vazio.
- Reinicializar histórias e curadoria em novo lote.
- Preservar correspondência entre entradas e resultados.
- Documentar retestes com commit e ambiente.
- Registrar evidências suficientes para avaliação dos CATP.

### 9.5 Responsabilidades técnicas de referência

| Frente | Responsável | Encaminhamento |
|---|---|---|
| Interface Streamlit | Tissiany Delmiro | Mensagens, navegação e estado |
| Gemini e análise LLM | Jaqueline de Lira | Falhas, tentativas, fallback e rastreabilidade |
| Persistência OCI | Jaqueline de Lira | Bucket vazio, gravação e recuperação |
| Apoio de integração e orquestração | Luciene Godoy | Colaboração conforme alinhamento |
| Testes integrados | Ketlyn Barbosa | Execução e evidências |
| Gestão e aceite | Marcus | Acompanhamento e decisão formal |

**Nota:** as atribuições representam referências de acompanhamento. A distribuição detalhada de tarefas deverá ser confirmada com as integrantes.

A responsabilidade principal pela persistência OCI foi retificada por Jaqueline na Issue #27.

### 9.6 Riscos a acompanhar

- Instabilidade do provedor LLM.
- Uso indevido de fallback mock.
- Credenciais e configuração OCI.
- Persistência não confirmada.
- Falhas com bucket vazio.
- Perda de rastreabilidade.
- Mistura de resultados entre lotes.
- Divergência entre testes unitários e integração.
- Diferenças entre commits e branches.
- Aprovação baseada apenas em mensagens visuais.
- Falta de evidências formais.

---

## 10. Registro de decisões de escopo

| ID | Tema | Situação | Decisão |
|---|---|---|---|
| DEC-001 | CATP-012 — CQF Score 0–100 | Proposta de transferência para fase posterior | Pendente |
| DEC-002 | Aviso global, KPIs e origem dos dados | Escopo e prioridade a confirmar | Pendente |
| DEC-003 | Fallback mock | Exigir identificação clara de conteúdo demonstrativo | Correção pendente |
| DEC-004 | Sucesso OCI | Exigir confirmação real de persistência | Validação pendente |
| DEC-005 | Estado entre lotes | Reinicializar histórias e curadoria | Correção pendente |
| DEC-006 | Tratamento de falhas Gemini | Testar tentativas e recuperação | Correção pendente |

### 10.1 Regra para decisões pendentes

Nenhum requisito poderá ser considerado aprovado ou excluído sem decisão formal.

Para transferência de escopo, registrar:

- Justificativa.
- Responsável.
- Data.
- Aprovação.
- Evidência.
- Fase de destino.

O CATP-012 permanece **Não executado**, com aplicabilidade **Pendente de decisão**.

---

## 11. Resumo executivo de homologação

| Indicador | Resultado atual |
|---|---|
| Casos CATP formalmente aprovados | 0 comprovados neste relatório |
| Casos CATP formalmente reprovados | 0 registrados |
| Casos com execução formal e evidência completa | 0 registrados |
| Verificações locais preliminares | Registradas em 29/10/2026 |
| Importação CSV | Prévia de duas interações verificada |
| Gemini real | Teste direto positivo informado por Jaqueline |
| Gemini integrado ao Streamlit | Não homologado |
| Fallback mock | Observado na sessão histórica |
| Rastreabilidade | Positiva no teste direto; integração pendente |
| Persistência OCI | Não homologada |
| Bucket vazio | Correção não confirmada |
| Estado entre lotes | Correção pendente |
| Seis cenários integrados | Aguardando execução formal |
| Três demonstrações obrigatórias | Sem evidência formal completa |
| Issue #27 | Aberta |
| CATP-012 | Decisão de escopo pendente |
| Aceite do MVP | Não concedido |

> Os indicadores refletem as evidências formalmente registradas neste documento. Não significam que a equipe jamais tenha realizado outros testes técnicos.

### 11.1 Avaliação do Project Manager

A sessão histórica associada ao commit `9fcb06e` identificou problemas de confiabilidade na apresentação de resultados após falhas do Gemini.

Posteriormente, Jaqueline informou teste direto bem-sucedido na `main`, com três histórias reais e autores correspondentes às entradas.

Essa evidência demonstra avanço técnico, mas não comprova o funcionamento integrado de Streamlit, Gemini e OCI.

Persistem pendências relativas a:

- Recuperação de falhas do Gemini.
- Reinicialização entre lotes.
- Tratamento do bucket vazio.
- Persistência e recuperação real.
- Execução dos testes CATP.
- Consolidação das evidências.

**Recomendação:** manter o aceite do MVP pendente até a conclusão das correções e da homologação formal.

---

## 12. Checklist de encerramento do Card 23

- [ ] Executar e documentar os CATP aplicáveis.
- [ ] Mapear os seis cenários integrados.
- [ ] Executar os seis cenários.
- [ ] Demonstrar conquista profissional.
- [ ] Demonstrar projeto de destaque.
- [ ] Demonstrar superação.
- [ ] Gerar depoimento estruturado em cada demonstração.
- [ ] Gerar case de sucesso em cada demonstração.
- [ ] Validar citações literais e IDs.
- [ ] Confirmar fidelidade factual.
- [ ] Verificar curadoria humana.
- [ ] Verificar autorização independente.
- [ ] Comprovar gravação OCI.
- [ ] Comprovar recuperação OCI.
- [ ] Verificar idempotência.
- [ ] Testar bucket vazio.
- [ ] Testar falhas controladas.
- [ ] Testar dados inválidos.
- [ ] Corrigir defeitos impeditivos.
- [ ] Realizar retestes.
- [ ] Consolidar evidências.
- [ ] Registrar decisões de escopo.
- [ ] Emitir parecer técnico conclusivo.
- [ ] Obter decisão expressa de aceite.

### 12.1 Atividades preliminares realizadas

- [x] Inspecionar o fluxo local de importação CSV.
- [x] Registrar a prévia das interações.
- [x] Identificar falha Gemini na sessão histórica.
- [x] Identificar fallback mock.
- [x] Registrar divergência histórica entre autores.
- [x] Inspecionar mensagens de conclusão e persistência.
- [x] Abrir a Issue #27.
- [x] Comunicar o impedimento à equipe.
- [x] Receber esclarecimentos técnicos de Jaqueline.
- [x] Registrar evidência do teste direto positivo do Gemini.
- [x] Distinguir o commit histórico da referência posterior.
- [x] Corrigir documentalmente a responsabilidade OCI.
- [ ] Obter correções técnicas confirmadas.
- [ ] Executar retestes integrados.
- [ ] Consolidar evidências formais.
- [ ] Atualizar a matriz CATP após execução.
- [ ] Emitir parecer conclusivo.
- [ ] Deliberar sobre o aceite.

**Importante:** as atividades preliminares concluídas não representam aprovação dos requisitos de aceitação.

---

## 13. Parecer técnico e decisão final

### 13.1 Parecer técnico preliminar — 29/10/2026

A sessão Streamlit associada ao commit histórico `9fcb06e` apresentou falhas de análise real, acionamento de fallback mock e histórias demonstrativas sem correspondência com as entradas utilizadas.

A análise posterior de Jaqueline esclareceu que esse commit antecedia integrações relevantes dos PRs #20 e #21.

Em teste direto posterior na `main`, Jaqueline informou geração real de três histórias pelo Gemini, com autores preservados e sem fallback mock.

Esse teste não incluiu a interface Streamlit nem a persistência OCI.

Também foram identificadas pendências relacionadas a tentativas de recuperação de falhas, estado entre lotes e comportamento com bucket OCI vazio.

Portanto, **não existem evidências suficientes neste relatório para homologar o pipeline integrado completo**.

### 13.2 Parecer técnico conclusivo

**PENDENTE.**

Inserir após:

- Conclusão das correções.
- Execução formal dos testes.
- Registro dos resultados.
- Consolidação das evidências.
- Avaliação dos defeitos remanescentes.

### 13.3 Decisão do Project Manager

**PENDENTE — NÃO HÁ APROVAÇÃO ANTECIPADA DO MVP.**

**Data do aceite ou rejeição:** A preencher.

**Commit/versão objeto da decisão:** A preencher.

**Evidências consultadas:** A consolidar.

**Justificativa e ressalvas:** A preencher.

### 13.4 Condições para emissão do aceite

O aceite somente poderá ser considerado após:

1. Correção ou tratamento formal dos defeitos impeditivos.
2. Reteste dos casos afetados pela Issue #27.
3. Comprovação da análise real integrada.
4. Comprovação de rastreabilidade das fontes.
5. Comprovação de persistência e recuperação OCI.
6. Verificação de estado entre lotes.
7. Verificação dos controles de curadoria e autorização.
8. Conclusão dos seis cenários integrados.
9. Conclusão das três demonstrações obrigatórias.
10. Registro de evidências vinculadas ao commit homologado.
11. Resolução das decisões de escopo.
12. Parecer técnico fundamentado.
13. Decisão expressa do Project Manager.

**SITUAÇÃO FINAL DA VERSÃO 0.4: HOMOLOGAÇÃO PENDENTE — SEM ACEITE DO MVP.**

---

## Referências

- CATP v1.1 — `docs/CATP_TEST_PLAN.md`
- Card 23 — Testes Integrados e Demonstração
- CQF v1.0
- Issue #27 — https://github.com/No-Country-simulation/G10-Brasil-Equipe-18/issues/27
- PR #20 — Persistência OCI
- PR #21 — Streamlit Secrets
- PR #26 — https://github.com/No-Country-simulation/G10-Brasil-Equipe-18/pull/26
- PR #28 — https://github.com/No-Country-simulation/G10-Brasil-Equipe-18/pull/28
- PR #29 — https://github.com/No-Country-simulation/G10-Brasil-Equipe-18/pull/29
- Commit histórico da sessão Streamlit — `9fcb06e`
- Referência posterior de integração na `main` — `2b65357`
- Arquivo CSV preliminar — `data/samples/teste_importacao_catp001.csv`
- Arquivo JSON do teste direto — `data/samples/teste_recuperacao.json`
- Comentário técnico de Jaqueline — https://github.com/No-Country-simulation/G10-Brasil-Equipe-18/issues/27#issuecomment-6501535223
- Retificação de responsabilidade OCI — https://github.com/No-Country-simulation/G10-Brasil-Equipe-18/issues/27#issuecomment-6503962505

---

**Nota final:** este documento é um instrumento de gestão da homologação. Não altera o CATP aprovado, não substitui testes de aceitação e não concede aprovação automática ao MVP.
