"""Testes automatizados para o Grupo A do CATP (CATP-001, CATP-002, CATP-003).

Valida ingestão de arquivos CSV e JSON no frontend, preservação de campos e tratamento de dados inválidos.
"""
import sys
from pathlib import Path

import pytest

# Adiciona o diretório app/ para importação
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from services import data_service as svc

REPO_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = REPO_ROOT / "data" / "samples"


def test_catp_001_importacao_csv_valido():
    """CATP-001: Valida processamento e extração correta de arquivo CSV válido."""
    caminho = SAMPLES_DIR / "catp001_amostra_valida.csv"
    assert caminho.exists(), f"Arquivo de teste não encontrado: {caminho}"

    itens = svc.parse_interacoes(caminho.name, caminho.read_bytes())

    assert len(itens) == 6
    assert itens[0]["autor"] == "Marina Costa"
    assert itens[0]["canal"] == "#conquistas"
    assert itens[0]["_id_efetivo"] == 1
    assert "primeira vaga" in itens[0]["texto"]


def test_catp_002_importacao_json_valido():
    """CATP-002: Valida importação correta de arquivo JSON válido."""
    caminho = SAMPLES_DIR / "catp002_amostra_valida.json"
    assert caminho.exists(), f"Arquivo de teste não encontrado: {caminho}"

    itens = svc.parse_interacoes(caminho.name, caminho.read_bytes())

    assert len(itens) == 6
    assert itens[1]["autor"] == "Lucas Almeida"
    assert itens[1]["canal"] == "#projetos"
    assert itens[1]["_id_efetivo"] == 2


def test_catp_003_dados_invalidos_csv_sem_colunas():
    """CATP-003: Valida tratamento de erro para CSV sem colunas obrigatórias."""
    caminho = SAMPLES_DIR / "catp003_invalido_sem_colunas.csv"
    assert caminho.exists(), f"Arquivo de teste não encontrado: {caminho}"

    with pytest.raises(ValueError) as excinfo:
        svc.parse_interacoes(caminho.name, caminho.read_bytes())

    assert "faltam os campos" in str(excinfo.value)


def test_catp_003_dados_invalidos_json_malformado():
    """CATP-003: Valida tratamento de erro amigável para JSON com erro de sintaxe."""
    caminho = SAMPLES_DIR / "catp003_json_malformado.json"
    assert caminho.exists(), f"Arquivo de teste não encontrado: {caminho}"

    with pytest.raises(ValueError) as excinfo:
        svc.parse_interacoes(caminho.name, caminho.read_bytes())

    assert "JSON inválido" in str(excinfo.value)
