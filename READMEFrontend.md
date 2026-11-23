# CommunityLab · Front-end (Streamlit)

Interface do CommunityLab integrada à análise por LLM, à curadoria humana e ao OCI Object Storage. Permite importar interações, consultar histórias detectadas, editar rascunhos e registrar decisões de curadoria.

Situação documental conferida em **22/11/2026**. Código integrado à main, implantação e homologação funcional são etapas distintas.

Os exemplos fornecidos para demonstração usam dados fictícios. Na Importação, a natureza de cada lote é declarada como fictícios, reais ou não informado. Essa declaração não é deduzida pelo provedor de IA nem comprova anonimização.

> Os conteúdos gerados são rascunhos sujeitos à revisão humana. Validação factual, aprovação editorial e autorização para publicação são controles separados. Nada é publicado automaticamente.

## Estado das integrações e da implantação

| Entrega | Situação |
|---|---|
| Persistência de decisões e campos editados — #57 | Integrada. A reabertura do lote pelo Histórico foi implementada e testada com bucket simulado; falta conferir com o OCI real. |
| Conferência de citações — #59 | Integrada ao Estúdio e à Curadoria. |
| Identificação do ambiente de análise — #60 | Integrada; identifica processamento/provedor, não a natureza das mensagens. |
| Tratamento de resposta truncada — #61 | Integrado, com nova tentativa sobre o mesmo lote. |
| Natureza dos dados — #62 e #63 | Integrada ao pacote e à interface. |
| Correção de anonimização — #64 | Integrada em `fcc077e` e implantada na VM conforme registro de Luciene. |
| Cases de sucesso — #67 | Integrados em `07ae36c`. |
| Testemunhos estruturados e correção de citações — #68 | Integrados em `a4ca159`, incluindo a correção `016c12d`. |
| Indicador de história sem ativos — #73 | Integrado em `d33de32`; apresenta “Sem ativos gerados”, em cinza. |

### Última implantação confirmada

Luciene informou uma implantação em **22/11/2026, às 19h28, horário de Brasília**, com:

- SHA `fcc077e`, correspondente ao merge do #64.
- Container em execução e com saúde `healthy`.
- Modelo `pt_core_news_sm` carregado.
- Teste resumido de anonimização com resultado OK, com texto mascarado.

Esse registro não inclui os merges posteriores de cases, testemunhos e indicador de história sem ativos.

A implantação consolidada dessas entregas e seus retestes pela interface continuam pendentes. O teste resumido de máscara não equivale à homologação completa da anonimização.

## Identidade visual

O CommunityLab utiliza navegação lateral escura e destaques em violeta.

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
- Textos diretos e compreensíveis.
- Cards com bordas suaves e cantos arredondados.
- Cores acompanhadas de rótulos e explicações.
- A paleta e as diretrizes visuais não substituem uma auditoria de acessibilidade.

## Módulos da interface

| Módulo | Comportamento |
|---|---|
| Dashboard | Apresenta contagens e atalhos. Não equivale ao painel analítico avançado previsto no Card 22. |
| Importação | Recebe CSV, JSON colado ou mensagens do Discord, conforme configuração. Apresenta prévia, filtro por canal, avisos de IDs e declaração da natureza do lote. |
| Histórias | Apresenta histórias detectadas, categorias, relevância, natureza declarada dos dados e acesso ao Estúdio. |
| Estúdio de Conteúdo | Permite consultar evidências e editar os campos dos ativos disponíveis. |
| Curadoria | Permite validar fatos, decidir editorialmente e registrar autorização de publicação. |
| Histórico | Lista pacotes persistidos no OCI, permite visualizar o JSON, baixar os objetos disponíveis e reabrir um lote salvo para continuar a revisão. |

### Fluxo de trabalho

1. Carregar as interações.
2. Declarar a natureza dos dados antes de confirmar a importação.
3. Importar e processar o lote.
4. Consultar histórias e evidências.
5. Editar rascunhos no Estúdio.
6. Registrar decisões na Curadoria.
7. Consultar os pacotes no Histórico.
8. Se precisar, reabrir um lote salvo pelo Histórico e continuar a revisão.

