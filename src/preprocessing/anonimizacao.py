"""Módulo de anonimização de dados pessoais no texto.

Responsável por mascarar e-mails, telefones, CPFs e nomes próprios utilizando 
uma abordagem de melhor esforço, preservando termos técnicos e menções já pseudonimizadas.
"""
import re
from typing import Tuple, Dict

# Lista de exceções conhecidas (termos técnicos e de produtos que não devem virar [NOME])
EXCECOES_TECNICAS = {
    "python", "oracle", "streamlit", "github", "discord", "slack",
    "sql", "langgraph", "pandas", "pytest", "pydantic", "json", "csv",
    "alura", "docker", "kubernetes", "linux", "aws", "gcp", "azure",
    "git", "fastapi", "react", "node", "javascript", "typescript", "html", "css",
    "api", "apis", "power bi", "oracle cloud", "github actions",
}

# Locais comuns preservados tanto no NER quanto no fallback.
LOCAIS_CONHECIDOS = {
    "são paulo", "sao paulo", "rio de janeiro", "brasil", "brasília", "brasilia",
    "salvador", "curitiba", "belo horizonte", "recife", "fortaleza", "porto alegre",
    "são", "paulo", "rio", "janeiro", "belo", "horizonte", "porto", "alegre",
}

# No caminho do spaCy (NER) preserva apenas locais de mais de uma palavra.
# Palavras soltas (ex.: "paulo", "rio") ficam apenas no fallback, que compara
# palavra por palavra e precisa delas para evitar falsos positivos.
LOCAIS_CONHECIDOS_MULTIPALAVRA = frozenset(
    local for local in LOCAIS_CONHECIDOS if " " in local
)

# Preposições e locuções que introduzem um nome de pessoa imediatamente à frente.
# "a" sozinho fica de fora porque costuma preceder lugares ("fui a Paris").
# "à" (a + a) e "com a/o" são padrões frequentes no português do Brasil.
_CONTEXTO_PESSOA = re.compile(
    r"\b("
    r"com|à|pela|pelo|e a|e o|junto com|junto da|junto do"
    r")(\s+(?:a|o))?\s*$"
)
_CONTEXTO_PESSOA_APOS = re.compile(
    r"^\s*(?:(?:me|nos|a gente|o time|a equipe)\s+)?"
    r"(?:ajudou|ajudaram|orientou|orientaram|ensinou|ensinaram|"
    r"indicou|indicaram|revisou|revisaram|apoiou|apoiaram|"
    r"acompanhou|acompanharam|mentora|mentorou|recomendou|"
    r"convidou|chamou|participou|contribuiu)\b",
    re.IGNORECASE,
)
_PARTICULAS_NOME = frozenset({"da", "das", "de", "do", "dos", "e"})

# Formas frequentes que o modelo pode rotular como PROPN antes de uma tecnologia.
VERBOS_ESTUDO = {
    "estudei", "estudamos", "estudava", "estudar", "estudando",
    "aprendi", "aprendemos", "aprendeu", "aprender", "aprendendo",
    "usei", "usamos", "utilizei", "utilizamos", "trabalhei", "trabalhamos",
}


def _normalizar_texto(texto: str) -> str:
    return re.sub(r"\s+", " ", texto.strip().lower())


def _eh_local_conhecido(texto: str) -> bool:
    """Indica se uma entidade corresponde a um local conhecido."""
    return _normalizar_texto(texto) in LOCAIS_CONHECIDOS


def _eh_local_conhecido_multipalavra(texto: str) -> bool:
    """Indica se uma entidade corresponde a um local conhecido de mais de uma palavra."""
    return _normalizar_texto(texto) in LOCAIS_CONHECIDOS_MULTIPALAVRA


def _loc_em_contexto_de_pessoa(texto: str, ent) -> bool:
    """Aceita LOC como pessoa quando o contexto imediato indica companhia."""
    if _eh_local_conhecido_multipalavra(ent.text):
        return False
    prefixo = texto[:ent.start_char].lower()
    return bool(_CONTEXTO_PESSOA.search(prefixo))


def _eh_termo_tecnico_em_contexto_de_estudo(texto: str) -> bool:
    """Evita mascarar uma atividade de estudo que o NER tomou por entidade."""
    palavras = re.findall(r"[^\W\d_]+", texto.lower(), flags=re.UNICODE)
    if len(palavras) < 2 or palavras[0] not in VERBOS_ESTUDO:
        return False
    restante = texto.lower()[len(palavras[0]):]
    return any(
        re.search(rf"(?<!\w){re.escape(termo)}(?!\w)", restante)
        for termo in EXCECOES_TECNICAS
    )


