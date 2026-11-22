# CommunityLab · Front-end (Streamlit)

Interface do CommunityLab integrada à análise por LLM, à curadoria humana e ao OCI Object Storage. Permite importar interações, consultar histórias detectadas, editar rascunhos e registrar decisões de curadoria.

Situação documental conferida em **22/11/2026**. Código integrado à main, implantação na VM e homologação funcional são etapas distintas.

Os exemplos fornecidos para demonstração usam dados fictícios. Na Importação, a natureza de cada lote é declarada como fictícios, reais ou não informado. Essa declaração não é deduzida pelo provedor de IA nem comprova anonimização.

A correção de anonimização do PR #64 foi integrada à main em `fcc077e`. O PR #67, de cases de sucesso, foi integrado em `07ae36c`. Implantação e retestes da versão consolidada continuam pendentes.

O PR #68, de testemunhos estruturados, permanece em revisão, agora com base main. O commit complementar `016c12d` trata as recusas de citações literais relatadas na revisão. Nova revisão e repetição dos casos com IA real continuam pendentes.

A recuperação editorial completa em nova sessão também permanece pendente.

> Os conteúdos gerados são rascunhos sujeitos à revisão humana. Aprovação editorial e autorização para publicação são controles separados. Nada é publicado automaticamente.

## Identidade visual

O CommunityLab utiliza visual limpo, com navegação lateral escura e destaques em violeta.

### Paleta de cores

| Cor | Código | Uso |
|---|---|---|
| Azul-marinho | `#101B32` | Sidebar e navegação |
| Violeta | `#7C3AED` | Ações e destaques |
| Ciano | `#22D3EE` | Detalhes sobre fundo escuro |
| Branco-neutro | `#F8FAFC` | Fundo da área de trabalho |
| Verde | `#10B981` / `#047857` | Indicadores de sucesso |
| Texto principal | `#0F172A` | Títulos e conteúdo |
| Texto secundário | `#64748B` | Legendas e informações auxiliares |
| Borda suave | `#E2E8F0` | Cards e divisores |

### Diretrizes

- Fonte Inter.
- Textos naturais, diretos e compreensíveis.
- Cards com bordas suaves e cantos arredondados.
- Cores acompanhadas de rótulos e explicações.
- A paleta e as diretrizes visuais não substituem uma auditoria de acessibilidade.

## Módulos da interface

| Módulo | Comportamento |
|---|---|
| Dashboard | Apresenta contagens e atalhos de navegação. Não equivale ao painel analítico avançado previsto no Card 22. |
| Importação | Recebe CSV, JSON colado ou mensagens do Discord, conforme configuração. Exibe prévia, filtro por canal, avisos de IDs e declaração da natureza do lote. |
| Histórias | Apresenta histórias detectadas, categorias, relevância e acesso ao Estúdio. Exibe a natureza declarada dos dados. |
| Estúdio de Conteúdo | Permite consultar evidências e editar os campos dos ativos disponíveis. |
| Curadoria | Permite validar fatos, decidir editorialmente e registrar autorização de publicação. |
| Histórico | Lista pacotes persistidos no OCI, permite visualizar o JSON e baixar os objetos disponíveis. |

### Fluxo de trabalho

1. Importar interações.
2. Declarar a natureza dos dados.
3. Processar o lote com o provedor configurado.
4. Consultar histórias e evidências.
5. Editar rascunhos no Estúdio.
6. Registrar decisões na Curadoria.
7. Consultar os pacotes no Histórico.

Consultar um pacote no Histórico não significa restaurar automaticamente o lote completo para edição em uma nova sessão.

## Curadoria humana

A interface possui três controles independentes:

- **Validação factual:** Pendente, Validada, Evidências insuficientes ou Contradição não resolvida.
- **Curadoria editorial:** Rascunho, Ajustes solicitados, Aprovado ou Rejeitado.
- **Autorização de publicação:** Não registrada ou Registrada.

### Regras

- Com **Contradição não resolvida**, o botão Aprovar fica desabilitado.
- Aprovação editorial não exige, por si só, autorização de publicação.
- O indicador **Liberado para publicação** depende de validação factual, aprovação editorial e autorização registrada.
- Nenhum conteúdo é publicado automaticamente.
- A conferência de citações não substitui a avaliação contextual e factual do ativo inteiro.
- A ação **Regenerar** alterna entre variações já disponíveis. Não realiza uma nova chamada ao LLM; sem variações, não altera o conteúdo.

O PR #57 integrou a persistência de decisões e campos editados no pacote. O reteste funcional da versão consolidada na VM continua pendente.

