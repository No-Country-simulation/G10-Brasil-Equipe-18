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
    "git", "fastapi", "react", "node", "javascript", "typescript", "html", "css"
}

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
            if ent.label_ == "PER":
                txt_limpo = ent.text.strip()
                # Preserva menções já pseudonimizadas
                if txt_limpo.startswith("@membro_") or txt_limpo.startswith("membro_"):
                    continue
                # Preserva termos técnicos
                if txt_limpo.lower() in EXCECOES_TECNICAS:
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
        locais_conhecidos = {
            "são", "paulo", "rio", "janeiro", "brasil", "brasilia", "brasília", 
            "salvador", "curitiba", "belo", "horizonte", "recife", "fortaleza", "porto", "alegre"
        }
        palavras = texto_anonimo.split()
        palavras_anonimizadas = []
        for i, palavra in enumerate(palavras):
            palavra_limpa = re.sub(r'[^\w@]', '', palavra)
            if palavra_limpa.startswith("@membro_") or palavra_limpa.startswith("membro_"):
                palavras_anonimizadas.append(palavra)
                continue
            if palavra_limpa.lower() in locais_conhecidos:
                palavras_anonimizadas.append(palavra)
                continue
            palavra_anterior = re.sub(r'[^\w]', '', palavras[i-1].lower()) if i > 0 else ""
            if palavra_anterior == "em" and (palavra_limpa.lower() in locais_conhecidos or (i + 1 < len(palavras) and re.sub(r'[^\w]', '', palavras[i+1].lower()) in locais_conhecidos)):
                palavras_anonimizadas.append(palavra)
                continue
            if (
                i > 0 
                and palavra_limpa 
                and palavra_limpa[0].isupper() 
                and not (palavra_limpa.lower() == "foi" and palavras[i - 1].endswith((".", "!", "?")))
                and palavra_limpa.lower() not in EXCECOES_TECNICAS
                and not palavra_limpa.isupper()
            ):
                palavra_substituida = palavra.replace(palavra_limpa, '[NOME]')
                palavras_anonimizadas.append(palavra_substituida)
                contagem["nome"] += 1
            else:
                palavras_anonimizadas.append(palavra)
        texto_anonimo = " ".join(palavras_anonimizadas)

    return texto_anonimo, contagem