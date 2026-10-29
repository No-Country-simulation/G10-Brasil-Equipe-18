# CommunityLab — Relatório de Homologação e Aceite do MVP

**Projeto:** CommunityLab — Detector Inteligente de Histórias de Sucesso e Testemunhos
**Hackathon:** ONE G10 — Equipe 18
**Documento:** `COMMUNITYLAB_HOMOLOGACAO_MVP.md`
**Versão:** 0.3 — Consolidação documental dos PRs #26 e #28 (não constitui aceite)
**Data de preparação:** 26/10/2026
**Última atualização:** 29/10/2026
**Referência funcional:** `docs/CATP_TEST_PLAN.md` — CATP v1.1
**Referência de gestão:** Card 23 — Testes Integrados e Demonstração
**Responsável funcional e consolidação:** Marcus — Project Manager
**Responsável principal pelos testes integrados (Card 23):** Ketlyn Barbosa
**Apoio técnico:** Tissiany Delmiro, Jaqueline de Lira e Luciene Godoy

**Status geral:** HOMOLOGAÇÃO PENDENTE — SEM ACEITE DO MVP

> **Regra de evidência:** nenhuma implementação declarada, commit integrado, teste unitário informado ou demonstração simulada constitui, isoladamente, aprovação de um caso de aceitação. A aprovação exige execução, observação e evidências vinculadas ao commit testado.

