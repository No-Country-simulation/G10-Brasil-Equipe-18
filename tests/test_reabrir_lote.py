"""Reabrir um lote salvo no OCI pelo Histórico, em uma sessão nova (CATP-022).

O que estes testes garantem:
- histórias, textos editados e as três dimensões da Curadoria voltam do pacote,
  com o parecer no campo certo (observação ou motivo);
- os contadores refletem o que foi recuperado;
- nada do lote anterior sobra (decisões, edições, interações, pacotes);
- a IA não é chamada ao reabrir;
- pacote antigo abre com os padrões; leitura que falha preserva a sessão;
- a decisão seguinte vai para o pacote do lote reaberto.
Sem OCI e sem LLM: o bucket é simulado.
"""
import copy
import json
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "app"))

from mocks.mock_data import HISTORIAS  # noqa: E402
from services import data_service as svc  # noqa: E402
from state import contagem_ativos_completa  # noqa: E402

_STREAMLIT = sys.modules["streamlit"]


@pytest.fixture(autouse=True)
def _streamlit_integro():
    # test_oci_storage apaga sys.modules["streamlit"] ao terminar; sem este
    # reparo, o AppTest e os imports tardios daqui falham com
    # "DeltaGeneratorSingleton instance already exists".
    sys.modules.setdefault("streamlit", _STREAMLIT)


APP_PATH = str(RAIZ / "app" / "main.py")
CAMINHO_A = "ativos/LOTE-A/pacote-distribuicao.json"
CAMINHO_B = "ativos/LOTE-B/pacote-distribuicao.json"
EVID_B = "ativos/LOTE-B/evidencias.json"
H1T, H1C = "hist-001:testemunho", "hist-001:case"
H2T, H2C = "hist-002:testemunho", "hist-002:case"


class Sessao(dict):
    """Sessão mínima, com acesso por atributo como o st.session_state."""

    def __getattr__(self, nome):
        try:
            return self[nome]
        except KeyError as erro:
            raise AttributeError(nome) from erro

    def __setattr__(self, nome, valor):
        self[nome] = valor


class Bucket:
    """Bucket em memória, no contrato do oci_storage."""

    def __init__(self, objetos):
        self.objetos = {k: json.loads(json.dumps(v)) for k, v in objetos.items()}
        self.gravacoes = []

    def ler_objeto(self, caminho):
        if caminho not in self.objetos:
            raise FileNotFoundError(caminho)
        return json.loads(json.dumps(self.objetos[caminho]))

    def salvar_objeto(self, caminho, dados):
        self.objetos[caminho] = json.loads(json.dumps(dados))
        self.gravacoes.append(caminho)
        return {"salvo_em": "2026-11-20T10:00:00+00:00", "tamanho": 10}

    def listar_pacotes(self):
        return [
            {"caminho": c, "lote": c.split("/")[1], "salvo_em": "2026-11-20T09:00:00", "tamanho": "1,0 KB"}
            for c in self.objetos
        ]


class BucketQueFalhaAoLer(Bucket):
    def ler_objeto(self, caminho):
        raise RuntimeError("credencial expirada")


def _linha(lote, chave, validacao="pendente", status="rascunho", aut="nao_registrada", parecer=""):
    hid, aid = chave.split(":")
    return {"lote": lote, "id_historia": hid, "id_ativo": aid, "validacao_factual": validacao,
            "status_curadoria": status, "autorizacao": aut, "parecer": parecer}


def _pacote(lote, historias=None, curadoria=None, versao="1.1", natureza="ficticios"):
    pacote = {
        "versao_schema": versao,
        "lote": lote,
        "gerado_em": "2026-11-20T08:00:00+00:00",
        "origem_analise": "gemini",
        "historias": copy.deepcopy(historias if historias is not None else HISTORIAS[:2]),
        "evidencias": [],
    }
    if natureza is not None:
        pacote["natureza_dados"] = natureza
    if curadoria is not None:
        pacote["curadoria"] = curadoria
    return pacote