## Como executar

Pré-requisito: Python 3.10 ou superior, com dependências compatíveis com a versão utilizada.

Na raiz do repositório:

```bash
python -m venv .venv
```

Ative o ambiente virtual.

**Windows — CMD:**

```cmd
.venv\Scripts\activate.bat
```

**Windows — PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

Instale as dependências da interface:

```bash
python -m pip install -r requirements-front.txt
```

Inicie a aplicação:

```bash
python -m streamlit run app/main.py
```

O endereço local padrão é `http://localhost:8501`.

A execução integrada também depende da configuração dos provedores e do armazenamento. Para implantação em VM Oracle com Docker, consulte:

- [Guia de implantação na VM Oracle](docs/DEPLOYMENT_ORACLE_VM.md)
- [Instruções gerais de execução](COMO_RODAR.md)

## Configuração dos provedores de LLM

A análise tenta os provedores nesta ordem:

**Gemini → Cohere → Groq**

Se um provedor não tiver chave configurada ou falhar, o próximo é tentado. Se todos falharem, a aplicação apresenta o erro; não substitui a falha por histórias fictícias.

As configurações podem ser fornecidas em `.streamlit/secrets.toml` ou por variáveis de ambiente.

Exemplo de estrutura:

```toml
GEMINI_API_KEY = "SUBSTITUA_PELA_SUA_CHAVE"
GEMINI_MODEL = "MODELO_DISPONIVEL_NA_SUA_CONTA"

COHERE_API_KEY = "SUBSTITUA_PELA_SUA_CHAVE"
COHERE_MODEL = "MODELO_DISPONIVEL_NA_SUA_CONTA"

GROQ_API_KEY = "SUBSTITUA_PELA_SUA_CHAVE"
GROQ_MODEL = "MODELO_DISPONIVEL_NA_SUA_CONTA"

LLM_MAX_OUTPUT_TOKENS = 8192
```

Substitua os exemplos pelos modelos compatíveis com o adaptador e disponíveis na conta utilizada. Configure as chaves dos provedores que serão usados.

- Não inclua credenciais no repositório.
- O arquivo `.streamlit/secrets.toml` deve permanecer fora do versionamento.
- O prompt está em `app/services/prompt_analise.txt`.
- Configurar um provedor não comprova sua validação funcional no ambiente implantado.
- O rótulo de análise real identifica o provedor utilizado; não determina se as mensagens são reais ou fictícias.

### Respostas truncadas

O PR #61 integrou tratamento específico para respostas encerradas com `MAX_TOKENS`.

A interface permite nova tentativa sobre o mesmo lote. Pode ser necessário reduzir o lote ou ajustar `LLM_MAX_OUTPUT_TOKENS`.

A nova tentativa não garante sucesso, e aumentar o limite depende das condições do modelo utilizado.

## Natureza declarada dos dados

Na Importação, antes de iniciar o processamento, a pessoa declara:

| Valor | Rótulo |
|---|---|
| `ficticios` | Fictícios — exemplo ou teste |
| `reais` | Reais — relatos de pessoas |
| `nao_informado` | Não informado |

### Comportamento

- O padrão é **Não informado**.
- Um lote novo não herda a declaração do lote anterior.
- Sem interações carregadas, o controle fica desabilitado.
- Após clicar em **Importar interações**, a declaração fica travada para aquele lote.
- Para alterar a declaração, carregue um lote novo.
- Para reenviar o mesmo arquivo como novo lote, remova-o do campo de upload antes de selecioná-lo novamente.

Nas Histórias:

- **Dados fictícios (declarado):** amarelo.
- **Dados reais (declarado):** azul.
- **Natureza não informada:** cinza.

Nenhum desses selos usa verde como indicação de validação.

A natureza não é inferida pelo autor, conteúdo, origem do arquivo, Discord ou provedor de análise.

**Limitação conhecida:** a nota “Exemplo fictício…” na Importação ainda depende da origem do lote, embora a declaração seja independente.

## Rastreabilidade das interações

Cada interação recebe um ID efetivo antes dos filtros.

### Regras de ID

1. Um `id` explícito é aceito quando é inteiro maior ou igual a 1.
2. Booleanos não são aceitos como IDs inteiros.
3. Se o ID estiver ausente ou inválido, é utilizada a posição no lote original, começando em 1.
4. A substituição de IDs inválidos gera aviso na Importação.
5. IDs efetivos duplicados provocam rejeição do lote.
6. Os IDs efetivos não são recalculados após filtros.

