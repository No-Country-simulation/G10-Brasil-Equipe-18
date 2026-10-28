"""Módulo centralizado de configurações do CommunityLab.

Define constantes e limites com suporte a sobrescrita via variáveis de ambiente,
conforme especificado na documentação do projeto.
"""
import os

# --- Limites de Texto e Limpeza ---
TAMANHO_MINIMO_TEXTO: int = int(os.getenv("TAMANHO_MINIMO_TEXTO", "10"))
TAMANHO_MAXIMO_TEXTO: int = int(os.getenv("TAMANHO_MAXIMO_TEXTO", "4000"))

# --- Classificação e IA ---
LIMIAR_CONFIANCA: float = float(os.getenv("LIMIAR_CONFIANCA", "0.6"))
MAX_TENTATIVAS_LLM: int = int(os.getenv("MAX_TENTATIVAS_LLM", "2"))
TAMANHO_LOTE: int = int(os.getenv("TAMANHO_LOTE", "50"))

# --- Segurança e Pseudonimização ---
SAL_PADRAO: str = os.getenv("SAL_PSEUDONIMIZACAO", "communitylab_default_salt")

# --- Modo Demonstração ---
# Controla se o sistema opera em modo demonstração (oculta erros de credencial)
# Apenas "1", "true" ou "sim" (case-insensitive) ativam; qualquer outro valor desativa
_modo_demo_str = os.getenv("MODO_DEMONSTRACAO", "").lower()
MODO_DEMONSTRACAO: bool = _modo_demo_str in ("1", "true", "sim")

# --- Schemas ---
VERSAO_SCHEMA_INTERACAO: str = "1.0"
VERSAO_SCHEMA_ATIVO: str = "1.0"
VERSAO_SCHEMA_LOTE: str = "1.1"
VERSAO_SCHEMA_HISTORIA: str = "1.1"