### Reabrir um lote pelo Histórico

Cada pacote principal da tabela tem o botão **Reabrir**. Ele lê o pacote salvo no bucket e leva para a Curadoria, sem repetir a análise pela IA.

O que volta do pacote:

- as histórias, com os textos já editados (campos estruturados do testemunho e do case);
- as três dimensões da Curadoria de cada ativo (validação factual, status editorial e autorização);
- o parecer, no campo certo: observação para **Ajustes solicitados** e motivo para **Rejeitado**;
- a natureza declarada dos dados e a origem da análise;
- os contadores, calculados a partir desses estados.

O que não volta:

- as **interações originais**: o pacote guarda só as histórias e os trechos citados. Em lote reaberto, o KPI de interações mostra "—" e a conferência de citações informa "Conferência indisponível: a mensagem original não é guardada no pacote". Guardar as interações anonimizadas exigiria mudar o contrato do pacote e depende de acordo com a equipe.

Regras de uso:

- Com um lote já aberto na sessão, o sistema pede confirmação antes de substituí-lo. Se houver decisão não gravada no bucket, o aviso é mais forte.
- Tudo do lote anterior sai da sessão: decisões, edições, filtros, interações e pacotes. A decisão seguinte é gravada no pacote do lote reaberto.
- Lote antigo (schema 1.0) ou sem decisões gravadas abre com tudo pendente, em rascunho e sem autorização, com um aviso na Curadoria. A natureza ausente aparece como "não informada".
- Se houver mais de um pacote principal do mesmo lote, abre o mais recente e avisa.
- Se a leitura falhar, a sessão atual é mantida e a tela mostra o motivo. Nenhum dado fictício é usado no lugar.
- Pacote fora do formato do app (por exemplo, o teste antigo `TESTE-001`, com `id_historia` e sem `ativos`) é recusado, com a sessão intacta. Cada história precisa ter `id` e `ativos` em lista. Se só parte das histórias estiver fora do formato, o pacote inteiro é recusado: descartar essas histórias as apagaria do bucket na próxima decisão.
- O diálogo de confirmação fecha ao cancelar e ao reabrir. Com a tabela ainda carregando, o clique espera a execução em andamento (ver Limitações). O rodapé do Histórico informa que o pacote guarda histórias, trechos citados e rascunhos, não as mensagens originais.

A função de serviço é `recuperar_lote` em `app/services/data_service.py`.

### Histórias sem ativos

Uma história preservada sem ativos apresenta o indicador cinza **Sem ativos gerados**.

A ausência de ativos não é apresentada como rejeição editorial. O #73 corrigiu a avaliação de uma lista vazia de estados, que anteriormente produzia o indicador “Rejeitado”.

A correção preserva os estados de revisão humana pendente, rejeição e revisão concluída quando existem ativos.

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
- A ação **Regenerar** alterna entre variações já disponíveis. Não realiza uma nova chamada ao LLM; sem variações, mantém o conteúdo.

O #57 integrou a persistência de decisões e campos editados no pacote. O reteste funcional da versão consolidada permanece pendente. A recuperação em nova sessão está descrita em [Reabrir um lote pelo Histórico](#reabrir-um-lote-pelo-histórico).

## Como executar

Pré-requisito: **Python 3.11 ou superior**, com dependências compatíveis com a versão utilizada.

O `pyproject.toml` exige Python `>=3.11`. A imagem Docker utiliza `python:3.11-slim`.

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
python -m pip install -e .
```

Inicie a aplicação:

```bash
python -m streamlit run app/main.py
```

O endereço local padrão é `http://localhost:8501`.

A execução integrada também depende da configuração dos provedores e do armazenamento.

Consulte:

- [Instruções gerais de execução](COMO_RODAR.md)
- [Guia de implantação na VM Oracle](docs/DEPLOYMENT_ORACLE_VM.md)

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

### Streamlit Community Cloud

No gerenciamento do aplicativo:

1. Abra **Settings**.
2. Acesse **Secrets**.
3. Informe as chaves e os modelos necessários no formato TOML.
4. Clique em **Save**.
5. Se necessário, utilize **Reboot**.

