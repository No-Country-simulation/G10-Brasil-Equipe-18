# Card 13 — Testemunhos estruturados

## Implementação proposta

Depende da branch do PR #67 (Card 14). Acrescenta um testemunho na mesma chamada
que solicita os demais ativos. Não substitui card de conquista por testemunho.

A primeira versão é extrativa: título (até 200 caracteres), descrição (até 2000)
e citação (até 500) devem corresponder a trechos literais da única interação de
origem já preparada/anonimizada. A citação deve coincidir com uma das citações
conferidas da história, incluindo o ID da interação. O prompt orienta preservação
de contexto e omissão diante de dúvida, intenção futura ou insuficiência.

Isso verifica procedência textual, não veracidade nem suficiência semântica. Uma
seleção literal ainda pode ignorar negação ou contexto; a revisão humana permanece
necessária. Não há garantia de anonimização, cujo ajuste é uma frente separada.
A proposta extrativa e seus limites precisam de aprovação técnica/editorial.

## Contrato

| Representação | Valor |
|---|---|
| ID local | testemunho_estruturado |
| Tipo editorial canônico | testemunho_estruturado |
| Formulário do front | testemunho |
| Campos editáveis | titulo, descricao, citacao |
| Texto canônico | descricao + duas quebras + citação entre aspas |
| Vínculos | interacoes_origem e citacoes derivados da fonte |

`services.testemunhos.converter_testemunho_canonico` implementa a projeção inicial
do rascunho para o schema canônico 1.0. Recebe ID único e instante com fuso da
aplicação chamadora, preserva título e vínculos e inicia `status_revisao=pendente`.
Não cria aprovação/autorização a partir do LLM. O chamador é responsável pela
unicidade do ID no lote e pelo instante real de criação.

O helper é testado contra `schemas/ativo_gerado_schema.json`; não é um novo
exportador automático de arquivos canônicos na OCI e não reconstitui campos a
partir do texto composto. A saída persistida pelo fluxo existente é o envelope
1.1, preservando os campos estruturados. O adaptador geral de todos os formatos e
a restauração do lote pelo Histórico em nova sessão continuam separados.

## Fluxo

- O normalizador deriva o ID da interação da fonte, ignorando vínculos e estados
  humanos sugeridos pelo modelo.
- Testemunhos duplicados, campos vazios/nulos, inventados ou citações sem evidência
  são recusados. A história permanece revisável com `testemunho_pendente`.
- Estúdio e Curadoria mostram o aviso; ausência de ativos é tratada pelo Card 14.
- Edição dos três campos usa as mesmas chaves do fluxo existente; campos editados
  são preservados no pacote. Aprovação editorial, validação factual e autorização
  continuam independentes, sem aprovação automática pela conferência literal.
- Uma edição humana pode mudar a correspondência com a fonte. O PR #59 é a frente
  de conferência/revalidação das citações editáveis e deve ser testado em conjunto.

## Testes

```bash
python -m pytest -q tests/test_testemunhos_estruturados.py
python -m pytest -q tests/test_cases_sucesso.py tests/test_testemunhos_estruturados.py
python -m pytest -q tests
python scripts/validar_exemplos_card05.py
```

Cobertura: três categorias, schema/composição canônica, campos ausentes/inventados,
citação não conferida, duplicidade, duas histórias sem mistura, case e testemunho
na mesma chamada simulada, ID/instante canônicos inválidos, edição/pacote com
storage simulado e AppTest dos três campos até Curadoria, com decisões pendentes.
Todos os dados dos testes são fictícios. Não são evidências de API/OCI reais.

## Homologação ainda necessária

Revisar contrato e abordagem extrativa com a equipe; usar provedor real com dados
fictícios nos três cenários; testar relato insuficiente, negação e plano futuro;
conferir anonimização, fontes, edição/revalidação pelo #59 e pacote real na OCI.
Registrar SHA, provedor, lote e resultados. Implementação local/suíte aprovada não
representam aceite do Card 13 nem homologação geral do MVP.

## Execução local em 22/11/2026

`python -m pytest -q tests`: **3.729 passed em 6,60s**, incluindo os 20 testes
novos do Card 13 sobre os 3.709 da branch dos cases. Validador Card 05 passou
(2 schemas, 2 interações, 2 ativos, 2 vínculos e 4 rejeições esperadas).
A regressão AppTest está em `tests/test_card13_testemunho_interface.py`.
Resultados locais com dados/serviços simulados; não equivalem a deploy/homologação.
