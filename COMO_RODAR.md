# 🚀 Como Rodar o CommunityLab

## 📋 Pré-requisitos

- **Python 3.10 ou superior**
- **pip** (gerenciador de pacotes Python)
- **Git**

---

## 🎨 Front-end (Streamlit) - Modo Demonstração

O front-end roda **independentemente** com dados fictícios para demonstração e validação do fluxo.

### 1. Clone o repositório (se ainda não tem)
```bash
git clone https://github.com/No-Country-simulation/G10-Brasil-Equipe-18.git
cd G10-Brasil-Equipe-18
```

### 2. Vá para a branch do front-end
```bash
git checkout feat/frontend-streamlit
git pull origin feat/frontend-streamlit
```

### 3. (Opcional) Crie um ambiente virtual
```bash
python -m venv .venv
```

**Ative o ambiente:**
- Windows: `.venv\Scripts\activate`
- Linux/Mac: `source .venv/bin/activate`

### 4. Instale as dependências
```bash
pip install -e .
```

### 5. Rode o aplicativo
```bash
streamlit run app/main.py
```

**No Windows, se não funcionar:**
```bash
python -m streamlit run app/main.py
```

### 6. Abra no navegador
O Streamlit vai abrir automaticamente em: **http://localhost:8501**

Se não abrir, acesse manualmente o endereço acima.

---

## 🎨 O que você vai ver no front-end

### Navegação (6 módulos):
1. **📊 Dashboard** - Visão geral com KPIs
2. **📥 Importação** - Upload de interações (CSV/JSON)
3. **💬 Histórias** - Listagem de histórias detectadas
4. **✨ Estúdio de Conteúdo** - Edição de rascunhos com evidências
5. **✅ Curadoria** - Validação e aprovação (3 controles independentes)
6. **🗄️ Histórico** - Pacotes salvos no OCI

### Identidade Visual:
- ✅ Sidebar azul-marinho (#101B32)
- ✅ Violeta (#7C3AED) para ações de IA
- ✅ Design SaaS corporativo + IA
- ✅ Contraste WCAG AA

### Funcionalidades:
- ✅ Fluxo completo de ponta a ponta
- ✅ Dados fictícios para demonstração
- ✅ Rastreabilidade (evidências → rascunhos)
- ✅ Três controles de curadoria (RG-01, RG-02, RG-03)

---

## 🔌 Integração com Back-end (Quando Disponível)

### Arquitetura Atual

```
Front-end (Streamlit)
    ↓
app/services/data_service.py  ← ÚNICO ponto de integração
    ↓
app/mocks/mock_data.py  ← Dados fictícios (será substituído)
```

### Como Integrar o Back-end

1. **O front NÃO precisa mudar** - as telas já estão prontas
2. **Apenas `app/services/data_service.py` será alterado**
3. **Procure por `TODO(back)` no código** para ver os pontos de integração

### Funções que precisam ser conectadas:

| Função | O que faz (hoje) | O que fará (com back) |
|--------|------------------|----------------------|
| `analisar(interacoes)` | Retorna histórias fictícias | Envia interações ao back e recebe histórias + ativos |
| `regenerar(historia, ativo_id, vez)` | Alterna entre variações | Solicita novo rascunho ao back |
| `listar_pacotes()` | Retorna lista fictícia | Consulta objetos no bucket OCI |
| `salvar_no_oci(pacotes, lote_id)` | Mock | Persiste no OCI Object Storage |
| `conteudo_pacote(caminho)` | JSON fictício | Lê objeto do bucket |

### Exemplo de Integração:

**Antes (mock):**
```python
def analisar(interacoes):
    """TODO(back): enviar as interações e receber histórias + ativos gerados."""
    return copy.deepcopy(m.HISTORIAS)
```

**Depois (com back):**
```python
def analisar(interacoes):
    """Envia interações ao back e recebe histórias detectadas."""
    response = requests.post(f"{BACKEND_URL}/api/analisar", json={"interacoes": interacoes})
    return response.json()["historias"]
```

### Variáveis de Ambiente (quando tiver back):

Crie um arquivo `.env` na raiz:
```env
BACKEND_URL=http://localhost:8000
OCI_BUCKET=communitylab-ativos-marketing
OCI_NAMESPACE=your-namespace
# Outras configs conforme necessário
```

---

## 🐳 Com Docker (Futuro)

Quando o back estiver pronto, você poderá rodar tudo com:

```bash
docker-compose up
```

O `docker-compose.yml` orquestrará front + back + banco (se houver).

---

## 💡 Dicas

### Para Desenvolvedores:
- **Dados fictícios**: Todos os dados são inventados (ver `app/mocks/mock_data.py`)
- **Sem persistência**: Aprovar/rejeitar só vale durante a sessão
- **Hot reload**: O Streamlit recarrega automaticamente ao salvar arquivos
- **Debug**: Use `st.write()` para debug rápido

### Para Testadores:
- **Modo demonstração**: Na sidebar, você pode simular erros e estados diferentes
- **Fluxo completo**: Siga Dashboard → Importação → Histórias → Estúdio → Curadoria
- **Regras de curadoria**: Teste os 3 controles independentes (validação, aprovação, autorização)

### Para o Time:
- **Front roda sozinho**: Não precisa esperar o back para validar o fluxo
- **Design final**: Cores, layout e UX estão prontos
- **Pronto para integração**: Quando o back estiver pronto, a integração será rápida

---

## 📚 Documentação Adicional

- **README do Front**: `READMEFrontend.md` - documentação técnica completa
- **Especificação CQF**: `docs/CQF_SPECIFICATION.md` - regras de curadoria
- **Guia de desenvolvimento**: `CLAUDE.md` - instruções para evolução do front

---

## 🆘 Problemas Comuns

### Erro: "streamlit não é reconhecido"
**Solução**: Use `python -m streamlit run app/main.py`

### Erro de dependências
**Solução**: 
```bash
pip install --upgrade pip
pip install -e .
```

### Porta 8501 já em uso
**Solução**:
```bash
streamlit run app/main.py --server.port 8502
```

### O app não abre automaticamente
**Solução**: Acesse manualmente `http://localhost:8501`

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação em `READMEFrontend.md`
2. Procure por `TODO(back)` no código para pontos de integração
3. Consulte o time no grupo do projeto

---

**Última atualização**: ETAPAS 1-4 completas (identidade visual, navegação, estúdio, curadoria)
