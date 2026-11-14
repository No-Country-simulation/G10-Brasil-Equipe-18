"""Testes do fluxo de importação do Discord e do cursor OCI."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from services import data_service as svc
from telas import importacao


CAMINHO_CURSOR = "discord/cursor.json"


def test_carregar_cursor_discord_retorna_after_id():
    armazenamento = MagicMock()
    armazenamento.ler_objeto.return_value = {"after_id": "123456789"}

    with patch.object(svc, "_storage", return_value=armazenamento):
        assert svc.carregar_cursor_discord() == "123456789"

    armazenamento.ler_objeto.assert_called_once_with(CAMINHO_CURSOR)


def test_carregar_cursor_discord_sem_objeto_retorna_none():
    armazenamento = MagicMock()
    armazenamento.ler_objeto.return_value = None

    with patch.object(svc, "_storage", return_value=armazenamento):
        assert svc.carregar_cursor_discord() is None


def test_salvar_cursor_discord_grava_objeto_no_caminho_correto():
    armazenamento = MagicMock()

    with patch.object(svc, "_storage", return_value=armazenamento):
        svc.salvar_cursor_discord("987654321")

    armazenamento.salvar_objeto.assert_called_once_with(
        CAMINHO_CURSOR,
        {"after_id": "987654321"},
    )


def test_after_id_discord_extrai_marcador_entre_avisos():
    avisos = [
        "Aviso de pseudonimização",
        f"{svc.MARCADOR_ULTIMO_ID_DISCORD}123456789",
    ]

    assert svc.after_id_discord(avisos) == "123456789"
    assert svc.after_id_discord(["sem cursor"]) is None


def test_data_service_delega_busca_ao_carregador_discord():
    with patch(
        "src.ingestion.discord_load.buscar_mensagens_discord",
        return_value=([], [], []),
    ) as buscar:
        resultado = svc.buscar_mensagens_discord(
            canal_id="112233",
            after_id="123456789",
            limite=25,
        )

    assert resultado == ([], [], [])
    buscar.assert_called_once_with(
        limite=25,
        canal_id="112233",
        after_id="123456789",
    )


def test_data_service_usa_padrao_de_cinquenta_mensagens():
    with patch(
        "src.ingestion.discord_load.buscar_mensagens_discord",
        return_value=([], [], []),
    ) as buscar:
        svc.buscar_mensagens_discord()

    assert buscar.call_args.kwargs["limite"] == 50


def test_normalizar_interacoes_discord_usa_contrato_da_tela():
    itens = importacao._normalizar_interacoes_discord(
        [
            {
                "id": 1,
                "id_discord": "123456789012345678",
                "autor_id": "membro_123456",
                "canal": "112233",
                "tipo": "mensagem",
                "texto": "Consegui meu primeiro emprego!",
            }
        ]
    )

    assert itens == [
        {
            "id": 123456789012345678,
            "autor": "membro_123456",
            "canal": "112233",
            "tipo": "mensagem",
            "texto": "Consegui meu primeiro emprego!",
            "_id_efetivo": 123456789012345678,
        }
    ]


def test_tela_importacao_renderiza_aba_discord():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_string(
        """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "app"))
from services import data_service as svc
from state import init_state
from telas.importacao import render
svc.analisar = lambda interacoes: []
svc.listar_pacotes = lambda: []
init_state()
render()
"""
    )
    at.run()

    assert not at.exception
    assert at.button(key="buscar_discord").label == "Buscar mensagens do Discord"


def test_aba_discord_carrega_mensagens_e_guarda_cursor_pendente():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_string(
        f"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "app"))
import streamlit as st
from services import data_service as svc
from state import init_state
from telas import importacao
svc.analisar = lambda interacoes: []
svc.listar_pacotes = lambda: []
svc.carregar_cursor_discord = lambda: "111"
def buscar(canal_id=None, after_id=None, limite=50):
    st.session_state.discord_consulta = {{
        "canal_id": canal_id,
        "after_id": after_id,
        "limite": limite,
    }}
    return ([{{
        "id": 1,
        "id_discord": "222",
        "autor_id": "membro_123456",
        "canal": canal_id or "112233",
        "tipo": "mensagem",
        "texto": "Consegui um emprego!",
    }}], [], ["{svc.MARCADOR_ULTIMO_ID_DISCORD}222"])
svc.buscar_mensagens_discord = buscar
init_state()
st.session_state.historias = [{{"id": "hist-antiga"}}]
st.session_state.historia_atual = "hist-antiga"
importacao.render()
"""
    )
    at.run()
    assert at.slider(key="discord_limite").value == 50
    at.slider(key="discord_limite").set_value(80).run()
    at.button(key="buscar_discord").click().run()

    assert not at.exception
    assert at.session_state["discord_consulta"]["after_id"] == "111"
    assert at.session_state["discord_consulta"]["limite"] == 80
    assert at.session_state["interacoes"][0]["texto"] == "Consegui um emprego!"
    assert at.session_state["historias"] == []
    assert at.session_state["historia_atual"] is None
    assert at.session_state["avisos_discord"] == [
        f"{svc.MARCADOR_ULTIMO_ID_DISCORD}222"
    ]


def test_processamento_so_avanca_cursor_apos_salvar_pacotes():
    from telas import processamento

    avisos = [f"{svc.MARCADOR_ULTIMO_ID_DISCORD}987654321"]
    pacotes_nao_salvos = [{"status": "falhou", "persistencia": "real"}]
    pacotes_salvos = [{"status": "salvo", "persistencia": "real"}]

    with patch.object(svc, "salvar_cursor_discord") as salvar_cursor:
        assert not processamento._salvar_cursor_discord_se_confirmado(
            pacotes_nao_salvos, avisos
        )
        salvar_cursor.assert_not_called()

        assert processamento._salvar_cursor_discord_se_confirmado(
            pacotes_salvos, avisos
        )
        salvar_cursor.assert_called_once_with("987654321")
