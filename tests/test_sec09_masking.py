import pytest
from src.preprocessing import anonimizacao as a

@pytest.mark.parametrize("entrada,marcador", [
    ("11987654321", "[TELEFONE]"),
    ("+5521987654321", "[TELEFONE]"),
    ("https://example.invalid/perfil?nome=teste", "[URL]"),
    ("@usuario_teste", "[USUARIO]"),
    ("<@123456789012345678>", "[USUARIO]"),
    ("@membro_abc123", "@membro_abc123"),
])
def test_sec09_identificadores(monkeypatch, entrada, marcador):
    monkeypatch.setattr(a, "_obter_nlp", lambda: None)
    texto, contagem = a.anonimizar_texto(entrada)
    assert texto == marcador
    assert set(contagem) == {"email", "telefone", "cpf", "nome"}

def test_sec09_sem_download(monkeypatch):
    import sys
    from types import SimpleNamespace
    def ausente(*args):
        raise OSError("modelo ausente")
    monkeypatch.setitem(sys.modules, "spacy", SimpleNamespace(load=ausente))
    monkeypatch.setattr(a, "_NLP", None)
    assert a._obter_nlp() is None


def test_sec09_codigo_pedido_e_telefone(monkeypatch):
    monkeypatch.setattr(a, "_obter_nlp", lambda: None)
    texto, contagem = a.anonimizar_texto("O código do pedido é 99988877766 e telefone 99988877766.")
    assert "99988877766" in texto
    assert "[TELEFONE]" in texto
    assert contagem["telefone"] == 1
