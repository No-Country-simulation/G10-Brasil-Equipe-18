"""Card 13: testemunho extrativo e projeção canônica de rascunho."""
import re


def preparar_testemunho(ativo, fonte, citacoes, id_interacao):
    """Confere os três campos na fonte; não atribui decisão humana ao LLM."""
    campos = ativo.get("campos")
    if not isinstance(campos, dict):
        return None, "Campos do testemunho inválidos."
    limites = {"titulo": 200, "descricao": 2000, "citacao": 500}
    limpos = {}
    for nome, limite in limites.items():
        valor = campos.get(nome)
        if not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > limite:
            return None, f"Testemunho com {nome} ausente ou inválido."
        valor = valor.strip()
        if valor not in fonte:
            return None, f"{nome} do testemunho não corresponde a trecho literal da fonte."
        limpos[nome] = valor
    if not any(c.get("id_interacao") == id_interacao and c.get("texto") == limpos["citacao"] for c in citacoes):
        return None, "Citação do testemunho não corresponde às evidências conferidas da história."
    return {
        "id": "testemunho_estruturado", "nome": "Testemunho estruturado",
        "tipo": "testemunho", "campos": limpos,
        "interacoes_origem": [id_interacao],
        "citacoes": [{"texto": limpos["citacao"], "id_interacao": id_interacao}],
        "fontes": [{"afirmacao": limpos["descricao"], "fato": "Descrição extraída da interação de origem", "trecho": limpos["descricao"]}],
    }, ""


def converter_testemunho_canonico(ativo, id_ativo, criado_em):
    """Projeção inicial do rascunho; não exporta decisões da Curadoria.

    A aplicação chamadora atribui ID único no lote e instante real de criação.
    A composição não tenta desfazer a narrativa para reconstruir campos.
    """
    from datetime import datetime
    if ativo.get("id") != "testemunho_estruturado" or ativo.get("tipo") != "testemunho":
        raise ValueError("Ativo não é um testemunho estruturado do front.")
    if not isinstance(id_ativo, str) or not re.fullmatch(r"ativo_[0-9]{3,}", id_ativo):
        raise ValueError("ID canônico inválido.")
    momento = datetime.fromisoformat(criado_em.replace("Z", "+00:00"))
    if momento.tzinfo is None:
        raise ValueError("Instante de criação exige fuso horário.")
    campos = ativo["campos"]
    for nome in ("titulo", "descricao", "citacao"):
        if not isinstance(campos.get(nome), str) or not campos[nome].strip():
            raise ValueError("Campos estruturados incompletos.")
    ids = ativo.get("interacoes_origem")
    if not isinstance(ids, list) or not ids or any(type(i) is not int or i < 1 for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("Interações de origem inválidas.")
    return {
        "versao_schema": "1.0", "id_ativo": id_ativo,
        "tipo": "testemunho_estruturado", "titulo": campos["titulo"],
        "texto": campos["descricao"] + '\n\n"' + campos["citacao"] + '"',
        "interacoes_origem": list(ids), "status_revisao": "pendente",
        "criado_em": criado_em,
    }