def _curadoria_completa(lote):
    return [
        _linha(lote, H1T, "validada", "ajustes", parecer="Encurtar o segundo parágrafo."),
        _linha(lote, H1C, "insuficiente", "rejeitado", parecer="Fato não comprovado na origem."),
        _linha(lote, H2T, "validada", "aprovado", "registrada"),
        _linha(lote, H2C, "pendente", "rascunho"),
    ]


@pytest.fixture
def bucket(monkeypatch):
    def _montar(objetos):
        b = Bucket(objetos)
        monkeypatch.setattr(svc, "_storage", lambda: b)
        # Outros testes trocam svc.listar_pacotes no import e não restauram;
        # aqui a listagem vem sempre do bucket simulado.
        monkeypatch.setattr(svc, "listar_pacotes", lambda: [
            {"caminho": i["caminho"], "lote": i["lote"], "data": "20/11/2026 06:00", "tamanho": i["tamanho"],
             "status": "salvo", "persistencia": "real", "salvo_em": i["salvo_em"]}
            for i in b.listar_pacotes()
        ])
        return b

    return _montar


@pytest.fixture
def sem_ia(monkeypatch):
    def _falha(*_a, **_k):
        raise AssertionError("A IA não pode ser chamada ao reabrir um lote")

    monkeypatch.setattr(svc, "analisar", _falha)
    monkeypatch.setattr(svc, "regenerar", _falha)


def _aplicar(ss, lote):
    # Import tardio: test_oci_storage mexe em sys.modules['streamlit'] e quebraria os AppTest.
    from telas.historico import aplicar_lote_recuperado

    aplicar_lote_recuperado(ss, lote)


def _reabrir(caminho):
    lote = svc.recuperar_lote(caminho)
    assert lote["ok"], lote
    ss = Sessao(dados={})
    _aplicar(ss, lote)
    return ss


# ---------- serviço e aplicação na sessão ----------

def test_pareceres_voltam_no_campo_certo(bucket, sem_ia):
    bucket({CAMINHO_B: _pacote("LOTE-B", curadoria=_curadoria_completa("LOTE-B"))})
    ss = _reabrir(CAMINHO_B)

    assert ss.lote_id == "LOTE-B"
    assert ss.status_curadoria == {H1T: "ajustes", H1C: "rejeitado", H2T: "aprovado", H2C: "rascunho"}
    assert ss.validacao_factual[H1T] == "validada"
    assert ss.validacao_factual[H1C] == "insuficiente"
    assert ss.autorizacao[H2T] == "registrada"
    assert ss.autorizacao[H1T] == "nao_registrada"
    assert ss.observacoes == {H1T: "Encurtar o segundo parágrafo."}
    assert ss.motivos == {H1C: "Fato não comprovado na origem."}
    assert H2C not in ss.observacoes and H2C not in ss.motivos  # rascunho com parecer vazio


def test_campos_editados_voltam_pelos_campos_estruturados(bucket, sem_ia):
    historias = copy.deepcopy(HISTORIAS[:1])
    teste, case = historias[0]["ativos"][0], historias[0]["ativos"][1]
    teste["campos"].update({"titulo": "Título editado", "descricao": "Descrição editada", "citacao": "Citação editada"})
    case["campos"]["texto"] = "Texto do case editado\n\ncom dois parágrafos"
    bucket({CAMINHO_B: _pacote("LOTE-B", historias=historias)})
    ss = _reabrir(CAMINHO_B)

    campos_t = ss.historias[0]["ativos"][0]["campos"]
    assert (campos_t["titulo"], campos_t["descricao"], campos_t["citacao"]) == (
        "Título editado", "Descrição editada", "Citação editada")
    assert ss.historias[0]["ativos"][1]["campos"]["texto"] == "Texto do case editado\n\ncom dois parágrafos"


def test_contadores_refletem_estados_recuperados(bucket, sem_ia):
    bucket({CAMINHO_B: _pacote("LOTE-B", curadoria=_curadoria_completa("LOTE-B"))})
    ss = _reabrir(CAMINHO_B)
    contagem = contagem_ativos_completa(ss.historias, ss.status_curadoria, ss.status_ativos)
    assert contagem == {"total": 4, "rascunho": 1, "ajustes": 1, "aprovado": 1, "rejeitado": 1}