def _eh_inicio_de_frase(palavras: list[str], indice: int) -> bool:
    """Detecta palavras após ponto, exclamação ou interrogação."""
    if indice == 0:
        return True
    anterior = palavras[indice - 1].rstrip("\"'”’»)]}")
    return anterior.endswith((".", "!", "?"))


def _validar_cpf_digitos(digitos: str) -> bool:
    """Valida se uma sequência de 11 dígitos possui dígitos verificadores válidos de CPF."""
    if len(digitos) != 11 or not digitos.isdigit() or len(set(digitos)) == 1:
        return False
    soma = sum(int(digitos[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(digitos[9]):
        return False
    soma = sum(int(digitos[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    return resto == int(digitos[10])

_NLP = None

def _obter_nlp():
    """Carrega o modelo spaCy de português com cache singleton."""
    global _NLP
    if _NLP is None:
        try:
            import spacy
            try:
                _NLP = spacy.load("pt_core_news_sm")
            except OSError:
                import spacy.cli
                spacy.cli.download("pt_core_news_sm")
                _NLP = spacy.load("pt_core_news_sm")
        except Exception:
            _NLP = None
    return _NLP

def anonimizar_texto(texto: str) -> Tuple[str, Dict[str, int]]:
    """Mascara dados pessoais no texto e retorna o texto anonimizado 
    junto com a contagem de elementos mascarados por tipo.
    """
    if not texto:
        return "", {"email": 0, "telefone": 0, "cpf": 0, "nome": 0}

    contagem = {
        "email": 0,
        "telefone": 0,
        "cpf": 0,
        "nome": 0
    }

    texto_anonimo = texto

    # 1. Mascarar E-mails
    padrao_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    texto_anonimo, count = re.subn(padrao_email, '[EMAIL]', texto_anonimo)
    contagem["email"] += count

    # 2. Mascarar CPFs: formato tradicional (000.000.000-00) ou 11 dígitos verificados
    padrao_cpf_formatado = r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'
    texto_anonimo, count_formatados = re.subn(padrao_cpf_formatado, '[CPF]', texto_anonimo)
    contagem["cpf"] += count_formatados

    def _substituir_cpf_numerico(match):
        d = match.group(0)
        if _validar_cpf_digitos(d) or d == "00000000000":
            contagem["cpf"] += 1
            return '[CPF]'
        return d

    texto_anonimo = re.sub(r'\b\d{11}\b', _substituir_cpf_numerico, texto_anonimo)

    # 3. Mascarar Telefones brasileiros com DDD obrigatório (ex: (11) 98888-8888, 11 988888888, +55 11 98888-8888)
    padrao_telefone = r'(?<!\w)(?:\+?55\s?)?(?:\([1-9]{2}\)\s*|[1-9]{2}\s+)(?:9[0-9]{4}[-\s]?[0-9]{4}|[2-8][0-9]{3}[-\s]?[0-9]{4})(?!\w)'
    texto_anonimo, count = re.subn(padrao_telefone, '[TELEFONE]', texto_anonimo)
    contagem["telefone"] += count

    # 4. Mascarar Nomes próprios via NER (spaCy)
    nlp = _obter_nlp()
    if nlp is not None:
        doc = nlp(texto_anonimo)
        spans_per = []
        for ent in doc.ents:
            if ent.label_ != "PER" and not (
                ent.label_ == "LOC" and _loc_em_contexto_de_pessoa(texto_anonimo, ent)
            ):
                continue
            txt_limpo = ent.text.strip()
            txt_lower = txt_limpo.lower()
            # Preserva menções já pseudonimizadas.
            if txt_lower.startswith("@membro_") or txt_lower.startswith("membro_"):
                continue
            # Só entidades com núcleo nominal próprio são tratadas como nomes.
            if ent.root.pos_ != "PROPN":
                continue
            # Preserva termos técnicos conhecidos, sem inferir siglas por caixa alta.
            if txt_lower in EXCECOES_TECNICAS or _eh_local_conhecido_multipalavra(txt_limpo):
                continue
            tokens_lower = re.findall(r"[^\W\d_]+", txt_lower, flags=re.UNICODE)
            if tokens_lower and all(token in EXCECOES_TECNICAS for token in tokens_lower):
                continue
            if _eh_termo_tecnico_em_contexto_de_estudo(txt_limpo):
                continue
            if len(txt_limpo) < 2:
                continue
            spans_per.append((ent.start_char, ent.end_char))

        # Substitui da direita para a esquerda para não invalidar índices de caracteres
        spans_per.sort(key=lambda s: s[0], reverse=True)
        chars = list(texto_anonimo)
        for start, end in spans_per:
            chars[start:end] = list("[NOME]")
            contagem["nome"] += 1
        texto_anonimo = "".join(chars)
    else:
        # Fallback de melhor esforço caso o modelo spaCy não esteja disponível
        palavras = texto_anonimo.split()
        palavras_anonimizadas = []
        i = 0
        while i < len(palavras):
            palavra = palavras[i]
            palavra_limpa = re.sub(r"^[^\w@]+|[^\w@]+$", "", palavra)
            palavra_lower = palavra_limpa.lower()
            if (
                not palavra_limpa
                or palavra_lower.startswith("@membro_")
                or palavra_lower.startswith("membro_")
                or re.fullmatch(r"\[[A-Z_]+\][.,;:!?]*", palavra) is not None
            ):
                palavras_anonimizadas.append(palavra)
                i += 1
                continue

            if (
                palavra_lower == "power"
                and i + 1 < len(palavras)
                and re.sub(r"[^\w@]", "", palavras[i + 1]).lower()
                == "bi"
            ):
                palavras_anonimizadas.extend(palavras[i:i + 2])
                i += 2
                continue

            prefixo = " ".join(palavras[:i]).lower()
            contexto_anterior = bool(_CONTEXTO_PESSOA.search(prefixo))
            inicio_frase = _eh_inicio_de_frase(palavras, i)
            e_capitalizada = (
                palavra_limpa[0].isupper()
                and (not palavra_limpa.isupper() or contexto_anterior)
            )
            if not e_capitalizada:
                palavras_anonimizadas.append(palavra)
                i += 1
                continue

            # Agrupa nomes compostos, inclusive partículas como "da" e "de".
            fim = i + 1
            componentes = [palavra_limpa]
            while fim < len(palavras):
                if re.search(r"[.,!?;:]$", palavras[fim - 1]):
                    break
                proxima = re.sub(r"^[^\w@]+|[^\w@]+$", "", palavras[fim])
                proxima_lower = proxima.lower()
                if proxima_lower in _PARTICULAS_NOME:
                    if fim + 1 >= len(palavras):
                        break
                    seguinte = re.sub(
                        r"^[^\w@]+|[^\w@]+$", "", palavras[fim + 1]
                    )
                    proxima_continuacao = (
                        re.sub(r"[^\w@]", "", palavras[fim + 2]).lower()
                        if fim + 2 < len(palavras)
                        else ""
                    )
                    if (
                        proxima_lower == "e"
                        and (
                            seguinte.lower() in EXCECOES_TECNICAS
                            or f"{seguinte.lower()} {proxima_continuacao}"
                            in EXCECOES_TECNICAS
                        )
                    ):
                        break
                    if (
                        not seguinte
                        or not seguinte[0].isupper()
                        or (seguinte.isupper() and not contexto_anterior)
                    ):
                        break
                    componentes.extend((proxima, seguinte))
                    fim += 2
                    continue
                if (
                    proxima
                    and proxima[0].isupper()
                    and (
                        not proxima.isupper()
                        or proxima_lower in EXCECOES_TECNICAS
                        or contexto_anterior
                    )
                ):
                    componentes.append(proxima)
                    fim += 1
                    continue
                break

            nome = " ".join(componentes)
            componentes_nome = [
                componente.lower()
                for componente in componentes
                if componente.lower() not in _PARTICULAS_NOME
            ]
            nome_composto = len(componentes_nome) > 1
            contexto_depois = (
                inicio_frase
                and _CONTEXTO_PESSOA_APOS.match(" ".join(palavras[fim:])) is not None
            )
            local_conhecido = _eh_local_conhecido(nome)
            local_como_nome = (
                len(componentes_nome) == 1
                and local_conhecido
                and (contexto_anterior or contexto_depois)
            )
            termo_tecnico = (
                nome.lower() in EXCECOES_TECNICAS
                or all(
                    componente in EXCECOES_TECNICAS
                    for componente in componentes_nome
                )
            )
            deve_mascarar = (
                contexto_anterior
                or contexto_depois
                or (not inicio_frase and e_capitalizada)
                or (inicio_frase and nome_composto)
            )

            if (
                (local_conhecido and not local_como_nome)
                or termo_tecnico
                or not deve_mascarar
            ):
                palavras_anonimizadas.extend(palavras[i:fim])
                i = fim
                continue

            prefixo_token = palavra[:palavra.find(palavra_limpa)]
            ultima_palavra = palavras[fim - 1]
            ultima_limpa = re.sub(r"^[^\w@]+|[^\w@]+$", "", ultima_palavra)
            sufixo_token = ultima_palavra[
                ultima_palavra.rfind(ultima_limpa) + len(ultima_limpa):
            ]
            palavras_anonimizadas.append(f"{prefixo_token}[NOME]{sufixo_token}")
            contagem["nome"] += 1
            i = fim
        texto_anonimo = " ".join(palavras_anonimizadas)

    return texto_anonimo, contagem