Os nomes e a posição dos controles podem variar conforme a interface do serviço.

As credenciais pertencem às configurações do aplicativo, nunca ao repositório.

### Identificação do ambiente de análise

O Processamento apresenta um dos rótulos:

- **Demonstração**
- **Análise real (Gemini)**, **Análise real (Cohere)** ou **Análise real (Groq)**, conforme o provedor que respondeu
- **Não confirmado**

O rótulo identifica o processamento/provedor utilizado. Ele não determina se as mensagens são reais ou fictícias e não comprova sua anonimização.

### Respostas truncadas

O #61 integrou tratamento específico para respostas encerradas com `MAX_TOKENS`.

A interface permite nova tentativa sobre o mesmo lote. Pode ser necessário reduzir o lote ou ajustar `LLM_MAX_OUTPUT_TOKENS`.

A nova tentativa não garante sucesso, e aumentar o limite depende das condições do modelo utilizado.

## Natureza declarada dos dados

Na Importação, antes de confirmar o lote, a pessoa declara:

| Valor | Rótulo na interface |
|---|---|
| `ficticios` | Fictícios (exemplo ou teste) |
| `reais` | Reais (relatos de pessoas) |
| `nao_informado` | Não informado |

### Comportamento

- O padrão é **Não informado**.
- Um lote novo não herda a declaração do lote anterior.
- Reiniciar a demonstração também retorna a declaração ao padrão.
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

O valor é preservado como `natureza_dados` no pacote principal. Consulte o [contrato de integração](docs/CARD05_CONTRATOS_INTEGRACAO.md).

### Rótulos demonstrativos ainda pendentes de alinhamento

A nota “Exemplo fictício…” da Importação ainda depende da origem do lote, embora a declaração seja independente.

O componente de evidências citadas utiliza `modo_demonstracao=True` por padrão, e as telas não substituem esse valor. Por isso, o chip **Exemplo de demonstração** também pode aparecer com análise real e dados declarados como reais.

Esses rótulos não devem ser usados como prova da natureza dos dados. O alinhamento com a declaração do lote permanece pendente.

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

### Exemplo de entrada

Os registros abaixo são fictícios:

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

Uma colisão entre um ID explícito e um ID derivado da posição também provoca rejeição do lote.

### Exibição dos IDs

- **Importação:** coluna ID na prévia das interações.
- **Estúdio e Curadoria:** ID da interação nos metadados, separado do lote.
- **Evidências citadas:** identificação “interação nº N”.
- **Origem sem ID válido:** apresentação “ID não informado”, em vez de “ID 0”.

As regras possuem cobertura em `tests/test_front_ids.py`.

## Conferência de citações

Cada citação é conferida contra a interação indicada pelo seu `id_interacao`.

A regra está em `app/services/conferencia_citacao.py`. As telas utilizam as funções disponibilizadas pelo `data_service`.

| Resultado | Apresentação | Significado |
|---|---|---|
| Trecho literal conferido | Verde | O trecho corresponde ao texto da interação, sem marcador. |
| Compatível com anonimização · a parte mascarada não é conferida | Azul | A parte não mascarada corresponde ao original; o dado ocultado não é conferido. |
| Não confere | Amarelo, com motivo | O trecho apresenta incompatibilidade com a fonte. |
| Conferência indisponível | Neutro | A interação não está disponível ou a origem é ambígua. |
| ID não informado | Neutro | O ID está ausente ou inválido. |

### Onde aparece

- Nas evidências citadas do Estúdio e da Curadoria.
- Abaixo do campo Citação editável do testemunho, com revalidação após alterações.

O campo editável utiliza a origem da história. Quando há mais de uma origem ou nenhuma origem disponível, a conferência não adivinha qual utilizar.

### Limites da conferência

- O resultado é individual por citação; não existe selo geral de fidelidade por ativo.
- O azul não representa aprovação factual.
- Um termo mascarado indevidamente pode ser considerado compatível com anonimização.
- A presença literal de um trecho não comprova que toda a narrativa respeita o contexto.
- A conferência do campo Citação não equivale à conferência de todos os campos editáveis.
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

