"""Ingestão de mensagens do Discord via API REST.

Busca as últimas N mensagens de um canal e converte para o formato
de interações do pipeline (mesmo contrato de processar_json).

Configuração (variável de ambiente ou st.secrets):
    DISCORD_TOKEN        — token do bot
    CANAL_ID             — ID do canal padrão (pode ser sobrescrito por parâmetro)
    SAL_PSEUDONIMIZACAO  — sal secreto usado na pseudonimização dos autores
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

from src.ingestion.ingestion import pseudonimizar_autor


DISCORD_API = "https://discord.com/api/v10"
LIMITE_MAXIMO = 100  # limite máximo por requisição da API do Discord
MARCADOR_ULTIMO_ID = "__ultimo_id_discord__:"
SAL_PADRAO = "communitylab_default_salt"  # apenas para desenvolvimento
TIPOS_MENSAGEM_VALIDOS = {0, 19}  # 0 = mensagem comum, 19 = resposta
_REGEX_MENCAO = re.compile(r"<(@[!&]?|#)\d+>")


def _cfg(chave: str) -> str:
    """Lê a configuração da variável de ambiente; usa st.secrets como fallback."""
    valor = os.environ.get(chave, "")
    if valor:
        return valor
    try:
        import streamlit as st
        return str(st.secrets.get(chave, "") or "")
    except Exception:
        return ""


def _anonimizar_mencoes(texto: str) -> str:
    """Troca menções (<@123>, <@!123>, <@&123>, <#123>) por placeholders."""
    return _REGEX_MENCAO.sub(lambda m: "#canal" if m.group(1) == "#" else "@membro", texto)


def _rejeitar(posicao: int, msg_id: str, motivo: str) -> Dict[str, Any]:
    """Monta uma rejeição sem guardar dados pessoais do autor."""
    return {"posicao": posicao, "motivo": motivo, "original": {"id_discord": msg_id}}


def buscar_mensagens_discord(
    limite: int = 50,
    canal_id: Optional[str] = None,
    sal: Optional[str] = None,
    after_id: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    """Busca mensagens do canal após `after_id` (se fornecido) ou as últimas `limite`.

    Args:
        limite:   quantidade de mensagens a buscar (1 a 100 por chamada da API; padrão 50).
        canal_id: ID do canal; usa CANAL_ID da configuração se omitido.
        sal:      sal da pseudonimização; usa SAL_PSEUDONIMIZACAO se omitido.
        after_id: ID Discord da última mensagem já importada; retorna apenas
                  mensagens mais recentes que ela.

    Returns:
        (interacoes_validas, rejeitadas, avisos) — mesmo contrato de processar_json.
        As interações vêm em ordem cronológica (da mais antiga para a mais recente).
        Se houver mensagens, `avisos` inclui "__ultimo_id_discord__:<id>" com o ID
        da mensagem mais recente retornada, para usar como `after_id` na próxima chamada.
    """
    token = _cfg("DISCORD_TOKEN")
    canal = canal_id or _cfg("CANAL_ID")

    if not token:
        return [], [], ["DISCORD_TOKEN não configurado."]
    if not canal:
        return [], [], ["CANAL_ID não configurado."]

    avisos: List[str] = []
    sal = sal or _cfg("SAL_PSEUDONIMIZACAO")
    if not sal:
        sal = SAL_PADRAO
        avisos.append("SAL_PSEUDONIMIZACAO não configurado: usando sal padrão (inseguro fora de desenvolvimento).")

    limite = max(1, min(limite, LIMITE_MAXIMO))

    headers = {"Authorization": f"Bot {token}"}
    url = f"{DISCORD_API}/channels/{canal}/messages"
    params: Dict[str, Any] = {"limit": limite}
    if after_id:
        params["after"] = after_id

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
    except requests.RequestException as exc:
        return [], [], [f"Erro de conexão com o Discord: {exc}"]

    if resp.status_code == 401:
        return [], [], ["DISCORD_TOKEN inválido ou sem permissão."]
    if resp.status_code == 403:
        return [], [], ["Bot sem acesso ao canal informado."]
    if resp.status_code == 429:
        espera = resp.headers.get("Retry-After", "?")
        return [], [], [f"Limite de requisições do Discord atingido. Tente novamente em {espera} segundos."]
    if resp.status_code != 200:
        return [], [], [f"Discord API retornou HTTP {resp.status_code}: {resp.text[:200]}"]

    try:
        mensagens = resp.json()
    except ValueError:
        return [], [], ["Resposta do Discord não é um JSON válido."]

    if not isinstance(mensagens, list):
        return [], [], ["Resposta do Discord em formato inesperado (esperada uma lista de mensagens)."]

    interacoes_validas: List[Dict[str, Any]] = []
    rejeitadas: List[Dict[str, Any]] = []

    # Maior ID entre todas as mensagens retornadas (inclusive as rejeitadas),
    # para que a próxima busca incremental não reprocesse nada.
    ids_numericos = [int(m["id"]) for m in mensagens if str(m.get("id", "")).isdigit()]
    ultimo_id_discord = str(max(ids_numericos)) if ids_numericos else None

    # A API devolve do mais recente para o mais antigo; invertemos para ordem cronológica.
    for idx, msg in enumerate(reversed(mensagens), start=1):
        msg_id = str(msg.get("id", ""))
        author = msg.get("author") or {}

        if author.get("bot"):
            rejeitadas.append(_rejeitar(idx, msg_id, "Mensagem de bot"))
            continue
        if msg.get("type", 0) not in TIPOS_MENSAGEM_VALIDOS:
            rejeitadas.append(_rejeitar(idx, msg_id, "Mensagem de sistema"))
            continue

        texto = _anonimizar_mencoes((msg.get("content") or "").strip()).strip()
        if not texto:
            rejeitadas.append(_rejeitar(idx, msg_id, "Mensagem vazia (bot, embed ou anexo)"))
            continue

        try:
            data_iso = datetime.fromisoformat(
                msg["timestamp"].replace("Z", "+00:00")
            ).astimezone(timezone.utc).isoformat()
        except (KeyError, AttributeError, ValueError):
            rejeitadas.append(_rejeitar(idx, msg_id, "Timestamp ausente ou inválido"))
            continue

        # Usa o ID numérico do Discord (estável); nunca username ou nome de exibição.
        autor_bruto = str(author.get("id") or "desconhecido")

        interacoes_validas.append({
            "versao_schema": "1.0",
            "id": idx,
            "id_discord": msg_id,
            "autor_id": pseudonimizar_autor(autor_bruto, sal),
            "canal": canal,
            "tipo": "mensagem",
            "data": data_iso,
            "origem": "discord",
            "texto": texto,
            "status_revisao": "pendente",
        })

    if ultimo_id_discord:
        avisos.append(f"{MARCADOR_ULTIMO_ID}{ultimo_id_discord}")
    
    return interacoes_validas, rejeitadas, avisos
