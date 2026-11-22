"""Conferência de citação nas telas: a função do data_service, sem Streamlit.

Cobre a resolução da interação de origem pelo id_interacao e o resultado por
citação. A regra de comparação em si é testada em test_conferencia_citacao.py.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from mocks import mock_data as m
from services import data_service as svc

ORIGINAL_ANONIMIZADO = "Quem me ajudou foi Ana Souza na mentoria de carreira."


def _lote():
    """Lote demonstrativo com _id_efetivo, como a importação entrega às telas."""
    return svc._normalizar(copy.deepcopy(m.INTERACOES))


def _lote_com_anonimizado():
    lote = _lote()
    lote.append({"autor": "Fulana", "canal": "#carreira", "tipo": "mensagem",
                 "texto": ORIGINAL_ANONIMIZADO, "_id_efetivo": 7})
    return lote


def test_citacao_literal_valida_confere():
    confere, motivo, id_int = svc.conferencia_da_citacao(
        {"texto": "Fizemos tudo em equipe!", "id_interacao": 2}, _lote())
    assert (confere, motivo, id_int) == (True, svc.MOTIVO_LITERAL, 2)


def test_citacao_alterada_nao_confere_e_traz_motivo():
    confere, motivo, _ = svc.conferencia_da_citacao(
        {"texto": "Fizemos tudo sozinhos!", "id_interacao": 2}, _lote())
    assert confere is False
    assert motivo


def test_citacao_com_marcador_valido_e_compativel_com_anonimizacao():
    confere, motivo, id_int = svc.conferencia_da_citacao(
        {"texto": "Quem me ajudou foi [NOME] na mentoria de carreira.", "id_interacao": 7},
        _lote_com_anonimizado())
    assert (confere, id_int) == (True, 7)
    assert motivo == svc.MOTIVO_ANONIMIZADO
    assert motivo != svc.MOTIVO_LITERAL  # os dois True nunca se confundem


def test_mesma_historia_com_resultados_diferentes_por_citacao():
    lote = _lote_com_anonimizado()
    historia = {"citacoes": [
        {"texto": "Fizemos tudo em equipe!", "id_interacao": 2},
        {"texto": "Quem me ajudou foi [NOME] na mentoria de carreira.", "id_interacao": 7},
        {"texto": "Fizemos tudo sozinhos!", "id_interacao": 2},
    ]}
    resultados = [svc.conferencia_da_citacao(c, lote)[:2] for c in historia["citacoes"]]
    assert resultados[0] == (True, svc.MOTIVO_LITERAL)
    assert resultados[1] == (True, svc.MOTIVO_ANONIMIZADO)
    assert resultados[2][0] is False
    assert len({r[1] for r in resultados}) == 3


def test_vinculo_de_origem_confere_na_interacao_certa_e_nao_na_outra():
    lote = _lote()
    trecho = "Fizemos tudo em equipe!"  # texto da interação 2
    assert svc.conferencia_da_citacao({"texto": trecho, "id_interacao": 2}, lote)[0] is True
    for outra in (1, 3, 4):
        assert svc.conferencia_da_citacao({"texto": trecho, "id_interacao": outra}, lote)[0] is False


def test_interacao_inexistente_e_neutra_nunca_verdadeira():
    confere, motivo, id_int = svc.conferencia_da_citacao(
        {"texto": "Fizemos tudo em equipe!", "id_interacao": 999}, _lote())
    assert confere is None
    assert motivo == svc.MOTIVO_INDISPONIVEL
    assert id_int == 999


def test_sem_id_valido_diz_id_nao_informado_sem_conferir():
    for id_ruim in (None, 0, -1, "2", True, 2.0):
        confere, motivo, id_int = svc.conferencia_da_citacao(
            {"texto": "Fizemos tudo em equipe!", "id_interacao": id_ruim}, _lote())
        assert (confere, motivo, id_int) == (None, svc.MOTIVO_SEM_ID, None), id_ruim
    assert svc.conferencia_da_citacao({"texto": "Fizemos tudo em equipe!"}, _lote())[0] is None


def test_revalidacao_a_cada_edicao_muda_o_resultado():
    lote = _lote()
    historia = {"interacoes_origem": [2]}
    texto = "Fizemos tudo em equipe!"
    assert svc.conferencia_da_citacao_do_ativo(texto, historia, lote)[0] is True
    editado = "Fizemos tudo em equipe, sem ajuda!"
    assert svc.conferencia_da_citacao_do_ativo(editado, historia, lote)[0] is False
    assert svc.conferencia_da_citacao_do_ativo(texto, historia, lote)[0] is True


def test_caso_real_do_lote_demonstrativo_lucas_interacao_2():
    lote = _lote()
    lucas = next(i for i in lote if i["_id_efetivo"] == 2)
    assert lucas["autor"] == "Lucas Almeida"
    confere, motivo, _ = svc.conferencia_da_citacao(
        {"texto": "Fizemos tudo em equipe!", "id_interacao": 2}, lote)
    assert (confere, motivo) == (True, svc.MOTIVO_LITERAL)


def test_citacao_do_ativo_usa_interacao_de_origem_da_historia():
    lote = _lote()
    confere, _, id_int = svc.conferencia_da_citacao_do_ativo(
        "Fizemos tudo em equipe!", {"interacoes_origem": [2]}, lote)
    assert (confere, id_int) == (True, 2)


def test_ativo_com_varias_origens_fica_indisponivel_sem_conferir():
    confere, motivo, id_int = svc.conferencia_da_citacao_do_ativo(
        "Fizemos tudo em equipe!", {"interacoes_origem": [1, 2]}, _lote())
    assert (confere, motivo, id_int) == (None, svc.MOTIVO_VARIAS_ORIGENS, None)


def test_ativo_sem_origem_diz_id_nao_informado():
    for historia in ({"interacoes_origem": []}, {}):
        confere, motivo, _ = svc.conferencia_da_citacao_do_ativo(
            "Fizemos tudo em equipe!", historia, _lote())
        assert (confere, motivo) == (None, svc.MOTIVO_SEM_ID)


def test_mocks_do_estudio_conferem_na_citacao_e_na_variacao():
    """Todas as citações editáveis dos mocks, inclusive as regeneradas, são literais."""
    lote = _lote()
    for h in m.HISTORIAS:
        for ativo in h["ativos"]:
            if ativo["tipo"] != "testemunho":
                continue
            for campos in [ativo["campos"], *ativo.get("variacoes", [])]:
                confere, motivo, _ = svc.conferencia_da_citacao_do_ativo(campos["citacao"], h, lote)
                assert (confere, motivo) == (True, svc.MOTIVO_LITERAL), (h["id"], campos["citacao"])


# ---- Rótulos e cores (styles.conferencia_html) ----

def test_os_dois_confere_tem_rotulo_e_cor_diferentes():
    from styles import conferencia_html
    literal = conferencia_html(True, svc.MOTIVO_LITERAL)
    anonimizado = conferencia_html(True, svc.MOTIVO_ANONIMIZADO)
    assert "chip-green" in literal and "chip-blue" not in literal
    assert "chip-blue" in anonimizado and "chip-green" not in anonimizado


def test_rotulo_azul_avisa_que_a_parte_mascarada_nao_e_conferida():
    from styles import conferencia_html
    html = conferencia_html(True, svc.MOTIVO_ANONIMIZADO)
    assert "a parte mascarada não é conferida" in html


def test_nao_confere_mostra_o_motivo_e_nunca_fica_verde():
    from styles import conferencia_html
    html = conferencia_html(False, "trecho alterado ou não encontrado na mensagem original")
    assert "chip-yellow" in html and "chip-green" not in html and "chip-blue" not in html
    assert "trecho alterado ou não encontrado na mensagem original" in html


def test_resultado_neutro_nunca_fica_verde_nem_azul():
    from styles import conferencia_html
    for motivo in (svc.MOTIVO_SEM_ID, svc.MOTIVO_INDISPONIVEL, svc.MOTIVO_VARIAS_ORIGENS):
        html = conferencia_html(None, motivo)
        assert "chip-green" not in html and "chip-blue" not in html
        assert motivo in html


def test_evidencias_mostram_resultado_por_citacao_e_a_interacao_de_origem():
    from styles import evidencias_citadas
    historia = {"citacoes": [
        {"texto": "Fizemos tudo em equipe!", "id_interacao": 2},
        {"texto": "Quem me ajudou foi [NOME] na mentoria de carreira.", "id_interacao": 7},
        {"texto": "Fizemos tudo sozinhos!", "id_interacao": 2},
    ]}
    html = evidencias_citadas(historia, _lote_com_anonimizado(), modo_demonstracao=False)
    assert "chip-green" in html and "chip-blue" in html and "chip-yellow" in html
    assert "interação nº <b>2</b>" in html and "interação nº <b>7</b>" in html
