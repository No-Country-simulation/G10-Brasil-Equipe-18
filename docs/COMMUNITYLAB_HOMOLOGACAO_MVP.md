# CommunityLab — Relatório de Homologação e Aceite do MVP

**Projeto:** CommunityLab — Detector Inteligente de Histórias de Sucesso e Testemunhos  
**Hackathon:** ONE G10 — Equipe 18  
**Documento:** COMMUNITYLAB_HOMOLOGACAO_MVP.md  
**Versão:** 0.2 — Atualização de integrações e impedimentos (não constitui aceite) 
**Data de preparação:** 26/10/2026  
**Referência funcional:** `docs/CATP_TEST_PLAN.md` — CATP v1.1  
**Referência de gestão:** Card 23 — Testes Integrados e Demonstração  
**Responsável funcional e consolidação:** Marcus — Project Manager  
**Responsável principal pelos testes integrados (Card 23):** Ketlyn Barbosa  
**Apoio técnico:** Tissiany Delmiro, Jaqueline de Lira e Luciene Godoy  
**Status geral:** HOMOLOGAÇÃO PENDENTE — SEM ACEITE DO MVP

> **Regra de evidência:** nenhuma implementação declarada, commit integrado, teste unitário informado ou demonstração simulada constitui, isoladamente, aprovação de um caso de aceitação. A aprovação exige execução, observação e evidências vinculadas ao commit testado.

## 1. Objetivo e escopo

Consolidar o planejamento, a execução, os resultados e as evidências da homologação integrada do MVP, desde a importação CSV/JSON, análise por IA e detecção de histórias até evidências rastreáveis, geração de depoimentos estruturados e cases, curadoria humana e persistência/recuperação real no OCI Object Storage.

**Critérios essenciais:** fidelidade às fontes; identificação de evidências literais e IDs; ausência de fatos inventados; três casos demonstrativos (conquista profissional, projeto de destaque e superação); dois formatos principais de ativo (depoimento estruturado e case de sucesso); curadoria humana; separação entre aprovação editorial e autorização; persistência real OCI; ausência de defeitos críticos impeditivos.

**Fora de qualquer conclusão automática:** posts LinkedIn são complementares; painel analítico é opcional conforme Card 23. A pontuação CQF 0–100 (CATP-012) está **pendente de decisão formal de escopo**.

## 2. Identificação do ambiente de homologação

| Campo | Registro |
|---|---|
| Data(s) de execução | A preencher |
| Executor(es) | A preencher por caso |
| Ambiente e sistema operacional | A preencher |
| Aplicação / URL | A preencher |
| Branch | `main` (confirmar no momento da execução) |
| Commit exato (SHA) | A preencher — obrigatório |
| Versão do Streamlit e dependências | A preencher |
| Provedor LLM / modo de execução | A preencher, sem divulgar segredos |
| OCI: região, bucket e identificadores não sensíveis | A preencher |
| Dados de teste / versão dos arquivos | A preencher |
| Limitações do ambiente | A preencher |

**Commits informados pela equipe como incorporados à `main` (a confirmar na execução):** `b38595f`, `e29d1d6`, `095b04d`, `b323fd2`, `7959443`. A presença desses commits não substitui o registro do SHA efetivamente homologado.

### Atualização de integrações — 28/10/2026

- **PR #20 — Correção da persistência OCI e do status do processamento:** aprovado por Jaqueline e integrado à `main` (merge `a05ae6b`). A revisão técnica registrou teste de gravação real no bucket OCI, tratamento de falha simulada e reenvio sem repetir as etapas de análise. A homologação integrada permanece pendente.
- **PR #21 — Suporte a credenciais OCI via Streamlit Secrets:** desenvolvido por Tissiany, aprovado por Jaqueline e integrado à `main` (merge `2b65357`). Permite configurar credenciais OCI pelo Streamlit Secrets. A configuração e a execução integrada ainda precisam ser validadas no ambiente de homologação.
- **Pendência identificada:** comportamento da aplicação quando o bucket OCI está vazio, com correção prevista em PR separado.

