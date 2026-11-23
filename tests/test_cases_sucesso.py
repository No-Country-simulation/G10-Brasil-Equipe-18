"""Card 14: fluxo com respostas e storage simulados, sem API/OCI reais."""
import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from services import llm, llm_provider, data_service as svc

CENARIOS = [
    ("conquista_profissional", "Estudei por oito meses. Consegui minha primeira vaga como analista.", "Consegui minha primeira vaga como analista."),
    ("projeto_destaque", "Criei um painel de vendas com SQL. Entreguei o projeto para a equipe.", "Entreguei o projeto para a equipe."),
    ("superacao", "Tive dificuldade no primeiro módulo. Retomei os estudos e concluí o módulo.", "Retomei os estudos e concluí o módulo."),
]


def resposta(tipo, texto, resultado, indice=1):
    return {
        "id": f"hist-{indice:03d}", "indice_interacao": indice,
        "sentimento": "positivo", "relevancia": "alta", "tipo_insight": "conquista",
        "topicos": ["carreira"], "tipo": tipo, "resumo": texto,
        "resultados": [resultado], "fatos": [resultado], "destaques": [resultado],
        "ativos": [{"id": "case_sucesso", "tipo": "texto", "campos": {"texto": texto}}],
    }


def normalizar(h, texto, ident=41):
    return llm._normalizar([h], [{"id": ident, "autor": "membro_teste", "canal": "#teste", "texto": texto}])


@pytest.mark.parametrize("tipo,texto,resultado", CENARIOS)
def test_tres_categorias_com_case_rastreado(tipo, texto, resultado):
    h = normalizar(resposta(tipo, texto, resultado), texto)[0]
    case = h["ativos"][0]
    assert case["id"] == "case_sucesso" and case["tipo"] == "texto"
    assert case["campos"]["texto"] == texto
    assert case["interacoes_origem"] == [41]
    assert case["citacoes"] == [{"texto": resultado, "id_interacao": 41}]
    assert h["case_pendente"] == ""
    assert not {"aprovado", "autorizacao_publicacao", "status_revisao"} & case.keys()


@pytest.mark.parametrize("alteracao", ["inventado", "resultado", "citacao", "duplicado", "vazio", "null"])
def test_case_invalido_nao_apaga_historia(alteracao):
    tipo, texto, resultado = CENARIOS[0]
    h = resposta(tipo, texto, resultado)
    campos = h["ativos"][0]["campos"]
    if alteracao == "inventado": campos["texto"] += " Aumentou a renda em 50%."
    if alteracao == "resultado": h["resultados"] = ["Concluiu dois projetos."]
    if alteracao == "citacao": campos["texto"] = "Estudei por oito meses."
    if alteracao == "duplicado": h["ativos"] *= 2
    if alteracao == "vazio": campos["texto"] = ""
    if alteracao == "null": campos["texto"] = None
    saida = normalizar(h, texto)
    assert len(saida) == 1
    assert saida[0]["ativos"] == [] and saida[0]["case_pendente"]


@pytest.mark.parametrize("titulo", [
    "Contratação na Oracle",
    "Consegui minha primeira vaga na Oracle!",
    "a" * 201,
    None,
    "",
])
def test_titulo_fora_da_fonte_e_descartado_sem_perder_o_case(titulo):
    """Estilo Cohere: título parafraseado não pode derrubar o case conferido."""
    tipo, texto, resultado = CENARIOS[0]
    h = resposta(tipo, texto, resultado)
    h["ativos"][0]["campos"]["titulo"] = titulo
    historia = normalizar(h, texto)[0]

    assert [a["id"] for a in historia["ativos"]] == ["case_sucesso"]
    case = historia["ativos"][0]
    assert "titulo" not in case
    assert historia["case_pendente"] == ""
    assert case["campos"]["texto"] == texto


def test_titulo_literal_continua_no_case():
    tipo, texto, resultado = CENARIOS[0]
    h = resposta(tipo, texto, resultado)
    h["ativos"][0]["campos"]["titulo"] = "Consegui minha primeira vaga como analista."
    case = normalizar(h, texto)[0]["ativos"][0]

    assert case["titulo"] == "Consegui minha primeira vaga como analista."
    assert case["campos"] == {"texto": texto}


def test_fonte_insuficiente_preserva_outros_ativos():
    texto = "Quero conseguir minha primeira vaga."
    h = resposta("conquista_profissional", texto, "Consegui minha primeira vaga.")
    h["destaques"] = [texto]
    h["ativos"].append({"id": "post_linkedin", "tipo": "texto", "campos": {"texto": texto}})
    saida = normalizar(h, texto)[0]
    assert [a["id"] for a in saida["ativos"]] == ["post_linkedin"]
    assert saida["case_pendente"]


