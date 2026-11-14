"""Provedor de LLM com fallback automático entre Gemini, Cohere e Groq.

Uso em llm.py:
    from services.llm_provider import LLMProvider
    provider = LLMProvider()
    resposta = provider.gerar(prompt, payload_json)

Ordem de tentativa: Gemini → Cohere → Groq.
Chaves lidas de st.secrets ou variáveis de ambiente. Nunca no código.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field

import requests

logger = logging.getLogger(__name__)

# ---------- Configurações padrão ----------
GEMINI_MODELO_PADRAO = "gemini-3.6-flash"
COHERE_MODELO_PADRAO = "command-r-plus"
GROQ_MODELO_PADRAO = "llama-3.1-8b-instant" #"qwen/qwen3.8-27b"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
COHERE_ENDPOINT = "https://api.cohere.com/v2/chat"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
MAX_TOKENS_PADRAO = 8192
TIMEOUT_PADRAO = 60


class ErroProvedor(RuntimeError):
    """Falha em todos os provedores disponíveis."""


@dataclass
class RespostaProvedor:
    texto: str
    finish_reason: str = ""


@dataclass
class ResultadoLLM:
    texto: str
    provedor: str          # "gemini" | "cohere" | "groq"
    modelo: str
    fallback_usado: bool = False
    erro_primario: str = ""
    finish_reason: str = ""


# ---------- Helpers de configuração ----------

def _secrets() -> dict:
    try:
        import streamlit as st
        return dict(st.secrets)
    except Exception:
        return {}


def _cfg(chave: str, padrao: str = "") -> str:
    s = _secrets()
    return str(s.get(chave) or os.environ.get(chave) or padrao).strip()


def _max_tokens_configurado() -> int:
    valor = _cfg("LLM_MAX_OUTPUT_TOKENS", str(MAX_TOKENS_PADRAO))
    try:
        limite = int(valor)
    except (TypeError, ValueError):
        return MAX_TOKENS_PADRAO
    return limite if limite > 0 else MAX_TOKENS_PADRAO


# ---------- Adaptadores ----------

def _chamar_gemini(
    prompt: str,
    payload: str,
    modelo: str,
    max_tokens: int,
    timeout: int,
) -> RespostaProvedor:
    chave = _cfg("GEMINI_API_KEY")
    if not chave:
        raise ErroProvedor("GEMINI_API_KEY não configurada.")
    corpo = {
        "contents": [{"parts": [{"text": prompt}, {"text": payload}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.4,
            "maxOutputTokens": max_tokens,
        },
    }
    resposta = requests.post(
        GEMINI_ENDPOINT.format(modelo=modelo),
        params={"key": chave},
        json=corpo,
        timeout=timeout,
    )
    if resposta.status_code != 200:
        raise ErroProvedor(f"Gemini {resposta.status_code}: {resposta.text[:200]}")
    try:
        dados = resposta.json()
        candidato = dados["candidates"][0]
        partes = candidato["content"]["parts"]
        texto = "".join(str(parte.get("text", "")) for parte in partes)
        return RespostaProvedor(
            texto=texto,
            finish_reason=str(candidato.get("finishReason") or ""),
        )
    except (KeyError, IndexError, TypeError) as e:
        raise ErroProvedor(f"Resposta inesperada do Gemini: {e}") from e


def _chamar_groq(
    prompt: str,
    payload: str,
    modelo: str,
    max_tokens: int,
    timeout: int,
) -> RespostaProvedor:
    chave = _cfg("GROQ_API_KEY")
    if not chave:
        raise ErroProvedor("GROQ_API_KEY não configurada.")
    corpo = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": payload},
        ],
        "temperature": 0.4,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    resposta = requests.post(
        GROQ_ENDPOINT,
        headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"},
        json=corpo,
        timeout=timeout,
    )
    if resposta.status_code != 200:
        raise ErroProvedor(f"Groq {resposta.status_code}: {resposta.text[:200]}")
    try:
        dados = resposta.json()
        escolha = dados["choices"][0]
        return RespostaProvedor(
            texto=str(escolha["message"]["content"]),
            finish_reason=str(escolha.get("finish_reason") or ""),
        )
    except (KeyError, IndexError, TypeError) as e:
        raise ErroProvedor(f"Resposta inesperada do Groq: {e}") from e


def _chamar_cohere(
    prompt: str,
    payload: str,
    modelo: str,
    max_tokens: int,
    timeout: int,
) -> RespostaProvedor:
    chave = _cfg("COHERE_API_KEY")
    if not chave:
        raise ErroProvedor("COHERE_API_KEY não configurada.")
    corpo = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": payload},
        ],
        "temperature": 0.4,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    resposta = requests.post(
        COHERE_ENDPOINT,
        headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"},
        json=corpo,
        timeout=timeout,
    )
    if resposta.status_code != 200:
        raise ErroProvedor(f"Cohere {resposta.status_code}: {resposta.text[:200]}")
    try:
        dados = resposta.json()
        partes = dados["message"]["content"]
        texto = "".join(
            str(parte.get("text", ""))
            for parte in partes
            if isinstance(parte, dict)
        )
        if not texto:
            raise ErroProvedor("Resposta inesperada da Cohere: conteúdo vazio.")
        return RespostaProvedor(
            texto=texto,
            finish_reason=str(dados.get("finish_reason") or ""),
        )
    except (KeyError, IndexError, TypeError) as e:
        raise ErroProvedor(f"Resposta inesperada da Cohere: {e}") from e


# ---------- Classe principal ----------

@dataclass
class LLMProvider:
    """Provedor com fallback automático entre Gemini, Cohere e Groq.

    Args:
        gemini_modelo: modelo Gemini a usar (padrão: GEMINI_MODEL do ambiente).
        cohere_modelo: modelo Cohere a usar (padrão: COHERE_MODEL do ambiente).
        groq_modelo:   modelo Groq a usar (padrão: GROQ_MODEL do ambiente).
        max_tokens:    limite de tokens na resposta.
        timeout:       timeout em segundos por chamada.
    """
    gemini_modelo: str = field(default_factory=lambda: _cfg("GEMINI_MODEL", GEMINI_MODELO_PADRAO))
    cohere_modelo: str = field(default_factory=lambda: _cfg("COHERE_MODEL", COHERE_MODELO_PADRAO))
    groq_modelo: str = field(default_factory=lambda: _cfg("GROQ_MODEL", GROQ_MODELO_PADRAO))
    max_tokens: int = field(default_factory=_max_tokens_configurado)
    timeout: int = TIMEOUT_PADRAO

    def gerar(self, prompt: str, payload: dict | str) -> ResultadoLLM:
        """Envia prompt + payload ao LLM primário; usa o secundário se falhar.

        Args:
            prompt:  instrução do sistema (string).
            payload: dados da requisição (dict serializado para JSON ou string).

        Returns:
            ResultadoLLM com o texto gerado e metadados do provedor usado.

        Raises:
            ErroProvedor: se ambos os provedores falharem.
        """
        payload_str = json.dumps(payload, ensure_ascii=False) if not isinstance(payload, str) else payload

        if len(payload_str) > 100_000:
            raise ErroProvedor("Payload excede 100 000 caracteres. Reduza o lote antes de enviar.")

        provedores = self._ordem()
        erro_primario = ""

        for idx, (nome, fn, modelo) in enumerate(provedores):
            try:
                saida = fn(prompt, payload_str, modelo, self.max_tokens, self.timeout)
                if isinstance(saida, str):
                    texto, finish_reason = saida, ""
                else:
                    texto = getattr(saida, "texto", None)
                    finish_reason = str(getattr(saida, "finish_reason", "") or "")
                    if not isinstance(texto, str):
                        raise ErroProvedor("Resposta do adaptador sem texto válido.")
                return ResultadoLLM(
                    texto=texto,
                    provedor=nome,
                    modelo=modelo,
                    fallback_usado=idx > 0,
                    erro_primario=erro_primario,
                    finish_reason=finish_reason,
                )
            except (ErroProvedor, requests.RequestException) as e:
                erro_primario = str(e)
                logger.warning("[llm_provider] %s falhou: %s", nome, erro_primario)

        raise ErroProvedor(
            f"Todos os provedores falharam. Último erro: {erro_primario}"
        )

    def como_callable(self) -> "Callable[[str], str]":
        """Retorna callable compatível com classificar_interacao (Callable[[str], str])."""
        return lambda prompt: self.gerar(prompt, {}).texto

    def provedor_disponivel(self) -> str | None:
        """Retorna o primeiro provedor com chave configurada na ordem de fallback."""
        for nome, chave in (
            ("gemini", "GEMINI_API_KEY"),
            ("cohere", "COHERE_API_KEY"),
            ("groq", "GROQ_API_KEY"),
        ):
            if _cfg(chave):
                return nome
        return None

    def _ordem(self) -> list[tuple]:
        return [
            ("gemini", _chamar_gemini, self.gemini_modelo),
            ("cohere", _chamar_cohere, self.cohere_modelo),
            ("groq", _chamar_groq, self.groq_modelo),
        ]
