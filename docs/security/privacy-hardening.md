# Privacy Hardening — CommunityLab

Status: validação específica concluída parcialmente; homologação integrada pendente.

## Controles

| Controle | Implementação reportada | Validação |
|---|---|---|
| SEC-01 | Sal privado obrigatório para dados reais; bloqueio de natureza desconhecida na análise; demonstrações fictícias podem usar sal público. | Testes específicos aprovados em execuções complementares. |
| SEC-07 | Minimização de metadados enviados ao LLM. | 3 testes específicos aprovados, incluindo regressão existente. |
| Camada de serviço | Propagação explícita da natureza dos dados e resolução do sal por análise. | 183 testes aprovados em execuções complementares após ajustes. |
| SEC-08 | Governança de provedores para dados reais. | Implementacao preparada; homologacao pendente. PR #81 ainda precisa ser integrado. |
| SEC-09 | Ampliação do mascaramento de telefones, URLs e menções; remoção do download automático do modelo spaCy. | 7 testes aprovados. |
| SEC-10A/B | HMAC-SHA-256, sufixo decimal de 20 dígitos, preservação de pseudônimos existentes e bloqueio de colisões na ingestão CSV/JSON/DataFrame. | 9 testes aprovados. |
| SEC-10C | Bloqueio de colisões no Discord, rejeição de autores inválidos e preservação do cursor em caso de colisão. | 5 testes aprovados. |

Os resultados acima foram reportados durante o desenvolvimento local; não representam uma única execução integrada nem devem ser somados como cobertura exclusiva.

## Operação segura

Configurar SAL_PSEUDONIMIZACAO com segredo de alta entropia por ambiente, fora do repositório. Não registrar seu valor em logs ou evidências. Rotação exige planejamento de continuidade dos identificadores. Não utilizar dados reais para demonstrações sem autorização e controles adequados. Instalar o modelo spaCy no provisionamento, quando necessário, e validar a disponibilidade antes de processar dados reais. Revisar conteúdo e evidências antes de exportação ou publicação.

## Limitações e riscos residuais

- Pseudonimização e mascaramento de melhor esforço não garantem anonimização nem conformidade integral com a LGPD.
- Contexto, citações literais e atributos indiretos podem permitir reidentificação. URLs removidas podem reduzir a utilidade do conteúdo.
- Colisões são detectadas dentro do lote; não há garantia de unicidade global entre lotes. Identificadores históricos permanecem inalterados; reimportar autores originais pode produzir identificadores diferentes.
- A preservação de pseudônimos recebidos não comprova sua origem ou autenticidade.
- Revisão de permissões, retenção, exclusão, bases legais e condições contratuais dos provedores continua necessária.
- Configuração efetiva de segredos em produção OCI/Streamlit e homologação integrada ainda não verificadas.

## Critérios de encerramento

1. Verificar integração do PR #81 e implementar SEC-08 com autorização explícita de provedores para dados reais.
2. Revisar diff consolidado e verificar ausência de segredos versionados.
3. Executar suíte integrada e registrar resultado real, sem duplicar contagens.
4. Confirmar configuração operacional e registrar limitações remanescentes.
5. Submeter Pull Request para revisão independente; não contornar proteção de branch.

## SEC-08: configuracao

LLM_PROVEDORES_DADOS_REAIS: lista separada por virgulas (gemini, cohere, groq), vazia por padrao. Nenhum provedor autorizado implicitamente.