def test_sem_mistura_com_o_lote_anterior(bucket, sem_ia):
    bucket({CAMINHO_B: _pacote("LOTE-B", historias=HISTORIAS[:1],
                               curadoria=[_linha("LOTE-B", H1T, status="aprovado")])})
    ss = Sessao(dados={})
    from state import resetar_lote
    resetar_lote(ss)
    ss.interacoes = [{"autor": "A", "canal": "#a", "texto": "x"}]
    ss.ultimo_upload = ("a.json", 10)
    ss.lote_id = "LOTE-A"
    ss.historias = copy.deepcopy(HISTORIAS)
    ss.status_curadoria = {H2C: "rejeitado", H1C: "ajustes"}
    ss.observacoes = {H1C: "obs do A"}
    ss.motivos = {H2C: "motivo do A"}
    ss.regen = {H1T: 2}
    ss.historia_atual = "hist-002"
    ss.pacotes_oci = [{"caminho": CAMINHO_A}]
    ss.dados.update({"c:hist-001:case:texto": "edição do A", "f:cat": "Carreira", "f:rel": 10,
                     "f:canal": "#a", "aba:hist-001": "Case de sucesso", "natureza_dados": "reais"})
    ss["w::c:hist-001:case:texto"] = "edição do A"
    ss["validacao_hist-001:case"] = "Validada"
    ss["aut_hist-001:case"] = True

    _aplicar(ss, svc.recuperar_lote(CAMINHO_B))

    assert ss.lote_id == "LOTE-B"
    assert [h["id"] for h in ss.historias] == ["hist-001"]
    assert ss.interacoes == [] and ss.ultimo_upload is None
    assert ss.status_curadoria == {H1T: "aprovado"}
    assert ss.observacoes == {} and ss.motivos == {} and ss.regen == {}
    assert ss.historia_atual is None
    assert [p["caminho"] for p in ss.pacotes_oci] == [CAMINHO_B]
    assert not [k for k in ss.dados if k.startswith(("c:", "f:", "aba"))]
    assert not [k for k in ss if k.startswith(("w::c:", "validacao_", "aut_")) and ":" in k]
    assert "validacao_factual" in ss  # o estado da Curadoria continua existindo, só limpo
    assert ss.dados["natureza_dados"] == "ficticios"


def test_pacote_1_0_abre_com_padroes_e_aviso(bucket, sem_ia):
    bucket({CAMINHO_B: _pacote("LOTE-B", versao="1.0", natureza=None)})
    lote = svc.recuperar_lote(CAMINHO_B)
    assert lote["ok"] and lote["natureza_dados"] == "nao_informado"
    assert lote["decisoes"] == {}
    assert any("não tem decisões" in a for a in lote["avisos"])
    ss = Sessao(dados={})
    _aplicar(ss, lote)
    assert ss.dados["natureza_dados"] == "nao_informado"
    assert ss.status_curadoria == {} and ss.autorizacao == {}
    contagem = contagem_ativos_completa(ss.historias, ss.status_curadoria, ss.status_ativos)
    assert contagem["rascunho"] == contagem["total"]


def test_leitura_que_falha_devolve_motivo_e_nao_dado(monkeypatch):
    b = BucketQueFalhaAoLer({CAMINHO_B: _pacote("LOTE-B")})
    monkeypatch.setattr(svc, "_storage", lambda: b)
    monkeypatch.setattr(svc, "listar_pacotes", lambda: [])
    lote = svc.recuperar_lote(CAMINHO_B)
    assert lote["ok"] is False and "credencial expirada" in lote["motivo"]
    assert "historias" not in lote


def test_nao_aceita_pacote_de_evidencias(bucket):
    bucket({EVID_B: {"versao_schema": "1.0", "lote": "LOTE-B", "evidencias": []}})
    assert svc.recuperar_lote(EVID_B)["ok"] is False


def test_pacote_sem_lista_de_historias_falha(bucket):
    bucket({CAMINHO_B: {"versao_schema": "1.1", "lote": "LOTE-B"}})
    assert svc.recuperar_lote(CAMINHO_B)["ok"] is False


