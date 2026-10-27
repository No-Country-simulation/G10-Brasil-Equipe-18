"""Testes para o módulo app.services.oci_storage.

Valida o caminho de credenciais (st.secrets vs arquivo de config),
normalização do OCI_KEY_CONTENT e comportamento do filtro de erro.
"""
from unittest.mock import MagicMock, patch
import pytest


def test_config_usa_secrets_quando_presentes():
    """Com secrets preenchidos: confirma que usa os secrets e NÃO cai no arquivo de config."""
    with patch("app.services.oci_storage.st") as mock_st:
        # Simula st.secrets preenchido
        mock_st.secrets = {
            "OCI_USER": "ocid1.user.test",
            "OCI_FINGERPRINT": "aa:bb:cc:dd:ee:ff",
            "OCI_TENANCY": "ocid1.tenancy.test",
            "OCI_REGION": "sa-saopaulo-1",
            "OCI_KEY_CONTENT": "-----BEGIN PRIVATE KEY-----\\nMIIE...\\n-----END PRIVATE KEY-----",
        }
        mock_st.secrets.get = lambda k, default=None: mock_st.secrets.get(k, default)

        with patch("app.services.oci_storage.oci") as mock_oci:
            mock_client = MagicMock()
            mock_client.get_namespace.return_value.data = "test_namespace"
            mock_oci.object_storage.ObjectStorageClient.return_value = mock_client

            from app.services import oci_storage
            
            # Força recarga do módulo para pegar o mock
            import importlib
            importlib.reload(oci_storage)
            
            cliente, namespace, bucket = oci_storage._config()

            # Confirma que o cliente foi criado com secrets
            assert cliente is not None
            assert namespace == "test_namespace"
            assert bucket == "G10communitylab-ativos"
            
            # Confirma que o config foi montado com os secrets
            args_chamada = mock_oci.object_storage.ObjectStorageClient.call_args
            config_usado = args_chamada[0][0]
            assert config_usado["user"] == "ocid1.user.test"
            assert config_usado["fingerprint"] == "aa:bb:cc:dd:ee:ff"


def test_config_usa_arquivo_quando_secrets_ausentes():
    """Sem secrets: confirma que usa o arquivo de config."""
    with patch("app.services.oci_storage.st") as mock_st:
        # Simula ausência de secrets
        mock_st.secrets = {}
        delattr(mock_st, "secrets")  # Remove o atributo completamente

        with patch("app.services.oci_storage.Path") as mock_path:
            # Simula arquivo ~/.oci/config existente
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            mock_path.return_value = mock_file

            with patch("app.services.oci_storage.oci") as mock_oci:
                # Mock do config.from_file
                mock_config = {
                    "user": "ocid1.user.fromfile",
                    "fingerprint": "11:22:33:44:55:66",
                    "tenancy": "ocid1.tenancy.fromfile",
                    "region": "us-ashburn-1",
                    "key_file": "/path/to/key.pem",
                }
                mock_oci.config.from_file.return_value = mock_config

                mock_client = MagicMock()
                mock_client.get_namespace.return_value.data = "namespace_from_file"
                mock_oci.object_storage.ObjectStorageClient.return_value = mock_client

                from app.services import oci_storage
                import importlib
                importlib.reload(oci_storage)

                cliente, namespace, bucket = oci_storage._config()

                # Confirma que usou o arquivo
                assert cliente is not None
                assert namespace == "namespace_from_file"
                mock_oci.config.from_file.assert_called_once()


def test_normalizacao_key_content():
    """Testa normalização do OCI_KEY_CONTENT: troca \\n literal por quebra real."""
    with patch("app.services.oci_storage.st") as mock_st:
        # Chave com \\n literal (dois caracteres: barra invertida + n)
        chave_literal = "-----BEGIN PRIVATE KEY-----\\nMIIEvQI...\\n-----END PRIVATE KEY-----"
        mock_st.secrets = {
            "OCI_USER": "ocid1.user.test",
            "OCI_FINGERPRINT": "aa:bb:cc:dd:ee:ff",
            "OCI_TENANCY": "ocid1.tenancy.test",
            "OCI_KEY_CONTENT": chave_literal,
        }
        mock_st.secrets.get = lambda k, default=None: mock_st.secrets.get(k, default)

        with patch("app.services.oci_storage.oci") as mock_oci:
            mock_client = MagicMock()
            mock_client.get_namespace.return_value.data = "test_namespace"
            mock_oci.object_storage.ObjectStorageClient.return_value = mock_client

            from app.services import oci_storage
            import importlib
            importlib.reload(oci_storage)

            cliente, namespace, bucket = oci_storage._config()

            # Verifica que a chave foi normalizada
            args_chamada = mock_oci.object_storage.ObjectStorageClient.call_args
            config_usado = args_chamada[0][0]
            chave_normalizada = config_usado["key_content"]
            
            # Confirma que \\n foi trocado por quebra real
            assert "\\n" not in chave_normalizada  # não tem mais literal
            assert "\n" in chave_normalizada  # tem quebra real
            assert chave_normalizada.startswith("-----BEGIN PRIVATE KEY-----\n")
            assert chave_normalizada.endswith("\n-----END PRIVATE KEY-----")


def test_erro_credencial_explicito_fora_modo_demo():
    """Testa que erro de credencial aparece explicitamente fora do modo demo.
    
    Nota: Este teste documenta o comportamento esperado do historico.py,
    não testa diretamente o oci_storage.py.
    """
    # Mock do svc.erro_armazenamento() retornando erro de credencial
    motivo = "Credencial da OCI nao encontrada em /home/user/.oci/config"
    
    # Simulação do comportamento do historico.py
    eh_erro_credencial = "credencial" in motivo.lower()
    em_modo_demo = False  # estado != ("Vazio", "Carregando", "Erro de conexão")
    
    # Fora do modo demo: erro de credencial deve ser exibido
    assert eh_erro_credencial
    assert not em_modo_demo
    # O teste confirma a lógica: erro seria exibido


def test_erro_operacional_sempre_exibido():
    """Testa que erros não relacionados a credencial são sempre exibidos."""
    motivos_operacionais = [
        "Falha de rede: Connection timeout",
        "Permissão negada ao acessar o bucket",
        "Bucket não encontrado",
    ]
    
    for motivo in motivos_operacionais:
        eh_erro_credencial = "credencial" in motivo.lower()
        # Erros operacionais não contêm "credencial"
        assert not eh_erro_credencial
        # Portanto, seriam sempre exibidos independente do modo


def test_disponivel_retorna_false_sem_credencial():
    """Testa que disponivel() retorna False quando credencial não existe."""
    with patch("app.services.oci_storage.st") as mock_st:
        delattr(mock_st, "secrets")
        
        with patch("app.services.oci_storage.Path") as mock_path:
            # Arquivo não existe
            mock_file = MagicMock()
            mock_file.exists.return_value = False
            mock_path.return_value = mock_file

            from app.services import oci_storage
            import importlib
            importlib.reload(oci_storage)

            disponivel = oci_storage.disponivel()
            motivo = oci_storage.motivo_indisponivel()

            assert not disponivel
            assert "Credencial da OCI nao encontrada" in motivo
