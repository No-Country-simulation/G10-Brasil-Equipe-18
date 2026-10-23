"""Análise de interações com dois provedores de LLM: Groq (principal) + Gemini (fallback).

Substitui o mock de `data_service.analisar()` por uma chamada real.

ESTRATÉGIA DE DOIS PROVEDORES
-------------------------------
- Groq (llama-3.3-70b-versatile): análise principal — maior throughput, sem rate-limit
  agressivo, contexto mais amplo para análise semântica complexa de histórias.
- Gemini (gemini-3.5-flash): fallback — caso o Groq falhe ou não esteja configurado.

Configurável via LLM_STRATEGY em .streamlit/secrets.toml:
  "groq_first"   → Groq principal, Gemini fallback (padrão)
  "gemini_first" → Gemini principal, Groq fallback

O modelo responde no vocabulário fechado de
`docs/architecture/docs_data_ml/guia_rotulagem.md` e nos campos de `analise`
do `schemas/interacao_schema.json`: sentimento, relevancia, topicos,
tipo_insight, justificativa e confianca. Da história, responde `tipo`
(conquista_profissional | superacao | projeto_destaque), `resumo`,
`resultados`, `fatos` e `destaques`.

Contrato de saída (o que as telas consomem, com os campos do contrato junto):
{
  "id", "autor", "iniciais", "canal", "origem", "categoria",
  "sentimento", "relevancia", "relevancia_nivel", "mensagem_original",
  "destaques", "fatos", "ativos",
  "tipo_insight", "topicos", "justificativa", "confianca",
  "tipo", "tipos_alternativos", "resumo", "resultados"
}

`categoria` e `relevancia` numérica são derivadas (`tipo` e faixa), para a tela
não mudar. Valor fora da lista fechada é recusado com o motivo escrito em
ULTIMAS_RECUSADAS; valor apenas escrito de outra forma (caixa ou acento) é
aceito com o ajuste registrado em ULTIMOS_AVISOS — nada é corrigido em silêncio.
"""
from __future__ import annotations

import json
import os
import re
import time
import unicodedata

import requests

# ── Gemini ───────────────────────────────────────────────────────────────────
MODELO_PADRAO_GEMINI = "gemini-3.5-flash"
MODELOS_FALLBACK_GEMINI = ["gemini-3.5-flash-lite"]
ENDPOINT_GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"

# Mantido por compatibilidade com código existente que importa MODELO_PADRAO/ENDPOINT
MODELO_PADRAO = MODELO_PADRAO_GEMINI
MODELOS_FALLBACK = MODELOS_FALLBACK_GEMINI
ENDPOINT = ENDPOINT_GEMINI

