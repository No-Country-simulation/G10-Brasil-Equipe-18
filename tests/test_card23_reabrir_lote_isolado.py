"""Reabrir um lote pelo Histórico não pode reaproveitar rascunho de outro lote.

Os lotes A e B têm os mesmos ids (hist-001 / case_sucesso). Um texto editado
no lote A, no Estúdio (chave "e:") ou na Curadoria (chave "c:"), não pode
aparecer no lote B depois de aplicar_lote_recuperado. Sem OCI e sem LLM: o
pacote recuperado é simulado.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))

TEXTO_A = "Texto editado no lote A"
CAMPO = "hist-001:case_sucesso:texto"


class Sessao(dict):
    """Sessão mínima, com acesso por atributo como o st.session_state."""

    def __getattr__(self, nome):
        try:
            return self[nome]
        except KeyError as erro:
            raise AttributeError(nome) from erro

    def __setattr__(self, nome, valor):
        self[nome] = valor


def _lote_b():
    historia = {"id": "hist-001", "titulo": "História do lote B", "ativos": [
        {"id": "case_sucesso", "nome": "Case de sucesso", "tipo": "texto",
         "campos": {"texto": "Texto original do lote B"}}]}
    return {"ok": True, "lote_id": "LOTE-B", "historias": [historia], "pacotes": [],
            "natureza_dados": "ficticios", "origem_analise": "gemini",
            "decisoes": {}, "avisos": []}


def _reabrir_b_com_sessao_do_lote_a(prefixo):
    # Import tardio: outros testes mexem em sys.modules['streamlit'].
    from telas.historico import aplicar_lote_recuperado

    ss = Sessao(dados={f"{prefixo}:{CAMPO}": TEXTO_A}, lote_id="LOTE-A")
    ss[f"w::{prefixo}:{CAMPO}"] = TEXTO_A  # widget do campo editável
    aplicar_lote_recuperado(ss, _lote_b())
    return ss


@pytest.mark.parametrize("prefixo", ["e", "c"], ids=["estudio-e", "curadoria-c"])
def test_reabrir_lote_nao_reaproveita_texto_editado_de_outro_lote(prefixo):
    ss = _reabrir_b_com_sessao_do_lote_a(prefixo)

    assert ss.lote_id == "LOTE-B"
    assert f"{prefixo}:{CAMPO}" not in ss.dados
    assert f"w::{prefixo}:{CAMPO}" not in ss
    assert TEXTO_A not in ss.dados.values()
    assert TEXTO_A not in [v for k, v in ss.items() if k != "dados"]
