"""Testes de preservação, unicidade e invalidez de IDs de interação (CATP-007).

Cenários testados (sem Streamlit, sem rede):
1. IDs explícitos preservados
2. Filtro por canal mantém IDs originais
3. IDs duplicados rejeitam o lote
4. Lote misto (com e sem id) aceito
5. ID inválido (0, negativo, texto, booleano) vira posição + aviso
6. Lote sem IDs usa posições (não mudam após filtrar)
7. Colisão id explícito vs posição rejeitada
8. Citação inventada NUNCA é marcada como conferida
9. Citação sem interação resulta em indisponível (nunca validada)
"""
import sys
from pathlib import Path

# Adiciona app/ ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

import pytest

from services import data_service as svc


def test_ids_explicitos_preservados():
    """Cenário 1: IDs explícitos 101, 205, 309, 412 são preservados."""
    itens = [
        {"id": 101, "autor": "Ana", "canal": "#geral", "texto": "msg 1"},
        {"id": 205, "autor": "Bob", "canal": "#geral", "texto": "msg 2"},
        {"id": 309, "autor": "Carlos", "canal": "#projetos", "texto": "msg 3"},
        {"id": 412, "autor": "Diana", "canal": "#projetos", "texto": "msg 4"},
    ]
    
    resultado = svc._normalizar(itens)
    
    assert len(resultado) == 4
    assert resultado[0]["_id_efetivo"] == 101
    assert resultado[1]["_id_efetivo"] == 205
    assert resultado[2]["_id_efetivo"] == 309
    assert resultado[3]["_id_efetivo"] == 412
    assert svc.ERRO_IDS_DUPLICADOS == ""
    assert len(svc.AVISOS_IDS) == 0


def test_filtro_por_canal_mantem_ids():
    """Cenário 2: Filtrar por #conquistas mantém IDs 101 e 309."""
    itens = [
        {"id": 101, "autor": "Ana", "canal": "#conquistas", "texto": "msg 1"},
        {"id": 205, "autor": "Bob", "canal": "#geral", "texto": "msg 2"},
        {"id": 309, "autor": "Carlos", "canal": "#conquistas", "texto": "msg 3"},
        {"id": 412, "autor": "Diana", "canal": "#geral", "texto": "msg 4"},
    ]
    
    resultado = svc._normalizar(itens)
    filtrado = [i for i in resultado if i["canal"] == "#conquistas"]
    
    assert len(filtrado) == 2
    assert filtrado[0]["_id_efetivo"] == 101
    assert filtrado[1]["_id_efetivo"] == 309


def test_ids_duplicados_rejeitados():
    """Cenário 3: Dois registros com id 101 são rejeitados."""
    itens = [
        {"id": 101, "autor": "Ana", "canal": "#geral", "texto": "msg 1"},
        {"id": 101, "autor": "Bob", "canal": "#geral", "texto": "msg 2"},
    ]
    
    with pytest.raises(ValueError) as excinfo:
        svc._normalizar(itens)
    
    assert "IDs duplicados" in str(excinfo.value)
    assert "ID 101" in str(excinfo.value)
    assert "Ana" in str(excinfo.value)
    assert "Bob" in str(excinfo.value)


def test_lote_misto_aceito():
    """Cenário 4: Lote com IDs 101, sem id, 309 aceito. IDs efetivos: 101, 2, 309."""
    itens = [
        {"id": 101, "autor": "Ana", "canal": "#geral", "texto": "msg 1"},
        {"autor": "Bob", "canal": "#geral", "texto": "msg 2"},  # sem id
        {"id": 309, "autor": "Carlos", "canal": "#geral", "texto": "msg 3"},
    ]
    
    resultado = svc._normalizar(itens)
    
    assert len(resultado) == 3
    assert resultado[0]["_id_efetivo"] == 101
    assert resultado[1]["_id_efetivo"] == 2  # posição
    assert resultado[2]["_id_efetivo"] == 309
    assert svc.ERRO_IDS_DUPLICADOS == ""


