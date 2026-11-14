# CommunityLab · Front-end (Streamlit) 

Interface do CommunityLab, feita em Streamlit. Por enquanto ela funciona sozinha, com **dados fictícios**, para o time poder ver e validar o fluxo antes de o back ficar pronto.

> Todos os nomes, mensagens e depoimentos do front são inventados. Nada aqui representa pessoas reais.

## Identidade Visual

O CommunityLab usa um estilo híbrido **SaaS corporativo + IA**, com visual limpo, profissional e acessível.

### Paleta de cores

| Cor                  | Código                                  | Uso                                                |
| -------------------- | --------------------------------------- | -------------------------------------------------- |
| **Azul-marinho**     | `#101B32`                               | Sidebar e navegação                                |
| **Violeta**          | `#7C3AED`                               | Cor primária, ações de IA e destaques              |
| **Ciano**            | `#22D3EE`                               | Detalhes tecnológicos (SOMENTE sobre fundo escuro) |
| **Branco-neutro**    | `#F8FAFC`                               | Fundo da área de trabalho                          |
| **Verde**            | `#10B981` (fundos) / `#047857` (textos) | Sucesso e aprovação                                |
| **Texto principal**  | `#0F172A`                               | Títulos e conteúdo principal                       |
| **Texto secundário** | `#64748B`                               | Labels, legendas e informações auxiliares          |
| **Borda suave**      | `#E2E8F0`                               | Bordas de cards e divisores                        |

### Regras de contraste

- Todos os pares texto/fundo seguem **WCAG AA** (4.5:1 para texto normal, 3:1 para texto grande)
- Verde `#047857` é usado para **texto sobre fundo claro** (legibilidade garantida)
- Ciano `#22D3EE` aparece **apenas sobre azul-marinho** (nunca sobre fundo claro)
- Sidebar escura: texto claro `#F8FAFC` sobre azul-marinho `#101B32`

### Tipografia

- **Fonte:** Inter (pesos 400, 500, 600, 700)
- **Tom:** Natural, direto, sem jargão técnico excessivo
- **Slogan:** "Histórias reais. Impacto inteligente."

### Componentes

- **Cards:** Fundo branco com borda `#E2E8F0`, cantos arredondados (10px)
- **Botões:** Estados normal, hover e ativo com transições suaves
- **Chips:** Cores semânticas (verde = sucesso, amarelo = pendente, vermelho = erro, roxo = IA)
- **Sidebar:** Azul-marinho com destaque violeta no item ativo

## O que o front faz

O fluxo tem 6 módulos, organizados no menu lateral:

| Módulo                  | O que acontece                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Dashboard**           | Visão geral com KPIs (interações, histórias, ativos gerados) e ações rápidas para navegar                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **Importação**          | Upload de CSV/JSON ou JSON colado, com prévia das interações e filtro por canal. Botão "Importar interações" dá início ao processamento                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **Histórias**           | Lista as histórias detectadas com categoria, relevância e trecho original. Filtros por categoria e relevância mínima. Botão "Ver no Estúdio" para cada história                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Estúdio de Conteúdo** | Visualização lado a lado de evidências e rascunhos. Coluna esquerda: mensagem original com destaques, fatos extraídos. Coluna direita: conteúdo editável (Testemunho estruturado ou Case de sucesso), contador de caracteres, seção "Fontes deste conteúdo" com rastreabilidade, botões Regenerar, Copiar e Enviar para curadoria                                                                                                                                                                                                                                           |
| **Curadoria**           | Revisa os rascunhos com três controles independentes: (1) Validação factual (Pendente, Validada, Evidências insuficientes, Contradição não resolvida), (2) Curadoria editorial (Rascunho, Ajustes solicitados, Aprovado, Rejeitado), (3) Autorização de publicação (Não registrada, Registrada). A autorização NÃO bloqueia a aprovação editorial. Regra RG-02: com "Contradição não resolvida", o botão Aprovar fica desabilitado. Regra RG-03: "Liberado para publicação" aparece apenas quando Validada + Aprovado + Registrada. O sistema nunca publica automaticamente |
| **Histórico**           | Lista os pacotes salvos no bucket OCI, com visualização do JSON e download                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