**Nota:** a integração dos PRs não representa aprovação automática dos casos CATP nem aceite do MVP.

## 3. Estados e critérios de classificação

- **Implementação:** Disponível / Parcial / Não implementada / Não verificada.
- **Aplicabilidade:** Aplicável / Não aplicável (com justificativa e decisão formal) / Pendente de decisão.
- **Execução:** Não executado / Aprovado / Reprovado / Bloqueado.
- **Evidência:** link para print, log sanitizado, arquivo de saída, ID de interação, chave de objeto OCI ou relatório técnico.
- **Regra de aprovação:** resultado observado corresponde ao esperado, com evidência suficiente e rastreável.

## 4. Matriz mestre de aceitação — CATP v1.1

Todos os casos abaixo iniciam como **Não executado** neste relatório, independentemente de relatos de testes anteriores. Atualizar apenas mediante comprovação da execução aplicável ao ambiente/commit registrado.

| ID | Funcionalidade / verificação | Resultado esperado (síntese) | Aplicabilidade | Execução | Evidência / defeito |
|---|---|---|---|---|---|
| CATP-001 | Importação CSV | Arquivo válido processado | Aplicável | Não executado | — |
| CATP-002 | Importação JSON | Dados válidos importados | Aplicável | Não executado | — |
| CATP-003 | Dados inválidos | Erro tratado e informado | Aplicável | Não executado | — |
| CATP-004 | Sentimentos | Resultado associado à interação original | Aplicável | Não executado | — |
| CATP-005 | Tópicos | Tópicos identificados e rastreáveis | Aplicável | Não executado | — |
| CATP-006 | Histórias | Histórias relevantes identificadas sem ficção em resultados vazios | Aplicável | Não executado | — |
| CATP-007 | Rastreabilidade | Citação literal vinculada ao ID original | Aplicável | Não executado | — |
| CATP-008 | Depoimentos | Depoimento estruturado fiel à fonte | Aplicável | Não executado | — |
| CATP-009 | Cases | Case estruturado sem fatos inventados | Aplicável | Não executado | — |
| CATP-010 | Curadoria humana | Quatro subcasos aplicáveis aprovados | Aplicável | Não executado | — |
| CATP-010a | Validação factual | Pendente / Validada / Insuficiente / Contradição | Aplicável | Não executado | — |
| CATP-010b | Curadoria editorial | Rascunho / Ajustes / Aprovado / Rejeitado | Aplicável | Não executado | — |
| CATP-010c | Autorização | Não registrada / Registrada, independente do editorial | Aplicável | Não executado | — |
| CATP-010d | Indicador RG-03 | Liberação condicionada aos requisitos aplicáveis | Aplicável | Não executado | — |
| CATP-011 | OCI e idempotência | Gravação e recuperação reais, sem duplicação do mesmo lote | Aplicável | Não executado | — |
| CATP-012 | CQF Score 0–100 | Pontuação conforme CQF se integrada ao MVP | **Pendente de decisão** | Não executado | — |
| CATP-013 | CQF contradições | Contradição não resolvida impede aprovação, se integrada | A confirmar | Não executado | — |
| CATP-014 | Autorização | Divulgação bloqueada sem autorização apropriada | Aplicável | Não executado | — |
| CATP-015 | Fluxo completo | Pipeline integrado executado com sucesso | Aplicável | Não executado | — |
| CATP-016 | Navegação Streamlit | Navegação entre seis módulos previstos | Aplicável | Não executado | — |
| CATP-017 | Estúdio | Fontes e conteúdo exibidos lado a lado | Aplicável | Não executado | — |
| CATP-018 | Regeneração RG-01 | Preserva fatos e não inventa informações | Aplicável | Não executado | — |
| CATP-019 | Curadoria — controles | Três controles independentes funcionam | Aplicável | Não executado | — |
| CATP-020 | Contradição RG-02 | Interface bloqueia aprovação de contradição não resolvida | Aplicável | Não executado | — |
| CATP-021 | Indicador RG-03 | Indicador corresponde às condições reais | Aplicável | Não executado | — |
| CATP-022 | Ajustes editoriais | Observações vinculadas ao conteúdo | Aplicável | Não executado | — |
| CATP-023 | Modo demonstração | Dados fictícios e resultados simulados explicitamente identificados | Aplicável | Não executado | — |

