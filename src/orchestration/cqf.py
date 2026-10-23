"""Motor de regras, cálculo e governança editorial do CommunityLab Quality Framework (CQF v1.0).

Implementa a matriz ponderada de pontuação e as três regras fundamentais de governança:
- RG-01: Integridade das evidências (não inventar fatos, citações literais verificadas).
- RG-02: Consistência factual (contradições não resolvidas bloqueiam a aprovação).
- RG-03: Trava de publicação (autorização independente do CQF Score e da aprovação editorial).
"""
from typing import Dict, Any, List, Tuple, Optional, Union, Sequence
from ..modelos import HistoriaDetectada, Interacao, AvaliacaoCQF


PESOS_CQF = {
    "relevancia": 0.25,
    "completude": 0.25,
    "clareza_impacto": 0.20,
    "evidencias": 0.30,
}


def calcular_cqf_score(
    relevancia: float,
    completude: float,
    clareza_impacto: float,
    evidencias: float,
) -> Dict[str, Any]:
    """Calcula o CQF Score e determina a prioridade editorial.

    Fórmula oficial:
        CQF Score = (R * 0.25 + C * 0.25 + I * 0.20 + E * 0.30) * 20

    Faixas:
        - 80 a 100: alta_prioridade
        - 60 a 79: prioridade_media
        - 0 a 59: baixa_prioridade
    """
    notas = {
        "relevancia": float(relevancia),
        "completude": float(completude),
        "clareza_impacto": float(clareza_impacto),
        "evidencias": float(evidencias),
    }

    for criterio, valor in notas.items():
        if not (0.0 <= valor <= 5.0):
            raise ValueError(f"Nota para '{criterio}' deve estar entre 0.0 e 5.0. Recebido: {valor}")

    soma_ponderada = (
        notas["relevancia"] * PESOS_CQF["relevancia"]
        + notas["completude"] * PESOS_CQF["completude"]
        + notas["clareza_impacto"] * PESOS_CQF["clareza_impacto"]
        + notas["evidencias"] * PESOS_CQF["evidencias"]
    )

    score_bruto = soma_ponderada * 20.0
    # Arredonda para 1 casa decimal ou número inteiro exato se for inteiro
    score = round(score_bruto, 1)
    if score.is_integer():
        score = float(int(score))

    if score >= 80.0:
        classificacao = "alta_prioridade"
    elif score >= 60.0:
        classificacao = "prioridade_media"
    else:
        classificacao = "baixa_prioridade"

    return {
        "cqf_score": score,
        "classificacao_editorial": classificacao,
        "pesos_aplicados": PESOS_CQF.copy(),
        "notas_entrada": notas,
    }