### Modelo e fallback por ambiente

Na imagem Docker, o modelo `pt_core_news_sm` é instalado e validado durante o build.

Em ambientes sem o modelo, incluindo a execução no Streamlit Cloud quando ele não está disponível, a anonimização de nomes utiliza fallback heurístico de melhor esforço.

O caminho efetivamente utilizado depende da disponibilidade do modelo no ambiente. Não deduza seu carregamento apenas pelo serviço de hospedagem.

Na VM, o registro de Luciene de 22/11 às 19h28 confirmou o modelo carregado no SHA `fcc077e`.

### Correção integrada — #64

O #64 foi aprovado por Tissiany e integrado à main em `fcc077e`.

Na revisão do head `f929124`, a revisora relatou:

- **3.682 testes aprovados**.
- Verificações locais com modelo spaCy real e fallback forçado.
- Mascaramento dos nomes testados: Paulo, Bianca Ferraz, Renata Moura, Carolina Teixeira e Bruno Carvalho.
- Preservação dos locais e termos técnicos testados no caminho com o modelo real.

Esses números pertencem à revisão daquela versão e não foram reexecutados para esta atualização documental.

A implantação do #64 está confirmada pelo registro da VM. O reteste completo pela interface continua pendente.

### Limitações

- A anonimização não é garantia de remoção de todos os dados pessoais.
- O fallback mascarou os nomes isolados testados, mas apresentou falsos positivos em palavras comuns, cidades e termos técnicos.
- Exemplos observados incluem “Estudei SQL”, “Porto Alegre” e “Cloud Foundations”.
- Os resultados testados não devem ser generalizados para todos os nomes, termos ou contextos.
- A declaração de dados reais ou fictícios não comprova que a anonimização foi suficiente.
- Para mensagens reais, confirme o caminho de anonimização utilizado e a suficiência da preparação antes do envio ao provedor.

Para demonstração e retestes, utilize dados fictícios.

## Integração das telas com os serviços

As telas utilizam `app/services/data_service.py` como ponto de acesso à análise, à rastreabilidade e ao armazenamento. A integração com LLM e OCI está implementada.

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

As evidências de bucket privado, autenticação, permissões, acesso negado e condições gratuitas da conta continuam acompanhadas no Card 18.

O rótulo visual “OCI Always Free” não comprova a modalidade ou o consumo da conta.

### Persistência e recuperação editorial

O #57 integrou a gravação de decisões de curadoria e campos editados.

O botão **Reabrir** do Histórico reconstrói a sessão a partir do pacote: histórias, textos editados, decisões e pareceres. Os testes automatizados usam um bucket simulado e cobrem o cenário do CATP-022 (pedir ajuste, abrir sessão nova, reabrir pelo Histórico e ver a observação no mesmo ativo). Consultar o JSON salvo, por si só, não comprova a reconstrução; ela deve ser conferida na interface com o OCI real.

As interações originais não são guardadas no pacote e, por isso, não voltam ao reabrir.

Permanecem pendentes:

- Reteste funcional da persistência na versão consolidada.
- Conferência da reabertura de lote na interface com o OCI real (os testes automatizados usam bucket simulado).
- Decisão da equipe sobre guardar as interações anonimizadas no pacote.
- Validação integrada dos cases e testemunhos na VM.
- Verificação de leitura de lotes antigos com os campos opcionais novos.

## Formatos dos dados e contratos

O contrato e os esquemas de integração são documentados em:

- [Contrato de integração — Card 05](docs/CARD05_CONTRATOS_INTEGRACAO.md)
- [Testemunhos estruturados — Card 13](docs/CARD13_TESTEMUNHOS_ESTRUTURADOS.md)
- [Cases de sucesso — Card 14](docs/CARD14_CASES_SUCESSO.md)

A representação interna do front e o contrato canônico são estruturas distintas. Não substitua uma pela outra sem adaptação explícita.

### Interações

As interações de entrada utilizam campos como:

- `id`, quando informado.
- `autor`.
- `canal`.
- `tipo`.
- `texto`.

