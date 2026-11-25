"""Regressão: resultados e diagnósticos não dependem de estado global."""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from services import llm, llm_provider, data_service as svc


def test_provedores_e_diagnosticos_concorrentes(monkeypatch):
    barreira = Barrier(2, timeout=10)

    class Provider:
        def __init__(self, **kwargs):
            pass

        def gerar(self, prompt, payload, **kwargs):
            provedor = json.loads(payload)[0]["texto"]
            return llm_provider.ResultadoLLM(texto=json.dumps({"historias": [{"id": provedor}]}), provedor=provedor, modelo="teste")

    def normalizar(historias, interacoes, **kwargs):
        nome = historias[0]["id"]
        llm._registro("avisos").append(nome)
        barreira.wait()
        return historias

    monkeypatch.setattr(llm_provider, "LLMProvider", Provider)
    monkeypatch.setattr(llm, "_normalizar", normalizar)
    monkeypatch.setattr(llm, "anonimizar_texto", lambda texto: (texto, {}))
    monkeypatch.setattr(llm, "normalizar_texto", lambda texto: texto)
    def executar(nome):
        return svc.analisar([{"id": 1, "autor": "teste", "texto": nome}], natureza_dados="ficticios")
    with ThreadPoolExecutor(max_workers=2) as pool:
        a, b = list(pool.map(executar, ["gemini", "cohere"]))
    assert (a.provedor, a.avisos, a[0]["id"]) == ("gemini", ("gemini",), "gemini")
    assert (b.provedor, b.avisos, b[0]["id"]) == ("cohere", ("cohere",), "cohere")


def test_falhas_carregam_tipo_proprio(monkeypatch):
    def falhar(itens, **kwargs):
        if itens[0]:
            raise llm.ErroRespostaTruncada("limite")
        raise llm.ErroAnalise("falha")
    monkeypatch.setattr(llm, "analisar", falhar)
    def executar(flag):
        try:
            svc.analisar([flag])
        except svc.FalhaAnalise as erro:
            return erro
    with ThreadPoolExecutor(max_workers=2) as pool:
        a, b = list(pool.map(executar, [True, False]))
    assert a.truncada is True
    assert b.truncada is False
