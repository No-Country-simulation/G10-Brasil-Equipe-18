# Deploy do CommunityLab em uma VM Oracle com Docker

Este guia executa o front Streamlit em um container Docker na VM. A imagem
não inclui credenciais; elas são fornecidas em tempo de execução.

## Requisitos

- VM Ubuntu 22.04/24.04 LTS.
- Docker Engine e plugin Docker Compose v2.
- Acesso SSH à VM.
- Credenciais dos provedores que serão usados e, se houver persistência,
  credenciais do OCI Object Storage.

Este guia considera Ubuntu 22.04/24.04 LTS. Ubuntu 20.04 não está incluído:
versões atuais do Docker Engine não publicam pacotes oficiais para essa versão.

## Arquivos do container

- `Dockerfile`: instala as dependências de `pyproject.toml`, instala e valida
  `pt_core_news_sm` durante o build e inicia `app/main.py` na porta 8501. O
  processo roda sem privilégios de root.
- `.dockerignore`: impede que arquivos locais, credenciais e dependências do
  host sejam enviados ao contexto ou incluídos na imagem.
- `compose.yaml`: inicia o serviço, define limites de porta e monta a
  configuração OCI como somente leitura.

## Preparar a configuração na VM

Clone ou atualize o repositório na VM depois que esta branch for integrada.
Na raiz do projeto:

```bash
cp .env.example .env
chmod 600 .env
mkdir -p .oci
chmod 700 .oci
```

Edite `.env` e substitua os valores de exemplo pelas chaves reais que serão
usadas (Gemini, Cohere, Groq e/ou Discord). Apague ou deixe vazios os
provedores que não serão usados. Não reutilize os textos de placeholder do
`.env.example` como credenciais.

Gere um sal secreto para a pseudonimização:

```bash
openssl rand -hex 32
```

Copie o resultado para `SAL_PSEUDONIMIZACAO` em `.env`. O Compose exige esse
valor e não inicia o serviço se ele estiver ausente. Mantenha o mesmo sal nas
próximas implantações; trocar o valor altera os pseudônimos dos autores.

Para dados reais, configure `LLM_PROVEDORES_DADOS_REAIS` no `.env` somente
com os provedores explicitamente autorizados (lista separada por vírgulas:
`gemini`, `cohere`, `groq`). O padrão vazio não autoriza nenhum provedor.
Não habilite provedores sem revisar as condições de tratamento dos dados.

Ajuste também os valores de execução no `.env`:

```dotenv
APP_UID=1000
APP_GID=1000
OCI_CONFIG_DIR=./.oci
STREAMLIT_BIND_ADDRESS=127.0.0.1
STREAMLIT_HOST_PORT=8501
```

Use `id -u` e `id -g` na VM para definir `APP_UID` e `APP_GID` conforme o
usuário que será dono dos arquivos OCI. Isso permite que o processo sem root
leia a configuração montada.

### Credenciais do OCI Object Storage

O código do serviço OCI usa um arquivo de configuração OCI ou Streamlit
secrets. Neste Compose, `.oci/` é montado em `/run/oci` como somente leitura;
por isso, crie `.oci/config` com o caminho da chave **dentro do container**:

```ini
[DEFAULT]
user=ocid1.user.oc1..seu_ocid
fingerprint=seu_fingerprint
tenancy=ocid1.tenancy.oc1..seu_ocid
region=sa-saopaulo-1
key_file=/run/oci/oci_api_key.pem
```

Coloque a chave privada correspondente em `.oci/oci_api_key.pem` e proteja os arquivos:

```bash
chmod 600 .oci/config .oci/oci_api_key.pem
```

Preencha `OCI_BUCKET_NAME`, `OCI_NAMESPACE` e `OCI_PROFILE` em `.env` quando
necessário. As variáveis `OCI_USER`, `OCI_FINGERPRINT`, `OCI_TENANCY` e
`OCI_KEY_CONTENT` do `.env.example` não substituem o arquivo OCI usado por
este container.

> `.env`, `.oci/` e `.streamlit/secrets.toml` não devem entrar na imagem nem
> ser commitados. `.dockerignore` e `.gitignore` os excluem.

## Validar e iniciar

Na raiz do repositório:

```bash
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps
```

Confira a saúde do Streamlit e os logs:

```bash
curl --fail http://127.0.0.1:8501/_stcore/health
docker compose logs -f communitylab
```

Para abrir a interface localmente, encaminhe a porta por SSH:

```bash
ssh -L 8501:127.0.0.1:8501 usuario@IP_DA_VM
```

Depois acesse `http://localhost:8501` no computador local.

## Acesso público

Por padrão, o Compose publica a porta somente em `127.0.0.1`; ela não fica
aberta para a internet. Para acesso externo, coloque um proxy reverso com
HTTPS e autenticação à frente do container. Na rede da VM/OCI, exponha apenas
as portas necessárias (normalmente 22 restrita ao IP administrativo e 443
para o proxy). O Streamlit deste projeto não fornece autenticação própria;
não o exponha diretamente à internet sem uma camada de proteção.

## Atualizar e parar

Após atualizar o código na VM:

```bash
docker compose up -d --build
docker compose ps
```

Para acompanhar os logs ou parar o serviço:

```bash
docker compose logs -f communitylab
docker compose down
```
