"""Armazenamento de pacotes no OCI Object Storage.

Grava cada lote como um objeto unico, nomeado pelo id do lote:

    ativos/<lote_id>/pacote-distribuicao.json

Gravar duas vezes o mesmo lote sobrescreve o objeto (idempotente), em vez de
criar uma copia. As credenciais ficam em ~/.oci/config e a configuracao do
bucket em variaveis de ambiente ou no arquivo .env da raiz do projeto.
"""

from __future__ import annotations

import json
import re
import os
from datetime import datetime, timezone
from pathlib import Path

PREFIXO = "ativos"
ARQUIVO_PACOTE = "pacote-distribuicao.json"
BUCKET_PADRAO = "G10communitylab-ativos"
CONFIG_PADRAO = "~/.oci/config"


class ErroArmazenamento(RuntimeError):
    """Falha ao falar com o OCI Object Storage."""


def _carregar_env() -> None:
    """Le o .env da raiz do projeto, sem depender de biblioteca externa."""
    for caminho in (Path.cwd() / ".env", Path(__file__).resolve().parents[2] / ".env"):
        if not caminho.exists():
            continue
        for linha in caminho.read_text(encoding="utf-8", errors="ignore").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            chave = chave.strip()
            if chave and chave not in os.environ:
                os.environ[chave] = valor.strip().strip('"').strip("'")


def _config() -> tuple[object, str, str]:
    """Devolve (cliente, namespace, bucket) prontos para uso."""
    _carregar_env()
    try:
        import oci  # import local: o app funciona mesmo sem o SDK instalado
    except ImportError as erro:  # pragma: no cover
        raise ErroArmazenamento(
            "SDK da OCI nao instalado. Rode: pip install oci"
        ) from erro

    # Tenta ler do Streamlit secrets primeiro
    _tem_secrets = False
    try:
        import streamlit as st
        _tem_secrets = hasattr(st, "secrets") and "OCI_USER" in st.secrets
    except ImportError:
        pass  # Streamlit não disponível, usa arquivo

    if _tem_secrets:
        # Secrets OCI presentes → usa obrigatoriamente, sem fallback silencioso
        try:
            config = {
                "user": st.secrets["OCI_USER"],
                "fingerprint": st.secrets["OCI_FINGERPRINT"],
                "tenancy": st.secrets["OCI_TENANCY"],
                "region": st.secrets.get("OCI_REGION", "sa-saopaulo-1"),
                "key_content": st.secrets["OCI_KEY_CONTENT"],
            }
            cliente = oci.object_storage.ObjectStorageClient(config)
            namespace = st.secrets.get("OCI_NAMESPACE") or cliente.get_namespace().data
            bucket = st.secrets.get("OCI_BUCKET_NAME", BUCKET_PADRAO)
            return cliente, namespace, bucket
        except Exception as erro:
            raise ErroArmazenamento(
                f"Falha ao autenticar via Streamlit secrets: {erro}"
            ) from erro

    # Fallback: arquivo ~/.oci/config
    arquivo = os.path.expanduser(os.environ.get("OCI_CONFIG_FILE", CONFIG_PADRAO))
    perfil = os.environ.get("OCI_PROFILE", "DEFAULT")
    if not Path(arquivo).exists():
        raise ErroArmazenamento(f"Credencial da OCI nao encontrada em {arquivo}")

    try:
        config = oci.config.from_file(arquivo, perfil)
        cliente = oci.object_storage.ObjectStorageClient(config)
        namespace = os.environ.get("OCI_NAMESPACE") or cliente.get_namespace().data
    except Exception as erro:  # credencial invalida, rede, permissao
        raise ErroArmazenamento(f"Falha ao autenticar na OCI: {erro}") from erro

    bucket = os.environ.get("OCI_BUCKET_NAME", BUCKET_PADRAO)
    return cliente, namespace, bucket


def nome_bucket() -> str:
    """Nome do bucket em uso, conforme a configuracao do ambiente."""
    _carregar_env()
    return os.environ.get("OCI_BUCKET_NAME", BUCKET_PADRAO)


def _lote_seguro(lote_id: str) -> str:
    """Sanitiza o id do lote para virar pasta: sem barra, espaco ou acento."""
    lote = (lote_id or "").strip()
    lote = re.sub(r"[^A-Za-z0-9._-]", "-", lote).strip(".-")
    return lote or "lote"