**Nota de integridade:** CATP-010 é um caso agregador e somente será aprovado após os quatro subcasos aplicáveis. A matriz contém 23 casos numerados principais e quatro subcasos adicionais.

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

**Atenção especial:** registrar explicitamente o cenário de **citação negativa**, IDs duplicados, IDs inválidos e impossibilidade de conferência, quando presentes nos arquivos reais. Uma evidência sem origem localizada não poderá ser validada automaticamente; o estado neutro informado pela equipe é **“Conferência indisponível”**.

### Modelo de registro individual

Copiar para cada execução:

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

## 6. Três demonstrações obrigatórias

| ID | História | Verificações mínimas | Execução | Evidências |
|---|---|---|---|---|
| DEMO-01 | Conquista profissional | Entrada, análise, fatos e citações, depoimento + case, curadoria, OCI | Não executado | — |
| DEMO-02 | Projeto de destaque | Participação e resultados somente quando informados; dois ativos, rastreabilidade, curadoria, OCI | Não executado | — |
| DEMO-03 | Superação | Dificuldades e conquistas fiéis à fonte, sem dramatização, dois ativos, curadoria, OCI | Não executado | — |

**Condição:** cada caso deve produzir os dois formatos principais, permitir verificação das fontes e passar pelas etapas aplicáveis do fluxo real. Demonstração mock deve ser identificada e não prova LLM/OCI reais.

## 7. Controles transversais de qualidade e curadoria

- **RG-01:** regeneração não altera nomes, números, fatos ou resultados sem evidência.
- **RG-02:** contradição não resolvida impede aprovação; testar lógica e interface.
- **RG-03:** liberação para publicação exige validação factual, aprovação editorial e autorização apropriada, sem transições automáticas entre controles.
- **Citações:** correspondência literal, ID de origem verificável, sem atribuição a terceiros.
- **Origem dos dados:** exemplos demonstrativos e histórias mock explicitamente diferenciados de análises reais.
- **Casos negativos:** nenhuma história artificial a partir de interações irrelevantes; nenhuma aprovação automática por ausência de origem ou por falha de persistência.

**Registro dos controles:** A preencher com os CATP correspondentes e evidências.

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

**Limitação conhecida:** a correção de status de persistência da PR #20 foi testada localmente sem credenciais OCI; a persistência real requer execução integrada com acesso autorizado. Verificar se a PR #20 foi revisada e integrada antes de usar seu comportamento como referência do MVP.

## 9. Defeitos, riscos e impedimentos

| ID | Data | Descrição | Gravidade | Responsável | Referência | Situação | Reteste |
|---|---|---|---|---|---|---|---|
| A preencher | — | — | — | — | — | — | — |

### Impedimentos identificados na verificação local — 28/10/2026

**IMP-001 — Gemini não configurado no ambiente local**
- Evidência: terminal registrou ausência da chave GEMINI_API_KEY e acionamento do fallback mock.
- Impacto: análise real por LLM não comprovada nesse ambiente.
- Situação: pendente de configuração segura e reteste.

**IMP-002 — Histórias demonstrativas após importação CSV**
- Evidência: foram importadas duas interações (membro_001 e membro_002), mas a interface apresentou três histórias fictícias predefinidas.
- Causa observada no código: fallback para m.HISTORIAS quando a análise LLM falha.
- Impacto: CATP-006 e rastreabilidade da análise real não comprovados.
- Situação: pendente de reteste com Gemini funcional.

