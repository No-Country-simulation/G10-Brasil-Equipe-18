from services import data_service as svc
import pytest


def historia(origens):
    return {"interacoes_origem": origens, "mensagem_original": "A equipe resolveu meu problema."}


def test_reabertura_fonte_unica():
    h = historia([7])
    assert svc.conferencia_da_citacao_do_ativo("resolveu meu problema", h, [])[0] is True
    assert svc.conferencia_da_citacao_do_ativo("ignorou meu problema", h, [])[0] is False


@pytest.mark.parametrize("origens", [[], [7, 8], [True], [0], ["7"]])
def test_reabertura_origem_invalida(origens):
    assert not svc.interacoes_para_conferencia(historia(origens), [])


def test_reabertura_id_divergente():
    fontes = svc.interacoes_para_conferencia(historia([7]), [])
    assert svc.conferencia_da_citacao({"texto": "resolveu meu problema", "id_interacao": 8}, fontes)[0] is None


def test_interacoes_presentes_tem_precedencia():
    fontes = [{"_id_efetivo": 8, "texto": "Outra mensagem"}]
    assert svc.interacoes_para_conferencia(historia([7]), fontes) == fontes
    assert svc.conferencia_da_citacao_do_ativo("resolveu meu problema", historia([7]), fontes)[0] is None
