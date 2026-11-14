"""Análise de interações com provedor de LLM (Gemini).

Substitui o mock de `data_service.analisar()` por uma chamada real.

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

As chaves de `GEMINI_API_KEY`, `COHERE_API_KEY` e `GROQ_API_KEY` são lidas
pelo `LLMProvider` de `st.secrets` ou das variáveis de ambiente. Nunca ficam no código.
O prompt de análise é mantido em `prompt_analise.txt`, ao lado deste módulo.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from pathlib import Path

import requests

from src.preprocessing import anonimizar_texto, normalizar_texto

MODELO_PADRAO = "gemini-1.5-flash"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"

# Provedor que atendeu a última chamada bem-sucedida ("gemini" | "cohere" | "groq").
ULTIMO_PROVEDOR: str = ""

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

PROMPT = Path(__file__).with_name("prompt_analise.txt").read_text(encoding="utf-8")


class ErroAnalise(RuntimeError):
    """Falha controlada na análise por LLM."""

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
    for posicao, item in enumerate(interacoes, start=1):
        # O id vem do lote quando existir; senao, usa a posicao para referencia.
        item = dict(item)
        id_lote = item.get("id")
        item["_id"] = id_lote if isinstance(id_lote, int) and id_lote >= 1 else posicao
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
        id_interacao = int(base.get("_id") or 0) if base else 0

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
        pass
    if ULTIMAS_AMBIGUIDADES:
        pass
    return saida


def analisar(interacoes: list, maximo: int = MAXIMO_HISTORIAS, timeout: int = 60) -> list:
    """Envia as interações ao LLMProvider (com fallback automático) e devolve as histórias no contrato do front."""
    global ULTIMO_PROVEDOR
    if not interacoes:
        raise ErroAnalise("Nenhuma interação para analisar.")

    interacoes_preparadas = []
    for interacao in interacoes:
        preparada = dict(interacao)
        texto = normalizar_texto(str(preparada.get("texto") or ""))
        preparada["texto"], _ = anonimizar_texto(texto)
        interacoes_preparadas.append(preparada)

    payload = []
    for posicao, interacao in enumerate(interacoes_preparadas, start=1):
        id_interacao = interacao.get("id")
        if not isinstance(id_interacao, int) or isinstance(id_interacao, bool) or id_interacao < 1:
            id_interacao = interacao.get("_id_efetivo")
        if not isinstance(id_interacao, int) or isinstance(id_interacao, bool) or id_interacao < 1:
            id_interacao = posicao
        payload.append(
            {
                "id": id_interacao,
                "autor": interacao.get("autor", ""),
                "canal": interacao.get("canal", ""),
                "tipo": interacao.get("tipo", "mensagem"),
                "texto": interacao["texto"],
            }
        )

    from services.llm_provider import LLMProvider, ErroProvedor
    # Instancia o provedor (ele já lê as chaves e gerencia a ordem e falhas)
    provider = LLMProvider(timeout=timeout)

    try:
        # O prompt do sistema e o payload dos dados
        prompt_texto = PROMPT.format(maximo=maximo)
        resultado = provider.gerar(
            prompt_texto,
            json.dumps(payload, ensure_ascii=False),
        )

        texto = resultado.texto

    except ErroProvedor as e:
        raise ErroAnalise(f"Falha em todos os provedores de LLM: {e}") from e
    except Exception as erro:
        raise ErroAnalise(f"Erro inesperado na chamada do LLM: {erro}") from erro

    # Desserializa e valida o JSON retornado.
    try:
        conteudo = json.loads(texto)
    except json.JSONDecodeError:
        # Tenta retirar apenas blocos Markdown; não tenta inventar/corrigir dados.
        texto_limpo = texto.replace("```json", "").replace("```", "").strip()
        try:
            conteudo = json.loads(texto_limpo)
        except json.JSONDecodeError as erro:
            finish_reason = resultado.finish_reason or "não informado"
            diagnostico_limite = ""
            if str(finish_reason).upper() == "MAX_TOKENS":
                diagnostico_limite = (
                    "A resposta foi truncada pelo limite de saída; aumente "
                    "LLM_MAX_OUTPUT_TOKENS. "
                )
            raise ErroAnalise(
                "JSON inválido do LLM: "
                f"provedor={resultado.provedor}; modelo={resultado.modelo}; "
                f"finish_reason={finish_reason}; {diagnostico_limite}"
                f"resposta_chars={len(texto)}; "
                f"parser_chars={len(texto_limpo)}; linha={erro.lineno}; "
                f"coluna={erro.colno}; posição={erro.pos}. "
                "O conteúdo da resposta não foi registrado por segurança."
            ) from erro

    historias = conteudo.get("historias") if isinstance(conteudo, dict) else conteudo
    if not isinstance(historias, list):
        raise ErroAnalise("JSON do modelo sem a chave 'historias'.")

    ULTIMO_PROVEDOR = resultado.provedor
    return _normalizar(historias, interacoes_preparadas)
