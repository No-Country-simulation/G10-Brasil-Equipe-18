"""Testes para o módulo app.services.oci_storage.

Testa o caminho de credenciais (st.secrets vs arquivo de config) e normalização
do OCI_KEY_CONTENT chamando código real com mocks, sem acessar OCI de verdade.
"""
import sys
from unittest.mock import MagicMock, patch
import pytest


def test_config_usa_secrets_quando_presentes():
    """Caso (a): secrets preenchidos - usa os secrets e NÃO cai no arquivo de config."""
    # Mock do OCI SDK antes de importar
    mock_oci = MagicMock()
    mock_client = MagicMock()
    mock_client.get_namespace.return_value.data = "test_namespace"
    mock_oci.object_storage.ObjectStorageClient.return_value = mock_client
    sys.modules['oci'] = mock_oci
    sys.modules['oci.object_storage'] = mock_oci.object_storage
    sys.modules['oci.config'] = mock_oci.config
    
    # Mock do streamlit com secrets completos
    mock_st = MagicMock()
    mock_st.secrets = {
        "OCI_USER": "ocid1.user.test",
        "OCI_FINGERPRINT": "aa:bb:cc:dd:ee:ff",
        "OCI_TENANCY": "ocid1.tenancy.test",
        "OCI_REGION": "sa-saopaulo-1",
        "OCI_KEY_CONTENT": "-----BEGIN PRIVATE KEY-----\\nMIIE...\\n-----END PRIVATE KEY-----",
    }
    sys.modules['streamlit'] = mock_st
    
    try:
        # Remove cache e importa
        if 'app.services.oci_storage' in sys.modules:
            del sys.modules['app.services.oci_storage']
        from app.services import oci_storage
        
        cliente, namespace, bucket = oci_storage._config()
        
        # Verifica que usou secrets
        assert cliente is not None
        assert namespace == "test_namespace"
        assert bucket == "G10communitylab-ativos"
        
        # Verifica que NÃO caiu no arquivo
        mock_oci.config.from_file.assert_not_called()
        
        # Verifica que config foi montado com secrets e normalização aplicada
        args_chamada = mock_oci.object_storage.ObjectStorageClient.call_args
        config_usado = args_chamada[0][0]
        assert config_usado["user"] == "ocid1.user.test"
        assert config_usado["fingerprint"] == "aa:bb:cc:dd:ee:ff"
        # Verifica normalização: \\n literal virou \n real
        assert "\n" in config_usado["key_content"]
        assert "\\n" not in config_usado["key_content"]
    finally:
        for mod in ['streamlit', 'oci', 'oci.object_storage', 'oci.config', 'app.services.oci_storage']:
            if mod in sys.modules:
                del sys.modules[mod]


def test_config_usa_arquivo_quando_secrets_ausentes():
    """Caso (b): sem secrets - usa o arquivo de config."""
    # Mock do OCI SDK
    mock_oci = MagicMock()
    mock_client = MagicMock()
    mock_client.get_namespace.return_value.data = "namespace_from_file"
    mock_oci.object_storage.ObjectStorageClient.return_value = mock_client
    mock_oci.config.from_file.return_value = {
        "user": "ocid1.user.fromfile",
        "fingerprint": "11:22:33:44:55:66",
        "tenancy": "ocid1.tenancy.fromfile",
        "region": "us-ashburn-1",
        "key_file": "/path/to/key.pem",
    }
    sys.modules['oci'] = mock_oci
    sys.modules['oci.object_storage'] = mock_oci.object_storage
    sys.modules['oci.config'] = mock_oci.config
    
    # Mock do streamlit SEM secrets
    mock_st = MagicMock()
    if hasattr(mock_st, 'secrets'):
        delattr(mock_st, 'secrets')
    sys.modules['streamlit'] = mock_st
    
    try:
        with patch("app.services.oci_storage.Path") as mock_path_class:
            # Mock do Path
            mock_path_inst = MagicMock()
            mock_path_inst.exists.return_value = True
            mock_path_class.return_value = mock_path_inst
            
            # Remove cache e importa
            if 'app.services.oci_storage' in sys.modules:
                del sys.modules['app.services.oci_storage']
            from app.services import oci_storage
            
            cliente, namespace, bucket = oci_storage._config()
            
            # Verifica que usou o arquivo
            assert cliente is not None
            assert namespace == "namespace_from_file"
            mock_oci.config.from_file.assert_called_once()
    finally:
        for mod in ['streamlit', 'oci', 'oci.object_storage', 'oci.config', 'app.services.oci_storage']:
            if mod in sys.modules:
                del sys.modules[mod]


