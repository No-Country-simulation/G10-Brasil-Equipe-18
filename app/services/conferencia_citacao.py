"""Conferência de citação contra a mensagem original.

A citação nasce do texto que passou pela anonimização, então pode conter
marcadores como [NOME] ou [EMAIL] onde a mensagem original tem o dado real.
A comparação direta (`trecho in original`) falha nesses casos. Esta função
compara aceitando o marcador como trecho variável e exigindo que todo o
resto do texto apareça literalmente, na mesma ordem.

O trecho variável tem limite: no máximo MAX_PALAVRAS_MARCADOR palavras e
sem atravessar fim de frase. Sem esses limites, uma citação com marcador
consegue "pular" meia mensagem e casar com texto que não é dela.

Distingue dois sucessos, e a interface não deve tratá-los como iguais:

- MOTIVO_LITERAL — o trecho não tem marcador e aparece literal na mensagem.
- MOTIVO_ANONIMIZADO — o trecho tem marcador e o texto literal bate, com a
  lacuna coberta por conteúdo de forma compatível com o tipo do marcador.

Limitação declarada: nada aqui prova que a anonimização foi correta nem que
o conteúdo do ativo é fiel ao relato. MOTIVO_ANONIMIZADO diz que a citação é
compatível com o texto anonimizado e que a lacuna tem a forma esperada do
tipo; o dado real por trás do marcador não é conferido, e a comparação com
a mensagem original sem transformação é o caso MOTIVO_LITERAL.
"""
import re

MARCADORES = ("[NOME]", "[EMAIL]", "[CPF]", "[TELEFONE]")

MOTIVO_LITERAL = "trecho literal conferido"
MOTIVO_ANONIMIZADO = "trecho compatível com anonimização"

# Nome completo cabe em 5 palavras; e-mail e telefone em uma ou duas.
MAX_PALAVRAS_MARCADOR = 5
# Janela em caracteres só como teto técnico, para a expressão não correr solta.
JANELA_CARACTERES = 80

_PADRAO_MARCADOR = re.compile("|".join(re.escape(m) for m in MARCADORES))
_FIM_DE_FRASE = re.compile(r"[.!?][\s\"')\]]|\n")

# Forma esperada do conteúdo escondido atrás de cada marcador. Não valida o
# dado real (não temos acesso a ele): só impede que um marcador de um tipo
# cubra texto de outro, que é o que deixaria a lacuna genérica.
_FORMAS = {
    "[EMAIL]": re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+"),
    "[CPF]": re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}"),
    "[TELEFONE]": re.compile(r"[\d()+\-\s]{8,}"),
    "[NOME]": re.compile(r"[^\W\d_]+(?:[ '\-.][^\W\d_]+)*"),
}

_SO_NOME = re.compile(r"^[^\W\d_]+(?:[ '\-.][^\W\d_]+)*$")


def _partes(trecho):
    """Divide o trecho em (pedaços literais, marcadores encontrados)."""
    partes, posicao = [], 0
    for achado in _PADRAO_MARCADOR.finditer(trecho):
        partes.append(("literal", trecho[posicao:achado.start()]))
        partes.append(("marcador", achado.group(0)))
        posicao = achado.end()
    partes.append(("literal", trecho[posicao:]))
    return partes


def _cabe_no_tipo(marcador, texto):
    """O conteúdo coberto tem a forma esperada do tipo do marcador?"""
    texto = (texto or "").strip()
    if not texto:
        return False
    forma = _FORMAS.get(marcador)
    if forma is None:
        return False
    if marcador == "[NOME]":
        if len(texto.split()) > MAX_PALAVRAS_MARCADOR:
            return False
        return bool(_SO_NOME.match(texto))
    if marcador == "[TELEFONE]":
        return bool(forma.fullmatch(texto)) and sum(c.isdigit() for c in texto) >= 8
    return bool(forma.fullmatch(texto))


def conferir_citacao(trecho, original):
    """Devolve (confere, motivo).

    confere=True quando todo o texto literal da citação aparece no original,
    na mesma ordem, e cada marcador cobre um trecho curto, sem atravessar fim
    de frase e com forma compatível com o tipo. O motivo distingue o sucesso
    literal do sucesso com anonimização, e confere=False vem sempre com o
    motivo, para a tela poder explicar em vez de só reprovar.
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
            return True, MOTIVO_LITERAL
        return False, "trecho não encontrado na mensagem original"

    if not any(tipo == "literal" and texto.strip() for tipo, texto in partes):
        return False, "citação só com marcador, sem trecho literal"

    marcadores = [texto for tipo, texto in partes if tipo == "marcador"]
    expressao = "".join(
        re.escape(texto) if tipo == "literal" else f"(.{{1,{JANELA_CARACTERES}}}?)"
        for tipo, texto in partes
    )

    houve_lacuna_limite = False
    houve_lacuna_de_tipo = False
    for achado in re.finditer(expressao, original, flags=re.DOTALL):
        coberturas = [g for g in achado.groups() if g is not None]
        if len(coberturas) != len(marcadores):
            continue
        if any(
            len(g.split()) > MAX_PALAVRAS_MARCADOR or _FIM_DE_FRASE.search(g)
            for g in coberturas
        ):
            houve_lacuna_limite = True
            continue
        if not all(
            _cabe_no_tipo(marcador, cobertura)
            for marcador, cobertura in zip(marcadores, coberturas)
        ):
            houve_lacuna_de_tipo = True
            continue
        return True, MOTIVO_ANONIMIZADO

    if houve_lacuna_de_tipo:
        return False, "marcador cobrindo conteúdo incompatível com o tipo"
    if houve_lacuna_limite:
        return False, "marcador cobrindo trecho longo ou atravessando fim de frase"
    return False, "trecho alterado ou não encontrado na mensagem original"
