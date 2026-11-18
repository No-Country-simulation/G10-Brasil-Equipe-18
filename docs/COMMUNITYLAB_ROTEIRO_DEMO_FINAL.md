
# CommunityLab — Roteiro de Demonstração Final do MVP

**Projeto:** CommunityLab — Inteligência de Comunidades com IA  
**Equipe:** 18 — Hackathon ONE G10  
**Versão:** 1.0 — Roteiro preliminar flexível  
**Responsável pela coordenação:** Project Manager  
**Duração-alvo:** 5 minutos  
**Apresentador:** A definir  
**Status:** Preparação da demonstração — homologação do MVP pendente

---

## 1. Objetivo da apresentação

Demonstrar como o CommunityLab transforma dados de comunidades em informações organizadas e conteúdos de marketing, utilizando inteligência artificial, processamento de dados e uma interface de curadoria.

A apresentação deverá evidenciar:

- O problema de negócio abordado.
- A proposta de valor do CommunityLab.
- A arquitetura e as tecnologias utilizadas.
- O fluxo funcional do MVP.
- Os benefícios esperados para gestores de comunidades e equipes de marketing.
- O estágio real de implementação e homologação.

**Regra de comunicação:** não declarar como concluída ou homologada uma funcionalidade que ainda dependa de testes, integrações ou validação documental.

---

## 2. Organização da apresentação

O roteiro permite dois formatos:

**Formato A — Apresentador único**

Uma pessoa conduz toda a narrativa, opera a interface e realiza o encerramento.

**Formato B — Apresentação compartilhada**

As falas podem ser distribuídas entre os integrantes, respeitando o limite total de cinco minutos.

A distribuição definitiva será definida pela equipe.

| Bloco | Tempo | Responsável |
|---|---|---|
| Problema e oportunidade | 0:00–0:40 | A definir |
| Solução CommunityLab | 0:40–1:20 | A definir |
| Arquitetura e tecnologias | 1:20–2:00 | A definir |
| Demonstração do MVP | 2:00–4:10 | A definir |
| Benefícios e encerramento | 4:10–5:00 | A definir |

---

## 3. Roteiro detalhado

### Bloco 1 — Problema e oportunidade

**Tempo:** 0:00–0:40

**Fala sugerida:**

"Comunidades digitais produzem diariamente um volume significativo de mensagens, opiniões, dúvidas e experiências.

Entretanto, transformar essas interações em conhecimento útil para decisões de negócio e estratégias de marketing exige tempo, organização e capacidade de análise.

Foi a partir desse desafio que desenvolvemos o CommunityLab."

**Recurso visual sugerido:** tela de abertura com o problema de negócio.

**Mensagem central:** existe uma oportunidade de transformar conversas em inteligência acionável.

---

### Bloco 2 — Apresentação da solução

**Tempo:** 0:40–1:20

**Fala sugerida:**

"O CommunityLab é uma solução de inteligência de comunidades com IA.

Nossa proposta é receber dados de comunidades, organizar e analisar essas informações, identificar temas e sentimentos relevantes e apoiar a criação de conteúdos de marketing.

O objetivo é transformar dados dispersos em insights e materiais que possam ser avaliados e utilizados pelas equipes responsáveis."

**Recurso visual sugerido:** visão geral do fluxo do produto.

**Mensagem central:** transformar dados de comunidades em inteligência e conteúdo.

---

### Bloco 3 — Arquitetura e tecnologias

**Tempo:** 1:20–2:00

**Fala sugerida:**

"Para construir o MVP, estruturamos uma arquitetura que combina processamento de dados, inteligência artificial, interface de usuário e persistência.

Utilizamos Python e bibliotecas de análise de dados, uma interface desenvolvida com Streamlit e componentes de integração com modelos de linguagem.

Também trabalhamos com mecanismos de armazenamento e automação, cuja validação integrada faz parte dos critérios de homologação.

Essa arquitetura foi planejada para permitir evolução modular e maior rastreabilidade do processamento."

