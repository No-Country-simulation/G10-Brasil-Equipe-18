"""Card 13: respostas fictícias, API/storage simulados e AppTest."""
import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator, FormatChecker

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from services import llm, llm_provider, data_service as svc
from services.testemunhos import converter_testemunho_canonico, preparar_testemunho

CENARIOS = [
    ("conquista_profissional", "Estudei por oito meses. Consegui minha primeira vaga como analista."),
    ("projeto_destaque", "Criei um painel com SQL. Entreguei o projeto para a equipe."),
    ("superacao", "Tive dificuldade no primeiro módulo. Retomei e concluí o módulo."),
]


def dados(tipo, texto, indice=1):
    citacao = texto.split('. ', 1)[-1]
    h = {
        "id": f"hist-{indice:03d}", "indice_interacao": indice,
        "sentimento": "positivo", "relevancia": "alta", "tipo_insight": "conquista",
        "topicos": ["carreira"], "tipo": tipo, "resumo": texto,
        "resultados": [citacao], "fatos": [citacao], "destaques": [citacao],
        "ativos": [{"id": "testemunho_estruturado", "tipo": "aprovado", "campos": {
            "titulo": citacao, "descricao": texto, "citacao": citacao},
            "interacoes_origem": [999], "autorizacao": "registrada"}],
    }
    fonte = {"id": 40 + indice, "autor": f"membro_{indice}", "canal": "#teste", "texto": texto}
    return h, fonte


def normalizar(h, fonte):
    return llm._normalizar([h], [fonte])


