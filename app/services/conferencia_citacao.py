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

O marcador pode estar no meio ou no fim da citação: no fim, o original segue
depois dele, então a lacuna é lida como um trecho curto a partir dali.

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

MOTIVO_TIPO = "marcador cobrindo conteúdo incompatível com o tipo"
MOTIVO_LIMITE = "marcador cobrindo trecho longo ou atravessando fim de frase"

# Nome completo cabe em 5 palavras; e-mail e telefone em uma ou duas.
MAX_PALAVRAS_MARCADOR = 5

_PADRAO_MARCADOR = re.compile("|".join(re.escape(m) for m in MARCADORES))
_FIM_DE_FRASE = re.compile(r"[.!?][\s\"')\]]|\n")
_PONTUACAO_FINAL = ".,;:!?"

# Forma esperada do conteúdo escondido atrás de cada marcador. Não valida o
# dado real (não temos acesso a ele): só impede que um marcador de um tipo
# cubra texto de outro, que é o que deixaria a lacuna genérica.
_SO_NOME = re.compile(r"^[^\W\d_]+(?:[ '\-.][^\W\d_]+)*$")
_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
_CPF = re.compile(r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$")
_TELEFONE = re.compile(r"^[\d()+\-\s]{8,}$")


def _literais_e_marcadores(trecho):
    """Separa o trecho em literais e marcadores.

    Devolve (literais, marcadores): `marcadores[i]` fica entre `literais[i]`
    e `literais[i + 1]`, então a lista de literais tem sempre um item a mais.
    """
    literais, marcadores, posicao = [], [], 0
    for achado in _PADRAO_MARCADOR.finditer(trecho):
        literais.append(trecho[posicao:achado.start()])
        marcadores.append(achado.group(0))
        posicao = achado.end()
    literais.append(trecho[posicao:])
    return literais, marcadores


def _cabe_no_tipo(marcador, texto):
    """O conteúdo coberto tem a forma esperada do tipo do marcador?"""
    texto = (texto or "").strip()
    if not texto:
        return False
    if marcador == "[NOME]":
        return bool(_SO_NOME.match(texto)) and len(texto.split()) <= MAX_PALAVRAS_MARCADOR
    if marcador == "[EMAIL]":
        return bool(_EMAIL.match(texto))
    if marcador == "[CPF]":
        return bool(_CPF.match(texto))
    if marcador == "[TELEFONE]":
        return bool(_TELEFONE.match(texto)) and sum(c.isdigit() for c in texto) >= 8
    return False


def _avaliar_lacuna(marcador, lacuna):
    """Devolve (ok, motivo) para o texto coberto por um marcador."""
    if not (lacuna or "").strip():
        return False, MOTIVO_TIPO
    if len(lacuna.split()) > MAX_PALAVRAS_MARCADOR or _FIM_DE_FRASE.search(lacuna):
        return False, MOTIVO_LIMITE
    if not _cabe_no_tipo(marcador, lacuna.strip()):
        return False, MOTIVO_TIPO
    return True, ""


def _lacuna_final_ok(marcador, resto):
    """Marcador no fim da citação: o original pode continuar depois dele.

    Tenta de uma a MAX_PALAVRAS_MARCADOR palavras a partir do ponto onde o
    texto literal terminou, aceitando a primeira que tenha a forma do tipo.
    """
    palavras = (resto or "").split()
    for total in range(1, min(len(palavras), MAX_PALAVRAS_MARCADOR) + 1):
        candidato = " ".join(palavras[:total]).rstrip(_PONTUACAO_FINAL)
        if _cabe_no_tipo(marcador, candidato):
            return True
    return False


def _casa(literais, marcadores, indice, posicao, original, falhas):
    """Tenta casar literais[indice] daqui, aplicando o marcador anterior."""
    literal = literais[indice]
    if indice == len(literais) - 1:
        # Sobrou só o rabo: ele precisa aparecer, e não há marcador depois.
        return original.find(literal, posicao) != -1

    marcador = marcadores[indice]
    proximo = literais[indice + 1]
    ultimo_literal = indice + 1 == len(literais) - 1

    inicio = original.find(literal, posicao)
    while inicio != -1:
        fim = inicio + len(literal)
        if ultimo_literal and not proximo:
            # Citação termina em marcador: o original segue depois dele.
            if _lacuna_final_ok(marcador, original[fim:]):
                return True
            falhas.add(MOTIVO_TIPO)
        elif not proximo:
            # Dois marcadores colados, sem nada entre eles: sem âncora para
            # conferir a lacuna dos dois.
            falhas.add(MOTIVO_LIMITE)
        else:
            # O próximo literal ancora a lacuna — inclusive quando ele é só um
            # espaço entre dois marcadores.
            seguinte = original.find(proximo, fim)
            while seguinte != -1:
                ok, motivo = _avaliar_lacuna(marcador, original[fim:seguinte])
                if ok and _casa(literais, marcadores, indice + 1, seguinte, original, falhas):
                    return True
                if motivo:
                    falhas.add(motivo)
                seguinte = original.find(proximo, seguinte + 1)
        inicio = original.find(literal, inicio + 1)
    return False


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

    literais, marcadores = _literais_e_marcadores(trecho)
    if not marcadores:
        # Sem marcador: conferência literal, igual à de hoje.
        if trecho in original:
            return True, MOTIVO_LITERAL
        return False, "trecho não encontrado na mensagem original"

    if not any(literal.strip() for literal in literais):
        return False, "citação só com marcador, sem trecho literal"

    falhas = set()
    if _casa(literais, marcadores, 0, 0, original, falhas):
        return True, MOTIVO_ANONIMIZADO

    if MOTIVO_TIPO in falhas:
        return False, MOTIVO_TIPO
    if MOTIVO_LIMITE in falhas:
        return False, MOTIVO_LIMITE
    return False, "trecho alterado ou não encontrado na mensagem original"