**Tecnologias e componentes previstos no projeto:**

- Python.
- Pandas e componentes de processamento textual.
- Streamlit.
- Integração com LLM, incluindo Gemini.
- OCI Object Storage.
- Componentes de automação e orquestração.

**Atenção:** a apresentação deverá identificar quais componentes foram efetivamente executados e validados antes de demonstrá-los como operacionais.

**Mensagem central:** arquitetura modular com processamento, IA, curadoria e persistência.

---

### Bloco 4 — Demonstração do MVP

**Tempo:** 2:00–4:10

A demonstração deverá utilizar um conjunto de dados previamente preparado, sem informações pessoais sensíveis.

#### 4.1 Importação

**Ação prevista:** abrir a tela de Importação e apresentar um arquivo de exemplo em CSV ou JSON.

**Fala sugerida:**

"O fluxo começa com a importação dos dados da comunidade. A partir dessa entrada, o sistema organiza as informações para as etapas seguintes de análise."

**Evidência necessária:** execução bem-sucedida da importação no ambiente utilizado na demonstração.

#### 4.2 Histórias

**Ação prevista:** acessar a tela Histórias e apresentar resultados previamente validados.

**Fala sugerida:**

"Nesta etapa, buscamos identificar informações relevantes e histórias que possam orientar a produção de conteúdo e a comunicação com a comunidade."

**Evidência necessária:** resultados disponíveis e verificáveis no ambiente de demonstração.

#### 4.3 Estúdio

**Ação prevista:** acessar o Estúdio e apresentar um exemplo de conteúdo gerado ou preparado.

**Fala sugerida:**

"O Estúdio organiza a transformação dos insights em propostas de conteúdo, como publicações para LinkedIn e materiais de destaque para comunicação."

**Evidência necessária:** exemplo identificado como real, previamente gerado ou ilustrativo, conforme sua origem.

#### 4.4 Curadoria

**Ação prevista:** acessar a tela de Curadoria.

**Fala sugerida:**

"A curadoria permite que o conteúdo passe por avaliação humana antes de sua utilização. A inteligência artificial apoia o processo, mas não substitui a revisão e a decisão dos responsáveis."

**Evidência necessária:** fluxo disponível para apresentação ou registro de sua limitação atual.

#### 4.5 Histórico

**Ação prevista:** acessar a tela Histórico.

**Fala sugerida:**

"O Histórico foi concebido para apoiar a consulta e a rastreabilidade dos registros processados, contribuindo para a continuidade das atividades."

**Evidência necessária:** comprovação do comportamento efetivamente disponível.

**Observação:** a navegação entre as cinco telas não comprova, isoladamente, a operação completa das integrações Gemini e OCI.

---

### Bloco 5 — Benefícios e encerramento

**Tempo:** 4:10–5:00

**Fala sugerida:**

"O principal valor do CommunityLab está em aproximar a inteligência artificial das necessidades reais de quem gerencia comunidades e desenvolve estratégias de comunicação.

Com a solução, buscamos reduzir o esforço de organização das informações, facilitar a identificação de assuntos relevantes e apoiar a criação de conteúdos com supervisão humana.

Além do produto, o projeto representa uma experiência de trabalho colaborativo, gestão ágil, integração de tecnologias e validação de software.

O CommunityLab demonstra como dados, IA e conhecimento de negócio podem ser combinados para transformar conversas em oportunidades de ação.

Muito obrigado!"

**Mensagem central:** valor de negócio, aprendizado técnico e potencial de evolução.

---

## 4. Plano de contingência

A apresentação deverá possuir alternativas previamente preparadas.

| Situação | Procedimento |
|---|---|
| Interface não inicia | Utilizar capturas de tela verificadas do fluxo |
| Falha na importação | Apresentar arquivo de exemplo e evidência de teste anterior |
| Gemini indisponível | Utilizar saída previamente gerada, identificando sua origem |
| OCI indisponível | Explicar o fluxo previsto e informar que a validação está pendente |
| Navegação apresenta erro | Continuar com imagens ou vídeo de execução previamente validada |
| Tempo insuficiente | Priorizar problema, proposta de valor e fluxo principal |