A regra está centralizada em `calcular_ids_efetivos()` de `app/services/data_service.py`.

### Exemplo

```json
[
  {
    "id": 101,
    "autor": "Pessoa de exemplo A",
    "canal": "#conquistas",
    "tipo": "mensagem",
    "texto": "Consegui minha primeira vaga."
  },
  {
    "autor": "Pessoa de exemplo B",
    "canal": "#geral",
    "tipo": "mensagem",
    "texto": "Compartilho uma experiência."
  }
]
```

O primeiro registro utiliza o ID 101. O segundo utiliza o ID efetivo 2, correspondente à posição original.

## Conferência de citações

Cada citação é conferida contra a interação indicada pelo seu `id_interacao`.

A regra está em `app/services/conferencia_citacao.py`. As telas utilizam as funções disponibilizadas pelo `data_service`.

| Resultado | Apresentação | Significado |
|---|---|---|
| Trecho literal conferido | Verde | O trecho corresponde ao texto da interação, sem marcador. |
| Compatível com anonimização | Azul | A parte não mascarada corresponde ao original; o dado ocultado não é conferido. |
| Não confere | Amarelo, com motivo | O trecho apresenta incompatibilidade com a fonte. |
| Conferência indisponível | Neutro | A interação não está disponível ou a origem é ambígua. |
| ID não informado | Neutro | O ID está ausente ou inválido. |

### Onde aparece

- Nas evidências citadas do Estúdio e da Curadoria.
- Abaixo do campo de citação editável, com revalidação após alterações.

O campo editável utiliza a origem da história. Quando há mais de uma origem ou nenhuma origem disponível, a conferência não adivinha qual utilizar.

### Limites da conferência

- O resultado é individual por citação.
- O azul não representa aprovação factual.
- Um termo mascarado indevidamente pode ser considerado compatível com anonimização.
- A presença literal de um trecho não comprova que toda a narrativa respeita o contexto.
- Nenhum resultado autoriza publicação.

## Preparação textual e anonimização

Antes do envio ao provedor, o serviço de análise aplica normalização e anonimização ao texto.

Os dados reconhecidos podem ser substituídos por marcadores como:

- `[NOME]`
- `[EMAIL]`
- `[TELEFONE]`
- `[CPF]`

O autor também é pseudonimizado antes do envio. Valores já no formato esperado de pseudônimo são preservados.

Na resposta, o texto de origem e as citações são vinculados à interação correspondente, em vez de confiar apenas no texto repetido pelo modelo.

Na imagem Docker, o modelo `pt_core_news_sm` é instalado e validado durante o build. Sem o modelo disponível, há fallback heurístico de melhor esforço.

### Correção integrada — PR #64

O PR #64 foi aprovado por Tissiany e integrado à main em `fcc077e`.

A revisora relatou:

- **3.682 testes aprovados** no head `f929124`.
- Verificações locais com modelo spaCy real e fallback forçado.
- Mascaramento dos nomes testados: Paulo, Bianca Ferraz, Renata Moura, Carolina Teixeira e Bruno Carvalho.
- Preservação dos locais e termos técnicos testados no caminho com o modelo real.

Esses resultados pertencem à revisão local da branch. Não comprovam que a correção já está implantada ou homologada pela interface.

### Limitações

- A anonimização não deve ser tratada como garantia de remoção de todos os dados pessoais.
- O fallback mascarou os nomes isolados testados, mas apresentou falsos positivos em palavras comuns, cidades e termos técnicos.
- Exemplos observados pela revisora incluem “Estudei SQL”, “Porto Alegre” e “Cloud Foundations”.
- Os resultados dos casos testados não devem ser generalizados para todos os nomes, termos ou contextos.
- A declaração de dados reais ou fictícios não comprova que a anonimização foi suficiente.
- Para uso de mensagens reais, é necessário confirmar a disponibilidade do modelo ou encaminhar o conteúdo para revisão humana antes do envio ao provedor.
- Implantação do #64 e reteste pela interface continuam pendentes.

Para demonstração e retestes, utilize dados fictícios.

## Integração das telas com os serviços

As telas utilizam `app/services/data_service.py` como ponto de acesso à análise, à rastreabilidade e ao armazenamento. A integração com LLM e OCI já está implementada.

| Função | Comportamento atual |
|---|---|
| `analisar(interacoes)` | Encaminha as interações para análise pelo serviço de LLM. |
| `regenerar(historia, ativo_id, vez)` | Alterna entre variações disponíveis no ativo; não solicita nova geração ao LLM. |
| `listar_pacotes()` | Consulta os objetos persistidos no bucket. |
| `salvar_no_oci(pacotes, lote_id, historias=None, natureza_dados=None)` | Grava os pacotes do lote com os dados fornecidos. |
| `reenviar_pacote(pacote)` | Tenta novamente a gravação de um pacote que falhou. |
| `conteudo_pacote(caminho)` | Lê o JSON de um objeto armazenado. |