def test_id_zero_vira_posicao_com_aviso():
    """Cenário 5: id=0, negativo, texto viram posição e geram aviso."""
    itens = [
        {"id": 0, "autor": "Ana", "canal": "#geral", "texto": "msg 1"},
        {"id": -5, "autor": "Bob", "canal": "#geral", "texto": "msg 2"},
        {"id": "texto", "autor": "Carlos", "canal": "#geral", "texto": "msg 3"},
        {"id": False, "autor": "Diana", "canal": "#geral", "texto": "msg 4"},  # False não colide
    ]
    
    resultado = svc._normalizar(itens)
    
    assert len(resultado) == 4
    assert resultado[0]["_id_efetivo"] == 1  # posição (id=0 inválido)
    assert resultado[1]["_id_efetivo"] == 2  # posição (id=-5 inválido)
    assert resultado[2]["_id_efetivo"] == 3  # posição (id="texto" inválido)
    assert resultado[3]["_id_efetivo"] == 4  # posição (id=False inválido)
    
    avisos = svc.AVISOS_IDS
    assert len(avisos) == 4
    assert "ID inválido" in avisos[0]
    assert "Ana" in avisos[0]
    assert "0" in avisos[0]


def test_lote_sem_ids_usa_posicoes():
    """Cenário 6: Lote sem IDs usa posições 1, 2, 3. Filtro não muda."""
    itens = [
        {"autor": "Ana", "canal": "#conquistas", "texto": "msg 1"},
        {"autor": "Bob", "canal": "#geral", "texto": "msg 2"},
        {"autor": "Carlos", "canal": "#conquistas", "texto": "msg 3"},
    ]
    
    resultado = svc._normalizar(itens)
    
    assert resultado[0]["_id_efetivo"] == 1
    assert resultado[1]["_id_efetivo"] == 2
    assert resultado[2]["_id_efetivo"] == 3
    
    # Filtrar não muda IDs
    filtrado = [i for i in resultado if i["canal"] == "#conquistas"]
    assert filtrado[0]["_id_efetivo"] == 1
    assert filtrado[1]["_id_efetivo"] == 3


def test_colisao_id_explicito_vs_posicao():
    """Cenário 7: id explícito 2 + segundo item sem id (posição 2) = colisão."""
    itens = [
        {"autor": "Ana", "canal": "#geral", "texto": "msg 1"},  # posição 1
        {"id": 2, "autor": "Bob", "canal": "#geral", "texto": "msg 2"},  # id explícito 2
        # Se o segundo item não tivesse id, seria posição 2 -> colisão!
    ]
    
    # Este caso NÃO é colisão (Bob tem id explícito 2, que é a própria posição)
    resultado = svc._normalizar(itens)
    assert len(resultado) == 2
    assert resultado[0]["_id_efetivo"] == 1
    assert resultado[1]["_id_efetivo"] == 2
    
    # Agora testar colisão real: primeiro item com id=2, segundo sem id
    itens_colisao = [
        {"id": 2, "autor": "Ana", "canal": "#geral", "texto": "msg 1"},  # id explícito 2
        {"autor": "Bob", "canal": "#geral", "texto": "msg 2"},  # posição 2
    ]
    
    with pytest.raises(ValueError) as excinfo:
        svc._normalizar(itens_colisao)
    
    assert "IDs duplicados" in str(excinfo.value)
    assert "ID 2" in str(excinfo.value)


def test_citacao_inventada_nunca_conferida():
    """Cenário 8: Citação 'Ganhei um prêmio internacional' nunca é marcada como conferida."""
    from styles import evidencias_citadas
    
    historia = {
        "citacoes": [
            {"texto": "Ganhei um prêmio internacional", "id_interacao": 1}
        ]
    }
    
    interacoes = [
        {"_id_efetivo": 1, "texto": "Completei meu primeiro projeto no curso."}
    ]
    
    html = evidencias_citadas(historia, interacoes, modo_demonstracao=False)
    
    # A citação NÃO deve ter selo verde e o motivo da reprovação aparece
    assert "chip-green" not in html
    assert "Trecho literal conferido" not in html
    assert "não encontrado na mensagem original" in html.lower()


def test_citacao_sem_interacao_indisponivel():
    """Cenário 9: Citação cuja interação não existe no lote resulta em indisponível."""
    from styles import evidencias_citadas
    
    historia = {
        "citacoes": [
            {"texto": "Consegui minha primeira vaga", "id_interacao": 999}  # ID não existe
        ]
    }
    
    interacoes = [
        {"_id_efetivo": 1, "texto": "Mensagem qualquer"}
    ]
    
    html = evidencias_citadas(historia, interacoes, modo_demonstracao=False)
    
    # Deve mostrar "Conferência indisponível", NUNCA "validada"
    assert "Conferência indisponível" in html
    assert "Trecho literal conferido" not in html
    assert "validada" not in html.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