@pytest.mark.parametrize("tipo,texto", CENARIOS)
def test_tres_categorias_e_projecao_canonica(tipo, texto):
    h, fonte = dados(tipo, texto)
    historia = normalizar(h, fonte)[0]
    ativo = historia["ativos"][0]
    assert ativo["tipo"] == "testemunho"
    assert ativo["interacoes_origem"] == [41]
    assert "autorizacao" not in ativo
    assert historia["testemunho_pendente"] == ""
    canonico = converter_testemunho_canonico(ativo, "ativo_001", "2026-11-22T15:00:00Z")
    schema = json.loads((Path(__file__).resolve().parents[1] / "schemas/ativo_gerado_schema.json").read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(canonico)
    assert canonico["texto"] == texto + '\n\n"' + ativo["campos"]["citacao"] + '"'
    assert canonico["status_revisao"] == "pendente"


@pytest.mark.parametrize("campo", ["descricao", "citacao"])
@pytest.mark.parametrize("valor", [None, "", "Concluiu um curso na Oracle e ganhou 50%."])
def test_campos_incompletos_ou_inventados_preservam_historia(campo, valor):
    h, fonte = dados(*CENARIOS[0])
    h["ativos"][0]["campos"][campo] = valor
    saida = normalizar(h, fonte)
    assert len(saida) == 1 and saida[0]["ativos"] == []
    assert saida[0]["testemunho_pendente"]


@pytest.mark.parametrize("titulo", [
    None,
    "",
    "Concluiu um curso na Oracle e ganhou 50%.",   # estilo Cohere: parafraseado
    "a" * 201,
])
def test_titulo_invalido_e_derivado_da_citacao_sem_perder_o_testemunho(titulo):
    h, fonte = dados(*CENARIOS[0])
    h["ativos"][0]["campos"]["titulo"] = titulo
    historia = normalizar(h, fonte)[0]

    assert [a["id"] for a in historia["ativos"]] == ["testemunho_estruturado"]
    assert historia["testemunho_pendente"] == ""
    ativo = historia["ativos"][0]
    assert ativo["campos"]["titulo"] == ativo["campos"]["citacao"]
    canonico = converter_testemunho_canonico(ativo, "ativo_001", "2026-11-23T12:00:00Z")
    assert canonico["titulo"] == ativo["campos"]["citacao"]


def test_titulo_literal_diferente_da_citacao_e_preservado():
    h, fonte = dados(*CENARIOS[0])
    h["ativos"][0]["campos"]["titulo"] = "Estudei por oito meses."
    ativo = normalizar(h, fonte)[0]["ativos"][0]

    assert ativo["campos"]["titulo"] == "Estudei por oito meses."
    assert ativo["campos"]["citacao"] == "Consegui minha primeira vaga como analista."


def test_titulo_derivado_corta_em_palavra_inteira():
    frase = "Aprendi a trabalhar em equipe durante o projeto. "
    citacao = (frase * 6).strip()          # 281 caracteres: acima do limite de 200
    fonte = citacao + " Consegui a vaga."
    ativo, erro = preparar_testemunho(
        {"campos": {"titulo": "", "descricao": citacao, "citacao": citacao}},
        fonte,
        [{"texto": citacao, "id_interacao": 41}],
        41,
    )

    assert erro == ""
    titulo = ativo["campos"]["titulo"]
    assert titulo == citacao[:200].rsplit(" ", 1)[0]
    assert len(titulo) <= 200 and titulo in fonte and not titulo.endswith(" ")


@pytest.mark.parametrize("separador", ["\n", "\t"])
def test_titulo_derivado_trata_quebra_de_linha_e_tabulacao_como_limite(separador):
    palavras = ["Aprendi", "a", "trabalhar", "em", "equipe", "durante", "o", "projeto,"] * 8
    citacao = separador.join(palavras)          # sem espaços: só o separador testado
    fonte = citacao + separador + "Consegui a vaga."
    ativo, erro = preparar_testemunho(
        {"campos": {"titulo": "", "descricao": citacao, "citacao": citacao}},
        fonte,
        [{"texto": citacao, "id_interacao": 41}],
        41,
    )

    assert erro == ""
    titulo = ativo["campos"]["titulo"]
    assert len(titulo) <= 200
    assert titulo in citacao                      # recorte literal da citação, preservado
    assert citacao[len(titulo)] == separador      # cortou no limite, não no meio da palavra



def test_citacao_literal_mas_nao_conferida_e_recusada():
    h, fonte = dados(*CENARIOS[0])
    h["ativos"][0]["campos"]["citacao"] = "Estudei por oito meses."
    assert normalizar(h, fonte)[0]["ativos"] == []


def test_testemunhos_duplicados_nao_geram_colisao():
    h, fonte = dados(*CENARIOS[0]); h["ativos"] *= 2
    assert normalizar(h, fonte)[0]["ativos"] == []


def test_duas_historias_sem_mistura():
    ha, fa = dados(*CENARIOS[0]); hb, fb = dados(*CENARIOS[1], indice=2)
    ha["ativos"][0]["campos"]["descricao"] = fb["texto"]
    historias = llm._normalizar([ha, hb], [fa, fb])
    assert historias[0]["ativos"] == []
    assert historias[1]["ativos"][0]["interacoes_origem"] == [42]


def test_testemunho_e_case_na_mesma_resposta(monkeypatch):
    h, fonte = dados(*CENARIOS[0])
    h["ativos"].append({"id": "case_sucesso", "campos": {"texto": fonte["texto"]}})
    chamadas = []
    class Provedor:
        def __init__(self, **kwargs): pass
        def gerar(self, prompt, payload, *, natureza_dados):
            chamadas.append(prompt)
            return SimpleNamespace(texto=json.dumps({"historias": [h]}), provedor="teste", finish_reason="STOP")
    monkeypatch.setattr(llm_provider, "LLMProvider", Provedor)
    monkeypatch.setattr(llm, "anonimizar_texto", lambda t: (t, {}))
    historias = llm.analisar([fonte], natureza_dados="ficticios")
    assert len(chamadas) == 1 and "testemunho_estruturado" in chamadas[0]
    assert {a["id"] for a in historias[0]["ativos"]} == {"case_sucesso", "testemunho_estruturado"}


@pytest.mark.parametrize("id_ativo,instante", [("errado", "2026-11-22T15:00:00Z"), ("ativo_001", "2026-11-22T15:00:00")])
def test_projecao_exige_identidade_e_instante_da_aplicacao(id_ativo, instante):
    h, fonte = dados(*CENARIOS[0]); a = normalizar(h, fonte)[0]["ativos"][0]
    with pytest.raises(ValueError): converter_testemunho_canonico(a, id_ativo, instante)


def test_campos_editados_preservados_no_pacote(monkeypatch):
    h, fonte = dados(*CENARIOS[0]); historias = normalizar(h, fonte)
    editadas = svc.aplicar_edicoes(historias, {"c:hist-001:testemunho_estruturado:descricao": "Descrição revisada pela equipe."})
    objetos = {}
    class Storage:
        @staticmethod
        def caminho_do_lote(lote, nome): return "ativos/" + lote + "/pacote.json"
        @staticmethod
        def salvar_objeto(caminho, dados):
            objetos[caminho] = json.loads(json.dumps(dados)); return {"tamanho": 100}
    monkeypatch.setattr(svc, "_storage", lambda: Storage)
    svc.salvar_no_oci([{"caminho": "pacote.json"}], "teste", editadas, "ficticios")
    ativo = next(iter(objetos.values()))["historias"][0]["ativos"][0]
    assert ativo["campos"]["descricao"] == "Descrição revisada pela equipe."
    assert ativo["campos"]["citacao"] == h["destaques"][0]
    assert ativo["interacoes_origem"] == [41]