def test_config_falha_explicitamente_com_secrets_invalidos():
    """Caso (c): secrets presentes mas credencial falha - para com erro explícito, sem fallback."""
    # Mock do OCI SDK que falha
    mock_oci = MagicMock()
    mock_oci.object_storage.ObjectStorageClient.side_effect = Exception("Invalid credentials")
    sys.modules['oci'] = mock_oci
    sys.modules['oci.object_storage'] = mock_oci.object_storage
    sys.modules['oci.config'] = mock_oci.config
    
    mock_st = MagicMock()
    mock_st.secrets = {
        "OCI_USER": "ocid1.user.invalid",
        "OCI_FINGERPRINT": "invalid",
        "OCI_TENANCY": "ocid1.tenancy.invalid",
        "OCI_KEY_CONTENT": "INVALID KEY",
    }
    sys.modules['streamlit'] = mock_st
    
    try:
        # Remove cache e importa
        if 'app.services.oci_storage' in sys.modules:
            del sys.modules['app.services.oci_storage']
        from app.services import oci_storage
        
        # Deve levantar erro explícito, não cair no arquivo
        with pytest.raises(oci_storage.ErroArmazenamento) as exc_info:
            oci_storage._config()
        
        assert "Falha ao autenticar via Streamlit secrets" in str(exc_info.value)
        # Verifica que NÃO tentou fallback para arquivo
        mock_oci.config.from_file.assert_not_called()
    finally:
        for mod in ['streamlit', 'oci', 'oci.object_storage', 'oci.config', 'app.services.oci_storage']:
            if mod in sys.modules:
                del sys.modules[mod]


def test_normalizacao_key_content_chamando_codigo_real():
    """Caso (d): OCI_KEY_CONTENT com \\n literal sai com quebra real, chamando função real."""
    # Mock do OCI SDK
    mock_oci = MagicMock()
    mock_client = MagicMock()
    mock_client.get_namespace.return_value.data = "test_ns"
    mock_oci.object_storage.ObjectStorageClient.return_value = mock_client
    sys.modules['oci'] = mock_oci
    sys.modules['oci.object_storage'] = mock_oci.object_storage
    sys.modules['oci.config'] = mock_oci.config
    
    mock_st = MagicMock()
    # Chave com \\n literal (como vem de secrets.toml quando colada)
    mock_st.secrets = {
        "OCI_USER": "ocid1.user.test",
        "OCI_FINGERPRINT": "aa:bb:cc:dd:ee:ff",
        "OCI_TENANCY": "ocid1.tenancy.test",
        "OCI_KEY_CONTENT": "-----BEGIN PRIVATE KEY-----\\nLINHA1\\nLINHA2\\n-----END PRIVATE KEY-----",
    }
    sys.modules['streamlit'] = mock_st
    
    try:
        # Remove cache e importa
        if 'app.services.oci_storage' in sys.modules:
            del sys.modules['app.services.oci_storage']
        from app.services import oci_storage
        
        # Chama a função real
        cliente, namespace, bucket = oci_storage._config()
        
        # Pega o config que foi passado para o cliente
        args_chamada = mock_oci.object_storage.ObjectStorageClient.call_args
        config_usado = args_chamada[0][0]
        chave_normalizada = config_usado["key_content"]
        
        # Verifica normalização: \\n literal foi trocado por \n real
        assert "\\n" not in chave_normalizada, "Sequência literal \\\\n ainda presente"
        assert "\n" in chave_normalizada, "Quebras reais ausentes"
        assert "LINHA1\nLINHA2" in chave_normalizada, "Linhas não foram separadas corretamente"
        assert chave_normalizada.startswith("-----BEGIN PRIVATE KEY-----\n")
    finally:
        for mod in ['streamlit', 'oci', 'oci.object_storage', 'oci.config', 'app.services.oci_storage']:
            if mod in sys.modules:
                del sys.modules[mod]