Nenhuma evidência simulada ou previamente gravada deverá ser apresentada como execução ao vivo.

---

## 5. Preparação dos materiais

Antes da apresentação, preparar:

- [ ] Arquivo CSV de demonstração.
- [ ] Arquivo JSON alternativo.
- [ ] Dados fictícios ou anonimizados.
- [ ] Resultado de análise previamente verificado.
- [ ] Exemplo de conteúdo de marketing.
- [ ] Capturas de tela das cinco telas.
- [ ] Vídeo de contingência, se viável.
- [ ] Ambiente Streamlit preparado.
- [ ] Evidências de testes disponíveis.
- [ ] Relação de funcionalidades homologadas e pendentes.
- [ ] Cronômetro e ensaio da apresentação.

---

## 6. Critérios de prontidão

A demonstração será considerada preparada quando:

1. O roteiro estiver aprovado pela equipe.
2. Os responsáveis pelas falas estiverem definidos.
3. Os dados de demonstração estiverem disponíveis.
4. As funcionalidades escolhidas tiverem sido verificadas.
5. Os materiais de contingência estiverem preparados.
6. O ensaio respeitar o limite de tempo.
7. As limitações conhecidas estiverem documentadas.
8. A apresentação não depender de correções de última hora.

A prontidão da apresentação não equivale à homologação integral do MVP.

---

## 7. Perguntas prováveis da banca

### Qual problema o CommunityLab resolve?

A dificuldade de transformar grandes volumes de interações de comunidades em informações organizadas, insights e oportunidades de conteúdo.

### Qual é o diferencial da solução?

A combinação de processamento de dados, apoio de IA, geração de conteúdo e curadoria humana em um fluxo integrado.

### A IA publica conteúdos automaticamente?

A proposta do MVP prioriza a geração assistida e a curadoria. Qualquer publicação automática somente deverá ser afirmada se estiver efetivamente implementada e validada.

### Como os dados são armazenados?

A arquitetura contempla mecanismos de persistência, incluindo OCI Object Storage. O estado efetivo da integração deverá ser apresentado conforme as evidências disponíveis.

### O MVP está completamente homologado?

A resposta deverá refletir o relatório de homologação vigente e os resultados dos testes no momento da apresentação. Enquanto houver critérios pendentes, não declarar homologação integral.

### Quais são os próximos passos?

Concluir os testes integrados, resolver impedimentos, consolidar evidências e evoluir os recursos conforme a priorização do projeto.

---

## 8. Responsabilidades da equipe

A distribuição abaixo representa as áreas de atuação do projeto, não uma definição de quem apresentará.

| Integrante | Área de atuação | Participação na apresentação |
|---|---|---|
| Marcus | Gestão do projeto | A definir |
| Ketlyn | Machine Learning e testes | A definir |
| Jaqueline | Inteligência artificial e integrações | A definir |
| Tissiany | Full Stack e interface | A definir |
| Luciene | Automação e orquestração | A definir |

A escolha de apresentadores deverá considerar domínio do conteúdo, disponibilidade, fluidez das transições e limite de tempo.

---

## 9. Documentos relacionados

- `docs/COMMUNITYLAB_HOMOLOGACAO_MVP.md` — relatório de homologação.
- PR #28 — consolidação documental da homologação.
- PR #29 — correções do teste de regressão frontend.
- PR #30 — testes e evidências CATP.
- Issue #27 — pendências de integração Gemini e OCI.

Este roteiro não substitui os documentos de homologação nem altera seus critérios de aceite.

---

## 10. Controle de versão

**Versão:** 1.0  
**Estado:** Roteiro preliminar para revisão interna  
**Apresentadores:** Não definidos  
**Duração planejada:** 5 minutos  
**Próxima revisão:** Após validação do roteiro pela equipe e confirmação do estado funcional do MVP

**CommunityLab — Equipe 18 | Hackathon ONE G10**