def test_duas_historias_nao_aceitam_texto_da_outra():
    a, b = CENARIOS[:2]
    ha, hb = resposta(*a), resposta(*b, indice=2)
    ha["ativos"][0]["campos"]["texto"] = b[1]
    historias = llm._normalizar([ha, hb], [
        {"id": 41, "autor": "membro_a", "texto": a[1]},
        {"id": 99, "autor": "membro_b", "texto": b[1]},
    ])
    assert historias[0]["ativos"] == []
    assert historias[1]["ativos"][0]["interacoes_origem"] == [99]


def test_mesma_chamada_de_analise_gera_case(monkeypatch):
    chamadas = []
    tipo, texto, resultado = CENARIOS[0]
    class Provedor:
        def __init__(self, **kwargs): pass
        def gerar(self, prompt, payload):
            chamadas.append((prompt, json.loads(payload)))
            return SimpleNamespace(texto=json.dumps({"historias": [resposta(tipo, texto, resultado)]}), provedor="teste", finish_reason="STOP")
    monkeypatch.setattr(llm_provider, "LLMProvider", Provedor)
    monkeypatch.setattr(llm, "anonimizar_texto", lambda t: (t, {}))
    saida = llm.analisar([{"id": 41, "autor": "membro_teste", "texto": texto}])
    assert len(chamadas) == 1 and "case_sucesso" in chamadas[0][0]
    assert saida[0]["ativos"][0]["campos"]["texto"] == texto


def test_edicao_e_roundtrip_do_pacote_com_storage_simulado(monkeypatch):
    tipo, texto, resultado = CENARIOS[0]
    historias = normalizar(resposta(tipo, texto, resultado), texto)
    editadas = svc.aplicar_edicoes(historias, {"c:hist-001:case_sucesso:texto": "Revisão humana do case."})
    assert historias[0]["ativos"][0]["campos"]["texto"] == texto
    objetos = {}
    class Storage:
        @staticmethod
        def caminho_do_lote(lote, nome): return "ativos/" + lote + "/pacote.json"
        @staticmethod
        def salvar_objeto(caminho, dados):
            objetos[caminho] = json.loads(json.dumps(dados))
            return {"caminho": caminho, "tamanho": 100}
    monkeypatch.setattr(svc, "_storage", lambda: Storage)
    svc.salvar_no_oci([{"caminho": "pacote.json"}], "teste", editadas, "ficticios")
    salvo = next(iter(objetos.values()))
    case = salvo["historias"][0]["ativos"][0]
    assert case["campos"]["texto"] == "Revisão humana do case."
    assert case["interacoes_origem"] == [41]
    assert salvo["natureza_dados"] == "ficticios"


def test_case_editavel_no_estudio_e_curadoria():
    from streamlit.testing.v1 import AppTest
    tipo, texto, resultado = CENARIOS[0]
    h = normalizar(resposta(tipo, texto, resultado), texto)[0]
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app/main.py"), default_timeout=15).run()
    at.session_state["historias"] = [h]
    at.session_state["historia_atual"] = h["id"]
    at.session_state["pagina"] = "estudio"
    at.run()
    assert not at.exception
    next(t for t in at.text_area if t.label == "Texto do case").input("Case editado pela equipe.").run()
    at.button(key="enviar_hist-001").click().run()
    assert not at.exception
    assert any(t.value == "Case editado pela equipe." for t in at.text_area)
    chave = "hist-001:case_sucesso"
    assert at.session_state["validacao_factual"].get(chave, "pendente") == "pendente"
    assert at.session_state["status_curadoria"].get(chave, "rascunho") == "rascunho"
    assert at.session_state["autorizacao"].get(chave, "nao_registrada") != "registrada"


@pytest.mark.parametrize("pagina", ["estudio", "curadoria"])
def test_historia_sem_case_e_sem_outro_ativo_nao_quebra_tela(pagina):
    from streamlit.testing.v1 import AppTest
    tipo, texto, resultado = CENARIOS[0]
    h = resposta(tipo, texto, resultado)
    h["ativos"][0]["campos"]["texto"] = "Texto inventado."
    historia = normalizar(h, texto)[0]
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app/main.py"), default_timeout=15).run()
    at.session_state["historias"] = [historia]
    at.session_state["historia_atual"] = historia["id"]
    at.session_state["pagina"] = pagina
    at.run()
    assert not at.exception
    assert any("Case pendente" in w.value for w in at.warning)