# ── Groq ─────────────────────────────────────────────────────────────────────
MODELO_PADRAO_GROQ = "openai/gpt-oss-120b"
MODELOS_FALLBACK_GROQ = ["openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
ENDPOINT_GROQ = "https://api.groq.com/openai/v1/chat/completions"

# Rastreia qual provedor atendeu a última análise ("groq" ou "gemini")
ULTIMO_PROVEDOR_USADO: str = ""

# Quantidade maxima de historias por lote analisado.
MAXIMO_HISTORIAS = 3

# Listas fechadas do guia de rotulagem (docs/architecture/docs_data_ml/guia_rotulagem.md).
SENTIMENTOS = ("positivo", "neutro", "negativo")
RELEVANCIAS = ("alta", "media", "baixa")
TOPICOS = ("carreira", "estudos", "tecnologia", "ferramentas", "comunidade", "eventos", "outro")
TIPOS_INSIGHT = ("historia", "conquista", "duvida", "insight", "outro")
TIPOS_HISTORIA = ("conquista_profissional", "superacao", "projeto_destaque")

# Campos que a tela consome e que passam a ser derivados do vocabulario fechado:
# rotulo de exibicao a partir de `tipo` e nota de 0 a 100 a partir da faixa.
ROTULO_CATEGORIA = {
    "conquista_profissional": "Conquista profissional",
    "superacao": "Superação",
    "projeto_destaque": "Projeto de destaque",
}
NOTA_RELEVANCIA = {"alta": 90, "media": 70, "baixa": 30}

# Registro do que o modelo devolveu fora do contrato. Preenchido a cada analise,
# para nada sumir sem explicacao (mesmo padrao de `recusadas` no pacote).
ULTIMAS_RECUSADAS: list = []
ULTIMOS_AVISOS: list = []

# Historias que o modelo classificou em mais de um tipo possivel. O criterio de
# desempate ainda nao esta definido pela dona do contrato, entao o dado fica
# registrado em vez de a regra ser inventada aqui.
ULTIMAS_AMBIGUIDADES: list = []

PROMPT = """Você analisa mensagens de uma comunidade online para encontrar histórias com potencial de conteúdo.

Receberá uma lista de interações em JSON, cada uma com "autor", "canal", "tipo" e "texto".

Sua tarefa:
1. Selecionar até {maximo} interações que contenham uma história real, um problema concreto ou uma conquista verificável.
2. Para cada uma, classificar sentimento, relevância, tópicos e tipo de insight, conforme as definições abaixo.
3. Gerar dois ativos: um post para LinkedIn e um card de conquista.

DEFINIÇÕES — use exatamente estes valores

sentimento (tom da mensagem, não o assunto):
- positivo: satisfação, entusiasmo, elogio, comemoração.
- neutro: informação ou pergunta sem carga emocional clara.
- negativo: frustração, dificuldade, crítica, insatisfação.

relevancia (quanto serve como conteúdo):
- alta: específico e aproveitável — conquista concreta, dúvida recorrente ou dica acionável.
- media: útil, mas genérico, pontual ou dependente de contexto.
- baixa: sem conteúdo aproveitável — apoio, cumprimento, ruído.

topicos: um ou dois itens, escolhidos de: carreira, estudos, tecnologia, ferramentas, comunidade, eventos, outro. Use "outro" só quando nenhum outro se aplica. Sem repetir.

tipo_insight:
- conquista: relato de resultado concreto (vaga, aprovação, projeto concluído).
- historia: relato de experiência ou percurso, sem resultado marcante.
- duvida: pergunta ou pedido de ajuda.
- insight: dica, aprendizado ou prática que outras pessoas podem aplicar.
- outro: apoio, cumprimento ou comentário sem conteúdo aproveitável.
Desempates: mais de um tipo na mensagem, use o predominante; entre conquista e historia, use conquista quando houver resultado verificável no texto; dúvida com resposta na mesma mensagem, use o que ocupa a maior parte do texto.

tipo da história (só para quem for virar conteúdo): conquista_profissional, superacao, projeto_destaque.
Se mais de um tipo servir, escolha um e liste os outros em "tipos_alternativos". Não invente tipo fora dessa lista.

Responda SOMENTE com JSON válido, neste formato exato:
{{
  "historias": [
    {{
      "id": "hist-001",
      "indice_interacao": 1,
      "autor": "nome do autor da interação",
      "canal": "canal da interação",
      "sentimento": "positivo | neutro | negativo",
      "relevancia": "alta | media | baixa",
      "topicos": ["carreira"],
      "tipo_insight": "historia | conquista | duvida | insight | outro",
      "justificativa": "até 500 caracteres explicando a classificação",
      "confianca": 0.0,
      "tipo": "conquista_profissional | superacao | projeto_destaque",
      "tipos_alternativos": ["outro tipo que também serviria, ou lista vazia"],
      "resumo": "resumo factual, até 1000 caracteres",
      "resultados": ["impacto concreto alcançado"],
      "mensagem_original": "texto original, sem alterar",
      "destaques": ["trechos literais da mensagem"],
      "fatos": ["fato objetivo extraído, no formato Tema: detalhe"],
      "ativos": [
        {{
          "id": "post_linkedin",
          "nome": "Post para LinkedIn",
          "tipo": "texto",
          "campos": {{"texto": "post de até 120 palavras, português do Brasil, sem emoji, sem hashtag"}}
        }},
        {{
          "id": "card_conquista",
          "nome": "Card de conquista",
          "tipo": "card",
          "campos": {{"titulo": "até 60 caracteres", "frase": "uma frase de até 90 caracteres"}}
        }}
      ]
    }}
  ]
}}

Regras obrigatórias:
- Use apenas informação presente nas interações. Não invente nome, número ou fato.
- "indice_interacao" é a posição da interação no lote recebido, começando em 1.
- "destaques" deve conter trechos copiados do texto original, sem reescrever.
- "confianca" entre 0.0 e 1.0; abaixo de 0.6 o item vai para revisão prioritária.
- Se nenhuma interação tiver potencial, devolva {{"historias": []}}.
- Não escreva nada antes ou depois do JSON.
"""


class ErroAnalise(RuntimeError):
    """Falha controlada na análise por LLM."""


def _secrets_get(chave_secrets: str, default="") -> str:
    """Lê um valor de st.secrets ou variável de ambiente com fallback seguro."""
    try:
        import streamlit as st
        val = st.secrets.get(chave_secrets, None)
        if val is not None:
            return str(val)
    except Exception:
        pass
    return os.environ.get(chave_secrets, default)


def _chave_gemini() -> str:
    chave = _secrets_get("GEMINI_API_KEY")
    if not chave:
        raise ErroAnalise(
            "Chave do Gemini ausente. Defina GEMINI_API_KEY em .streamlit/secrets.toml "
            "ou como variável de ambiente."
        )
    return chave.strip()


# Alias de compatibilidade
_chave = _chave_gemini


def _chave_groq() -> str:
    chave = _secrets_get("GROQ_API_KEY")
    if not chave:
        raise ErroAnalise(
            "Chave do Groq ausente. Defina GROQ_API_KEY em .streamlit/secrets.toml "
            "ou como variável de ambiente."
        )
    return chave.strip()


def _modelo_gemini() -> str:
    return _secrets_get("GEMINI_MODEL", MODELO_PADRAO_GEMINI) or MODELO_PADRAO_GEMINI


# Alias de compatibilidade
_modelo = _modelo_gemini


def _modelo_groq() -> str:
    return _secrets_get("GROQ_MODEL", MODELO_PADRAO_GROQ) or MODELO_PADRAO_GROQ


def _estrategia() -> str:
    """Retorna 'groq_first' ou 'gemini_first' conforme configurado."""
    return _secrets_get("LLM_STRATEGY", "groq_first").lower()


def _maximo_historias() -> int:
    try:
        import streamlit as st
        val = st.secrets.get("MAX_HISTORIAS", None)
        if val is not None:
            return int(val)
    except Exception:
        pass
    env_val = os.environ.get("MAX_HISTORIAS", "")
    if env_val.isdigit():
        return int(env_val)
    return 3


def _temperatura() -> float:
    """Retorna a temperatura configurada (0.0 a 1.0, padrão 0.4)."""
    val = _secrets_get("GEMINI_TEMPERATURE") or _secrets_get("LLM_TEMPERATURE")
    try:
        if val:
            return float(val)
    except ValueError:
        pass
    return 0.4


def _iniciais(nome: str) -> str:
    partes = [p for p in re.split(r"\s+", (nome or "").strip()) if p]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()



def _colapsar(texto: str) -> str:
    """Reduz sequencias de espaco/quebra de linha a um espaco simples."""
    return re.sub(r"\s+", " ", (texto or "").strip())


def _achatado_com_mapa(texto: str):
    """Normaliza para comparacao (sem acento, minusculo, espaco simples).

    Devolve tambem o indice de cada caractere no texto original, para o
    recorte final sair do original com acento e caixa preservados.
    """
    achatado = []
    mapa = []
    anterior_espaco = True
    for i, ch in enumerate(texto or ""):
        if ch.isspace():
            if anterior_espaco:
                continue
            achatado.append(" ")
            mapa.append(i)
            anterior_espaco = True
            continue
        base = unicodedata.normalize("NFKD", ch)
        sem_acento = "".join(c for c in base if not unicodedata.combining(c))
        for c in sem_acento.lower():
            achatado.append(c)
            mapa.append(i)
        anterior_espaco = False
    while achatado and achatado[-1] == " ":
        achatado.pop()
        mapa.pop()
    return "".join(achatado), mapa


def _localizar(original: str, trecho: str):
    """Devolve o trecho como ele aparece no texto original, ou None.

    A comparacao ignora espaco, acento e maiuscula/minuscula. O valor
    devolvido e sempre o recorte do original, entao a citacao continua
    literal -- o que muda e so a tolerancia ao procurar.
    """
    if not original or not trecho:
        return None
    alvo = _colapsar(trecho)
    if not alvo:
        return None
    alvo_achatado, _ = _achatado_com_mapa(alvo)
    if not alvo_achatado:
        return None

    normalizado, mapa = _achatado_com_mapa(original)
    for candidato in (alvo_achatado, alvo_achatado.strip(".,;:!?'\"()[]")):
        if not candidato:
            continue
        posicao = normalizado.find(candidato)
        if posicao == -1:
            continue
        inicio_trecho = mapa[posicao]
        fim_trecho = mapa[posicao + len(candidato) - 1] + 1
        return original[inicio_trecho:fim_trecho]
    return None

def _fonte_confiavel(hist: dict, por_posicao: dict):
    """Devolve a interacao do lote que sustenta a historia, ou None.

    A fonte e sempre um item do lote recebido. O texto informado pelo modelo
    nunca serve como fonte de verdade: no maximo, ajuda a localizar o item,
    e so quando a busca e inequivoca.
    """
    try:
        posicao = int(hist.get("indice_interacao") or 0)
    except (TypeError, ValueError):
        posicao = 0
    if posicao in por_posicao:
        return por_posicao[posicao]

    informado = _colapsar(str(hist.get("mensagem_original") or ""))
    if not informado:
        return None
    candidatos = [
        item for item in por_posicao.values()
        if _colapsar(str(item.get("texto") or "")) == informado
    ]
    if len(candidatos) == 1:
        return candidatos[0]
    return None


def _cinza(valor) -> str:
    """Texto comparavel: sem acento, minusculo, espaco simples."""
    base = unicodedata.normalize("NFKD", str(valor or ""))
    sem_acento = "".join(c for c in base if not unicodedata.combining(c))
    return _colapsar(sem_acento).lower()


def _fechado(valor, opcoes):
    """Devolve o valor canonico da lista fechada, ou None se estiver fora dela.

    Compara sem acento e sem caixa. Quando o original difere do canonico, o
    ajuste vai para ULTIMOS_AVISOS: valor fora da lista e recusado, e o que foi
    reescrito nao muda em silencio.
    """
    alvo = _cinza(valor)
    if not alvo:
        return None
    for opcao in opcoes:
        if _cinza(opcao) == alvo:
            return opcao
    return None


def _registrar_recusa(identificador, motivos: list) -> None:
    ULTIMAS_RECUSADAS.append({"id": identificador, "motivo": "; ".join(motivos)})


def _anotar_ajuste(campo: str, original, canonico) -> None:
    if str(original) != str(canonico):
        ULTIMOS_AVISOS.append(f"{campo}: {original!r} ajustado para {canonico!r}.")


def _topicos_fechados(valor):
    """Valida a lista de topicos contra a lista fechada do guia de rotulagem."""
    motivos = []
    if isinstance(valor, str) and valor.strip():
        valor = [valor]
    if not isinstance(valor, (list, tuple)) or not valor:
        return [], ["Sem topico: a analise exige ao menos um topico da lista fechada."]

    escolhidos = []
    for item in valor:
        canonico = _fechado(item, TOPICOS)
        if canonico is None:
            motivos.append(f"topico fora da lista fechada: {item!r}.")
            continue
        if canonico in escolhidos:
            ULTIMOS_AVISOS.append(f"topicos: {canonico!r} repetido, mantido uma vez.")
            continue
        escolhidos.append(canonico)
    return escolhidos, motivos


def _confianca(valor):
    """Confianca entre 0 e 1. Valor invalido fica registrado e vira None."""
    if valor is None or valor == "":
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        ULTIMOS_AVISOS.append(f"confianca: {valor!r} nao e numero, descartada.")
        return None
    if numero < 0 or numero > 1:
        ULTIMOS_AVISOS.append(f"confianca: {valor!r} fora de 0..1, descartada.")
        return None
    return numero


def _tipos_alternativos(valor, escolhido: str):
    """Outros tipos que tambem serviriam para a historia, sem o tipo escolhido."""
    if valor is None or valor == "":
        return []
    if isinstance(valor, str):
        valor = [valor]
    if not isinstance(valor, (list, tuple)):
        ULTIMOS_AVISOS.append(f"tipos_alternativos: {valor!r} ignorado, esperada uma lista.")
        return []

    alternativos = []
    for item in valor:
        canonico = _fechado(item, TIPOS_HISTORIA)
        if canonico is None:
            ULTIMOS_AVISOS.append(
                f"tipos_alternativos: {item!r} ignorado, fora da lista fechada."
            )
            continue
        if canonico == escolhido or canonico in alternativos:
            continue
        alternativos.append(canonico)
    return alternativos


def _campos_classificacao(hist: dict):
    """Confere o vocabulario fechado. Devolve (campos canonicos, motivos)."""
    motivos = []
    campos = {}

    for campo, opcoes in (
        ("sentimento", SENTIMENTOS),
        ("relevancia", RELEVANCIAS),
        ("tipo_insight", TIPOS_INSIGHT),
        ("tipo", TIPOS_HISTORIA),
    ):
        bruto = hist.get(campo)
        canonico = _fechado(bruto, opcoes)
        if canonico is None:
            motivos.append(f"{campo} fora da lista fechada: {bruto!r}.")
            continue
        _anotar_ajuste(campo, bruto, canonico)
        campos[campo] = canonico

    if "tipo" in campos:
        campos["tipos_alternativos"] = _tipos_alternativos(
            hist.get("tipos_alternativos"), campos["tipo"]
        )
    else:
        campos["tipos_alternativos"] = []

    topicos, motivos_topicos = _topicos_fechados(hist.get("topicos"))
    motivos.extend(motivos_topicos)
    campos["topicos"] = topicos

    justificativa = _colapsar(str(hist.get("justificativa") or ""))
    if len(justificativa) > 500:
        ULTIMOS_AVISOS.append("justificativa: cortada em 500 caracteres.")
        justificativa = justificativa[:500].rsplit(" ", 1)[0] or justificativa[:500]
    campos["justificativa"] = justificativa
    campos["confianca"] = _confianca(hist.get("confianca"))
    return campos, motivos


def _normalizar(historias: list, interacoes: list) -> list:
    """Garante o contrato esperado pelas telas, sem confiar cegamente no modelo.

    Historia que nao fecha com o contrato nao entra na saida: vai para
    ULTIMAS_RECUSADAS com o motivo escrito.
    """
    global ULTIMAS_RECUSADAS, ULTIMOS_AVISOS, ULTIMAS_AMBIGUIDADES
    ULTIMAS_RECUSADAS = []
    ULTIMOS_AVISOS = []
    ULTIMAS_AMBIGUIDADES = []

    por_posicao = {}
    por_id_lote = {}  # índice por id original do lote (str e int)
    for posicao, item in enumerate(interacoes, start=1):
        # O id vem do lote quando existir; senao, usa a posicao para referencia.
        item = dict(item)
        id_lote = item.get("id")
        # Aceita tanto IDs numéricos quanto strings como "int_001"
        if id_lote is not None and str(id_lote).strip():
            item["_id"] = id_lote
            por_id_lote[str(id_lote)] = item
            # Se for numérico, também indexa pelo número inteiro
            try:
                por_id_lote[int(id_lote)] = item
            except (ValueError, TypeError):
                pass
        else:
            item["_id"] = posicao
        por_posicao[posicao] = item

    saida = []
    for n, hist in enumerate(historias, start=1):
        identificador = f"hist-{n:03d}"
        if not isinstance(hist, dict):
            _registrar_recusa(None, ["Historia em formato invalido: esperado um objeto."])
            continue
        if str(hist.get("id") or "").strip():
            identificador = str(hist["id"]).strip()
        autor = str(hist.get("autor") or "").strip()
        original = str(hist.get("mensagem_original") or "").strip()
        base = _fonte_confiavel(hist, por_posicao)
        canal = str(hist.get("canal") or (base.get("canal") if base else "") or "")
        # O texto usado para validar a citacao vem do lote, nunca do modelo.
        texto_fonte = str(base.get("texto") or "") if base else ""
        # Preserva o ID original do lote (pode ser str como "int_001" ou int)
        id_interacao = base.get("_id") if base else 0
        if id_interacao is None:
            id_interacao = 0

        ativos = []
        for ativo in hist.get("ativos") or []:
            if not isinstance(ativo, dict) or not ativo.get("id"):
                continue
            campos = ativo.get("campos") or {}
            if not isinstance(campos, dict) or not any(str(v).strip() for v in campos.values()):
                continue
            ativos.append(
                {
                    "id": str(ativo["id"]),
                    "nome": str(ativo.get("nome") or ativo["id"]),
                    "tipo": str(ativo.get("tipo") or "texto"),
                    "campos": {str(k): str(v) for k, v in campos.items()},
                    **({"variacoes": ativo["variacoes"]} if ativo.get("variacoes") else {}),
                }
            )

        motivos = []
        if not autor:
            motivos.append("Sem autor informado.")
        if not original:
            motivos.append("Sem mensagem original informada.")
        if not ativos:
            motivos.append("Sem ativo gerado: nao ha conteudo para publicar.")

        classificacao, motivos_classificacao = _campos_classificacao(hist)
        motivos.extend(motivos_classificacao)

        resumo = _colapsar(str(hist.get("resumo") or ""))
        if not resumo:
            motivos.append("Sem resumo: o contrato da historia exige resumo.")
        elif len(resumo) > 1000:
            ULTIMOS_AVISOS.append(f"{identificador}: resumo cortado em 1000 caracteres.")
            resumo = resumo[:1000].rsplit(" ", 1)[0] or resumo[:1000]

        resultados = [str(r).strip() for r in (hist.get("resultados") or []) if str(r).strip()]
        fatos = [str(f).strip() for f in (hist.get("fatos") or []) if str(f).strip()]
        if not fatos:
            motivos.append("Sem fato extraido: o contrato da historia exige ao menos um fato.")

        # Citacoes: cada trecho apontado pelo modelo e conferido contra o texto
        # original. Se nao existir literalmente, e descartado (nao inventamos).
        citacoes = []
        vistos = set()
        for destaque in hist.get("destaques") or []:
            recorte = _localizar(texto_fonte, str(destaque))
            # O contrato do pipeline limita a citacao a 500 caracteres.
            if recorte and len(recorte) > 500:
                recorte = recorte[:500].rsplit(" ", 1)[0] or recorte[:500]
            if not recorte or recorte.lower() in vistos:
                continue
            vistos.add(recorte.lower())
            citacoes.append({"texto": recorte, "id_interacao": id_interacao})

        if not citacoes:
            motivos.append("Sem citacao literal: nenhum destaque existe no texto original.")

        if motivos:
            _registrar_recusa(identificador, motivos)
            continue

        faixa = classificacao["relevancia"]
        if classificacao["tipos_alternativos"]:
            ULTIMAS_AMBIGUIDADES.append(
                {
                    "id": identificador,
                    "tipo": classificacao["tipo"],
                    "alternativos": classificacao["tipos_alternativos"],
                }
            )
        saida.append(
            {
                "id": identificador,
                "autor": autor,
                "iniciais": _iniciais(autor),
                "canal": canal,
                "origem": str(hist.get("origem") or "Mensagem da comunidade"),
                "categoria": ROTULO_CATEGORIA[classificacao["tipo"]],
                "sentimento": classificacao["sentimento"],
                "relevancia": NOTA_RELEVANCIA[faixa],
                "relevancia_nivel": faixa,
                "mensagem_original": original,
                "citacoes": citacoes,
                "interacoes_origem": [id_interacao] if id_interacao else [],
                "destaques": [c["texto"] for c in citacoes],
                "fatos": fatos,
                "ativos": ativos,
                "tipo_insight": classificacao["tipo_insight"],
                "topicos": classificacao["topicos"],
                "justificativa": classificacao["justificativa"],
                "confianca": classificacao["confianca"],
                "tipo": classificacao["tipo"],
                "tipos_alternativos": classificacao["tipos_alternativos"],
                "resumo": resumo,
                "resultados": resultados,
            }
        )

    if ULTIMAS_RECUSADAS:
        print(
            f"[analise] {len(ULTIMAS_RECUSADAS)} historia(s) recusada(s) pelo contrato",
            flush=True,
        )
    if ULTIMAS_AMBIGUIDADES:
        print(
            f"[analise] {len(ULTIMAS_AMBIGUIDADES)} historia(s) com mais de um tipo possivel",
            flush=True,
        )
    return saida


def _chamar_gemini(modelo: str, corpo: dict, chave: str, timeout: int, max_retries: int = 2) -> str:
    """Faz a chamada HTTP ao Gemini com retry exponencial para erros transitórios (429, 503)."""
    for tentativa in range(max_retries + 1):
        try:
            resposta = requests.post(
                ENDPOINT_GEMINI.format(modelo=modelo),
                params={"key": chave},
                json=corpo,
                timeout=timeout,
            )
            if resposta.status_code == 200:
                try:
                    dados = resposta.json()
                    return dados["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError, ValueError) as erro:
                    raise ErroAnalise(f"Resposta inesperada do Gemini ({modelo}): {erro}") from erro

            if resposta.status_code in (429, 503):
                if tentativa < max_retries:
                    espera = (2 ** tentativa) + 0.5
                    print(
                        f"[llm:gemini] {modelo} respondeu {resposta.status_code}. "
                        f"Aguardando {espera:.1f}s (backoff #{tentativa + 1})...",
                        flush=True,
                    )
                    time.sleep(espera)
                    continue
                raise ErroAnalise(f"{resposta.status_code}")

            raise ErroAnalise(f"Gemini respondeu {resposta.status_code}: {resposta.text[:300]}")
        except requests.exceptions.Timeout:
            if tentativa < max_retries:
                espera = 2 ** tentativa
                print(f"[llm:gemini] {modelo} timeout. Aguardando {espera}s...", flush=True)
                time.sleep(espera)
                continue
            raise
    raise ErroAnalise(f"Gemini {modelo}: máximo de retries atingido")


# Alias de compatibilidade (código externo que chame _chamar_modelo ainda funciona)
_chamar_modelo = _chamar_gemini


def _chamar_groq(modelo: str, prompt_texto: str, payload_texto: str, chave: str,
                 timeout: int, max_retries: int = 2) -> str:
    """Faz a chamada HTTP ao Groq (API compatível com OpenAI) com retry exponencial."""
    headers = {
        "Authorization": f"Bearer {chave}",
        "Content-Type": "application/json",
        "User-Agent": "CommunityLab-G10/1.0",
    }
    corpo = {
        "model": modelo,
        "messages": [
            {
                "role": "user",
                "content": f"{prompt_texto}\n\n{payload_texto}",
            }
        ],
        "temperature": _temperatura(),
        "response_format": {"type": "json_object"},
    }
    for tentativa in range(max_retries + 1):
        try:
            resposta = requests.post(
                ENDPOINT_GROQ,
                headers=headers,
                json=corpo,
                timeout=timeout,
            )
            if resposta.status_code == 200:
                try:
                    dados = resposta.json()
                    return dados["choices"][0]["message"]["content"]
                except (KeyError, IndexError, ValueError) as erro:
                    raise ErroAnalise(f"Resposta inesperada do Groq ({modelo}): {erro}") from erro

            if resposta.status_code in (429, 503):
                if tentativa < max_retries:
                    espera = (2 ** tentativa) + 0.5
                    print(
                        f"[llm:groq] {modelo} respondeu {resposta.status_code}. "
                        f"Aguardando {espera:.1f}s (backoff #{tentativa + 1})...",
                        flush=True,
                    )
                    time.sleep(espera)
                    continue
                raise ErroAnalise(f"Groq {resposta.status_code}")

            raise ErroAnalise(f"Groq respondeu {resposta.status_code}: {resposta.text[:300]}")
        except requests.exceptions.Timeout:
            if tentativa < max_retries:
                espera = 2 ** tentativa
                print(f"[llm:groq] {modelo} timeout. Aguardando {espera}s...", flush=True)
                time.sleep(espera)
                continue
            raise
    raise ErroAnalise(f"Groq {modelo}: máximo de retries atingido")


def _tentar_groq(prompt_texto: str, payload_texto: str, timeout: int) -> str:
    """Tenta chamar o Groq percorrendo os modelos da sequência de fallback."""
    chave = _chave_groq()
    modelo_cfg = _modelo_groq()
    sequencia = [modelo_cfg] + [m for m in MODELOS_FALLBACK_GROQ if m != modelo_cfg]
    ultimo_erro = ""
    for modelo in sequencia:
        try:
            texto = _chamar_groq(modelo, prompt_texto, payload_texto, chave, timeout)
            if modelo != modelo_cfg:
                print(f"[llm:groq] usando modelo de fallback: {modelo}", flush=True)
            return texto
        except ErroAnalise as e:
            ultimo_erro = str(e)
            print(f"[llm:groq] {modelo} falhou ({ultimo_erro}), tentando próximo...", flush=True)
        except requests.exceptions.Timeout:
            ultimo_erro = f"Timeout em {modelo}"
            print(f"[llm:groq] {modelo} timeout, tentando próximo...", flush=True)
    raise ErroAnalise(f"Todos os modelos Groq falharam. Último erro: {ultimo_erro}")


def _tentar_gemini(corpo: dict, timeout: int) -> str:
    """Tenta chamar o Gemini percorrendo os modelos da sequência de fallback."""
    chave = _chave_gemini()
    modelo_cfg = _modelo_gemini()
    sequencia = [modelo_cfg] + [m for m in MODELOS_FALLBACK_GEMINI if m != modelo_cfg]
    ultimo_erro = ""
    for modelo in sequencia:
        try:
            texto = _chamar_gemini(modelo, corpo, chave, timeout)
            if modelo != modelo_cfg:
                print(f"[llm:gemini] usando modelo de fallback: {modelo}", flush=True)
            return texto
        except ErroAnalise as e:
            ultimo_erro = str(e)
            print(f"[llm:gemini] {modelo} falhou ({ultimo_erro}), tentando próximo...", flush=True)
        except requests.exceptions.Timeout:
            ultimo_erro = f"Timeout em {modelo}"
            print(f"[llm:gemini] {modelo} timeout, tentando próximo...", flush=True)
    raise ErroAnalise(f"Todos os modelos Gemini falharam. Último erro: {ultimo_erro}")


def analisar(interacoes: list, maximo: int | None = None, timeout: int = 60) -> list:
    """Envia as interações ao LLM e devolve as histórias no contrato do front.

    Estratégia configurável via LLM_STRATEGY em secrets.toml:
    - "groq_first"  (padrão): Groq como principal, Gemini como fallback.
      Ideal para análise complexa — maior throughput, sem rate-limits agressivos.
    - "gemini_first": Gemini como principal, Groq como fallback.
    """
    if not interacoes:
        raise ErroAnalise("Nenhuma interação para analisar.")

    if maximo is None:
        maximo = _maximo_historias()

    payload_lista = [
        {
            "autor": i.get("autor", ""),
            "canal": i.get("canal", ""),
            "tipo": i.get("tipo", "mensagem"),
            "texto": i.get("texto", ""),
        }
        for i in interacoes
    ]
    payload_texto = json.dumps(payload_lista, ensure_ascii=False)
    prompt_texto = PROMPT.format(maximo=maximo)

    # Corpo para Gemini (formato específico)
    corpo_gemini = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_texto},
                    {"text": payload_texto},
                ]
            }
        ],
        "generationConfig": {"responseMimeType": "application/json", "temperature": _temperatura()},
    }

    estrategia = _estrategia()
    texto_resposta: str = ""
    provedor_usado: str = ""

    if estrategia == "gemini_first":
        # Gemini principal → Groq fallback
        try:
            texto_resposta = _tentar_gemini(corpo_gemini, timeout)
            provedor_usado = "gemini"
        except ErroAnalise as e_gemini:
            print(f"[llm] Gemini falhou ({e_gemini}), tentando Groq...", flush=True)
            texto_resposta = _tentar_groq(prompt_texto, payload_texto, timeout)
            provedor_usado = "groq"
    else:
        # groq_first (padrão): Groq principal → Gemini fallback
        try:
            texto_resposta = _tentar_groq(prompt_texto, payload_texto, timeout)
            provedor_usado = "groq"
        except ErroAnalise as e_groq:
            print(f"[llm] Groq falhou ({e_groq}), tentando Gemini...", flush=True)
            texto_resposta = _tentar_gemini(corpo_gemini, timeout)
            provedor_usado = "gemini"

    global ULTIMO_PROVEDOR_USADO
    ULTIMO_PROVEDOR_USADO = provedor_usado

    if provedor_usado and provedor_usado != estrategia.split("_")[0]:
        print(f"[llm] usando provedor de fallback: {provedor_usado}", flush=True)

    try:
        conteudo = json.loads(texto_resposta)
    except json.JSONDecodeError as erro:
        raise ErroAnalise(f"O modelo não devolveu JSON válido: {erro}") from erro

    historias = conteudo.get("historias") if isinstance(conteudo, dict) else conteudo
    if not isinstance(historias, list):
        raise ErroAnalise("JSON do modelo sem a chave 'historias'.")

    return _normalizar(historias, interacoes)