### Armazenamento no OCI

O módulo `app/services/oci_storage.py` realiza a gravação e a leitura dos pacotes.

Configuração:

- `OCI_BUCKET_NAME` — nome do bucket.
- `OCI_NAMESPACE` — namespace do tenancy.
- `OCI_CONFIG_FILE` — caminho do arquivo de configuração OCI.
- `OCI_PROFILE` — perfil utilizado no arquivo de configuração.

A autenticação por chave de API utiliza o arquivo de configuração OCI e a chave privada. Credenciais não devem ser incluídas no repositório.

Os objetos são organizados por lote:

```text
ativos/<lote_id>/<arquivo>.json
```

Repetir a gravação do mesmo lote e arquivo utiliza o mesmo caminho, evitando criar outro objeto apenas pela repetição da operação.

O pacote principal utiliza a versão **1.1** e registra a natureza declarada dos dados. O arquivo `evidencias.json` permanece na versão **1.0**.

Consulte o [contrato de integração](docs/CARD05_CONTRATOS_INTEGRACAO.md).

### Real, simulado e falha

Os resultados de armazenamento distinguem:

- `status`: `salvo` ou `falhou`.
- `persistencia`: `real` ou `simulada`.
- `motivo`: explicação quando não houve gravação real.

Sem credenciais configuradas:

- Nada é gravado no bucket.
- A tentativa retorna falha com motivo.
- A listagem retorna vazia.
- Não deve aparecer sucesso de gravação real.

As simulações de interface não comprovam persistência no OCI.

As evidências de bucket privado, autenticação, permissões, acesso negado e condições gratuitas da conta continuam acompanhadas no Card 18. O rótulo visual “OCI Always Free” não comprova a modalidade ou o consumo da conta.

### Persistência e recuperação editorial

O PR #57 integrou a gravação de decisões de curadoria e campos editados.

Isso não equivale à recuperação completa do lote para continuar a edição em outra sessão.

Permanecem pendentes:

- Reteste funcional da persistência na versão consolidada.
- Recuperação completa dos textos editados e das decisões em nova sessão.
- Validação integrada dos cases do #67.
- Revisão, integração e validação dos testemunhos do #68.

## Formatos de ativos

A interface possui suporte a campos editáveis conforme o tipo de ativo recebido. Implementação, implantação e homologação de cada formato são etapas distintas.

| Formato | Situação em 22/11/2026 |
|---|---|
| Post para LinkedIn e card de conquista | Presentes no fluxo existente; sujeitos à revisão de fidelidade e curadoria. |
| Case de sucesso | PR #67 integrado em `07ae36c`; implantação e validação integrada pendentes. |
| Testemunho estruturado | PR #68 em revisão, com base main e correção complementar em `016c12d`. |

### Case de sucesso — Card 14 / PR #67

A análise pode solicitar um case na mesma chamada dos formatos existentes.

A primeira versão utiliza narrativa extrativa: trechos da fonte, sem paráfrase livre, em `campos.texto`, com título opcional como metadado e vínculo à interação de origem.

Case sem resultado ou citação literal sustentados é omitido. A história permanece para revisão com aviso.

Edição e Curadoria utilizam o fluxo existente. A geração não aprova o conteúdo nem autoriza publicação.

O PR #67 foi aprovado por Jaqueline e integrado à main em `07ae36c`. Os testes locais não substituem a validação com provedor e OCI reais.

A verificação literal não comprova, sozinha, a fidelidade contextual da narrativa.

Consulte a [documentação do Card 14](docs/CARD14_CASES_SUCESSO.md).

### História preservada sem ativos

A revisão do #67 identificou um problema visual: uma história sem ativos pode aparecer com o indicador “Rejeitado”, porque a avaliação de todos os estados sobre uma lista vazia retorna verdadeiro.

Esse indicador não representa uma decisão humana registrada.

O achado foi classificado como não bloqueante para a integração do #67. A correção da interface para mostrar “Sem ativos gerados” ou omitir o indicador continua pendente nesta referência.

### Testemunho estruturado — PR #68

A proposta organiza título, descrição e citação com rastreabilidade à fonte.

Após a integração do #67, a base do #68 foi ajustada para main.