**Fluxo de trabalho:**
1. **Importar** → carregar interações da comunidade
2. **Processar** → análise automática (transição entre Importação e Histórias)
3. **Revisar** → explorar histórias e editar rascunhos no Estúdio
4. **Decidir** → validar, aprovar ou rejeitar na Curadoria
5. **Consultar** → verificar pacotes salvos no Histórico

**Regras de Curadoria (conforme CQF):**
- **Três controles independentes:** Validação factual, Curadoria editorial e Autorização de publicação funcionam de forma separada
- **RG-01:** A interface nunca preenche lacunas com informação inventada. "Regenerar" apenas alterna entre variações fictícias baseadas nas evidências
- **RG-02:** Com "Contradição não resolvida", o botão Aprovar fica desabilitado até que a contradição seja resolvida ou a validação seja alterada
- **RG-03:** O indicador "Liberado para publicação" aparece apenas quando os três controles estão completos: Validação = Validada, Curadoria = Aprovado, Autorização = Registrada
- **Autorização não bloqueia aprovação:** É possível aprovar editorialmente um ativo mesmo sem autorização registrada (útil para análise interna)
- **Nada é publicado automaticamente:** Mesmo com "Liberado para publicação", o sistema não publica. A decisão final é do time

**Princípio do produto:** a IA sugere, o time decide. Nada é publicado automaticamente, e cada ativo gerado aponta para a mensagem original.

## Como rodar

Pré-requisito: Python 3.10 ou superior.

```bash
pip install -r requirements-front.txt
streamlit run app/main.py
```

No Windows, se `streamlit` não for reconhecido:

```bash
python -m streamlit run app/main.py
```

O app abre em `http://localhost:8501`.

## Configuração dos provedores de LLM

A análise tenta os provedores nesta ordem: **Gemini → Cohere → Groq**. Se um provedor não tiver chave configurada ou falhar, o próximo é tentado. O app não substitui uma falha por histórias fictícias.

Configure as chaves em `.streamlit/secrets.toml` ou como variáveis de ambiente:

```toml
GEMINI_API_KEY = "sua-chave-gemini"
GEMINI_MODEL = "gemini-3.6-flash"
COHERE_API_KEY = "sua-chave-cohere"
COHERE_MODEL = "cohere.command-r-plus"
GROQ_API_KEY = "sua-chave-groq"
GROQ_MODEL = "llama-3.1-8b-instant"
LLM_MAX_OUTPUT_TOKENS = 8192
```

O arquivo `.streamlit/secrets.toml` está no `.gitignore` e não deve ser commitado. As credenciais não ficam no código. Se as chamadas aos três provedores falharem, a análise apresenta o erro em vez de exibir histórias fictícias como resultado. O texto do prompt fica em `app/services/prompt_analise.txt`, separado da lógica de integração.

**Streamlit Cloud (app publicado):** abra o app em `share.streamlit.io` → menu `⋮` → **Settings** → **Secrets**, cole as chaves e os modelos necessários e clique em **Save**. Se o app não recarregar sozinho, use **Reboot**. As chaves devem ser cadastradas nas configurações do app, nunca no repositório.

## Rastreabilidade de evidências (CATP-007)

Cada evidência citada está vinculada à interação original através do **ID da interação**. O front implementa validação rigorosa de IDs para garantir rastreabilidade completa.

### Regras de ID de interação

O ID é calculado **uma única vez antes de qualquer filtro ou validação**, seguindo esta ordem:

1. **ID explícito válido:** campo `id` inteiro >= 1 (booleano NÃO conta como inteiro)
2. **ID ausente ou inválido:** posição da interação no lote original, começando em 1

#### IDs inválidos
- Zero (`id: 0`)
- Negativo (`id: -5`)
- Texto (`id: "abc"`)
- Booleano (`id: true` ou `id: false`)

