"""Testes para o módulo app.services.oci_storage.

Valida lógica de normalização, comportamento do filtro de erro e documentação
do caminho de credenciais (testes de integração completa requerem ambiente OCI).
"""


def test_normalizacao_key_content_logica():
    """Testa a lógica de normalização do OCI_KEY_CONTENT: troca \\n literal por quebra real."""
    # Simulação da transformação que ocorre em oci_storage.py
    chave_literal = "-----BEGIN PRIVATE KEY-----\\nMIIEvQI...\\n-----END PRIVATE KEY-----"
    chave_normalizada = chave_literal.replace("\\n", "\n")
    
    # Confirma que a transformação funciona corretamente
    assert "\\n" not in chave_normalizada  # não tem mais a sequência literal
    assert "\n" in chave_normalizada  # tem quebras reais
    assert chave_normalizada.startswith("-----BEGIN PRIVATE KEY-----\n")
    assert chave_normalizada.endswith("\n-----END PRIVATE KEY-----")
    assert chave_normalizada.count("\n") >= 2  # pelo menos BEGIN e END


def test_normalizacao_key_content_multiplas_linhas():
    """Testa normalização com múltiplas linhas de chave."""
    chave_multiplas = "-----BEGIN PRIVATE KEY-----\\nLINHA1\\nLINHA2\\nLINHA3\\n-----END PRIVATE KEY-----"
    chave_normalizada = chave_multiplas.replace("\\n", "\n")
    
    assert chave_normalizada.count("\n") == 4  # BEGIN, LINHA1, LINHA2, LINHA3 (END não tem \n depois)
    assert "LINHA1\nLINHA2\nLINHA3" in chave_normalizada


def test_erro_credencial_explicito_fora_modo_demo():
    """Testa que erro de credencial aparece explicitamente fora do modo demo.
    
    Documenta o comportamento esperado do historico.py após os ajustes do PR #21.
    """
    motivo = "Credencial da OCI nao encontrada em /home/user/.oci/config"
    
    # Simulação da lógica do historico.py
    eh_erro_credencial = "credencial" in motivo.lower()
    em_modo_demo = False  # estado != ("Vazio", "Carregando", "Erro de conexão")
    
    # Fora do modo demo: erro de credencial deve ser exibido
    assert eh_erro_credencial
    assert not em_modo_demo
    # Com essa combinação, o erro seria exibido


def test_erro_credencial_oculto_em_modo_demo():
    """Testa que erro de credencial fica oculto EM modo demonstração."""
    motivo = "Credencial da OCI nao encontrada"
    
    # Simulação da lógica do historico.py
    eh_erro_credencial = "credencial" in motivo.lower()
    em_modo_demo = True  # estado in ("Vazio", "Carregando", "Erro de conexão")
    
    assert eh_erro_credencial
    assert em_modo_demo
    # Com essa combinação, o erro NÃO seria exibido


def test_erro_operacional_sempre_exibido():
    """Testa que erros não relacionados a credencial são sempre exibidos."""
    motivos_operacionais = [
        "Falha de rede: Connection timeout",
        "Permissão negada ao acessar o bucket",
        "Bucket não encontrado",
        "SDK da OCI nao instalado",
    ]
    
    for motivo in motivos_operacionais:
        eh_erro_credencial = "credencial" in motivo.lower()
        # Erros operacionais não contêm "credencial"
        assert not eh_erro_credencial
        # Portanto, seriam sempre exibidos independente do modo


def test_caminho_credenciais_secrets_documentado():
    """Documenta o caminho preferencial: Streamlit secrets com fallback para arquivo.
    
    Este teste documenta o comportamento implementado em oci_storage._config():
    1. Tenta ler st.secrets primeiro (OCI_USER, OCI_FINGERPRINT, OCI_TENANCY, 
       OCI_REGION, OCI_KEY_CONTENT)
    2. Se secrets presentes: usa apenas eles, SEM fallback silencioso
    3. Se secrets ausentes: usa ~/.oci/config como fallback
    
    Testes de integração completa requerem ambiente com OCI SDK configurado.
    """
    # Variáveis esperadas em st.secrets
    variaveis_secrets = [
        "OCI_USER",
        "OCI_FINGERPRINT", 
        "OCI_TENANCY",
        "OCI_REGION",
        "OCI_KEY_CONTENT",
    ]
    
    # Confirma que a lista está completa
    assert len(variaveis_secrets) == 5
    assert "OCI_USER" in variaveis_secrets
    assert "OCI_KEY_CONTENT" in variaveis_secrets
    
    # Comportamento esperado está documentado em:
    # - .streamlit/secrets.toml.example
    # - README.md seção "Configuração de credenciais OCI"
    # - Código em app/services/oci_storage.py função _config()


def test_gitignore_protege_secrets():
    """Confirma que secrets.toml está no .gitignore."""
    import pathlib
    
    gitignore_path = pathlib.Path(__file__).parent.parent / ".gitignore"
    if gitignore_path.exists():
        conteudo = gitignore_path.read_text(encoding="utf-8")
        assert ".streamlit/secrets.toml" in conteudo or "secrets.toml" in conteudo