> **Nota da versão 0.3:** consolida os registros de integração e impedimentos de 28/10/2026 (PR #26) com as verificações locais preliminares de 29/10/2026 e a Issue #27 (PR #28). Os testes técnicos informados por integrantes não substituem homologação integrada, não comprovam por si só o fluxo Gemini–Streamlit–OCI e não constituem aceite do MVP.

---

## 1. Objetivo e escopo

Consolidar o planejamento, a execução, os resultados e as evidências da homologação integrada do MVP, desde a importação CSV/JSON, análise por IA e detecção de histórias até evidências rastreáveis, geração de depoimentos estruturados e cases, curadoria humana e persistência/recuperação real no OCI Object Storage.

**Critérios essenciais:** fidelidade às fontes; identificação de evidências literais e IDs; ausência de fatos inventados; três casos demonstrativos (conquista profissional, projeto de destaque e superação); dois formatos principais de ativo (depoimento estruturado e case de sucesso); curadoria humana; separação entre aprovação editorial e autorização; persistência real OCI; ausência de defeitos críticos impeditivos.

**Fora de qualquer conclusão automática:** posts LinkedIn são complementares; painel analítico é opcional conforme Card 23. A pontuação CQF 0–100 (CATP-012) está **pendente de decisão formal de escopo**.

### 1.1 Objetivo da atualização de 29/10/2026

Registrar de forma rastreável as observações preliminares da execução local, identificar inconsistências no fluxo integrado e preservar a distinção entre:

- Funcionalidades observadas na interface.
- Funcionalidades efetivamente validadas.
- Processamento real por modelo de linguagem.
- Resultados demonstrativos ou mock.
- Persistência real na OCI.
- Mensagens de sucesso apresentadas pela interface.
- Testes ainda pendentes de execução formal.

Os resultados preliminares não autorizam a aprovação automática dos casos CATP.

---

## 2. Identificação do ambiente de homologação

| Campo | Registro |
|---|---|
| Data(s) de execução | 29/10/2026 — verificações locais preliminares |
| Executor(es) | Marcus — Project Manager, verificações funcionais locais |
| Ambiente e sistema operacional | Windows, VS Code, ambiente virtual Python `.venv` |
| Aplicação / URL | Streamlit local — `http://localhost:8501` |
| Branch | `docs/homologacao-mvp` |
| Commit de referência identificado | `9fcb06e` — `docs: adiciona relatório de homologação do MVP` |
| SHA completo | A registrar na execução formal |
| Versão do Streamlit e dependências | A confirmar |
| Provedor LLM / modo de execução | Gemini configurado; chamadas com falha e acionamento de fallback mock observados |
| OCI: região, bucket e identificadores não sensíveis | A confirmar em ambiente autorizado |
| Dados de teste / versão dos arquivos | `data/samples/teste_importacao_catp001.csv` — arquivo local de teste |
| Limitações do ambiente | Sem comprovação de processamento Gemini bem-sucedido ou persistência OCI real |
| Referência de defeito | GitHub Issue #27 |

**Commits informados pela equipe como incorporados à `main` (a confirmar na execução):** `b38595f`, `e29d1d6`, `095b04d`, `b323fd2`, `7959443`.

A presença desses commits não substitui o registro do SHA efetivamente homologado.

### 2.1 Atualização de integrações — 28/10/2026 (incorporada do PR #26)

- **PR #20 — Correção da persistência OCI e do status do processamento:** aprovado por Jaqueline e integrado à `main` (merge `a05ae6b`). Conforme o registro técnico do PR #26, a revisão informou teste de gravação real no bucket OCI, tratamento de falha simulada e reenvio sem repetir etapas de análise. **A homologação integrada permanece pendente.**
- **PR #21 — Suporte a credenciais OCI via Streamlit Secrets:** desenvolvido por Tissiany, aprovado por Jaqueline e integrado à `main` (merge `2b65357`). O suporte permite configurar credenciais OCI via Streamlit Secrets; a configuração e a execução integrada no ambiente de homologação ainda requerem validação.
- **Pendência de bucket vazio:** foi relatado comportamento problemático da aplicação com bucket OCI vazio, com correção prevista em PR separado. A integração dessa correção ainda não foi confirmada neste relatório.

**Nota de evidência:** o registro de merges e de testes técnicos não altera automaticamente os resultados CATP nem concede aceite ao MVP. A confirmação deve usar o SHA do ambiente efetivamente testado.

### 2.2 Limites da identificação do ambiente

A branch `docs/homologacao-mvp` foi utilizada para a verificação documental e funcional local.

O comando de verificação da pasta `app` não apresentou alterações locais rastreadas no momento da inspeção.

Isso não comprova, isoladamente, equivalência com a versão atual da branch `main`.

O commit `9fcb06e` é a referência identificada na sessão local. A homologação formal deverá registrar o SHA completo e confirmar a versão exata do código executado.

### 2.3 Arquivo CSV utilizado

Arquivo: `data/samples/teste_importacao_catp001.csv`

```csv
autor,canal,tipo,texto
membro_001,#conquistas-e-vagas,depoimento,Conquistei minha primeira vaga na área de IA!
membro_002,#duvidas-langgraph,pergunta_tecnica,Como estruturar nós condicionais no LangGraph?
```

**Observações:**

- Duas interações foram disponibilizadas.
- Dois canais distintos estavam presentes.
- A interface apresentou prévia das duas interações.
- A prévia foi observada, mas o processamento integrado não foi homologado.
- As histórias apresentadas posteriormente não corresponderam aos autores do CSV.

---

## 3. Estados e critérios de classificação

- **Implementação:** Disponível / Parcial / Não implementada / Não verificada.
- **Aplicabilidade:** Aplicável / Não aplicável (com justificativa e decisão formal) / Pendente de decisão.
- **Execução:** Não executado / Aprovado / Reprovado / Bloqueado.
- **Evidência:** link para print, log sanitizado, arquivo de saída, ID de interação, chave de objeto OCI ou relatório técnico.
- **Regra de aprovação:** resultado observado corresponde ao esperado, com evidência suficiente e rastreável.

### 3.1 Classificação das observações preliminares

**Verificação preliminar satisfatória:** comportamento específico observado, sem aprovação automática do caso CATP completo.

**Falha observada:** comportamento incompatível com o esperado, que deverá ser formalizado ou reproduzido no teste de aceitação.

**Não verificado:** ausência de evidência suficiente para concluir sucesso ou falha.

**Bloqueio de homologação:** condição que impede comprovar o requisito obrigatório.

**Teste formal aprovado:** somente após execução documentada com ambiente, commit, entradas, resultados e evidências.

### 3.2 Regra para os testes de 29/10/2026

Os testes locais preliminares serão registrados como observações técnicas. A matriz formal somente receberá o estado **Aprovado** quando houver evidências suficientes e confirmação do ambiente e commit testados.

O estado **Não executado** não significa ausência absoluta de qualquer verificação anterior.

---

## 4. Matriz mestre de aceitação — CATP v1.1

A matriz abaixo mantém a situação formal de homologação, acrescentando referências às verificações preliminares quando aplicável.

| ID | Funcionalidade / verificação | Resultado esperado (síntese) | Aplicabilidade | Execução formal | Evidência / observação |
|---|---|---|---|---|---|
| CATP-001 | Importação CSV | Arquivo válido processado | Aplicável | Não executado | Prévia de duas interações verificada; fluxo completo pendente |
| CATP-002 | Importação JSON | Dados válidos importados | Aplicável | Não executado | — |
| CATP-003 | Dados inválidos | Erro tratado e informado | Aplicável | Não executado | — |
| CATP-004 | Sentimentos | Resultado associado à interação original | Aplicável | Não executado | — |
| CATP-005 | Tópicos | Tópicos identificados e rastreáveis | Aplicável | Não executado | — |
| CATP-006 | Histórias | Histórias relevantes identificadas sem ficção em resultados vazios | Aplicável | Não executado | Falha preliminar: histórias mock após falha Gemini; Issue #27 |
| CATP-007 | Rastreabilidade | Citação literal vinculada ao ID original | Aplicável | Não executado | Divergência de autores observada; requer reteste |
| CATP-008 | Depoimentos | Depoimento estruturado fiel à fonte | Aplicável | Não executado | — |
| CATP-009 | Cases | Case estruturado sem fatos inventados | Aplicável | Não executado | — |
| CATP-010 | Curadoria humana | Quatro subcasos aplicáveis aprovados | Aplicável | Não executado | — |
| CATP-010a | Validação factual | Pendente / Validada / Insuficiente / Contradição | Aplicável | Não executado | — |
| CATP-010b | Curadoria editorial | Rascunho / Ajustes / Aprovado / Rejeitado | Aplicável | Não executado | — |
| CATP-010c | Autorização | Não registrada / Registrada, independente do editorial | Aplicável | Não executado | — |
| CATP-010d | Indicador RG-03 | Liberação condicionada aos requisitos aplicáveis | Aplicável | Não executado | — |
| CATP-011 | OCI e idempotência | Gravação e recuperação reais, sem duplicação do mesmo lote | Aplicável | Não executado | Persistência real não comprovada; Issue #27 |
| CATP-012 | CQF Score 0–100 | Pontuação conforme CQF se integrada ao MVP | Pendente de decisão | Não executado | Decisão de escopo pendente |
| CATP-013 | CQF contradições | Contradição não resolvida impede aprovação, se integrada | A confirmar | Não executado | — |
| CATP-014 | Autorização | Divulgação bloqueada sem autorização apropriada | Aplicável | Não executado | — |
| CATP-015 | Fluxo completo | Pipeline integrado executado com sucesso | Aplicável | Não executado | Falha preliminar Gemini e fallback; Issue #27 |
| CATP-016 | Navegação Streamlit | Navegação entre seis módulos previstos | Aplicável | Não executado | Navegação parcialmente observada |
| CATP-017 | Estúdio | Fontes e conteúdo exibidos lado a lado | Aplicável | Não executado | — |
| CATP-018 | Regeneração RG-01 | Preserva fatos e não inventa informações | Aplicável | Não executado | — |
| CATP-019 | Curadoria — controles | Três controles independentes funcionam | Aplicável | Não executado | — |
| CATP-020 | Contradição RG-02 | Interface bloqueia aprovação de contradição não resolvida | Aplicável | Não executado | — |
| CATP-021 | Indicador RG-03 | Indicador corresponde às condições reais | Aplicável | Não executado | — |
| CATP-022 | Ajustes editoriais | Observações vinculadas ao conteúdo | Aplicável | Não executado | — |
| CATP-023 | Modo demonstração | Dados fictícios e resultados simulados explicitamente identificados | Aplicável | Não executado | Falha preliminar na indicação de sucesso; Issue #27 |

**Nota de integridade:** CATP-010 é um caso agregador e somente será aprovado após os quatro subcasos aplicáveis. A matriz contém 23 casos numerados principais e quatro subcasos adicionais.

### 4.1 Síntese dos testes locais preliminares

| CATP | Observação | Conclusão preliminar |
|---|---|---|
| CATP-001 | CSV de duas interações apresentado corretamente na prévia | Prévia verificada; aprovação integral pendente |
| CATP-006 | Após falha Gemini, foram apresentadas histórias demonstrativas | Falha observada |
| CATP-007 | Autores das histórias não correspondiam aos autores do arquivo importado | Rastreabilidade não demonstrada |
| CATP-011 | Interface apresentou mensagem de salvamento, sem confirmação de persistência real | Não verificado |
| CATP-015 | Pipeline apresentou conclusão visual apesar da falha de análise real | Falha observada |
| CATP-016 | Navegação local parcialmente observada | Verificação parcial |
| CATP-023 | Resultados mock apareceram no fluxo com indicação de conclusão | Falha observada |

**Decisão:** não aprovar esses casos com base exclusivamente nas verificações preliminares.

### 4.2 Observação sobre os resultados demonstrativos

O CSV utilizado possuía os autores `membro_001` e `membro_002`.

Após a execução, a aplicação apresentou histórias demonstrativas associadas a Marina Costa, Lucas Almeida e Camila Santos.

Essa divergência indica que os resultados exibidos não demonstram análise rastreável das duas interações importadas. O comportamento deve ser corrigido e submetido a reteste.

---

## 5. Registro dos seis cenários de homologação integrada

A Tissiany informou que executará os **seis arquivos de teste preparados anteriormente**. Seus nomes, conteúdos e resultados **não foram fornecidos neste relatório**; preencher os identificadores reais antes da execução, sem presumir correspondência entre arquivo e cenário.

| Cenário | Arquivo / versão | Objetivo / CATP cobertos | Esperado | Observado | Execução | Evidências / defeitos |
|---|---|---|---|---|---|---|
| HINT-01 | A preencher | A mapear | A preencher | A preencher | Não executado | — |
| HINT-02 | A preencher | A mapear | A preencher | A preencher | Não executado | — |
| HINT-03 | A preencher | A mapear | A preencher | A preencher | Não executado | — |
| HINT-04 | A preencher | A mapear | A preencher | A preencher | Não executado | — |
| HINT-05 | A preencher | A mapear | A preencher | A preencher | Não executado | — |
| HINT-06 | A preencher | A mapear | A preencher | A preencher | Não executado | — |

**Atenção especial:** registrar explicitamente o cenário de **citação negativa**, IDs duplicados, IDs inválidos e impossibilidade de conferência, quando presentes nos arquivos reais.

Uma evidência sem origem localizada não poderá ser validada automaticamente; o estado neutro informado pela equipe é **“Conferência indisponível”**.

### 5.1 Execução local preliminar — 29/10/2026

**Identificador:** PRELIM-20261029-01  
**Responsável:** Marcus — Project Manager  
**Ambiente:** Streamlit local  
**Branch:** `docs/homologacao-mvp`  
**Commit de referência:** `9fcb06e`  
**Arquivo:** `data/samples/teste_importacao_catp001.csv`  
**Tipo:** Verificação funcional preliminar, não equivalente a cenário HINT formal.

**Passos observados:**

1. Disponibilização de arquivo CSV contendo duas interações.
2. Visualização da prévia de importação.
3. Acionamento de importação e processamento.
4. Exibição de progresso visual.
5. Apresentação de histórias e ativos.
6. Inspeção das mensagens do terminal e comportamento do fluxo.

**Resultado esperado:**

- Importação correta das duas interações.
- Processamento real quando configurado para Gemini.
- Falhas explicitamente identificadas.
- Ausência de substituição silenciosa por histórias fictícias.
- Evidências vinculadas aos autores e textos originais.
- Persistência OCI somente declarada após confirmação real.

**Resultado observado:**

- Prévia das duas interações apresentada.
- Progresso visual concluído.
- Falha de chamada Gemini observada.
- Acionamento de fallback mock.
- Exibição de histórias demonstrativas sem correspondência com os autores do CSV.
- Indicação visual de conclusão e salvamento sem comprovação suficiente de processamento real e persistência OCI.

**Conclusão:** fluxo integrado não homologado.

**Defeito vinculado:** Issue #27.

### 5.2 Modelo de registro individual

Copiar para cada execução formal:

```text
ID do teste / cenário:
Data e responsável:
Ambiente / branch / SHA:
Arquivo e versão / ID de lote:
Pré-condições:
Passos realizados:
Resultado esperado:
Resultado observado:
Implementação (disponível/parcial/não implementada/não verificada):
Aplicabilidade e justificativa:
Execução (aprovado/reprovado/bloqueado/não executado):
Evidências (links, prints, logs sanitizados, IDs):
Defeito vinculado / gravidade:
Reteste e conclusão:
```

---

## 6. Três demonstrações obrigatórias

| ID | História | Verificações mínimas | Execução | Evidências |
|---|---|---|---|---|
| DEMO-01 | Conquista profissional | Entrada, análise, fatos e citações, depoimento + case, curadoria, OCI | Não executado | — |
| DEMO-02 | Projeto de destaque | Participação e resultados somente quando informados; dois ativos, rastreabilidade, curadoria, OCI | Não executado | — |
| DEMO-03 | Superação | Dificuldades e conquistas fiéis à fonte, sem dramatização, dois ativos, curadoria, OCI | Não executado | — |

**Condição:** cada caso deve produzir os dois formatos principais, permitir verificação das fontes e passar pelas etapas aplicáveis do fluxo real.

Demonstração mock deve ser identificada e não prova LLM/OCI reais.

### 6.1 Restrição identificada na execução preliminar

As três histórias apresentadas após a importação do CSV de duas interações não constituem comprovação das três demonstrações obrigatórias.

Para aprovação, cada demonstração deverá utilizar entradas identificadas, apresentar evidências verificáveis e comprovar as etapas reais do pipeline.

---

## 7. Controles transversais de qualidade e curadoria

- **RG-01:** regeneração não altera nomes, números, fatos ou resultados sem evidência.
- **RG-02:** contradição não resolvida impede aprovação; testar lógica e interface.
- **RG-03:** liberação para publicação exige validação factual, aprovação editorial e autorização apropriada, sem transições automáticas entre controles.
- **Citações:** correspondência literal, ID de origem verificável, sem atribuição a terceiros.
- **Origem dos dados:** exemplos demonstrativos e histórias mock explicitamente diferenciados de análises reais.
- **Casos negativos:** nenhuma história artificial a partir de interações irrelevantes; nenhuma aprovação automática por ausência de origem ou por falha de persistência.

**Registro dos controles:** a preencher com os CATP correspondentes e evidências.

### 7.1 Riscos adicionais identificados

**Fallback mock:** o sistema não deve apresentar conteúdo demonstrativo como resultado efetivo de análise Gemini.

**Estado entre lotes:** uma nova importação deve invalidar ou reinicializar adequadamente resultados, histórias, curadoria e referências de persistência do lote anterior.

**Rastreabilidade:** histórias e ativos devem estar associados às interações efetivamente importadas.

**Mensagens de sucesso:** conclusão visual de etapas não substitui confirmação de processamento e armazenamento.

**Transparência:** falhas devem permitir diagnóstico e recuperação, sem induzir o usuário a acreditar que o processamento real foi concluído.

---

## 8. Comprovação da OCI Object Storage

| Controle | Evidência necessária | Situação |
|---|---|---|
| Conectividade e destino | Região, bucket e chave não sensíveis | Não verificado |
| Gravação | Identificador de lote, chave do objeto e confirmação real | Não verificado |
| Recuperação | Objeto recuperado e conteúdo íntegro | Não verificado |
| Idempotência | Duas gravações do mesmo lote, listagem e contagem sem duplicidade | Não verificado |
| Ativos e evidências | Histórias, citações, depoimentos e cases persistidos | Não verificado |
| Curadoria | Decisões persistidas e recuperadas após reinício | Não verificado |
| Falha controlada | Erro de persistência não apresentado como sucesso | Não verificado |
| Segurança | Logs e prints sem credenciais, tokens ou dados pessoais | Não verificado |

**Limitação conhecida:** a correção de status de persistência da PR #20 foi testada localmente sem credenciais OCI; a persistência real requer execução integrada com acesso autorizado.

**Atualização documental de 28/10:** o PR #26 registra que o PR #20 foi revisado e integrado à `main` (merge `a05ae6b`). Essa informação não comprova, isoladamente, a persistência OCI no ambiente local de 29/10 nem a homologação de ponta a ponta.

### 8.1 Observação técnica da execução preliminar

A inspeção do serviço de dados indicou a existência de mecanismos para registrar estados de persistência, incluindo distinção entre operação real e simulada.

Entretanto, a interface de processamento apresentou mensagem de salvamento associada ao progresso visual, sem comprovação de que todos os objetos haviam sido efetivamente gravados.

**Conclusão:** a mensagem de sucesso não constitui evidência de persistência real.

### 8.2 Critérios para reteste OCI

O reteste deverá comprovar:

1. Credenciais válidas em ambiente autorizado, sem divulgação de segredos.
2. Bucket e região corretamente configurados.
3. Gravação real de objetos.
4. Recuperação dos objetos gravados.
5. Integridade e correspondência com o lote original.
6. Idempotência quando exigida.
7. Persistência e recuperação das decisões de curadoria.
8. Tratamento correto de falhas.
9. Mensagens de interface compatíveis com o resultado real.

**Status:** pendente de execução e evidências.

---

## 9. Defeitos, riscos e impedimentos

| ID | Data | Descrição | Gravidade | Responsável | Referência | Situação | Reteste |
|---|---|---|---|---|---|---|---|
| Issue #27 | 29/10/2026 | Inconsistências na análise Gemini, fallback mock, mensagens de conclusão, estado entre lotes e persistência OCI | Urgente | A distribuir tecnicamente pela equipe | GitHub Issue #27 | Aberta | Pendente |

**Referência:** https://github.com/No-Country-simulation/G10-Brasil-Equipe-18/issues/27

### 9.1 Impedimentos identificados na verificação local — 28/10/2026 (incorporados do PR #26)

**IMP-001 — Gemini não configurado no ambiente local**

- **Evidência registrada:** o terminal indicou ausência da variável `GEMINI_API_KEY` e acionamento do fallback mock naquele ambiente.
- **Impacto:** análise real por LLM não comprovada naquela execução.
- **Situação registrada em 28/10:** pendente de configuração segura e reteste. A verificação de 29/10 também observou falha Gemini e fallback, sem comprovar sucesso integrado; a configuração pode diferir entre ambientes.

**IMP-002 — Histórias demonstrativas após importação CSV**

- **Evidência registrada:** foram importadas duas interações (`membro_001` e `membro_002`), mas a interface exibiu três histórias fictícias predefinidas.
- **Causa observada no código:** fallback para `m.HISTORIAS` quando a análise LLM falha.
- **Impacto:** CATP-006 e rastreabilidade da análise real não comprovados.
- **Situação:** pendente de correção e reteste com Gemini funcional; relacionado à Issue #27.

**IMP-003 — Persistência OCI e confirmação visual**

- **Evidência registrada:** o teste local anterior não comprovou gravação real. Posteriormente, o registro de revisão técnica do PR #20 informou gravação em bucket real, tratamento de falhas e retry.
- **Situação:** correção integrada à `main`; homologação do fluxo no ambiente de referência ainda pendente. O relato técnico do PR #20 não deve ser confundido com comprovação de persistência na sessão local de 29/10.

**IMP-004 — Fluxo integrado de ponta a ponta**

- **Evidência registrada:** importação CSV observada, porém análise executada em mock no teste local.
- **Impacto:** CATP-015 ainda não comprovado.
- **Situação:** pendente de execução integrada e registro de evidências.

**IMP-005 — Comportamento com bucket OCI vazio**

- **Evidência registrada:** problema relatado na revisão do PR #20, relacionado ao uso de `svc.listar_pacotes()` em `state.py`.
- **Situação:** correção prevista em PR separado; integração ainda não confirmada. A frente OCI está em alinhamento com Luciene.

**Nota de homologação:** estes impedimentos preservam o histórico de 28/10 e devem ser reconciliados com a Issue #27 e com os retestes posteriores. Não alteram automaticamente a matriz CATP nem constituem aceite.

### 9.2 Detalhamento da Issue #27

**Defeito 1 — Fallback mock após falha Gemini**

O serviço de análise aciona conteúdo demonstrativo após exceções na chamada Gemini. O comportamento não deve ser interpretado como análise real das interações.

**Defeito 2 — Conclusão visual antecipada**

O progresso da interface pode indicar etapas concluídas antes da confirmação efetiva dos resultados de análise e persistência.

**Defeito 3 — Persistência OCI não comprovada**

A interface pode apresentar mensagem de salvamento sem confirmação de persistência real.

**Defeito 4 — Estado entre importações**

O fluxo de nova importação exige verificação de reinicialização de histórias, resultados, estados de curadoria e referências do lote anterior.

**Defeito 5 — Divergência entre entrada e saída**

O CSV com duas interações apresentou três histórias demonstrativas com autores diferentes dos registros importados.

### 9.3 Critérios mínimos de correção

- Identificar explicitamente a origem real ou demonstrativa dos resultados.
- Não apresentar sucesso quando a chamada Gemini falhar.
- Não substituir silenciosamente resultados reais por histórias fictícias.
- Confirmar a persistência OCI antes de informar sucesso.
- Apresentar falhas e alternativas de recuperação.
- Reinicializar corretamente o estado de uma nova importação.
- Preservar correspondência entre lote, interações, histórias e evidências.
- Executar e documentar retestes dos casos CATP afetados.

### 9.4 Responsabilidades técnicas sugeridas

| Frente | Responsável de referência | Encaminhamento |
|---|---|---|
| Interface Streamlit e estado da aplicação | Tissiany Delmiro | Avaliar mensagens de sucesso, fallback e reinicialização |
| Integração Gemini e análise LLM | Jaqueline de Lira | Avaliar falhas, tratamento de exceções e origem das histórias |
| Persistência e orquestração OCI | Luciene Godoy | Verificar confirmação real de gravação e recuperação |
| Testes integrados | Ketlyn Barbosa | Executar retestes e consolidar evidências técnicas |
| Gestão e aceite | Marcus | Acompanhar defeito, riscos e decisão final |

A distribuição acima é uma proposta de coordenação, não uma confirmação de atribuição ou aceite individual de todas as tarefas. **Atualização de alinhamento em 29/10:** Luciene informou que o escopo OCI voltou à sua responsabilidade, incluindo persistência e cenário de bucket vazio. As demais atribuições devem ser confirmadas com as integrantes.

### 9.5 Riscos a acompanhar

- Integração LLM real.
- Credenciais e persistência OCI.
- Rastreabilidade das fontes.
- Controles independentes de curadoria.
- Divergências entre testes unitários e fluxo completo.
- Diferenças entre branch de desenvolvimento e `main`.
- Rotulagem incompleta de dados demonstrativos.
- Mistura de resultados entre lotes.
- Aprovação baseada exclusivamente em mensagens visuais de sucesso.

---

## 10. Registro de decisões de escopo

| ID | Tema | Proposta / situação | Decisão | Evidência / data |
|---|---|---|---|---|
| DEC-001 | CATP-012 — CQF Score 0–100 | Proposta de transferir a fase posterior, mantendo os controles obrigatórios de qualidade | Aguardando deliberação da equipe | A preencher |
| DEC-002 | Aviso global, KPIs e opção B de origem dos dados | Informados como entrega em PR separado | Escopo e prioridade a confirmar | A preencher |
| DEC-003 | Tratamento de fallback mock | Necessidade de diferenciar resultados reais e demonstrativos | Correção proposta na Issue #27; validação pendente | 29/10/2026 |
| DEC-004 | Critério de sucesso OCI | Exigir confirmação de persistência real antes de informar sucesso | Correção proposta na Issue #27; validação pendente | 29/10/2026 |

**Regra:** até decisão formal, o CATP-012 permanece documentado, **Não executado**, com aplicabilidade **Pendente de decisão**.

Se transferido, registrar justificativa, responsáveis, data, evidência de aprovação e fase de destino; não rotular como teste aprovado.

---

## 11. Resumo executivo de homologação

| Indicador | Resultado atual |
|---|---|
| Casos CATP aprovados formalmente | 0 comprovados neste relatório |
| Casos CATP reprovados formalmente | 0 registrados na matriz formal |
| Casos CATP executados formalmente com evidência completa | 0 registrados |
| Verificações locais preliminares | Realizadas em 29/10/2026 |
| Importação CSV | Prévia de duas interações verificada |
| Processamento Gemini real | Não homologado; falhas observadas |
| Fallback mock | Acionamento observado |
| Rastreabilidade das histórias | Não comprovada; divergência observada |
| Persistência OCI real | Não verificada |
| Seis cenários integrados | Aguardando execução e relatório |
| Três demonstrações obrigatórias | Sem evidência formal registrada |
| Defeitos críticos ou impeditivos | Issue #27 aberta, prioridade urgente |
| CATP-012 | Aguardando decisão de escopo |
| Recomendação técnica | Não emitir aceite até concluir correções e homologação |
| Aceite do MVP | Não concedido / pendente |

> Os números de execução formal indicam ausência de evidências completas registradas neste documento, não provam que a equipe jamais tenha executado testes em outros ambientes.

### 11.1 Avaliação do Project Manager

As verificações preliminares identificaram comportamentos que comprometem a confiabilidade do fluxo integrado quando resultados demonstrativos são apresentados após falhas de processamento real.

O funcionamento visual da interface não é suficiente para comprovar a execução correta da análise Gemini, a rastreabilidade das histórias ou a persistência OCI.

A Issue #27 foi aberta para acompanhamento técnico.

**Recomendação:** manter o aceite do MVP suspenso até que os defeitos impeditivos sejam tratados, os retestes sejam documentados e os requisitos obrigatórios estejam comprovados.

---

## 12. Checklist de encerramento do Card 23

- [ ] Executar e documentar os testes CATP aplicáveis ao escopo aprovado.
- [ ] Mapear e registrar os seis cenários integrados e seus resultados.
- [ ] Demonstrar conquista profissional, projeto de destaque e superação.
- [ ] Comprovar depoimento estruturado e case de sucesso em cada demonstração.
- [ ] Validar citações literais e IDs das interações de origem.
- [ ] Confirmar fidelidade e ausência de fatos inventados.
- [ ] Verificar curadoria humana e independência da autorização de publicação.
- [ ] Comprovar gravação, recuperação e idempotência reais na OCI.
- [ ] Testar falhas controladas, dados inválidos e cenários negativos.
- [ ] Corrigir e retestar defeitos críticos impeditivos.
- [ ] Documentar bloqueios, limitações e decisões de escopo.
- [ ] Consolidar evidências, relatório e recomendação técnica.
- [ ] Obter decisão expressa de aceite do Project Manager.

### 12.1 Acompanhamento da execução preliminar

- [x] Inspecionar o fluxo local de importação CSV.
- [x] Registrar a prévia de duas interações.
- [x] Identificar falha Gemini e acionamento de fallback mock.
- [x] Identificar divergência entre autores importados e histórias exibidas.
- [x] Inspecionar a lógica de conclusão visual e persistência.
- [x] Registrar defeito na Issue #27.
- [x] Comunicar o impedimento à equipe.
- [ ] Obter correção técnica e revisão da Issue #27.
- [ ] Executar retestes integrados.
- [ ] Consolidar evidências formais.
- [ ] Atualizar a matriz CATP com os resultados comprovados.
- [ ] Emitir parecer técnico conclusivo.
- [ ] Deliberar sobre o aceite do MVP.

**Importante:** os itens marcados como concluídos nesta subseção representam atividades preliminares de investigação, não aprovação dos critérios de aceite.

---

## 13. Parecer técnico e decisão final

**Parecer técnico preliminar — 29/10/2026:**

As verificações locais identificaram falhas de confiabilidade na apresentação de resultados do fluxo integrado.

O acionamento de fallback mock após falha Gemini, a apresentação de histórias sem correspondência com o lote importado e a ausência de comprovação de persistência OCI impedem a homologação do pipeline completo.

A Issue #27 permanece como referência para correção e reteste.

**Parecer técnico conclusivo:** PENDENTE — inserir síntese da equipe após testes formais, limitações, defeitos e recomendação fundamentada.

**Decisão do Project Manager:** PENDENTE — **não há aprovação antecipada do MVP**.

**Data do aceite ou rejeição:** A preencher.

**Commit/versão objeto da decisão:** A preencher.

**Evidências consultadas:** A consolidar após os testes formais.

**Justificativa e ressalvas:** A preencher na deliberação final.

### 13.1 Condições para emissão do aceite

O aceite somente poderá ser considerado após:

1. Correção ou tratamento formal dos defeitos impeditivos.
2. Reteste dos casos afetados pela Issue #27.
3. Comprovação de análise real e rastreabilidade das fontes.
4. Comprovação de persistência e recuperação OCI.
5. Verificação dos controles de curadoria e autorização.
6. Conclusão dos cenários integrados e demonstrações obrigatórias.
7. Registro de evidências vinculadas ao commit homologado.
8. Resolução das decisões de escopo pendentes.
9. Parecer técnico fundamentado.
10. Decisão expressa do Project Manager.

**Situação final desta versão:** HOMOLOGAÇÃO PENDENTE — SEM ACEITE DO MVP.

---

## Referências

- CATP v1.1 — `docs/CATP_TEST_PLAN.md`
- Card 23 — Testes Integrados e Demonstração
- CQF v1.0
- GitHub Issue #27 — https://github.com/No-Country-simulation/G10-Brasil-Equipe-18/issues/27
- PR #26 — https://github.com/No-Country-simulation/G10-Brasil-Equipe-18/pull/26 (origem dos registros de 28/10)
- PR #28 — https://github.com/No-Country-simulation/G10-Brasil-Equipe-18/pull/28 (base da consolidação)
- Commit local de referência — `9fcb06e`
- Arquivo preliminar de teste — `data/samples/teste_importacao_catp001.csv`
- Resultados técnicos e evidências formais a anexar

Este relatório é um instrumento de gestão de homologação; não altera o CATP aprovado nem substitui os testes de aceitação.