Quando um ID é inválido, o sistema:
- Usa a posição da interação (começando em 1)
- Gera um **aviso visível** na tela de Importação listando as interações afetadas
- **Nunca pode ser silencioso** - o usuário deve saber que IDs foram recalculados

#### IDs duplicados

Se dois ou mais registros têm o mesmo ID efetivo (seja explícito ou por posição), o lote é **rejeitado imediatamente** com mensagem em português detalhando:
- Quais IDs estão duplicados
- Quais interações (autor e posição) colidem
- Isso vale tanto para upload de arquivo quanto para JSON colado
- Exemplo de colisão: primeiro item com `id: 2` explícito, segundo item sem id (vira posição 2)

#### Preservação após filtros

Os IDs calculados são armazenados em `_id_efetivo` e **nunca mudam após filtros**. Exemplo:

```json
[
  {"id": 101, "autor": "Ana", "canal": "#conquistas"},  // ID efetivo: 101
  {"autor": "Bob", "canal": "#geral"},                   // ID efetivo: 2 (posição)
  {"id": 309, "autor": "Carlos", "canal": "#conquistas"} // ID efetivo: 309
]
```

Após filtrar por `#conquistas`, os IDs continuam 101 e 309 (não viram 1 e 2).

### Conferência literal de evidências

A seção "Evidências citadas" no Estúdio e na Curadoria mostra cada trecho com conferência automática:

- ✅ **Selo verde** "Trecho literal conferido" — o trecho existe palavra por palavra no texto da interação
- ⚠️ **Selo amarelo** "Trecho não encontrado na mensagem original" — a interação existe no lote mas o trecho não está nela (NUNCA marca como validada)
- 🔄 **Conferência indisponível** (neutro, sem selo) — a interação com aquele ID não existe no lote atual (exemplo: citação de ID 999 mas o lote só tem IDs 1-10)

**Regra crítica:** o sistema **NUNCA marca automaticamente como validada** quando a interação não existe no lote.

### Modo demonstração

Quando `modo_demonstracao=True` (padrão), as evidências citadas recebem o chip cinza "Exemplo de demonstração" para deixar claro que são dados fictícios.

### Exibição de IDs

- **Importação:** coluna "ID" na prévia das interações
- **Estúdio e Curadoria:** linha "ID da interação" nos metadados (separada do campo "Lote")
- **Evidências citadas:** "interação nº N" para cada trecho
- **ID não informado:** quando `id_interacao` é 0 ou ausente, exibe "ID não informado" em vez de "ID 0"

### Implementação técnica

- **Função centralizada:** `calcular_ids_efetivos(itens)` em `app/services/data_service.py`
  - Retorna lista de IDs, lista de avisos e mensagem de erro (se houver duplicados)
  - Valida unicidade **antes** de qualquer outra operação
  - Campo `_id_efetivo` adicionado a cada interação
- **Compatibilidade:** mesma regra do `llm.py` linha 220 (campo `id` inteiro >= 1, senão posição)
- **Testes:** `tests/test_front_ids.py` cobre 9 cenários sem Streamlit e sem rede

## Modo demonstração

Na barra lateral, em **Modo demonstração**, dá para:

- simular erro ao salvar no OCI (mostra a tela de falha e o botão "Tentar novamente");
- alternar a tela de Histórico entre os estados normal, vazio, carregando e erro de conexão;
- reiniciar a demonstração.

Para acelerar ou desacelerar a simulação do Processamento, use a variável `COMMUNITYLAB_DELAY` (segundos por etapa).

## Estrutura de pastas

```
app/
  main.py                    entrada do app, menu lateral e roteamento
  state.py                   estado da sessão
  styles.py                  CSS e helpers de HTML
  telas/                     uma tela por arquivo
    dashboard.py             (nova) visão geral do sistema
    importacao.py            (era ingestao.py) upload de interações
    processamento.py
    historias.py
    estudio.py               (nova) placeholder para ETAPA 3
    curadoria.py
    historico.py             (era oci.py) consulta de pacotes salvos
  services/
    data_service.py          ÚNICO ponto de contato com os dados
  mocks/
    mock_data.py             dados fictícios
.streamlit/
  config.toml                tema (cores)
requirements-front.txt
```

