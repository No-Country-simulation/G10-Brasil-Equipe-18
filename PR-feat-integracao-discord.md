# PR — feat/integracao-discord

> Rascunho de preenchimento do template de PR com base nos 12 commits do branch `feat/integracao-discord`.
> Autor: LuGodoy <lucienegodoy@icloud.com>
> Status: sem commit, sem push. Copiar o conteúdo abaixo para o PR.

---

## 📌 Escopo

Integra o front-end do CommunityLab com o Discord como fonte de dados, adicionando: ingestão de mensagens via API REST, provedor LLM com fallback (Gemini → Cohere → Groq), data_service e estado que aguardam fonte de dados, aba Discord na tela de Importação, progresso persistente no Processamento, variáveis de ambiente, dependências do pyproject e atualizações de documentação e testes. Nenhuma credencial real é incluída.

## 📋 Vínculo com o Trello

- **Card:** [informar o link ou ID do card do Trello]
- **Status:** Backlog / Em andamento / Em revisão
- **Responsável:** LuGodoy

## 🛠️ Alterações realizadas

Doze commits no branch `feat/integracao-discord`, do mais antigo para o mais recente:

| Commit | Tipo | Escopo | Arquivos |
|--------|------|--------|----------|
| `0a83ef8` | docs | Marca CATP-011 (persistência OCI) como executado | `docs/CATP_TEST_PLAN.md` |
| `79900c0` | chore | Ignora `info_project.md` no `.gitignore` | `.gitignore` |
| `5d1dd69` | feat | Variáveis de ambiente do Discord e provedores LLM (`.env.example`) | `.env.example` |
| `303d36e` | feat | Ingestão de mensagens do Discord via API REST (filtro, anonimização, pseudonimização, cursor incremental) | `src/ingestion/discord_load.py`, `tests/test_discord_load.py` |
| `99541ed` | feat | Provedor LLM com fallback Gemini/Cohere/Groq e prompt externo (`prompt_analise.txt`) | `app/services/llm.py`, `app/services/llm_provider.py`, `app/services/prompt_analise.txt`, 5 arquivos de teste |
| `e965bc2` | feat | `data_service` e estado aguardam fonte de dados (Discord); `analisar()` falha sem mock | `app/services/data_service.py`, `app/state.py`, 3 arquivos de teste |
| `46029c0` | fix | Resolve caminho do app no teste de regressão (`AppTest` aponta para `app/main.py`) | `tests/test_front_regressao.py` |
| `6b26be1` | docs | Documenta ingestão Discord, provedores LLM e variáveis de ambiente no README | `READMEFrontend.md` |
| `39fb22c` | feat | Aba Discord na Importação e progresso persistente no Processamento; botão "Importar interações" | `app/telas/importacao.py`, `app/telas/processamento.py`, 2 arquivos de teste |
| `82a70da` | feat | Estados vazios de Estúdio e Curadoria direcionam para Importação | `app/telas/curadoria.py`, `app/telas/estudio.py` |
| `7669ff3` | test | Valida precedência de `OCI_NAMESPACE` via variável de ambiente nos testes de config | `tests/test_oci_storage.py` |
| `a09d814` | chore | Adiciona dependências ausentes ao `pyproject.toml` (`streamlit`, `requests`, `oci`) | `pyproject.toml` |

## 🎯 Regras de negócio afetadas

- [x] Não se aplica. (os commits tratam de infraestrutura, integração Discord, LLM, configuração e testes; não alteram RG-01, RG-02 nem RG-03 de rastreabilidade, validação factual e curadoria independente)

## 🧪 Cenários CATP

- **Cenários:** CATP-011
- **Critérios de aceitação:** persistência e idempotência no OCI Object Storage implementadas e cobertas por testes aprovados (ver commit `0a83ef8`)

## ✅ Testes e evidências

- [x] Testes automatizados
- [ ] Testes manuais
- [ ] Testes de integração
- [ ] Não executados — justificativa registrada abaixo

**Testes incluídos/alterados nos commits:**
- `tests/test_discord_load.py` — 213 inserções (ingestão Discord, offline)
- `tests/test_llm_provider.py` — 131 inserções
- `tests/test_llm_diagnostics.py` — 90 inserções
- `tests/test_llm_privacy.py` — 71 inserções
- `tests/test_llm_token_budget.py` — 59 inserções
- `tests/test_data_service_analysis.py` — 84 inserções
- `tests/test_front_state_initialization.py` — 52 inserções
- `tests/test_lote_id_unique.py` — 36 inserções
- `tests/test_importacao_discord.py` — 201 inserções
- `tests/test_processamento_progress.py` — 23 inserções
- `tests/test_oci_storage.py` — 12 inserções, 10 deleções
- `tests/test_llm.py` — 5 inserções
- `tests/test_front_regressao.py` — 3 inserções, 2 deleções

**Comandos executados:**

```bash
git log --oneline feat/integracao-discord
git show --stat <cada-commit>
```

**Resultados obtidos:** 12 commits no branch, todos autor LuGodoy, working tree limpo na branch atual (`chore/front-completa-template-secrets`).

**Evidências:** commits locais no branch `feat/integracao-discord` (repositório local, sem push).

## 🔐 Dados reais ou fictícios

- [x] Nenhum dado real utilizado.

**Origem dos dados:** os testes são offline (sem rede); credenciais Discord e OCI são apenas placeholders em `.env.example` e `secrets.toml.example`; nenhuma chave real entra no repositório.

**Cuidados com privacidade e segurança:** `.gitignore` ignora `.env` e `info_project.md`; pseudonimização de autores com sal na ingestão Discord; anonimização de menções; prompt de análise externo em `prompt_analise.txt`.

## ⚠️ Pendências e riscos

- Preencher o link/ID do card do Trello na seção acima antes de abrir o PR.
- Verificar compatibilidade das versões declaradas em `pyproject.toml` com `requirements-front.txt` e `app/requirements.txt`.
- O `secrets.toml` real deve ser criado localmente por cada desenvolvedor e nunca versionado.
- A validação de CATP-011 foi feita com mocks, sem credencial OCI real no ambiente.

## 🔍 Como validar

1. Abrir o branch `feat/integracao-discord` e revisar os 12 commits listados acima.
2. Confirmar que `pyproject.toml` declara `streamlit>=1.37`, `requests>=2.31` e `oci>=2.100`.
3. Confirmar que `.env.example` contém `DISCORD_TOKEN`, `CANAL_ID` e campos OCI (somente placeholders).
4. Executar a suíte de testes (`pytest`) e confirmar que passam, incluindo os de ingestão Discord, LLM, data_service e OCI.
5. Verificar que nenhuma credencial real está presente nos arquivos alterados.

## 🚀 Checklist antes de solicitar revisão

- [ ] Escopo e vínculo com o Trello informados. (vínculo do Trello pendente do autor)
- [x] Alterações e regras de negócio documentadas.
- [x] Cenários CATP identificados, quando aplicáveis (CATP-011).
- [x] Testes e evidências registrados sem declarar validações não realizadas.
- [x] Dados reais e simulados claramente diferenciados.
- [x] Nenhuma credencial, chave ou dado sensível incluído no PR.
- [x] Instruções de validação disponíveis para os revisores.

---

**Resumo:** 12 commits no branch `feat/integracao-discord`, todos do autor LuGodoy, cobrindo integração Discord, provedor LLM com fallback, data_service, telas, configuração, documentação e testes. Não foi feito commit nem push deste rascunho.
