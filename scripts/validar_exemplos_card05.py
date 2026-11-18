"""Valida exemplos sintéticos do Card 05. Não chama Streamlit, LLM ou OCI."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def validar():
    interacoes = read("data/samples/card05/interacoes_canonicas.json")
    ativos = read("data/samples/card05/ativos_canonicos.json")
    entrada = read("data/samples/card05/entrada_app.json")
    envelope = read("data/samples/card05/envelope_proposto.json")
    vi = Draft202012Validator(read("schemas/interacao_schema.json"), format_checker=FormatChecker())
    va = Draft202012Validator(read("schemas/ativo_gerado_schema.json"), format_checker=FormatChecker())
    for schema in (vi.schema, va.schema):
        Draft202012Validator.check_schema(schema)
    for obj in interacoes:
        vi.validate(obj)
    for obj in ativos:
        va.validate(obj)
    fontes = {x["id"]: x["texto"] for x in entrada}
    canonicos = {x["id_ativo"]: x for x in ativos}
    historias = {x["id"]: x for x in envelope["historias"]}
    assert len(fontes) == len(entrada) == 2
    assert len(canonicos) == len(ativos) == 2
    assert len(historias) == 2
    for h in historias.values():
        for c in h["citacoes"]:
            assert c["id_interacao"] in h["interacoes_origem"]
            assert c["texto"] in fontes[c["id_interacao"]]
    for link in envelope["vinculos"]:
        h = historias[link["id_historia"]]
        ativo = canonicos[link["id_ativo"]]
        front = next(x for x in h["ativos"] if x["id"] == link["id_local"])
        assert ativo["interacoes_origem"] == h["interacoes_origem"]
        if ativo["tipo"] == "testemunho_estruturado":
            assert front["tipo"] == "testemunho"
            campos = front["campos"]
            assert ativo["titulo"] == campos["titulo"]
            assert ativo["texto"] == campos["descricao"] + '\n\n"' + campos["citacao"] + '"'
            assert any(campos["citacao"] == c["texto"] for c in h["citacoes"])
        else:
            assert ativo["tipo"] == "case_sucesso"
            assert front["tipo"] == "texto"
            assert ativo["texto"] == front["campos"]["texto"]
    for estado in envelope["curadoria"]:
        assert estado["lote"] == envelope["lote"]
        assert estado["id_ativo"] in canonicos
        assert estado["status_curadoria"] == "rascunho"
        assert estado["validacao_factual"] == "pendente"
        assert estado["autorizacao"] == "nao_registrada"
    def rejeita(validador, obj):
        try:
            validador.validate(obj)
        except ValidationError:
            return
        raise AssertionError("Exemplo inválido aceito")
    invalido = copy.deepcopy(ativos[0]); del invalido["interacoes_origem"]
    rejeita(va, invalido)
    invalido = copy.deepcopy(ativos[0]); invalido["campos"] = {}
    rejeita(va, invalido)
    invalido = copy.deepcopy(ativos[0]); invalido["oci_object_path"] = "ativos/LOTE-EXEMPLO/pacote-distribuicao.json"
    rejeita(va, invalido)
    invalido = copy.deepcopy(interacoes[0]); invalido["id"] = True
    rejeita(vi, invalido)
    return {"schemas_validos": 2, "interacoes_validas": len(interacoes), "ativos_validos": len(ativos),
            "vinculos_conferidos": len(envelope["vinculos"]), "rejeicoes_esperadas": 4,
            "llm_oci_streamlit": "não executados"}

if __name__ == "__main__":
    print(json.dumps(validar(), ensure_ascii=False, indent=2))