## Como o back se conecta (importante)

As telas **não** importam o back diretamente. Elas só chamam funções do arquivo `app/services/data_service.py`. Hoje essas funções devolvem dados fictícios. Quando o back estiver pronto, basta trocar o corpo delas por chamadas reais, e as telas continuam iguais.

Procure por `TODO(back)` no arquivo para achar os pontos de integração:

| Função                               | O que o back precisa fazer                                                                       |
| ------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `analisar(interacoes)`               | Receber as interações e devolver as histórias detectadas com os ativos gerados                   |
| `regenerar(historia, ativo_id, vez)` | Gerar um novo rascunho para um ativo                                                             |
| `listar_pacotes()`                   | Listar os objetos do bucket no OCI Object Storage                                                |
| `salvar_no_oci(pacotes, lote_id)`    | Gravar o pacote no OCI. **Precisa ser idempotente**: tentar de novo não pode duplicar resultados |
| `reenviar_pacote(pacote)`            | Tentar gravar de novo um pacote que falhou                                                       |
| `conteudo_pacote(caminho)`           | Ler o JSON de um objeto do bucket                                                                |

### Armazenamento no OCI (implementado)

O módulo `app/services/oci_storage.py` grava e lê os pacotes no bucket. O `data_service.py` já chama esse módulo nas quatro funções acima; sem credencial configurada, o app volta para os dados fictícios.

Configuração por variável de ambiente (ou no `.env` da raiz):

- `OCI_BUCKET_NAME` — padrão `G10communitylab-ativos`
- `OCI_NAMESPACE` — namespace do tenancy (se vazio, é consultado na API)
- `OCI_CONFIG_FILE` — padrão `~/.oci/config`
- `OCI_PROFILE` — padrão `DEFAULT`

Credencial: chave de API do usuário, em `~/.oci/config` com a chave privada. Nada de segredo no repositório.

Formato: cada lote vira `ativos/<lote_id>/<arquivo>.json`. Como o nome vem do lote, regravar sobrescreve — repetir a gravação não duplica. O caminho é montado pelo backend a partir do lote e do nome do arquivo recebido, e não copiado do dado: o mesmo lote com o mesmo arquivo cai sempre no mesmo objeto. Vários arquivos por lote continuam suportados, diferenciados pelo nome.

### Real, simulado e falha

Cada item devolvido pelo armazenamento carrega três campos:

- `status`: `salvo` (o objeto entrou no bucket) ou `falhou`
- `persistencia`: `real` ou `simulada`
- `motivo`: explicação quando não houve gravação real

Sem credencial configurada, nada é gravado: os itens voltam com `status="falhou"`, `persistencia="simulada"` e o motivo preenchido, e a listagem devolve lista vazia. Nunca aparece `salvo` sem gravação no bucket.

### Formato provisório dos dados

O formato abaixo é o que o front usa **hoje**. Ele é só um ponto de partida e **pode mudar**: quem define o contrato oficial é o back, e o time deve decidir em conjunto.

Interação (entrada):

```json
{ "autor": "Marina Costa", "canal": "#conquistas", "tipo": "mensagem", "texto": "..." }
```

Antes de enviar ao provedor, `llm.analisar()` inclui o ID efetivo e aplica
`normalizar_texto()` e `anonimizar_texto()` de `src.preprocessing` ao texto.
Marcadores como `[EMAIL]`, `[TELEFONE]`, `[CPF]` e `[NOME]` são enviados no lugar dos
valores reconhecidos. O campo `autor` é mantido no formato do front; a ingestão
do Discord já o pseudonimiza, mas arquivos CSV/JSON ainda podem trazer o nome
original e precisam de pseudonimização própria para dados reais.

História detectada (saída):

