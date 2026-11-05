"""Testes de navegação com lote vazio - Issue #27, Review PR #32."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app_lote_vazio():
    """App com estado vazio (sem histórias)."""
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app" / "main.py"))
    app.run()
    # Garante que não há histórias
    app.session_state.historias = []
    app.session_state.interacoes = []
    app.session_state.lote_id = "lote-vazio-teste"
    return app


def test_tela_historias_exibe_mensagem_com_lote_vazio(app_lote_vazio):
    """Tela Histórias deve exibir mensagem amigável quando não há histórias."""
    app = app_lote_vazio
    app.session_state.tela_atual = "historias"
    app.run()
    
    # Verifica se existe mensagem informativa
    assert any("Nenhuma história detectada" in str(el.value) for el in app.markdown if hasattr(el, 'value'))
    # Verifica se existe botão para ir para Importação
    assert any(btn.label == "→ Ir para Importação" for btn in app.button)


def test_tela_estudio_exibe_mensagem_com_lote_vazio(app_lote_vazio):
    """Tela Estúdio deve exibir mensagem amigável quando não há histórias."""
    app = app_lote_vazio
    app.session_state.tela_atual = "estudio"
    app.run()
    
    # Verifica se existe mensagem informativa
    assert any("Nenhuma história disponível" in str(el.value) for el in app.markdown if hasattr(el, 'value'))
    # Verifica se existe botão para ir para Importação
    assert any(btn.label == "→ Ir para Importação" for btn in app.button)


def test_tela_curadoria_exibe_mensagem_com_lote_vazio(app_lote_vazio):
    """Tela Curadoria deve exibir mensagem amigável quando não há histórias."""
    app = app_lote_vazio
    app.session_state.tela_atual = "curadoria"
    app.run()
    
    # Verifica se existe mensagem informativa
    assert any("Nenhuma história disponível" in str(el.value) for el in app.markdown if hasattr(el, 'value'))
    # Verifica se existe botão para ir para Importação
    assert any(btn.label == "→ Ir para Importação" for btn in app.button)


def test_navegacao_botao_importacao_funciona(app_lote_vazio):
    """Botão 'Ir para Importação' deve navegar para a tela correta."""
    app = app_lote_vazio
    app.session_state.tela_atual = "historias"
    app.run()
    
    # Encontra e clica no botão
    botao = next((btn for btn in app.button if btn.label == "→ Ir para Importação"), None)
    assert botao is not None
    botao.click().run()
    
    # Verifica se navegou para importacao
    assert app.session_state.tela_atual == "importacao"


def test_navegacao_entre_telas_sem_historias_nao_quebra():
    """Navegar entre telas vazias não deve causar erros."""
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app" / "main.py"))
    app.run()
    app.session_state.historias = []
    app.session_state.interacoes = []
    
    telas = ["historias", "estudio", "curadoria"]
    
    for tela in telas:
        app.session_state.tela_atual = tela
        app.run()
        # Verifica que não há exceções
        assert app.exception is None, f"Erro ao renderizar tela '{tela}' com lote vazio"
