# CommunityLab Acceptance Test Plan (CATP)

**Versão:** 1.0  
**Projeto:** CommunityLab — Hackathon ONE G10  
**Equipe:** 18  
**Responsável funcional:** Marcus — Project Manager  
**Status:** Planejamento inicial — testes ainda não executados

## 1. Objetivo

Estabelecer um plano estruturado de testes de aceitação para verificar se o MVP do CommunityLab atende aos requisitos funcionais, mantém a fidelidade das informações e executa corretamente o fluxo integrado de processamento.

O CATP complementa o CommunityLab Quality Framework (CQF v1.0), sem substituí-lo.

## 2. Escopo dos testes

O plano contempla:

- Importação de interações em CSV e JSON.
- Validação e tratamento de dados.
- Análise de sentimentos e extração de tópicos.
- Identificação de histórias de sucesso relevantes.
- Rastreabilidade das evidências originais.
- Geração de depoimentos estruturados.
- Geração de casos de sucesso.
- Revisão e curadoria humana no Streamlit.
- Integração e persistência na OCI Object Storage.
- Controles de qualidade e governança definidos pelo CQF, caso integrados ao MVP.

## 3. Matriz inicial de testes

| ID | Funcionalidade | Resultado esperado | Status |
|---|---|---|---|
| CATP-001 | Importação CSV | Arquivo válido processado corretamente | Não executado |
| CATP-002 | Importação JSON | Dados válidos importados corretamente | Não executado |
| CATP-003 | Dados inválidos | Erro tratado e informado ao usuário | Não executado |
| CATP-004 | Análise de sentimentos | Resultado associado à interação original | Não executado |
| CATP-005 | Extração de tópicos | Tópicos identificados e rastreáveis | Não executado |
| CATP-006 | Detecção de histórias | Histórias relevantes identificadas | Não executado |
| CATP-007 | Rastreabilidade | Evidências vinculadas às fontes originais | Não executado |
| CATP-008 | Geração de depoimentos | Depoimento estruturado e fiel à fonte | Não executado |
| CATP-009 | Geração de casos de sucesso | Caso estruturado sem fatos inventados | Não executado |
| CATP-010 | Curadoria humana | Revisão e decisão registradas | Não executado |
| CATP-011 | Persistência OCI | Resultado armazenado e recuperável | Não executado |
| CATP-012 | CQF — Pontuação | Cálculo conforme especificação, se implementado | Não executado |
| CATP-013 | CQF — Contradições | Aprovação bloqueada diante de contradição não resolvida, se implementado | Não executado |
| CATP-014 | Autorização | Divulgação impedida sem autorização apropriada | Não executado |
| CATP-015 | Fluxo completo | Processamento integrado executado com sucesso | Não executado |

## 4. Procedimento de execução

Cada teste deverá registrar:

- Identificador do teste.
- Data de execução.
- Responsável pela execução.
- Versão ou commit do sistema testado.
- Dados de entrada.
- Procedimento executado.
- Resultado esperado.
- Resultado observado.
- Status: aprovado, reprovado, bloqueado ou não executado.
- Evidências de execução, quando disponíveis.
- Referência ao defeito identificado, quando aplicável.

## 5. Critérios de aceitação

Um teste somente poderá ser considerado aprovado quando o comportamento observado corresponder ao resultado esperado e houver evidência suficiente para sustentar a decisão.

A documentação de um caso de teste não equivale à sua execução.

Falhas relevantes deverão ser registradas, corrigidas e submetidas a novo teste.

## 6. Responsabilidades

**Marcus — Project Manager:** planejamento funcional, coordenação dos testes de aceitação, consolidação dos resultados e acompanhamento das pendências.

**Equipe técnica:** apoio à preparação do ambiente, execução dos testes pertinentes, análise de falhas e correções, conforme distribuição acordada.

## 7. Integração com o CQF

O CQF avalia a qualidade editorial e estabelece controles de governança sobre histórias e conteúdos.

O CATP verifica se as funcionalidades implementadas atendem aos comportamentos esperados.

Os seis cenários documentados em `CQF_VALIDATION_REPORT.md` poderão ser utilizados como referências para testes de aceitação, com adaptações aos formatos reais de entrada e saída do MVP.

## 8. Critério de encerramento

A execução do CATP será considerada encerrada quando os testes aplicáveis ao escopo aprovado forem executados, seus resultados documentados e as falhas impeditivas de aceitação forem resolvidas ou formalmente tratadas.

A decisão final de aceite dependerá da avaliação conjunta dos responsáveis pelo projeto.

---

**Documento de planejamento funcional — CATP v1.0.**