O ID efetivo é calculado antes dos filtros e preservado durante o processamento.

### Histórias e campos aditivos

A representação interna das histórias inclui:

- Identificador da história.
- Autor e canal.
- Categoria e sentimento.
- Relevância numérica e `relevancia_nivel`.
- `mensagem_original`.
- `citacoes`, com texto e `id_interacao`.
- `interacoes_origem`.
- `destaques`.
- Fatos e ativos disponíveis.

`citacoes`, `interacoes_origem`, `relevancia_nivel` e `destaques` fazem parte da evolução aditiva do formato e devem ser preservados nos mapeamentos aplicáveis.

As citações e os destaques são vinculados à fonte conferida. A relevância é uma classificação do processamento, não uma probabilidade ou garantia de veracidade.

### Ativos do front

Os ativos utilizam identificadores, nome, tipo de apresentação e `campos`.

Os tipos de apresentação do formulário não devem ser confundidos com os tipos do contrato canônico. Por exemplo, o case é apresentado como `tipo="texto"` e o testemunho como `tipo="testemunho"`.

Quando disponíveis, os vínculos incluem:

- `interacoes_origem`.
- `citacoes`.
- `fontes`.

A estrutura de uma fonte utiliza campos como:

```json
{
  "afirmacao": "Trecho relacionado ao conteúdo",
  "fato": "Descrição do vínculo com a evidência",
  "trecho": "Trecho literal da interação de origem"
}
```

Esse exemplo descreve a forma do vínculo e não constitui evidência de um relato real.

### Pontos de alinhamento entre front, serviços e contrato

- Manter o mapeamento entre IDs internos e IDs canônicos.
- Preservar os campos estruturados dos testemunhos.
- Documentar título do case como metadado na raiz do ativo, exibido como legenda e separado da narrativa.
- Alinhar título opcional no contrato canônico com sua exigência atual na geração e no helper de testemunho.
- Definir o tratamento de título apagado durante a curadoria.
- Documentar a relação entre campos editados e citações/fontes originais preservadas.
- Definir o destino dos campos opcionais `revisor`, `observacao_revisor` e `id_avaliacao_cqf`.
- Validar os pacotes completos e a leitura de lotes antigos.
- Não apresentar o helper de conversão de testemunho como exportador canônico geral.

## Formatos de ativos

A interface possui suporte a campos editáveis conforme o tipo de ativo recebido.

| Formato | Situação em 22/11/2026 |
|---|---|
| Post para LinkedIn e card de conquista | Presentes no fluxo existente; sujeitos à revisão de fidelidade e curadoria. |
| Case de sucesso | #67 integrado em `07ae36c`; implantação consolidada e validação na VM pendentes. |
| Testemunho estruturado | #68 integrado em `a4ca159`, incluindo `016c12d`; revisão e reteste dos casos com modelo real realizados, com validação na VM pendente. |

### Case de sucesso — Card 14 / #67

A análise pode solicitar um case na mesma chamada dos formatos existentes.

A primeira versão utiliza narrativa extrativa: trechos da fonte, sem paráfrase livre, em `campos.texto`, com vínculo à interação de origem.

O título é opcional na geração. Quando presente, fica como metadado na raiz do ativo e é exibido como legenda, separado do texto, sem edição nesta versão.

A geração confere:

- Narrativa formada por trechos literais da fonte, na ordem.
- Presença de resultado ou avanço literal na narrativa.
- Presença de citação conferida da mesma interação.
- Título, quando presente, como trecho da fonte.

Case recusado pela conferência é omitido, e a história permanece para revisão com aviso.

A seção **Fontes deste conteúdo** apresenta as fontes derivadas das citações conferidas, com a indicação “Trecho literal da interação de origem”.

O texto do case é editável no Estúdio e na Curadoria.

**Limitação:** não existe conferência automática no campo Texto do case nem aviso quando a edição deixa de corresponder a trechos da fonte. Os vínculos exibidos não devem ser interpretados como validação automática do texto editado.

A presença literal de uma expressão não comprova conquista, resultado ou fidelidade contextual. Negação, expectativa e esforço sem resultado continuam exigindo avaliação humana.