**IMP-003 — Persistência OCI e confirmação visual**
- Evidência: o teste local anterior não comprovou gravação real. Posteriormente, a revisão técnica do PR #20 confirmou gravação em bucket real, tratamento de falhas e retry.
- Situação: correção integrada à main; homologação no ambiente de referência ainda pendente.

**IMP-004 — Fluxo integrado de ponta a ponta**
- Evidência: importação CSV observada, porém análise executada em mock no teste local.
- Impacto: CATP-015 ainda não comprovado.
- Situação: pendente de execução integrada e registro de evidências.

**IMP-005 — Comportamento com bucket OCI vazio**
- Evidência: problema relatado na revisão do PR #20, relacionado à utilização de svc.listar_pacotes() em state.py.
- Situação: correção prevista em PR separado; integração ainda não confirmada.

**Nota de homologação:** os registros acima documentam impedimentos e resultados parciais. Não alteram automaticamente os estados da matriz CATP nem constituem aceite do MVP.

**Riscos a acompanhar:** integração LLM real, credenciais e persistência OCI, rastreabilidade das fontes, controles independentes de curadoria, divergências entre testes unitários e fluxo completo, diferenças entre branch de desenvolvimento e `main`, rotulagem incompleta de dados demonstrativos.

## 10. Registro de decisões de escopo

| ID | Tema | Proposta / situação | Decisão | Evidência / data |
|---|---|---|---|---|
| DEC-001 | CATP-012 — CQF Score 0–100 | **Proposta** de transferir a fase posterior, mantendo os controles obrigatórios de qualidade | **Aguardando deliberação da equipe** | A preencher |
| DEC-002 | Aviso global, KPIs e opção B de origem dos dados | Informados como entrega em PR separado | Escopo e prioridade a confirmar | A preencher |

**Regra:** até decisão formal, o CATP-012 permanece documentado, **Não executado**, com aplicabilidade **Pendente de decisão**. Se transferido, registrar justificativa, responsáveis, data, evidência de aprovação e fase de destino; não rotular como teste aprovado.

## 11. Resumo executivo de homologação

| Indicador | Resultado atual |
|---|---|
| Casos CATP aprovados | 0 comprovados neste relatório |
| Casos CATP reprovados | 0 registrados |
| Casos CATP executados com evidência | 0 registrados |
| Seis cenários integrados | Aguardando execução e relatório |
| Três demonstrações obrigatórias | Sem evidência registrada |
| OCI real | Não verificada neste relatório |
| Defeitos críticos impeditivos | Situação ainda não consolidada |
| CATP-012 | Aguardando decisão de escopo |
| Recomendação técnica | **Não emitir até concluir a homologação** |
| Aceite do MVP | **Não concedido / pendente** |

> Os números acima indicam **ausência de evidências registradas neste documento**, não provam que a equipe jamais tenha executado testes em outros ambientes.

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

## 13. Parecer técnico e decisão final

**Parecer técnico:** PENDENTE — inserir síntese da equipe após testes, limitações, defeitos e recomendação fundamentada.  
**Decisão do Project Manager:** PENDENTE — **não há aprovação antecipada do MVP**.  
**Data do aceite ou rejeição:** A preencher.  
**Commit/versão objeto da decisão:** A preencher.  
**Evidências consultadas:** A preencher.  
**Justificativa e ressalvas:** A preencher.

---

**Referências:** CATP v1.1 (`docs/CATP_TEST_PLAN.md`), Card 23 — Testes Integrados e Demonstração, CQF v1.0 e resultados técnicos a serem anexados. Este relatório é um instrumento de gestão de homologação; não altera o CATP aprovado nem substitui os testes de aceitação.
