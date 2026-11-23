# AGENTS.md — Módulo de dados do CommunityLab

Regras para quem escreve código na **ingestão, processamento e análise**. Detalhes ficam em `docs/`:

- `docs/contrato_saida.md`: estruturas de entrada e saída de cada módulo.
- `docs/guia_rotulagem.md`: critérios de sentimento, relevância e tipo de insight.
- `docs/avaliacao.md`: resultado da avaliação de qualidade (preencher com números medidos).

## Comandos

```bash
pip install -e .
pytest -q                           # testes, devem rodar em poucos segundos e sem rede
python validar.py exemplos/cenarios_demo.json   # valida schemas e exemplos
```

Versão alvo: Python 3.11+ (confirmar com a equipe).

## Estrutura

```
src/communitylab/
  leitura.py        bytes -> texto, com fallback de encoding
  ingestao.py       texto -> interações validadas
  limpeza.py        vazias, curtas, duplicatas
  anonimizacao.py   pseudonimiza autor e mascara dados pessoais no texto
  contrato.py       validação contra schemas/
  classificacao.py  chamada injetada ao LLM, validação e fallback
  lotes.py          divisão em lotes e controle de custo
  agregacao.py      contagens e rankings por tópico e sentimento
  avaliacao.py      métricas contra o conjunto de referência
tests/
```

Dependências em uma direção só: `leitura → ingestao → limpeza → anonimizacao → classificacao → agregacao`. `contrato` pode ser usado por qualquer módulo. Nenhum módulo importa outro "para trás".

## Regras

1. **Nunca quebrar na mão do usuário.** Arquivo corrompido, linha malformada ou resposta ruim do LLM viram avisos e registros de rejeição, não exceções para a interface.
2. **Módulos puros.** Funções recebem dados e devolvem dados. Sem estado global, sem rede, sem `print`, sem ler variáveis de ambiente e sem efeitos colaterais no `import`. I/O fica numa camada fina nas bordas.
3. **Sem dependência de Streamlit ou do SDK da OCI** dentro deste pacote. A interface e a orquestração é que importam estas funções.
4. **LLM injetado como função** (`chamar_llm(prompt) -> str`). Nada de SDK de provedor aqui. Os prompts são da Jaqueline.
5. **Contrato único.** Tudo que sai deste módulo segue `schemas/`. Valor fora da enumeração é rejeitado, nunca "corrigido em silêncio". Nunca preencher análise inválida com valor padrão.
6. **Schemas não mudam sem aviso.** Alterou formato: atualize o schema, a `versao_schema`, os exemplos e avise a Tissiany e a Luciene.
7. **Privacidade.** Nenhum dado pessoal vai para o LLM, log ou bucket. Não registrar texto original em log.
8. **Segredos fora do repositório.** Chaves de API, credenciais OCI e o sal da pseudonimização nunca entram no código nem nos testes.
9. **Dependências novas:** só com justificativa. Preferir a biblioteca padrão.

## Leitura e encoding

Tentar em ordem: `utf-8-sig` (cobre arquivos com e sem BOM), `cp1252`, `latin-1` e, por último, `utf-8` com `errors="replace"` (com aviso). `latin-1` aceita qualquer byte, por isso nunca vem antes de `cp1252`. Retornar `(texto, encoding_usado, avisos)` e nunca levantar exceção. Normalizar para Unicode NFC, remover caracteres de controle e unificar quebras de linha.

## Configuração

Estes valores ficam em **constantes nomeadas** em um único lugar (`config.py`), nunca espalhados no código. Os valores abaixo são provisórios e devem ser confirmados pela equipe:

| Constante | Valor provisório |
|-----------|------------------|
| `TAMANHO_MINIMO_TEXTO` | 10 caracteres |
| `LIMIAR_CONFIANCA` | 0,6 |
| `MAX_TENTATIVAS_LLM` | 2 |
| `TAMANHO_LOTE` | a definir com Jaqueline e Luciene |

## Testes

`pytest`, rápidos e sem rede. O LLM é sempre uma função falsa. Cobertura mínima:

- **Leitura:** bytes em cada encoding e bytes inválidos, sem exceção.
- **Ingestão:** CSV com `,` e `;`, quebra de linha dentro do texto, JSON em lista e em lote, JSON inválido, campo faltando.
- **Limpeza:** vazia, curta, duplicata com variação de caixa e pontuação.
- **Anonimização:** e-mail, telefone, CPF, autor com nome real vira `membro_###`, `@membro_###` preservado, **falsos positivos conhecidos** (ex.: "Python", "Oracle", "Streamlit" não podem virar `[NOME]`).
- **Contrato:** objeto válido, enum inválido, campo extra, `analise` incompleta.
- **Classificação:** resposta válida, JSON cercado de texto, inválida com nova tentativa, tentativas esgotadas, baixa confiança.
- **Lotes e agregação:** divisão, falha parcial, contagem com vários tópicos, ordenação estável.

## Antes de abrir pull request

- [ ] `pytest -q` passa
- [ ] `python validar.py exemplos/cenarios_demo.json` passa
- [ ] Nenhuma função de negócio faz I/O ou imprime
- [ ] Sem chaves, credenciais ou dados pessoais reais
- [ ] Schemas e docs atualizados, se o formato mudou
- [ ] README do módulo atualizado (entradas, saídas, limitações)