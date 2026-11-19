"""Conferência de citação contra a mensagem original.

A citação nasce do texto que passou pela anonimização, então pode conter
marcadores como [NOME] ou [EMAIL] onde a mensagem original tem o dado real.
A comparação direta (`trecho in original`) falha nesses casos. Esta função
compara aceitando o marcador como trecho variável e exigindo que todo o
resto do texto apareça literalmente, na mesma ordem.

O trecho variável tem limite: no máximo MAX_PALAVRAS_MARCADOR palavras e
sem atravessar fim de frase. Sem esses limites, uma citação com marcador
consegue "pular" meia mensagem e casar com texto que não é dela.
"""
import re

MARCADORES = ("[NOME]", "[EMAIL]", "[CPF]", "[TELEFONE]")

# Nome completo cabe em 5 palavras; e-mail e telefone em uma ou duas.
MAX_PALAVRAS_MARCADOR = 5
# Janela em caracteres só como teto técnico, para a expressão não correr solta.
JANELA_CARACTERES = 80

_PADRAO_MARCADOR = re.compile("|".join(re.escape(m) for m in MARCADORES))
_FIM_DE_FRASE = re.compile(r"[.!?][\s\"')\]]|\n")


def _partes(trecho):
    """Divide o trecho em (pedaços literais, marcadores encontrados)."""
    partes, posicao = [], 0
    for achado in _PADRAO_MARCADOR.finditer(trecho):
        partes.append(("literal", trecho[posicao:achado.start()]))
        partes.append(("marcador", achado.group(0)))
        posicao = achado.end()
    partes.append(("literal", trecho[posicao:]))
    return partes


def conferir_citacao(trecho, original):
    """Devolve (confere, motivo).

    confere=True quando todo o texto literal da citação aparece no original,
    na mesma ordem, e cada marcador cobre um trecho curto que não atravessa
    fim de frase. confere=False vem sempre com o motivo, para a tela poder
    explicar em vez de só reprovar.
    """
    trecho = (trecho or "").strip()
    original = (original or "").strip()
    if not trecho:
        return False, "citação vazia"
    if not original:
        return False, "mensagem original ausente"

    partes = _partes(trecho)
    if len(partes) == 1:
        # Sem marcador: conferência literal, igual à de hoje.
        if trecho in original:
            return True, "trecho literal conferido"
        return False, "trecho não encontrado na mensagem original"

    if not any(tipo == "literal" and texto.strip() for tipo, texto in partes):
        return False, "citação só com marcador, sem trecho literal"

    expressao = "".join(
        re.escape(texto) if tipo == "literal" else f"(.{{1,{JANELA_CARACTERES}}}?)"
        for tipo, texto in partes
    )

    for achado in re.finditer(expressao, original, flags=re.DOTALL):
        coberturas = [g for g in achado.groups() if g is not None]
        if all(
            len(g.split()) <= MAX_PALAVRAS_MARCADOR and not _FIM_DE_FRASE.search(g)
            for g in coberturas
        ):
            return True, "trecho literal conferido"

    return False, "trecho alterado ou não encontrado na mensagem original"