def test_pacotes_do_lote_reaberto_incluem_so_o_do_proprio_lote(bucket):
    bucket({CAMINHO_A: _pacote("LOTE-A"), CAMINHO_B: _pacote("LOTE-B"),
            EVID_B: {"versao_schema": "1.0", "lote": "LOTE-B", "evidencias": []}})
    lote = svc.recuperar_lote(CAMINHO_B)
    assert sorted(p["caminho"] for p in lote["pacotes"]) == sorted([CAMINHO_B, EVID_B])


# ---------- tela (AppTest) ----------

def _abrir_historico(historias=None, **sessao):
    at = AppTest.from_file(APP_PATH, default_timeout=15)
    at.run()
    assert not at.exception, at.exception
    for chave, valor in sessao.items():
        at.session_state[chave] = valor
    if historias is not None:
        at.session_state["historias"] = historias
    at.session_state["pagina"] = "historico"
    at.run()
    assert not at.exception, at.exception
    return at


def _clicar_reabrir(at, caminho):
    at.button(key=f"reabrir_{caminho}").click().run()
    assert not at.exception, at.exception


def _textos(at):
    return " ".join(m.value for m in at.markdown)


def test_reabrir_na_tela_leva_a_curadoria_sem_excecao_e_sem_ia(bucket, sem_ia):
    bucket({CAMINHO_B: _pacote("LOTE-B", curadoria=_curadoria_completa("LOTE-B"))})
    at = _abrir_historico()
    _clicar_reabrir(at, CAMINHO_B)

    assert at.session_state["pagina"] == "curadoria"
    assert at.session_state["lote_id"] == "LOTE-B"
    assert at.session_state["status_curadoria"][H1T] == "ajustes"
    # parecer visível no mesmo ativo (hist-001, aba Testemunho)
    assert any("Encurtar o segundo parágrafo." in i.value for i in at.info)


def test_kpis_mostram_traco_quando_as_interacoes_nao_voltam(bucket, sem_ia):
    bucket({CAMINHO_B: _pacote("LOTE-B")})
    at = _abrir_historico(historias=[], interacoes=[{"autor": "A", "canal": "#a", "texto": "x", "_id_efetivo": 1}])
    # sessão com o lote A e interações: confirma antes de substituir
    at.session_state["historias"] = copy.deepcopy(HISTORIAS)
    at.run()
    at.button(key=f"reabrir_{CAMINHO_B}").click().run()
    at.button(key="reabrir_confirmar").click().run()
    assert not at.exception, at.exception
    assert at.session_state["interacoes"] == []

    for pagina in ("dashboard", "historias"):
        at.session_state["pagina"] = pagina
        at.session_state["f:rel"] = 0
        at.run()
        assert not at.exception, at.exception
        html = _textos(at)
        assert "—" in html and "Não guardadas no pacote" in html, pagina


def test_confirmacao_aparece_com_lote_carregado_e_cancelar_preserva(bucket, sem_ia):
    bucket({CAMINHO_B: _pacote("LOTE-B")})
    at = _abrir_historico(historias=copy.deepcopy(HISTORIAS), lote_id="LOTE-A")
    at.button(key=f"reabrir_{CAMINHO_B}").click().run()
    assert not at.exception, at.exception
    assert at.session_state["lote_id"] == "LOTE-A"  # nada mudou antes de confirmar
    assert at.button(key="reabrir_confirmar") is not None


def test_leitura_que_falha_na_tela_preserva_a_sessao(monkeypatch, sem_ia):
    b = Bucket({CAMINHO_B: _pacote("LOTE-B")})
    monkeypatch.setattr(svc, "_storage", lambda: b)
    monkeypatch.setattr(svc, "listar_pacotes", lambda: [
        {"caminho": CAMINHO_B, "lote": "LOTE-B", "data": "20/11/2026 06:00", "tamanho": "1,0 KB",
         "status": "salvo", "persistencia": "real", "salvo_em": "2026-11-20T09:00:00"}])
    at = _abrir_historico()
    # o bucket passa a falhar só na leitura do pacote
    monkeypatch.setattr(b, "ler_objeto", lambda caminho: (_ for _ in ()).throw(RuntimeError("bucket fora do ar")))
    at.session_state["lote_id"] = "LOTE-A"
    _clicar_reabrir(at, CAMINHO_B)

    assert at.session_state["pagina"] == "historico"
    assert at.session_state["lote_id"] == "LOTE-A"
    assert "bucket fora do ar" in at.session_state["erro_reabertura"]
    assert "Não foi possível reabrir o lote" in _textos(at)