def caminho_do_lote(lote_id: str, arquivo: str | None = None) -> str:
    """Caminho deterministico do objeto.

    O caminho e sempre montado aqui, nunca copiado do dado recebido: o mesmo
    lote com o mesmo arquivo cai sempre no mesmo objeto. Varios arquivos por
    lote continuam suportados, diferenciados pelo nome do arquivo.
    """
    nome = Path(str(arquivo or ARQUIVO_PACOTE).replace("\\", "/")).name.strip()
    nome = re.sub(r"[^A-Za-z0-9._-]", "-", nome).strip(".-") or ARQUIVO_PACOTE
    if not nome.lower().endswith(".json"):
        nome += ".json"
    return f"{PREFIXO}/{_lote_seguro(lote_id)}/{nome}"


def caminho_do_pacote(lote_id: str) -> str:
    """Caminho do pacote principal do lote."""
    return caminho_do_lote(lote_id, ARQUIVO_PACOTE)


def salvar_objeto(caminho: str, dados: dict) -> dict:
    """Grava um objeto em qualquer caminho do bucket."""
    cliente, namespace, bucket = _config()
    corpo = json.dumps(dados, ensure_ascii=False, indent=2).encode("utf-8")
    try:
        cliente.put_object(
            namespace_name=namespace,
            bucket_name=bucket,
            object_name=caminho,
            put_object_body=corpo,
            content_type="application/json",
        )
    except Exception as erro:
        raise ErroArmazenamento(f"Falha ao gravar {caminho}: {erro}") from erro
    return {
        "caminho": caminho,
        "tamanho_bytes": len(corpo),
        "tamanho": f"{len(corpo) / 1024:.1f} KB".replace(".", ","),
        "salvo_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "salvo",
    }


def ler_objeto(caminho: str) -> dict | None:
    """Le um objeto do bucket pelo caminho. None quando nao existe."""
    cliente, namespace, bucket = _config()
    try:
        resposta = cliente.get_object(namespace, bucket, caminho)
    except Exception as erro:
        if getattr(erro, "status", None) == 404:
            return None
        raise ErroArmazenamento(f"Falha ao ler {caminho}: {erro}") from erro
    return json.loads(resposta.data.content.decode("utf-8"))


def disponivel() -> bool:
    """True se a credencial e o bucket estao acessiveis."""
    try:
        _config()
        return True
    except ErroArmazenamento:
        return False


def motivo_indisponivel() -> str:
    """Motivo real da indisponibilidade: credencial ausente, invalida, rede."""
    try:
        _config()
        return ""
    except ErroArmazenamento as erro:
        return str(erro)


def salvar_pacote(lote_id: str, dados: dict) -> dict:
    """Grava o pacote do lote e devolve o resumo do que foi salvo."""
    cliente, namespace, bucket = _config()
    caminho = caminho_do_pacote(lote_id)
    corpo = json.dumps(dados, ensure_ascii=False, indent=2).encode("utf-8")

    try:
        cliente.put_object(
            namespace_name=namespace,
            bucket_name=bucket,
            object_name=caminho,
            put_object_body=corpo,
            content_type="application/json",
        )
    except Exception as erro:
        raise ErroArmazenamento(f"Falha ao gravar {caminho}: {erro}") from erro

    return {
        "caminho": caminho,
        "lote": lote_id,
        "tamanho_bytes": len(corpo),
        "tamanho": f"{len(corpo) / 1024:.1f} KB".replace(".", ","),
        "salvo_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "salvo",
    }


def ler_pacote(lote_id: str) -> dict | None:
    """Le o pacote do lote. Devolve None quando o lote nao existe."""
    cliente, namespace, bucket = _config()
    caminho = caminho_do_pacote(lote_id)
    try:
        resposta = cliente.get_object(namespace, bucket, caminho)
    except Exception as erro:
        if getattr(erro, "status", None) == 404:
            return None
        raise ErroArmazenamento(f"Falha ao ler {caminho}: {erro}") from erro

    return json.loads(resposta.data.content.decode("utf-8"))


def listar_pacotes() -> list[dict]:
    """Lista os pacotes salvos, do mais recente para o mais antigo."""
    cliente, namespace, bucket = _config()
    try:
        resposta = cliente.list_objects(
            namespace, bucket, prefix=f"{PREFIXO}/", fields="name,size,timeModified"
        )
    except Exception as erro:
        raise ErroArmazenamento(f"Falha ao listar o bucket: {erro}") from erro

    itens = []
    for objeto in resposta.data.objects:
        partes = objeto.name.split("/")
        if len(partes) < 2:
            continue
        itens.append(
            {
                "lote": partes[1],
                "caminho": objeto.name,
                "tamanho_bytes": objeto.size,
                "tamanho": f"{(objeto.size or 0) / 1024:.1f} KB".replace(".", ","),
                "salvo_em": str(objeto.time_modified or "")[:19],
            }
        )
    itens.sort(key=lambda item: item["salvo_em"], reverse=True)
    return itens
