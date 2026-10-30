"""Teste de regressão completo com AppTest (CATP-016).

Percorre todas as telas do front sem exceção:
- Importação
- Histórias
- Estúdio
- Curadoria
- Histórico

Sem rede, sem chave de API, delay zero.
O isolamento de credenciais é feito pela fixture `ocultar_secrets_reais`
em conftest.py, que renomeia temporariamente o .streamlit/secrets.toml
antes do teste e o restaura ao término — sem chamadas externas ao Gemini/OCI.
"""
import os
import sys
from pathlib import Path

# Adiciona app/ ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

# Configura ambiente para teste (sem rede, delay zero)
os.environ["COMMUNITYLAB_DELAY"] = "0"
os.environ.pop("GEMINI_API_KEY", None)

from streamlit.testing.v1 import AppTest


def test_regressao_front_completo():
    """Teste de regressão: percorre todas as telas sem exceção."""

    # Usa caminho absoluto: AppTest.from_file resolve relativo ao arquivo chamador
    # (tests/), não à raiz do projeto — sem o Path explícito buscaria tests/app/main.py
    app_path = str(Path(__file__).parent.parent / "app" / "main.py")

    # O conftest.py (fixture ocultar_secrets_reais) já oculta o secrets.toml
    # antes desta linha ser atingida — sem necessidade de secrets={} aqui.
    at = AppTest.from_file(app_path, default_timeout=10)
    at.run()

    # Verifica que o app iniciou sem erro
    assert not at.exception, f"Exceção ao iniciar: {at.exception}"

    # 2. HISTÓRIAS
    at.sidebar.button(key="nav_historias").click().run()
    assert not at.exception, f"Exceção na tela Histórias: {at.exception}"

    # 3. ESTÚDIO
    at.sidebar.button(key="nav_estudio").click().run()
    assert not at.exception, f"Exceção na tela Estúdio: {at.exception}"

    # 4. CURADORIA
    at.sidebar.button(key="nav_curadoria").click().run()
    assert not at.exception, f"Exceção na tela Curadoria: {at.exception}"

    # 5. HISTÓRICO
    at.sidebar.button(key="nav_historico").click().run()
    assert not at.exception, f"Exceção na tela Histórico: {at.exception}"

    # 1. IMPORTAÇÃO (voltar para tela inicial)
    at.sidebar.button(key="nav_importacao").click().run()
    assert not at.exception, f"Exceção na tela Importação: {at.exception}"

    print("✅ Regressão completa: todas as 5 telas navegaram sem exceção")


if __name__ == "__main__":
    test_regressao_front_completo()