def test_decisao_nova_grava_no_pacote_do_lote_reaberto(bucket, sem_ia):
    b = bucket({
        CAMINHO_A: _pacote("LOTE-A"),
        CAMINHO_B: _pacote("LOTE-B", curadoria=[_linha("LOTE-B", H1T, status="ajustes", parecer="ajustar")]),
    })
    at = _abrir_historico()
    _clicar_reabrir(at, CAMINHO_B)

    caixa = at.selectbox(key=f"validacao_{H1T}")
    caixa.set_value("Validada").run()
    assert not at.exception, at.exception

    assert b.gravacoes == [CAMINHO_B]
    gravado = b.objetos[CAMINHO_B]["curadoria"]
    linha = next(x for x in gravado if x["id_ativo"] == "testemunho" and x["id_historia"] == "hist-001")
    assert linha["validacao_factual"] == "validada" and linha["parecer"] == "ajustar"
    assert "curadoria" not in b.objetos[CAMINHO_A]


def test_catp_022_observacao_continua_ligada_ao_mesmo_ativo_em_sessao_nova(bucket, sem_ia):
    b = bucket({CAMINHO_B: _pacote("LOTE-B")})
    # Sessão 1: o pedido de ajuste é gravado como a Curadoria faz (salvar_decisoes).
    resultado = svc.salvar_decisoes(
        "LOTE-B", CAMINHO_B, HISTORIAS[:2],
        {"status_curadoria": {H2C: "ajustes"}, "observacoes": {H2C: "Citar o prazo do projeto."},
         "validacao_factual": {}, "autorizacao": {}, "motivos": {}},
    )
    assert resultado["ok"]

    # Sessão 2: aplicativo novo, lote aberto pelo Histórico.
    at = _abrir_historico()
    assert at.session_state["historias"] == []
    _clicar_reabrir(at, CAMINHO_B)
    assert at.session_state["observacoes"] == {H2C: "Citar o prazo do projeto."}
    assert at.session_state["status_curadoria"][H2C] == "ajustes"
    assert at.session_state["status_curadoria"][H1C] == "rascunho"

    # A observação aparece no ativo certo (hist-002, aba Case de sucesso).
    at.session_state["historia_atual"] = "hist-002"
    at.run()
    at.radio(key="w::aba:hist-002").set_value("Case de sucesso").run()
    assert not at.exception, at.exception
    assert any("Citar o prazo do projeto." in i.value for i in at.info)


def _dialogo_aberto(at):
    return any(b.key == "reabrir_confirmar" for b in at.button)


def test_cancelar_fecha_o_dialogo_e_preserva_a_sessao(bucket, sem_ia):
    bucket({CAMINHO_B: _pacote("LOTE-B")})
    at = _abrir_historico(historias=copy.deepcopy(HISTORIAS), lote_id="LOTE-A")
    at.button(key=f"reabrir_{CAMINHO_B}").click().run()
    assert _dialogo_aberto(at)

    at.button(key="reabrir_cancelar").click().run()
    assert not at.exception, at.exception
    assert not _dialogo_aberto(at)
    assert at.session_state["lote_id"] == "LOTE-A"
    assert at.session_state["pagina"] == "historico"
    at.run()  # uma execução qualquer depois do cancelamento não pode reabrir o diálogo
    assert not _dialogo_aberto(at)


def test_confirmar_fecha_o_dialogo_e_troca_o_lote(bucket, sem_ia):
    bucket({CAMINHO_B: _pacote("LOTE-B")})
    at = _abrir_historico(historias=copy.deepcopy(HISTORIAS), lote_id="LOTE-A")
    at.button(key=f"reabrir_{CAMINHO_B}").click().run()
    at.button(key="reabrir_confirmar").click().run()
    assert not at.exception, at.exception
    assert not _dialogo_aberto(at)
    assert at.session_state["lote_id"] == "LOTE-B"
    assert at.session_state["pagina"] == "curadoria"