Tissiany relatou validação do fluxo com análise real pela interface, além de testes locais e do validador do Card 05. OCI e recuperação em nova sessão não foram verificados nessa revisão.

Consulte a [documentação do Card 14](docs/CARD14_CASES_SUCESSO.md).

### Testemunho estruturado — Card 13 / #68

O testemunho vem da análise integrada e utiliza:

- `campos.titulo`.
- `campos.descricao`.
- `campos.citacao`.

Os três campos são editáveis no Estúdio e na Curadoria.

Na geração, os três precisam corresponder a trechos literais da fonte. Título e descrição continuam usando correspondência exata; a citação recupera o trecho da fonte tolerando espaços equivalentes.

A citação também precisa conter a evidência conferida inteira e pertencer à mesma interação.

A correção `016c12d`:

- Tolera diferenças de espaços e pontuação final na comparação com a evidência.
- Aceita citação literal ampliada que contenha a evidência inteira.
- Mantém a exigência de existência do trecho na fonte.
- Mantém a correspondência da interação.
- Recusa os casos testados de trechos menores que a evidência, conteúdo inventado e evidência de outra origem.

A tolerância na comparação não autoriza inventar pontuação ou texto ausente na fonte.

A conferência visual da citação aparece abaixo do campo Citação nas duas telas e é recalculada após edições.

O pacote preserva os campos estruturados `titulo`, `descricao` e `citacao`. O preenchimento posterior do formulário utiliza esses campos.

Após edição, `citacoes` e `fontes` podem continuar preservando os valores originais, enquanto `campos` contém a versão editada. Essa diferença exige documentação e alinhamento contratual; não significa que a versão editada foi automaticamente conferida como um todo.

#### Conversão canônica

`converter_testemunho_canonico` é um helper de projeção inicial.

Ele compõe o texto canônico com descrição, duas quebras de linha e citação entre aspas. Não é um exportador geral integrado, não restaura o Histórico e não exporta automaticamente as decisões da Curadoria.

O helper exige título preenchido, embora o contrato canônico o trate como opcional. Esse alinhamento permanece pendente.

#### Evidências de revisão

- Marcus informou 34 testes específicos e 3.744 testes da suíte aprovados no head `016c12d`, sem chamadas reais à IA ou OCI.
- Jaqueline repetiu os casos com modelo real: quatro de quatro testemunhos aceitos, em duas rodadas de duas interações, além de 51 testes locais de testemunho e case aprovados.
- Tissiany confirmou 3.744 testes no head e 3.793 após merge local com a main, validador do Card 05 e verificações de interface com AppTest.
- As contagens se referem às versões e aos ambientes dessas execuções. Não foram reexecutadas nesta atualização documental.

O reteste positivo dos casos corrigidos não encerra automaticamente o CATP-008 nem a homologação do MVP.

Permanecem pendentes a validação na implantação consolidada, os demais cenários aplicáveis, OCI e a conferência da reabertura de lote com o OCI real.

Consulte a [documentação do Card 13](docs/CARD13_TESTEMUNHOS_ESTRUTURADOS.md). As contagens históricas e a descrição anterior da igualdade de citações nesse documento também precisam ser conciliadas com `016c12d`.

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
    testemunhos.py
  mocks/
    mock_data.py
src/
  preprocessing/
docs/
tests/
.streamlit/
  config.toml
