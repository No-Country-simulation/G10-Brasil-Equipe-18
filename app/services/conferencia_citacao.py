"""Conferência de citação contra a mensagem original.

A REGRA — é isto que a função promete, e é o que os testes gerados cobrem.
Qualquer caso fora daqui é decisão de contrato, não de implementação:

1. Sem marcador: a citação confere quando o texto aparece literalmente na
   mensagem original (MOTIVO_LITERAL).
2. Com marcador: o texto literal da citação tem que aparecer no original, na
   mesma ordem, e cada marcador cobre uma lacuna — o trecho entre dois
   literais, ou o trecho logo depois do último literal quando o marcador
   fecha a citação (MOTIVO_ANONIMIZADO).
3. Toda lacuna tem no máximo MAX_PALAVRAS_MARCADOR palavras e não pode
   conter fim de frase.
4. A lacuna tem que ter a forma do tipo do marcador: [EMAIL] com arroba e
   domínio, [CPF] com 11 dígitos, [TELEFONE] com 8 dígitos ou mais, [NOME]
   só com letras e no máximo MAX_PALAVRAS_MARCADOR palavras.
5. O alinhamento não pode pular conteúdo: cada literal é conferido exatamente
   na posição em que foi encontrado, e o que fica entre dois literais é
   conferido pelas regras 3 e 4. Se nenhum alinhamento satisfaz as regras, a
   citação não confere.

Princípio: na dúvida, reprova. A função só responde que confere quando consegue
provar. O que é formato não muda o que foi dito e é tolerado: espaço a mais
(a limpeza do contrato já normaliza espaços) e reticências no fim da citação.
O que muda o texto é recusado. Se nenhuma leitura satisfaz as regras, o
resultado é não confere, com motivo — a função nunca tenta adivinhar.
Citação recortada no meio de palavra também não confere.

Decisões de contrato embutidas, para ficarem visíveis:
- Dois marcadores colados, sem literal entre eles, reprovam: sem âncora não há
  como medir a lacuna (MOTIVO_LIMITE).
- Marcador no início da citação confere pelo mesmo critério do meio: a lacuna
  é o trecho até o próximo literal.

Fora de escopo, de propósito: qual interação é a origem. O contrato
(`especificacao_dados` §4) exige citação literal amarrada ao `id_interacao`;
esta função recebe os dois textos, e resolver o id é de quem chama.

Limitação declarada: nada aqui prova que a anonimização foi correta nem que
o conteúdo do ativo é fiel ao relato. MOTIVO_ANONIMIZADO diz que a citação é
compatível com o texto anonimizado e que a lacuna tem a forma esperada do
tipo; o dado real por trás do marcador não é conferido, e a comparação sem
transformação é o caso MOTIVO_LITERAL.

Referências: `docs/architecture/docs_data_ml/especificacao_dados.md` §4
(citações literais com id_interacao), `docs/architecture/docs_data_ml/
contrato_saida.md` §4 (marcadores e melhor esforço na detecção de nomes) e
`docs/CQF_SPECIFICATION.md` (preservação de citações literais; edição exige
nova validação de fidelidade).
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
_SO_NOME = re.compile(r"^[^\W\d_]+(?:[ ,.\-'()]+[^\W\d_]+)*[.,)]?$")
_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
_CPF = re.compile(r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$")
_TELEFONE = re.compile(r"^[\d()+\-\s]{8,}$")


def _preparar(texto):
    """Normaliza só o que é formato: espaços repetidos e reticência final."""
    texto = re.sub(r"\s+", " ", (texto or "")).strip()
    return re.sub(r"(?:\.{2,}|…)$", "", texto).strip()


def _limite_de_palavra(original, posicao):
    """A posição cai em limite de palavra? (antes/depois não é letra ou número)"""
    if posicao < 0 or posicao >= len(original):
        return True
    return not original[posicao].isalnum()


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


def _ocorrencias(texto, alvo, inicio=0):
    """Todas as posições de `alvo` em `texto`, a partir de `inicio`."""
    posicao = texto.find(alvo, inicio)
    while posicao != -1:
        yield posicao
        posicao = texto.find(alvo, posicao + 1)


def _casa(literais, marcadores, indice, inicio, original, falhas):
    """Confere a partir de literais[indice], já localizado em `inicio`.

    O literal não é procurado de novo aqui: ele está exatamente onde foi
    encontrado. Procurar outra ocorrência mais adiante deixava a conferência
    pular o conteúdo intermediário sem validar.
    """
    fim = inicio + len(literais[indice])
    if indice == len(literais) - 1:
        # O último literal tem que terminar em limite de palavra: citação
        # recortada no meio de uma palavra não confere.
        if literais[indice] and not _limite_de_palavra(original, fim):
            return False
        return True

    marcador = marcadores[indice]
    proximo = literais[indice + 1]
    ultimo_literal = indice + 1 == len(literais) - 1

    if not proximo:
        if ultimo_literal:
            # Citação termina em marcador: o original segue depois dele.
            if _lacuna_final_ok(marcador, original[fim:]):
                return True
            falhas.add(MOTIVO_TIPO)
        else:
            # Dois marcadores colados, sem nada entre eles: sem âncora para
            # conferir a lacuna dos dois.
            falhas.add(MOTIVO_LIMITE)
        return False

    # O próximo literal ancora a lacuna — inclusive quando ele é só um espaço
    # entre dois marcadores.
    for seguinte in _ocorrencias(original, proximo, fim):
        ok, motivo = _avaliar_lacuna(marcador, original[fim:seguinte])
        if ok and _casa(literais, marcadores, indice + 1, seguinte, original, falhas):
            return True
        if motivo:
            falhas.add(motivo)
    return False


def conferir_citacao(trecho, original):
    """Devolve (confere, motivo).

    confere=True quando todo o texto literal da citação aparece no original,
    na mesma ordem, e cada marcador cobre um trecho curto, sem atravessar fim
    de frase e com forma compatível com o tipo. O motivo distingue o sucesso
    literal do sucesso com anonimização, e confere=False vem sempre com o
    motivo, para a tela poder explicar em vez de só reprovar.
    """
    trecho = _preparar(trecho)
    original = _preparar(original)
    if not trecho:
        return False, "citação vazia"
    if not original:
        return False, "mensagem original ausente"

    literais, marcadores = _literais_e_marcadores(trecho)
    if not marcadores:
        # Sem marcador: conferência literal, em limite de palavra.
        inicio = original.find(trecho)
        while inicio != -1:
            fim = inicio + len(trecho)
            if _limite_de_palavra(original, inicio - 1) and _limite_de_palavra(original, fim):
                return True, MOTIVO_LITERAL
            inicio = original.find(trecho, inicio + 1)
        return False, "trecho não encontrado na mensagem original"

    if not any(literal.strip() for literal in literais):
        return False, "citação só com marcador, sem trecho literal"

    falhas = set()
    for inicio in _ocorrencias(original, literais[0]):
        if literais[0] and not _limite_de_palavra(original, inicio - 1):
            continue
        if _casa(literais, marcadores, 0, inicio, original, falhas):
            return True, MOTIVO_ANONIMIZADO

    if MOTIVO_TIPO in falhas:
        return False, MOTIVO_TIPO
    if MOTIVO_LIMITE in falhas:
        return False, MOTIVO_LIMITE
    return False, "trecho alterado ou não encontrado na mensagem original"