Jaqueline relatou quatro recusas de testemunhos em duas rodadas com IA real, causadas pela exigência de igualdade exata entre a citação do testemunho e uma evidência conferida da história.

O commit complementar `016c12d` propõe:

- Tolerar diferenças de espaços e pontuação final na comparação com a evidência.
- Aceitar citação literal ampliada que contenha a evidência inteira.
- Manter a exigência de existência do trecho na fonte e de correspondência da interação.
- Recusar trechos menores que cortem a evidência, inclusive os casos de negação cobertos pelos testes.
- Preservar a recusa de conteúdo inventado ou atribuído a outra origem.

Marcus informou **34 testes específicos** e **3.744 testes da suíte completa** aprovados nessa versão. Essas execuções não fizeram chamadas reais à IA ou OCI.

A correção aguarda nova revisão e repetição dos casos com modelo real. O CATP-008 não é aprovado automaticamente por esses testes locais.

O helper de conversão canônica não deve ser apresentado como exportação automática já integrada.

## Estrutura principal

```text
app/
  main.py
  state.py
  styles.py
  telas/
    dashboard.py
    importacao.py
    processamento.py
    historias.py
    estudio.py
    curadoria.py
    historico.py
  services/
    data_service.py
    llm.py
    llm_provider.py
    prompt_analise.txt
    conferencia_citacao.py
    oci_storage.py
    cases.py
  mocks/
    mock_data.py
src/
  preprocessing/
docs/
tests/
.streamlit/
  config.toml
requirements-front.txt
```

A estrutura acima destaca os componentes principais; não é uma listagem completa do repositório.

O módulo `cases.py` foi integrado pelo #67. Os arquivos de testemunhos do #68 devem ser considerados parte da main somente após sua integração.

## Modo demonstração

Os controles de demonstração permitem exercitar estados da interface, como:

- Falha de gravação e nova tentativa.
- Histórico vazio.
- Carregamento.
- Erro de conexão.
- Reinício da demonstração.

A variável `COMMUNITYLAB_DELAY` ajusta o intervalo das etapas visuais do processamento.

Esses controles não substituem chamadas reais aos serviços nem comprovam que uma operação ocorreu no bucket.

A natureza declarada dos dados é independente do uso de controles de demonstração.

## Verificação das alterações

Para verificar problemas de espaços e formatação no diff:

```bash
git diff --check
```

Para executar os testes da pasta oficial, com as dependências de desenvolvimento instaladas:

```bash
python -m pytest -q tests
```

Resultados de testes pertencem à versão e ao ambiente em que foram executados. Não some contagens de suítes diferentes nem apresente testes locais como homologação da versão implantada.

## Limitações conhecidas e validações pendentes

- A IA pode produzir classificações ou narrativas inadequadas; a revisão humana continua necessária.
- Falhas dos provedores são apresentadas como erro, sem substituição por histórias fictícias.
- A nova tentativa após truncamento pode falhar novamente.
- A conferência de citações não comprova a fidelidade do ativo inteiro.
- O #64 está integrado, mas a implantação e o reteste pela interface continuam pendentes.
- O fallback de anonimização pode mascarar palavras comuns, cidades e termos técnicos indevidamente.
- Cases do #67 estão integrados, mas ainda dependem de implantação e validação integrada.
- O indicador de história sem ativos pode mostrar uma rejeição que não foi decidida por uma pessoa; correção de interface pendente.
- Testemunhos do #68 e sua correção de citações aguardam nova revisão e validação com IA real.
- A recuperação editorial completa em nova sessão continua pendente.
- A nota de exemplo fictício da Importação ainda depende da origem do lote.
- “Copiar texto” disponibiliza um bloco com o recurso de cópia do Streamlit.
- A configuração e as condições gratuitas da conta OCI dependem das evidências do Card 18.
- É necessário confirmar o SHA implantado e retestar a versão consolidada pela interface.
- A homologação geral do MVP e o aceite expresso são acompanhados no Card 23.

## Como contribuir

1. Utilize uma branch específica para a alteração.
2. Edite as telas em `app/telas/` e os serviços correspondentes em `app/services/`.
3. Preserve a separação entre exemplos fictícios e resultados dos serviços reais.
4. Não inclua credenciais ou dados pessoais nos exemplos.
5. Descreva o escopo, os testes e as limitações no Pull Request.
6. Vincule o PR ao card do Trello correspondente.
7. Solicite revisão técnica antes da integração.
8. Atualize a documentação conforme o comportamento efetivamente implementado.

**Princípio do produto:** a IA sugere, o time decide. Nada é publicado automaticamente.