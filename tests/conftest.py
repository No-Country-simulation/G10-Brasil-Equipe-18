"""conftest.py — configurações e fixtures compartilhadas para a suíte de testes.

A fixture `ocultar_secrets_reais` garante que o AppTest de regressão não leia
o .streamlit/secrets.toml real (que pode ter GEMINI_API_KEY ou credenciais OCI),
evitando chamadas externas durante testes automatizados.

O arquivo é renomeado para secrets.toml.pytest_backup antes de cada teste de
regressão e restaurado ao término, sem alteração de conteúdo.
"""
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
SECRETS_PATH = REPO_ROOT / ".streamlit" / "secrets.toml"
SECRETS_BACKUP = REPO_ROOT / ".streamlit" / "secrets.toml.pytest_backup"


@pytest.fixture(autouse=True)
def ocultar_secrets_reais(request):
    """Oculta temporariamente o secrets.toml durante testes que usam AppTest.

    Só age quando o teste usa AppTest (identificado pelo nome do arquivo).
    Para os demais testes, é um no-op sem custo.
    """
    # Só age no arquivo de regressão do front
    if "test_front_regressao" not in request.fspath.basename:
        yield
        return

    # Garante que GEMINI_API_KEY não vaze por variável de ambiente
    api_key_original = os.environ.pop("GEMINI_API_KEY", None)

    # Oculta o secrets.toml para o Streamlit não encontrá-lo
    ocultou = False
    if SECRETS_PATH.exists():
        SECRETS_PATH.rename(SECRETS_BACKUP)
        ocultou = True

    try:
        yield
    finally:
        # Restaura tudo ao estado original
        if ocultou and SECRETS_BACKUP.exists():
            SECRETS_BACKUP.rename(SECRETS_PATH)
        if api_key_original is not None:
            os.environ["GEMINI_API_KEY"] = api_key_original
