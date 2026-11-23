"""Regressão de edição do testemunho no formulário real do Streamlit."""
from pathlib import Path
from test_testemunhos_estruturados import dados, normalizar, CENARIOS

def test_edicao_tres_campos_chega_a_curadoria():
    from streamlit.testing.v1 import AppTest
    h, fonte = dados(*CENARIOS[0]); historia = normalizar(h, fonte)[0]
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app/main.py"), default_timeout=15).run()
    at.session_state["historias"] = [historia]; at.session_state["historia_atual"] = historia["id"]
    at.session_state["pagina"] = "estudio"; at.run()
    assert not at.exception
    next(t for t in at.text_input if t.label == "Título").input("Título revisado").run()
    next(t for t in at.text_area if t.label == "Descrição").input("Descrição revisada").run()
    next(t for t in at.text_area if t.label == "Citação").input("Citação revisada").run()
    at.button(key="enviar_hist-001").click().run()
    assert not at.exception
    assert any(t.value == "Título revisado" for t in at.text_input)
    assert {"Descrição revisada", "Citação revisada"} <= {t.value for t in at.text_area}
    chave = "hist-001:testemunho_estruturado"
    assert at.session_state["status_curadoria"].get(chave, "rascunho") == "rascunho"
    assert at.session_state["validacao_factual"].get(chave, "pendente") == "pendente"
    assert at.session_state["autorizacao"].get(chave) != "registrada"
