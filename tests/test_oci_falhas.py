"""Falhas controladas da persistencia: gravacao e recuperacao (Card 19)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services import data_service as svc


class StorageQueFalhaAoGravar:
    def caminho_do_lote(self, lote_id, arquivo=None):
        return f"ativos/{lote_id}/{arquivo}"

    def salvar_objeto(self, caminho, dados):
        raise RuntimeError("falha simulada de gravacao")


class StorageQueFalhaAoLer:
    def ler_objeto(self, caminho):
        raise RuntimeError("falha simulada de leitura")


PACOTES = [{"caminho": "pacote-distribuicao.json"}, {"caminho": "evidencias.json"}]
HISTORIAS = [{"autor": "Ana", "citacoes": [{"id_interacao": 1, "texto": "trecho"}]}]


def test_falha_na_gravacao_nao_vira_sucesso(monkeypatch):
    """Erro ao gravar tem que voltar como falha com motivo, nunca como salvo."""
    monkeypatch.setattr(svc, "_storage", lambda: StorageQueFalhaAoGravar())
    svc.ULTIMO_ERRO_OCI = ""

    resultado = svc.salvar_no_oci(PACOTES, "LOTE-TESTE-FALHA", historias=HISTORIAS)

    assert all(r["status"] == "falhou" for r in resultado)
    assert all("falha simulada de gravacao" in (r["motivo"] or "") for r in resultado)
    assert "falha simulada de gravacao" in svc.ULTIMO_ERRO_OCI


def test_falha_na_recuperacao_devolve_vazio_com_erro_registrado(monkeypatch):
    """Erro ao ler tem que devolver vazio e registrar o motivo, nunca conteudo inventado."""
    monkeypatch.setattr(svc, "_storage", lambda: StorageQueFalhaAoLer())
    svc.ULTIMO_ERRO_OCI = ""

    assert svc.conteudo_pacote("ativos/LOTE/pacote-distribuicao.json") is None
    assert "falha simulada de leitura" in svc.ULTIMO_ERRO_OCI