pyproject.toml
Dockerfile
```

A estrutura destaca os componentes principais; não é uma listagem completa do repositório.

## Modo demonstração

Os controles da barra lateral permitem exercitar estados da interface, como:

- Falha de gravação e nova tentativa.
- Histórico vazio.
- Carregamento.
- Erro de conexão.
- Reinício da demonstração.

A variável `COMMUNITYLAB_DELAY` ajusta o intervalo das etapas visuais do processamento.

Esses controles não substituem chamadas reais aos serviços nem comprovam que uma operação ocorreu no bucket.

A natureza declarada dos dados é independente do uso dos controles de demonstração.

Existe uma pendência visual observada no expansor Modo demonstração: fundo branco e texto sem visibilidade adequada no seletor Estado da tela Histórico. O estilo precisa de conferência e ajuste.

## Verificação das alterações

Para verificar problemas de espaços e formatação no diff:

```bash
git diff --check
```

Para instalar o projeto com dependências de desenvolvimento:

```bash
python -m pip install -e ".[dev]"
```

Para executar os testes da pasta oficial:

```bash
python -m pytest -q tests
```

Para conferir os exemplos canônicos do Card 05:

```bash
python scripts/validar_exemplos_card05.py
```

Resultados de testes pertencem à versão e ao ambiente em que foram executados.

Não some contagens de suítes diferentes nem apresente testes locais como homologação da versão implantada.

## Limitações conhecidas e validações pendentes

- A IA pode produzir classificações ou narrativas inadequadas; revisão humana continua necessária.
- Literalidade não comprova contexto, conquista, resultado ou ausência de contradição.
- Evidência que já omitiu uma negação pode passar nas verificações mecânicas; a recusa de citação menor não resolve todos os casos de contexto.
- Falhas dos provedores são apresentadas como erro, sem substituição por histórias fictícias.
- A nova tentativa após truncamento pode falhar novamente.
- A conferência de citações não comprova a fidelidade do ativo inteiro.
- O #64 está implantado na VM no último registro disponível, mas o reteste completo pela interface permanece pendente.
- O fallback de anonimização pode mascarar palavras comuns, cidades e termos técnicos indevidamente.
- Cases e testemunhos estão integrados à main, mas não constam da última implantação confirmada.
- O texto editado do case não possui conferência automática nem aviso de perda de correspondência com a fonte.
- Título e descrição do testemunho ainda exigem correspondência exata de espaços; uma descrição que una linhas da fonte pode ser recusada.
- O título do testemunho é obrigatório na geração e no helper, mas opcional no contrato canônico.
- Os campos editados e as citações/fontes originais podem divergir no pacote; o tratamento contratual precisa ser explicitado.
- Os avisos Case pendente e Testemunho pendente podem aparecer mesmo quando não gerar o formato é uma resposta adequada.
- Os motivos desses avisos incluem linguagem técnica e nomes de campos; sua apresentação precisa ser melhorada para a pessoa que faz curadoria.
- O Histórico consulta o bucket uma vez por execução para listar os pacotes (cerca de 2,7 s no OCI real). O botão **⬇ Baixar** de cada linha abre o diálogo do JSON, que já traz o botão de baixar, e só lê o objeto no clique. Antes, a tabela lia todos os objetos a cada execução (cerca de 0,5 s por objeto, ~40 s com 71 objetos). Cliques feitos enquanto a lista ainda carrega esperam essa execução. Ainda não há cache da lista de pacotes; isso fica para outra entrega.
- Em lote reaberto pelo Histórico, as interações originais não voltam (KPI "—" e conferência de citações indisponível); a reabertura ainda precisa ser conferida com o OCI real.
- A nota de exemplo fictício da Importação ainda depende da origem do lote.
- O chip Exemplo de demonstração nas evidências pode aparecer independentemente da natureza declarada e do provedor real.
- O expansor Modo demonstração possui pendência de estilo e legibilidade.
- Copiar texto disponibiliza um bloco com o recurso de cópia do Streamlit.
- As condições da conta OCI e suas evidências continuam acompanhadas no Card 18.
- A homologação geral e o aceite expresso são acompanhados no Card 23.

## Como contribuir

1. Utilize uma branch específica para a alteração.
2. Edite as telas em `app/telas/` e os serviços correspondentes em `app/services/`.
3. Preserve a separação entre exemplos fictícios e resultados dos serviços reais.
4. Não inclua credenciais ou dados pessoais nos exemplos.
5. Descreva o escopo, os testes e as limitações no Pull Request.
6. Vincule o PR ao card do Trello correspondente.
7. Solicite revisão técnica antes da integração.
8. Documente mudanças de formato no README e no contrato de integração.
9. Atualize a documentação conforme o comportamento efetivamente implementado.

**Princípio do produto:** a IA sugere, o time decide. Nada é publicado automaticamente.