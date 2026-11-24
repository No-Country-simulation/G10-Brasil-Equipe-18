"""Regressões do Card 23: isolamento, proveniência e natureza declarada."""
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
import state
from services import data_service as svc
from telas import importacao


class Sessao(dict):
    def __getattr__(self, nome):
        try:
            return self[nome]
        except KeyError as erro:
            raise AttributeError(nome) from erro

    def __setattr__(self, nome, valor):
        self[nome] = valor


def test_card23_limpeza_controles_do_lote():
    dados = {'c:h:a:texto': 'antigo', 'e:h:a': 1, 'f:cat': 'x',
             'f:rel': 'x', 'f:canal': 'x', 'aba_estudio': 'x',
             'discord_canal_id': '123'}
    ss = Sessao(dados=dados, mostrar_copia=True)
    chaves = ['w::c:h:a:texto', 'w::e:h:a', 'w::aba_estudio',
              'validacao_h:a', 'aut_h:a']
    ss.update(dict.fromkeys(chaves, 'antigo'))
    ss['discord_limite'] = 50
    state.limpar_estado_temporario_lote(ss)
    assert ss.dados == {'discord_canal_id': '123'}
    assert all(chave not in ss for chave in chaves)
    assert ss.discord_limite == 50
    assert ss.mostrar_copia is False


def test_card23_reset_sem_argumento(monkeypatch):
    ss = Sessao(dados={'c:h:a:texto': 'antigo'}, mostrar_copia=True)
    monkeypatch.setattr(state, 'st', SimpleNamespace(session_state=ss))
    state.resetar_lote()
    assert 'c:h:a:texto' not in ss.dados
    assert ss.mostrar_copia is False
    assert ss.lote_id


@pytest.mark.parametrize('origem,esperado', [('cohere','cohere'), ('gemini','gemini'), (None,'nao_informado')])
def test_card23_provedor_persistido_independe_global(monkeypatch, origem, esperado):
    gravados = []
    def salvar(caminho, dados):
        gravados.append(dados.copy())
        return {'salvo_em': '2026-11-24T12:00:00Z', 'tamanho': 100}
    storage = SimpleNamespace(caminho_do_lote=lambda lote, caminho: caminho,
                              salvar_objeto=salvar)
    monkeypatch.setattr(svc, '_storage', lambda: storage)
    pacotes = [{'caminho': 'pacote-distribuicao.json'}]
    for global_atual in ('gemini', 'cohere'):
        monkeypatch.setattr(svc, 'ORIGEM_ANALISE', global_atual)
        retorno = svc.salvar_no_oci(pacotes, 'LOTE-TESTE', [], origem_analise=origem)
        assert retorno[0]['status'] == 'salvo'
    assert [p['origem_analise'] for p in gravados] == [esperado, esperado]


@pytest.mark.parametrize('natureza,esperado', [
    ('ficticios','Dados fictícios (declarado)'),
    ('reais','Dados reais (declarado)'),
    ('nao_informado','Natureza não informada'),
    ('invalido','Natureza não informada'),
])
def test_card23_rotulo_natureza(monkeypatch, natureza, esperado):
    monkeypatch.setattr(importacao, 'valor', lambda *args: natureza)
    assert importacao._rotulo_natureza_declarada() == esperado
