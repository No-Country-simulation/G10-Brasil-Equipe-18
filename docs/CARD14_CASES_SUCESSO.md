# Card 14 — geração de cases de sucesso

## Entrega proposta para revisão técnica

O prompt da análise solicita um `case_sucesso` na mesma chamada de LinkedIn/card,
quando a interação relata resultado ou avanço concreto. A representação no front
é `id=case_sucesso`, `nome=Case de sucesso`, `tipo=texto`, `campos.texto`.
O título é metadado opcional (até 200 caracteres), exibido no Estúdio/Curadoria;
não cria campos obrigatórios de contexto, desafio, ações ou resultados.

Esta primeira versão é **extrativa**: a narrativa reúne trechos literais da única
interação de origem, na ordem da fonte, com parágrafos opcionais. Não gera uma
paráfrase livre. Isso limita a fluidez editorial em troca de verificação mecânica
de procedência. A equipe deve revisar esta escolha antes do aceite.

## Elegibilidade e fidelidade

- O prompt pede resultado/avanço em conquista profissional, projeto de destaque ou
  superação; dúvida, intenção e plano futuro sem avanço não bastam.
- A normalização exige um `resultados` literal presente na fonte e no case e uma
  citação conferida incluída na narrativa. Narrativa e título sem correspondência
  literal são recusados. Texto é limitado a 6000 caracteres.
- O ID da interação e as citações vêm da fonte já rastreada pela análise, nunca dos
  metadados sugeridos pelo modelo. Cases duplicados são recusados.
- Não há garantia semântica automática: uma frase literal pode ser selecionada fora
  de contexto ou classificada incorretamente pelo modelo. Negação, ironia,
  suficiência e significado do resultado precisam de revisão humana.
- Case ausente/recusado não apaga uma história válida: `case_pendente` registra o
  motivo, exibido no Estúdio e na Curadoria. Os outros formatos permanecem.
- Nenhuma aprovação, autorização ou validação factual vem do LLM. Os controles
  existentes da Curadoria permanecem independentes e inicialmente pendentes.
- A fonte é o texto preparado/anonimizado pela análise. Este PR não corrige nem
  garante a anonimização; limitações do #64 continuam separadas.

## Integração e persistência

O case usa o formulário de texto existente, com edição Estúdio → Curadoria,
cópia, metadados de origem e fontes. O pacote de histórias preserva os campos,
título, vínculo e citações pelo salvamento OCI existente. O título é metadado de
origem, não um novo campo editável nesta entrega.

A representação editorial canônica é `case_sucesso`, conforme Card 05, enquanto
`tipo=texto` é apenas o formulário. Esta entrega não implementa o adaptador geral
para arquivos canônicos independentes, nem a restauração completa de um lote pelo
Histórico em nova sessão. O pacote principal mantém versão 1.1; não modifica o
schema do ativo canônico. A inclusão opcional de metadados no ativo do front e de
`case_pendente` na história deve ser conferida pelas responsáveis pelo contrato.

## Exemplos fictícios dos testes

| Categoria | Fonte | Resultado citado |
|---|---|---|
| Conquista profissional | Estudei por oito meses. Consegui minha primeira vaga como analista. | Consegui minha primeira vaga como analista. |
| Projeto de destaque | Criei um painel de vendas com SQL. Entreguei o projeto para a equipe. | Entreguei o projeto para a equipe. |
| Superação | Tive dificuldade no primeiro módulo. Retomei os estudos e concluí o módulo. | Retomei os estudos e concluí o módulo. |

Os exemplos são respostas simuladas para testes, não evidência de execução de LLM.

## Validação reproduzível

```bash
python -m pytest -q tests/test_cases_sucesso.py
python -m pytest -q
python scripts/validar_exemplos_card05.py
```

Testes do Card 14 cobrem as três categorias, texto inventado, resultado sem fonte,
citação ausente na narrativa, título inventado, duplicação, campos vazios/nulos,
fonte insuficiente, duas histórias, chamada única com provedor simulado,
edição/roundtrip do pacote com storage simulado e AppTest Estúdio/Curadoria,
inclusive história sem ativos. Sem credenciais, API ou OCI reais.

## Reteste para revisão e homologação

1. Revisar elegibilidade, opção extrativa e metadados com Jaqueline/Tissiany.
2. Processar cada cenário com dados fictícios e provedor real; conferir conteúdo,
   IDs/citações e ausência de mistura entre participantes.
3. Exercitar uma dúvida, intenção futura, negação de conquista e fonte insuficiente.
4. Editar o case, enviar à Curadoria, conferir decisões independentes e gravar.
5. Conferir o JSON efetivamente salvo na OCI e registrar SHA, provedor, lote e prints.
6. Confirmar compatibilidade com os PRs #59–#61 antes da integração consolidada.

Implementação/testes locais não representam aprovação técnica, deploy, aceite do
Card 14 ou homologação geral do MVP. Testemunho estruturado (Card 13) é separado.