```json
{
  "id": "hist-001",
  "autor": "Marina Costa",
  "canal": "#conquistas",
  "categoria": "Conquista profissional",
  "sentimento": "Positivo",
  "relevancia": 96,
  "relevancia_nivel": "alta",
  "mensagem_original": "...",
  "citacoes": [{ "texto": "trecho literal do original", "id_interacao": 1 }],
  "interacoes_origem": [1],
  "destaques": ["trecho da mensagem usado no rascunho"],
  "fatos": ["Conquista: primeira vaga como dev júnior"],
  "ativos": [
    { "id": "post_linkedin", "nome": "Post para LinkedIn", "tipo": "texto", "campos": { "texto": "..." } },
    { "id": "card_conquista", "nome": "Card de conquista", "tipo": "card", "campos": { "titulo": "...", "frase": "..." } }
  ]
}
```

Campos novos (aditivos, outubro/2026):

- `citacoes` — cada trecho de prova com o `id_interacao` de origem. O trecho é recortado do texto preparado para análise (com dados pessoais reconhecidos mascarados), não copiado do modelo; se não existir literalmente nessa fonte, é descartado.
- `interacoes_origem` — lista de ids das interações que sustentam a história.
- `relevancia_nivel` — faixa derivada da numérica: `alta` (85+), `media` (60 a 84) e `baixa` (abaixo de 60).
- `destaques` passa a ser derivado das citações validadas, então o destaque em negrito na tela sempre corresponde a texto que existe na mensagem.

Pacote salvo no OCI (listagem):

```json
{ "caminho": "ativos/demo-001/pacote-distribuicao.json", "lote": "DEMO-001",
  "data": "15/10/2026 14:32", "tamanho": "2,4 KB", "status": "salvo" }
```

## Pontos para alinhar com o back

- **Tipos de ativo:** o front agora usa Testemunho estruturado (título + descrição + citação) e Case de sucesso (texto narrativo). Confirmar se o back vai gerar nesse formato.
- **Rastreabilidade:** o front espera um campo `fontes` em cada ativo, com a estrutura: `[{"afirmacao": "...", "fato": "...", "trecho": "..."}]`. Alinhar formato com o back.
- Se o campo `tipo` da interação vai ser preenchido e com quais valores.
- O que o pacote salvo no OCI deve conter. Hoje o JSON de exemplo só tem o status dos ativos. O ideal é guardar também o texto gerado, as citações com a mensagem de origem e se a autorização foi confirmada.
- Se o status de aprovação ou rejeição feito na Curadoria deve ser atualizado no bucket e como.
- **Fluxo:** o front agora tem Histórias → Estúdio → Curadoria. Confirmar se o back segue essa sequência.

## Limitações conhecidas do protótipo

- A análise sempre devolve as 3 histórias fictícias, mesmo que você envie outro arquivo (o arquivo é validado e aparece na prévia, mas não é analisado).
- Aprovar ou rejeitar só vale durante a sessão e não grava em lugar nenhum.
- "Copiar texto" mostra um bloco com ícone de copiar, porque o Streamlit não acessa a área de transferência.
- Testado no Streamlit 1.66. O `requirements-front.txt` pede `>=1.37`.
- Tipos de ativo disponíveis: Testemunho estruturado (título + descrição + citação) e Case de sucesso (texto narrativo completo).

## Como contribuir no front

1. Para mudar um texto ou visual de uma tela, edite o arquivo dela em `app/telas/`.
2. Para mudar os dados de exemplo, edite `app/mocks/mock_data.py`.
3. Para conectar o back, edite só `app/services/data_service.py`.
4. Não misture os mocks do front com a pasta de dados de demonstração do back.

## Como executar no Windows

1. Abra o Prompt de Comando ou PowerShell.
2. Navegue até a pasta do projeto:
   ```bash
   cd "c:\Users\communitylab-front\communitylab-front"
   ```
3. Ative o ambiente virtual (se existir):
   ```bash
   .\.venv\Scripts\Activate
   ```
4. Instale as dependências:
   ```bash
   pip install -r requirements-front.txt
   ```
5. Execute o aplicativo:
   ```bash
   streamlit run app/main.py
   ```
