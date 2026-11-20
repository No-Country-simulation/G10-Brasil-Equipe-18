"""Decisões da Curadoria persistidas no pacote do lote (CATP-022).

O que estes testes garantem:
- a decisão é montada no formato do envelope do Card 05, com as três dimensões
  separadas e o parecer ligado ao ativo;
- gravar acrescenta o bloco e preserva o conteúdo que já estava no pacote;
- pacote antigo, sem o bloco, aceita decisão nova;
- falha de leitura ou de gravação não vira sucesso silencioso.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "app"))

from services import data_service as svc  # noqa: E402

HISTORIAS = [
    {
        "id": "hist-001",
        "ativos": [
            {"id": "testemunho_estruturado", "nome": "Testemunho estruturado"},
            {"id": "case_sucesso", "nome": "Case de sucesso"},
        ],
    }
]

PACOTE_ANTIGO = {
    "versao_schema": "1.0",
    "lote": "LOTE-1",
    "gerado_em": "2026-11-19T23:00:00+00:00",
    "origem_analise": "cohere",
    "historias": HISTORIAS,
    "evidencias": [{"id_interacao": 1, "texto": "trecho"}],
}


class ArmazenamentoFalso:
    """Bucket em memória, no mesmo contrato do oci_storage."""

    def __init__(self, objetos=None):
        self.objetos = {k: json.loads(json.dumps(v)) for k, v in (objetos or {}).items()}
        self.gravacoes = []

    def ler_objeto(self, caminho):
        if caminho not in self.objetos:
            raise FileNotFoundError(caminho)
        return json.loads(json.dumps(self.objetos[caminho]))

    def salvar_objeto(self, caminho, dados):
        self.objetos[caminho] = json.loads(json.dumps(dados))
        self.gravacoes.append(caminho)
        return {"salvo_em": "2026-11-19T23:30:00+00:00", "tamanho": 1234}


class ArmazenamentoQueFalhaAoGravar(ArmazenamentoFalso):
    def salvar_objeto(self, caminho, dados):
        raise RuntimeError("bucket indisponível")


class ArmazenamentoQueFalhaAoLer(ArmazenamentoFalso):
    def ler_objeto(self, caminho):
        raise RuntimeError("credencial expirada")


def test_monta_bloco_com_as_tres_dimensoes_separadas():
    estado = {
        "validacao_factual": {"hist-001:testemunho_estruturado": "validada"},
        "status_curadoria": {"hist-001:testemunho_estruturado": "ajustes"},
        "autorizacao": {"hist-001:testemunho_estruturado": "nao_registrada"},
        "observacoes": {"hist-001:testemunho_estruturado": "Encurtar o segundo parágrafo."},
        "motivos": {},
    }
    bloco = svc.montar_bloco_curadoria("LOTE-1", HISTORIAS, estado)

    assert len(bloco) == 2
    linha = bloco[0]
    assert linha["lote"] == "LOTE-1"
    assert linha["id_historia"] == "hist-001"
    assert linha["id_ativo"] == "testemunho_estruturado"
    assert linha["validacao_factual"] == "validada"
    assert linha["status_curadoria"] == "ajustes"
    assert linha["autorizacao"] == "nao_registrada"
    assert linha["parecer"] == "Encurtar o segundo parágrafo."

    # Ativo sem decisão sai com o padrão, e não herda a decisão do vizinho.
    sem_decisao = bloco[1]
    assert sem_decisao["id_ativo"] == "case_sucesso"
    assert sem_decisao["validacao_factual"] == "pendente"
    assert sem_decisao["status_curadoria"] == "rascunho"
    assert sem_decisao["autorizacao"] == "nao_registrada"
    assert sem_decisao["parecer"] == ""


def test_motivo_de_rejeicao_entra_como_parecer():
    estado = {
        "validacao_factual": {},
        "status_curadoria": {"hist-001:case_sucesso": "rejeitado"},
        "autorizacao": {},
        "observacoes": {},
        "motivos": {"hist-001:case_sucesso": "Fato não comprovado na origem."},
    }
    bloco = svc.montar_bloco_curadoria("LOTE-1", HISTORIAS, estado)
    assert bloco[1]["parecer"] == "Fato não comprovado na origem."


def test_grava_acrescentando_e_preserva_o_conteudo(monkeypatch):
    caminho = "lotes/LOTE-1/lote_LOTE-1.json"
    armazenamento = ArmazenamentoFalso({caminho: PACOTE_ANTIGO})
    monkeypatch.setattr(svc, "_storage", lambda: armazenamento)

    resultado = svc.salvar_decisoes(
        "LOTE-1",
        caminho,
        HISTORIAS,
        {
            "validacao_factual": {"hist-001:case_sucesso": "validada"},
            "status_curadoria": {"hist-001:case_sucesso": "aprovado"},
            "autorizacao": {"hist-001:case_sucesso": "registrada"},
            "observacoes": {},
            "motivos": {},
        },
    )

    assert resultado["ok"] is True
    gravado = armazenamento.objetos[caminho]
    assert gravado["historias"] == HISTORIAS
    assert gravado["evidencias"] == PACOTE_ANTIGO["evidencias"]
    assert len(gravado["curadoria"]) == 2
    assert gravado["curadoria"][1]["status_curadoria"] == "aprovado"


def test_pacote_antigo_aceita_decisao_nova(monkeypatch):
    """Lote gravado antes deste bloco não tem 'curadoria' — e mesmo assim grava."""
    caminho = "lotes/LOTE-1/lote_LOTE-1.json"
    assert "curadoria" not in PACOTE_ANTIGO
    armazenamento = ArmazenamentoFalso({caminho: PACOTE_ANTIGO})
    monkeypatch.setattr(svc, "_storage", lambda: armazenamento)

    resultado = svc.salvar_decisoes("LOTE-1", caminho, HISTORIAS, {
        "validacao_factual": {}, "status_curadoria": {"hist-001:testemunho_estruturado": "ajustes"},
        "autorizacao": {},
        "observacoes": {"hist-001:testemunho_estruturado": "Ajustar o título."}, "motivos": {},
    })

    assert resultado["ok"] is True
    assert svc.ler_decisoes(caminho)["hist-001:testemunho_estruturado"]["parecer"] == "Ajustar o título."


def test_le_o_que_foi_gravado(monkeypatch):
    caminho = "lotes/LOTE-1/lote_LOTE-1.json"
    armazenamento = ArmazenamentoFalso({caminho: PACOTE_ANTIGO})
    monkeypatch.setattr(svc, "_storage", lambda: armazenamento)

    svc.salvar_decisoes("LOTE-1", caminho, HISTORIAS, {
        "validacao_factual": {"hist-001:case_sucesso": "insuficiente"},
        "status_curadoria": {"hist-001:case_sucesso": "ajustes"},
        "autorizacao": {},
        "observacoes": {"hist-001:case_sucesso": "Faltam evidências do resultado."},
        "motivos": {},
    })
    decisoes = svc.ler_decisoes(caminho)

    assert decisoes["hist-001:case_sucesso"] == {
        "validacao_factual": "insuficiente",
        "status_curadoria": "ajustes",
        "autorizacao": "nao_registrada",
        "parecer": "Faltam evidências do resultado.",
    }


def test_aplica_edicoes_nos_campos():
    historias = [{
        "id": "hist-001",
        "ativos": [{
            "id": "testemunho_estruturado",
            "campos": {"titulo": "Gerado pela IA", "descricao": "Descrição gerada", "citacao": "citação gerada"},
        }],
    }]
    edicoes = {"c:hist-001:testemunho_estruturado:titulo": "Título revisado pelo curador"}

    resultado = svc.aplicar_edicoes(historias, edicoes)
    campos = resultado[0]["ativos"][0]["campos"]

    assert campos["titulo"] == "Título revisado pelo curador"
    assert campos["descricao"] == "Descrição gerada"
    assert campos["citacao"] == "citação gerada"
    # a lista original não é alterada
    assert historias[0]["ativos"][0]["campos"]["titulo"] == "Gerado pela IA"


def test_ativo_sem_edicao_mantem_o_gerado():
    historias = [{
        "id": "hist-001",
        "ativos": [{"id": "case_sucesso", "campos": {"texto": "Texto gerado"}}],
    }]
    resultado = svc.aplicar_edicoes(historias, {"c:outra:ativo:texto": "não é deste ativo"})
    assert resultado[0]["ativos"][0]["campos"]["texto"] == "Texto gerado"


def test_gravacao_guarda_o_texto_editado(monkeypatch):
    caminho = "lotes/LOTE-1/lote_LOTE-1.json"
    historias = [{
        "id": "hist-001",
        "ativos": [{"id": "case_sucesso", "nome": "Case de sucesso", "campos": {"texto": "Texto da IA"}}],
    }]
    armazenamento = ArmazenamentoFalso({caminho: dict(PACOTE_ANTIGO, historias=historias)})
    monkeypatch.setattr(svc, "_storage", lambda: armazenamento)

    resultado = svc.salvar_decisoes(
        "LOTE-1", caminho, historias,
        {"validacao_factual": {}, "status_curadoria": {}, "autorizacao": {},
         "observacoes": {}, "motivos": {}},
        edicoes={"c:hist-001:case_sucesso:texto": "Texto revisado pelo curador"},
    )

    assert resultado["ok"] is True
    gravado = armazenamento.objetos[caminho]
    assert gravado["historias"][0]["ativos"][0]["campos"]["texto"] == "Texto revisado pelo curador"
    assert gravado["evidencias"] == PACOTE_ANTIGO["evidencias"]


def test_pacote_sem_bloco_devolve_vazio():
    assert svc.decisoes_do_bloco(PACOTE_ANTIGO) == {}
    assert svc.decisoes_do_bloco(None) == {}
    assert svc.decisoes_do_bloco({"curadoria": "texto"}) == {}


def test_falha_de_gravacao_nao_vira_sucesso(monkeypatch):
    caminho = "lotes/LOTE-1/lote_LOTE-1.json"
    monkeypatch.setattr(svc, "_storage", lambda: ArmazenamentoQueFalhaAoGravar({caminho: PACOTE_ANTIGO}))

    resultado = svc.salvar_decisoes("LOTE-1", caminho, HISTORIAS, {})
    assert resultado["ok"] is False
    assert resultado["motivo"]


def test_falha_de_leitura_nao_grava_por_cima(monkeypatch):
    caminho = "lotes/LOTE-1/lote_LOTE-1.json"
    armazenamento = ArmazenamentoQueFalhaAoLer({caminho: PACOTE_ANTIGO})
    monkeypatch.setattr(svc, "_storage", lambda: armazenamento)

    resultado = svc.salvar_decisoes("LOTE-1", caminho, HISTORIAS, {})
    assert resultado["ok"] is False
    assert armazenamento.gravacoes == []


def test_pacote_inexistente_nao_cria_objeto(monkeypatch):
    armazenamento = ArmazenamentoFalso()
    monkeypatch.setattr(svc, "_storage", lambda: armazenamento)

    resultado = svc.salvar_decisoes("LOTE-1", "lotes/LOTE-1/lote_LOTE-1.json", HISTORIAS, {})
    assert resultado["ok"] is False
    assert armazenamento.gravacoes == []


# O parecer é escolhido pelo status vigente, nunca pela ordem dos campos.
# Antes, "Solicitar ajustes" seguido de "Rejeitar" gravava a observação antiga
# e perdia o motivo da rejeição.

OBSERVACAO_AJUSTE = "Encurtar o segundo parágrafo."
MOTIVO_REJEICAO = "Fato não comprovado na origem."


def _estado(chave, status, observacoes=None, motivos=None):
    return {
        "validacao_factual": {},
        "status_curadoria": {chave: status},
        "autorizacao": {},
        "observacoes": observacoes or {},
        "motivos": motivos or {},
    }


def test_rejeicao_nao_herda_observacao_de_ajuste():
    """Sequência reproduzida na revisão: ajustes e depois rejeição."""
    chave = "hist-001:case_sucesso"
    estado = _estado(
        chave,
        "rejeitado",
        observacoes={chave: OBSERVACAO_AJUSTE},
        motivos={chave: MOTIVO_REJEICAO},
    )
    bloco = svc.montar_bloco_curadoria("LOTE-1", HISTORIAS, estado)
    assert bloco[1]["parecer"] == MOTIVO_REJEICAO


def test_aprovacao_nao_herda_observacao_de_ajuste():
    chave = "hist-001:case_sucesso"
    estado = _estado(chave, "aprovado", observacoes={chave: OBSERVACAO_AJUSTE})
    bloco = svc.montar_bloco_curadoria("LOTE-1", HISTORIAS, estado)
    assert bloco[1]["parecer"] == ""


def test_ativo_em_rascunho_nao_herda_observacao_antiga():
    chave = "hist-001:case_sucesso"
    estado = _estado(chave, "rascunho", observacoes={chave: OBSERVACAO_AJUSTE})
    bloco = svc.montar_bloco_curadoria("LOTE-1", HISTORIAS, estado)
    assert bloco[1]["parecer"] == ""


def test_parecer_vazio_quando_o_status_nao_tem_texto():
    chave = "hist-001:case_sucesso"
    estado = _estado(chave, "rejeitado")
    bloco = svc.montar_bloco_curadoria("LOTE-1", HISTORIAS, estado)
    assert bloco[1]["parecer"] == ""


def test_campo_do_parecer_segue_o_status():
    assert svc.campo_do_parecer("ajustes") == "observacoes"
    assert svc.campo_do_parecer("rejeitado") == "motivos"
    assert svc.campo_do_parecer("aprovado") is None
    assert svc.campo_do_parecer("rascunho") is None


def test_parecer_volta_para_o_campo_do_status_gravado():
    """Ida e volta: o parecer do pacote aponta para o campo certo do estado."""
    chave = "hist-001:case_sucesso"
    estado = _estado(
        chave,
        "rejeitado",
        observacoes={chave: OBSERVACAO_AJUSTE},
        motivos={chave: MOTIVO_REJEICAO},
    )
    bloco = svc.montar_bloco_curadoria("LOTE-1", HISTORIAS, estado)
    decisao = svc.decisoes_do_bloco({"curadoria": bloco})[chave]

    assert decisao["status_curadoria"] == "rejeitado"
    assert decisao["parecer"] == MOTIVO_REJEICAO
    assert svc.campo_do_parecer(decisao["status_curadoria"]) == "motivos"
