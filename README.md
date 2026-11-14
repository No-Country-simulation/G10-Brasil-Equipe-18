# CommunityLab 

![ONE G10](https://img.shields.io/badge/ONE-G10-00875A?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/LLM-Gemini-8A2BE2?style=for-the-badge)
![Oracle Cloud](https://img.shields.io/badge/Oracle_Cloud-F80000?style=for-the-badge&logo=oracle&logoColor=white)
![Status](https://img.shields.io/badge/Status-MVP_em_desenvolvimento-blue?style=for-the-badge)

**Detector Inteligente de Histórias de Sucesso e Testemunhos com IA**
**Hackathon ONE G10 — Equipe 18 | Oracle Next Education + Alura | Simulação No Country**

Situação em 14/11/2026: o código evoluiu com integrações recentes, incluindo o PR #35. O CATP v1.1 está publicado, mas a homologação integrada dos três cenários, dos controles de curadoria e da persistência real na OCI ainda depende de evidências consolidadas. O MVP não está homologado nem concluído.

---

## 💡 Sobre o projeto
O **CommunityLab** utiliza Inteligência Artificial para identificar histórias de sucesso, conquistas profissionais, projetos relevantes e relatos de superação em interações de comunidades digitais. A proposta é transformar esses relatos em sugestões de testemunhos, cases e conteúdos para redes sociais, preservando evidências rastreáveis e submetendo o material à curadoria humana.

A ferramenta apoia equipes de marketing e gestores de comunidades. A IA sugere; pessoas verificam, decidem e autorizam. Não há publicação automática no escopo do MVP.

---

## 🎯 O problema
Relatos de conquistas e experiências relevantes ficam dispersos em históricos de conversas. Identificá-los, conferir fatos, localizar citações originais e convertê-los em conteúdo editorial exige trabalho manual e pode introduzir erros de interpretação, atribuição ou consentimento.

---

## 🚀 Objetivo e escopo do MVP

Demonstrar um fluxo que permita:
1. Importar interações por CSV ou JSON.
2. Preparar e analisar dados para identificar histórias relevantes.
3. Gerar sugestões de ativos de conteúdo com auxílio de LLM.
4. Associar citações verificadas às interações de origem.
5. Revisar fatos, conteúdo editorial e autorização de divulgação separadamente.
6. Persistir e recuperar pacotes no OCI Object Storage, quando a integração estiver validada.
7. Demonstrar pelo menos três casos de uso com dados fictícios ou autorizados.
Fora do escopo inicial: captura direta obrigatória de Discord/Slack, publicação automática, monitoramento em tempo real e dashboards avançados.

---

## 📌 Estado das entregas — 14/11/2026

A incorporação de código à main não equivale à homologação funcional. Os estados abaixo refletem o acompanhamento do projeto e devem ser confrontados com o relatório CATP antes da aprovação final.
Componente	Estado conhecido	Evidência necessária para homologação
Integração LLM	Código de integração disponível	Execução real, fidelidade e tratamento de falhas
Interface Streamlit	Interface incorporada ao projeto	Navegação, Estúdio, curadoria e regressão de defeitos
Pipeline e orquestração	PR #35 integrado à main	Execução integrada com dados controlados e logs
Evidências e ativos	Implementações de extração e geração presentes	Testemunho estruturado e case fiel para cada cenário
OCI Object Storage	Código de persistência incorporado	Upload, recuperação, integridade e rastreabilidade em ambiente OCI real
Curadoria e autorização	Controles previstos e código em evolução	Comprovar estados independentes, persistência e bloqueio de divulgação indevida
Plano CATP v1.1	Documento incorporado pelo PR #4	Registrar resultados e evidências de execução
Três cenários demonstrativos	Conquista profissional, projeto de destaque e superação definidos	Demonstração ponta a ponta dos três casos

Referências: PR #4 · PR #35 · [Plano CATP v1.1](docs/CATP_TEST_PLAN.md).

Defeito conhecido a verificar: o Estúdio apresentou incompatibilidade com saída do tipo card que contém titulo e frase, mas não texto. A correção e o teste de regressão com DEMO-001 ainda exigem confirmação; evitar declarar o defeito resolvido sem evidência.

---

## 🏗️ Arquitetura funcional

```Interações de comunidades (CSV / JSON)
                 │
                 ▼
       Ingestão e normalização
                 │
                 ▼
       Preparação / análise IA
                 │
                 ▼
    Histórias candidatas + relevância
                 │
                 ▼
 Citações literais + IDs das interações
                 │
                 ▼
    Sugestões de ativos editoriais
                 │
                 ▼
   Curadoria humana em três controles
                 │
                 ▼
       Pacotes / OCI Object Storage
```
Este é o fluxo-alvo. A integração entre os módulos e a execução ponta a ponta dependem dos testes de aceitação.
Interface Streamlit
A proposta de interface contempla seis módulos: Dashboard, Importação, Histórias, Estúdio de Conteúdo, Curadoria e Histórico. O estado da aplicação utiliza st.session_state, e a camada app/services/data_service.py concentra chamadas a serviços e, quando aplicável, comportamentos demonstrativos.
Integração com IA e evidências
A integração Gemini está incorporada à main. As histórias podem conter citacoes (com trecho e id_interacao), interacoes_origem e relevancia_nivel (alta, media, baixa). O mecanismo de citação confere trechos contra o texto efetivamente recebido; não usa o texto inventado pelo modelo como fonte de verdade. Isso não dispensa validação factual humana.
Curadoria: três decisões independentes
- Validação factual: examina a suficiência e consistência das evidências; contradições precisam impedir liberação indevida.
- Aprovação editorial: avalia a qualidade e adequação do texto gerado.
- Autorização de divulgação: registra separadamente o consentimento ou a base autorizativa aplicável ao uso público.
RG-01: fatos e citações devem ser rastreáveis às fontes.
RG-02: contradições não podem resultar em aprovação factual indevida.
RG-03: aprovação editorial não substitui autorização para publicação.

A aplicação dessas regras no fluxo completo será verificada pelo CATP.
OCI Object Storage
O projeto dispõe de código para integração com o OCI Object Storage, incluindo alterações consolidadas no PR #35. Relatos de testes anteriores não substituem a homologação do fluxo atual.

Para aprovar a integração, demonstrar a sequência gerar ativo no pipeline → enviar ao bucket → identificar objeto → recuperar pela aplicação → verificar integridade → vincular à história e à evidência original. Registrar ambiente, commit testado, resultados e eventuais falhas no CATP-011.

Dados simulados e operações reais precisam permanecer claramente diferenciados. Não atribuir sucesso a operações de persistência que falharam.
Configuração de credenciais OCI
O sistema suporta dois métodos de configuração:
1. Streamlit Secrets (recomendado para deploy no Streamlit Cloud):
   - Configure as cinco variáveis em .streamlit/secrets.toml (desenvolvimento local) ou em Settings > Secrets do app publicado.
   - Variáveis: OCI_USER, OCI_FINGERPRINT, OCI_TENANCY, OCI_REGION, OCI_KEY_CONTENT.
   - Use .streamlit/secrets.toml.example como referência (apenas os NOMES das variáveis, sem valores reais).
   - Quando secrets estão presentes, o sistema usa apenas eles, sem fallback silencioso para o arquivo de config.
2. Arquivo ~/.oci/config (fallback para desenvolvimento local):
   - Usado automaticamente quando Streamlit secrets não estão disponíveis.
   - Configure conforme a documentação oficial da OCI.
Importante: secrets.toml está no .gitignore e nunca deve ser commitado. Em produção, substitua o sal de pseudonimização padrão em .env.

---

## 🛠️ Tecnologias

```
Tecnologia	Utilização
Python	Lógica de aplicação, ingestão e serviços
Streamlit	Interface de exploração e curadoria
Gemini (LLM)	Análise e geração de histórias e conteúdos
Pandas / Pydantic	Preparação e validação estruturada no pipeline, conforme integração
OCI Python SDK	Comunicação com Oracle Cloud
OCI Object Storage	Persistência de pacotes
pytest	Testes automatizados e de regressão
GitHub	Código, Pull Requests e revisões
Trello	Planejamento e acompanhamento do projeto
```

---

## 📁 Organização e documentação
Os diretórios relevantes incluem:

README.md
READMEFrontend.md          # documentação específica do front-end, quando disponível
requirements-front.txt     # dependências do front-end
app/                       # Streamlit, telas, estado, serviços e mocks
src/                       # módulos do pipeline, conforme PRs integrados
docs/
  CATP_TEST_PLAN.md        # critérios e cenários de aceitação
A estrutura pode evoluir conforme os Pull Requests forem integrados. Para executar o front-end, consultar READMEFrontend.md e COMO_RODAR.md, quando disponíveis na branch utilizada. Não incluir chaves de API nem arquivos .env reais em commits.

---

## 🧪 Testes e critérios de aceitação

plano oficial está em [`docs/CATP_TEST_PLAN.md`](docs/CATP_TEST_PLAN.md) (v1.1). A situação de cada teste deve ser confirmada no relatório de execução, pois a matriz documental não constitui, isoladamente, comprovação de homologação.
Teste	Objetivo	Estado documentado
CATP-007	Citações literais, rastreabilidade e ID da origem	Código integrado; teste integrado pendente
CATP-010a–010d	Separação de validação factual, decisão editorial, autorização e liberação	Pendente de validação integrada
CATP-011	Persistência, recuperação e ausência de duplicidade no OCI	Há relato de execução anterior; revalidação integrada em OCI real pendente de evidência
CATP-013/014	Contradições e autorização de divulgação	Pendente de validação integrada
CATP-015–023	Fluxos E2E, navegação, Estúdio, Curadoria e modo demonstração	Pendente de validação integrada

Não interpretar commits, screenshots ou testes locais isolados como homologação automática do MVP.

---

## 🧪 Casos de demonstração

1. Conquista profissional: identificação de relato de obtenção de emprego; extração de fatos e proposta de testemunho.
2. Projeto de destaque: identificação de projeto tecnológico; extração de evidências e proposta de case.
3. Superação: identificação de dificuldades e conquistas relatadas, com evidências e geração de testemunho estruturado e case.
Os três cenários devem produzir os dois formatos principais: testemunho estruturado e case de sucesso. Posts para LinkedIn são complementares.

Usar somente dados fictícios ou autorizados e manter explícito o modo demonstração.

---

## 🔐 Segurança, privacidade e responsabilidade

- Nunca versionar senhas, tokens, credenciais OCI ou chaves de API.
- Utilizar configurações externas, como variáveis de ambiente, secrets ou arquivos locais ignorados pelo Git.
- Limitar o acesso a dados pessoais e aos objetos armazenados.
- Não tratar a anonimização automatizada como garantia absoluta de ausência de dados pessoais.
- Preservar a proveniência de citações e a possibilidade de auditoria.
- Manter revisão humana e autorização apropriada antes da divulgação pública.
- Diferenciar claramente resultados reais, dados simulados e falhas técnicas.

---

## 👥 Equipe

```
Integrante	Responsabilidade
Marcus	Project Manager
Ketlyn Barbosa	Machine Learning Engineer
Tissiany Delmiro	Full Stack Developer
Jaqueline de Lira	AI Engineer
Luciene Godoy	Agent Engineer
```

---

## 🤝 Colaboração e governança

- Desenvolver em branches específicas (feature/, feat/, fix/, docs/, chore/).
- Adotar commits objetivos, preferencialmente em padrão Conventional Commits.
- Descrever escopo, impactos, testes e referências aos cards do Trello nos Pull Requests.
- Submeter mudanças à revisão técnica e respeitar a proteção da main, incluindo a aprovação exigida.
- Não realizar merge de funcionalidades críticas sem análise dos critérios de aceitação correspondentes.

---

## 🗺️ Próximas etapas para o Demo Day

- [x] Publicar o CATP v1.1 (PR #4).
- [x] Incorporar a consolidação técnica do PR #35 à main.
- [ ] Confirmar a correção e regressão do Estúdio (DEMO-001).
- [ ] Executar e registrar os testes CATP aplicáveis, distinguindo mocks de serviços reais.
- [ ] Comprovar persistência, recuperação e integridade de ativos em OCI real.
- [ ] Validar a separação entre validação factual, aprovação editorial e autorização de publicação.
- [ ] Executar os três cenários com testemunho, case, evidências e curadoria.
- [ ] Consolidar resultados, defeitos e limitações no relatório final de testes.
- [ ] Revisar diagrama e comandos de instalação contra o código efetivamente integrado.
- [ ] Obter revisão técnica da equipe e aprovação final do Project Manager.

---

## 📈 Resultados esperados

Ao final do hackathon, espera-se demonstrar a capacidade de identificar histórias relevantes, gerar sugestões editoriais rastreáveis, permitir curadoria responsável e recuperar ativos armazenados, com documentação e evidências de testes suficientes para avaliar o funcionamento do MVP.

---

## 📄 Licença e créditos
A licença será definida pela equipe, conforme as regras do Hackathon e a estratégia de disponibilização do código.

CommunityLab — Histórias que inspiram. Inteligência que transforma.
Hackathon ONE G10 — Oracle Next Education & Alura · Equipe 18
Prazo previsto de entrega: 24 de novembro de 2026.
