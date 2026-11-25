"""Card 14: cases extrativos, rastreados à única interação da história.

Não valida a veracidade do relato. A escolha editorial do LLM continua sujeita
à curadoria; a verificação impede inserir texto que não está na fonte.
"""
import re


def dividir_paragrafos(texto):
    """Parágrafos separados por linha em branco, sem espaços nas pontas."""
    return [p.strip() for p in re.split(r"\n\s*\n", texto.strip()) if p.strip()]


def paragrafos_literais_em_ordem(paragrafos, fonte):
    """True se cada parágrafo aparece literalmente na fonte, na ordem."""
    posicao = 0
    for paragrafo in paragrafos:
        inicio = fonte.find(paragrafo, posicao)
        if inicio < 0:
            return False
        posicao = inicio + len(paragrafo)
    return True


def preparar_case(ativo, fonte, resultados, citacoes, id_interacao):
    """Retorna (ativo do front, motivo). Não infere sucesso de termos-chave."""
    campos = ativo.get("campos")
    if not isinstance(campos, dict):
        return None, "Campos do case inválidos."
    texto = campos.get("texto")
    if not isinstance(texto, str) or not texto.strip():
        return None, "Case sem narrativa."
    # Parágrafos completos devem ser recortes exatos, na ordem da fonte.
    paragrafos = dividir_paragrafos(texto)
    if len(texto) > 6000:
        return None, "Case excede 6000 caracteres."
    if not paragrafos_literais_em_ordem(paragrafos, fonte):
        return None, "Narrativa não é uma sequência de trechos literais da fonte."
    resultados_validos = [r.strip() for r in resultados if isinstance(r, str) and r.strip() and r.strip() in fonte]
    narrativa = "\n\n".join(paragrafos)
    if not any(r in narrativa for r in resultados_validos):
        return None, "Sem resultado ou avanço literal na narrativa; revisão necessária."
    citacoes_validas = [dict(c) for c in citacoes if c.get("id_interacao") == id_interacao and c.get("texto") in narrativa]
    if not citacoes_validas:
        return None, "Case sem citação conferida na narrativa."
    # Título é metadado opcional (Card 05) e não decide o ativo: fora da fonte
    # ou acima de 200 caracteres, é descartado. Narrativa, resultado e citação
    # já foram conferidos acima, então o case permanece sem título.
    titulo = campos.get("titulo", "")
    titulo = titulo.strip() if isinstance(titulo, str) else ""
    if len(titulo) > 200 or (titulo and titulo not in fonte):
        titulo = ""
    return {
        "id": "case_sucesso", "nome": "Case de sucesso", "tipo": "texto",
        "campos": {"texto": narrativa},
        **({"titulo": titulo} if titulo else {}),
        "interacoes_origem": [id_interacao], "citacoes": citacoes_validas,
        "fontes": [{"afirmacao": c["texto"], "fato": "Trecho literal da interação de origem", "trecho": c["texto"]} for c in citacoes_validas],
    }, ""
