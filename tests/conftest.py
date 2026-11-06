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
SECRETS_BACKUP_BASE = REPO_ROOT / ".streamlit" / "secrets.toml.pytest_backup"


@pytest.fixture(autouse=True)
def ocultar_secrets_reais(request):
    """Oculta temporariamente o secrets.toml durante testes que usam AppTest.

    Só age quando o teste usa AppTest (identificado pelo nome do arquivo).
    Para os demais testes, é um no-op sem custo.

    Proteções implementadas:
    1. Se já existir um backup de execução anterior abortada e SECRETS_PATH não existir,
       restaura o arquivo antes do teste.
    2. Gera um destino de backup com sufixo numérico caso já exista um backup no disco,
       garantindo que nenhum backup prévio seja sobrescrito ou perdido.
    """
    # Só age no arquivo de regressão do front
    if "test_front_regressao" not in request.fspath.basename:
        yield
        return

    # Garante que GEMINI_API_KEY não vaze por variável de ambiente
    api_key_original = os.environ.pop("GEMINI_API_KEY", None)

    # Caso especial de autorrecuperação: se o secrets.toml original sumiu mas
    # o backup padrão existe (ex.: execução anterior abortada bruscamente), restaura primeiro
    if SECRETS_BACKUP_BASE.exists() and not SECRETS_PATH.exists():
        SECRETS_BACKUP_BASE.rename(SECRETS_PATH)

    # Determina um nome de backup seguro que não colida com nenhum arquivo existente
    backup_dest = SECRETS_BACKUP_BASE
    contador = 1
    while backup_dest.exists():
        backup_dest = REPO_ROOT / ".streamlit" / f"secrets.toml.pytest_backup_{contador}"
        contador += 1

    # Oculta o secrets.toml para o Streamlit não encontrá-lo
    ocultou = False
    if SECRETS_PATH.exists():
        SECRETS_PATH.rename(backup_dest)
        ocultou = True

    try:
        yield
    finally:
        # Restaura tudo ao estado original
        if ocultou and backup_dest.exists():
            backup_dest.rename(SECRETS_PATH)
        if api_key_original is not None:
            os.environ["GEMINI_API_KEY"] = api_key_original