def validar_integridade_evidencias(
    historia: Union[HistoriaDetectada, Dict[str, Any]],
    interacoes: Sequence[Union[Interacao, Dict[str, Any]]],
) -> Tuple[bool, List[str]]:
    """Regra RG-01: Integridade das Evidências.

    Verifica se todas as citações literais atribuídas à história existem
    efetivamente dentro do texto da interação de origem informada.
    """
    erros = []

    # Normalização de história
    if isinstance(historia, HistoriaDetectada):
        citacoes = [c.model_dump() for c in historia.citacoes]
        interacoes_origem = historia.interacoes_origem
    else:
        citacoes = historia.get("citacoes", [])
        interacoes_origem = historia.get("interacoes_origem", [])

    # Indexar interações por ID (suporta int, str e prefixo int_XXX)
    mapa_interacoes: Dict[Any, str] = {}
    for item in interacoes:
        if isinstance(item, Interacao):
            iid = item.id
            txt = item.texto
        elif isinstance(item, dict):
            iid = item.get("id")
            txt = item.get("texto", "")
        else:
            continue
        if iid is not None:
            mapa_interacoes[iid] = txt
            mapa_interacoes[str(iid)] = txt
            if isinstance(iid, int):
                mapa_interacoes[f"int_{iid:03d}"] = txt
            elif isinstance(iid, str) and iid.startswith("int_") and iid[4:].isdigit():
                try:
                    mapa_interacoes[int(iid[4:])] = txt
                except ValueError:
                    pass

    if not citacoes:
        erros.append("A história não possui nenhuma citação para sustentação factual.")

    # Constrói conjunto de origens com variações int/str para comparação robusta
    origens_equivalentes = set()
    for o in interacoes_origem:
        origens_equivalentes.add(o)
        origens_equivalentes.add(str(o))
        if isinstance(o, int):
            origens_equivalentes.add(f"int_{o:03d}")
        elif isinstance(o, str) and o.startswith("int_") and o[4:].isdigit():
            try:
                origens_equivalentes.add(int(o[4:]))
            except ValueError:
                pass

    for idx, cit in enumerate(citacoes, 1):
        id_interacao = cit.get("id_interacao")
        texto_citacao = cit.get("texto", "").strip()

        if id_interacao is None or id_interacao not in mapa_interacoes:
            erros.append(
                f"Citação #{idx} refere-se à interação ID {id_interacao}, inexistente no conjunto de origem."
            )
            continue

        if id_interacao not in origens_equivalentes:
            erros.append(
                f"Interação ID {id_interacao} citada não consta na lista de interacoes_origem da história."
            )

        texto_original = mapa_interacoes[id_interacao]
        # Normalização de espaços para correspondência resiliente a espaçamento e quebras de linha
        citacao_normalizada = " ".join(texto_citacao.split())
        original_normalizado = " ".join(texto_original.split())
        if citacao_normalizada not in original_normalizado:
            # Tenta removendo reticências (... / …), aspas e pontuações periféricas adicionadas pelo LLM
            citacao_limpa = citacao_normalizada.strip(' .…"\',;:!-')
            if not citacao_limpa or citacao_limpa not in original_normalizado:
                erros.append(
                    f"RG-01 Violação: Citação #{idx} ('{texto_citacao[:40]}...') não foi encontrada textualmente na interação ID {id_interacao}."
                )

    return len(erros) == 0, erros


def avaliar_aprovacao_editorial(
    status_validacao_factual: str,
    status_curadoria: str,
) -> Tuple[bool, str]:
    """Regra RG-02: Consistência Factual.

    Contradições relevantes não resolvidas bloqueiam a aprovação editorial,
    independentemente do CQF Score ou da intenção do revisor.
    """
    if status_validacao_factual == "contradicao_detectada":
        if status_curadoria == "aprovado":
            return False, "Bloqueio RG-02: Conteúdo com contradição factual detectada não pode ser aprovado."
        return False, "Contradição factual detectada: aguardando resolução ou esclarecimento."

    if status_validacao_factual == "evidencias_insuficientes":
        if status_curadoria == "aprovado":
            return False, "Bloqueio RG-01: Evidências insuficientes impedem a aprovação direta."
        return True, "Necessidade de complementação ou solicitação de informações adicionais."

    return True, "Conformidade factual validada."


def validar_liberacao_publicacao(
    status_curadoria: str,
    status_autorizacao: str,
    cqf_score: Optional[float] = None,
) -> Tuple[bool, str]:
    """Regra RG-03: Trava de Autorização para Publicação.

    A autorização é um controle estritamente independente do CQF Score e da aprovação editorial.
    Uma história aprovada (mesmo com score alto como 94) não pode ser publicada
    sem registro explícito de autorização de divulgação.
    """
    if status_autorizacao not in ("autorizada", "nao_aplicavel"):
        return (
            False,
            f"Bloqueio RG-03: Publicação bloqueada. Autorização de divulgação está '{status_autorizacao}'."
        )

    if status_curadoria != "aprovado":
        return (
            False,
            f"Publicação bloqueada. O conteúdo ainda não foi aprovado na curadoria (status: '{status_curadoria}')."
        )

    return True, "Liberado para publicação."


def consolidar_decisao_governança(
    cqf_score: float,
    status_validacao_factual: str,
    status_curadoria: str,
    status_autorizacao: str,
) -> str:
    """Determina a decisão editorial final combinando as regras RG-01, RG-02 e RG-03."""
    if status_validacao_factual == "contradicao_detectada":
        return "bloqueado_contradicao"

    if status_validacao_factual == "evidencias_insuficientes" or status_curadoria == "solicitar_ajustes":
        return "solicitar_informacoes"

    if status_curadoria == "rejeitado":
        return "rejeitado"

    if status_curadoria == "aprovado":
        if status_autorizacao not in ("autorizada", "nao_aplicavel"):
            return "bloqueado_sem_autorizacao"
        return "aprovado"

    return "solicitar_informacoes"
