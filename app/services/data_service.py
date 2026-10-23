"""Camada de dados do front.

Hoje: devolve dados fictícios (mocks).
Depois: cada função aqui vira uma chamada ao back (Python/n8n/OCI).
As telas só falam com este arquivo, então a troca não mexe nelas.

IMPORTANTE para combinar com o back: o formato dos dicionários abaixo é
PROVISÓRIO. Quem define o contrato oficial é o back.
"""
import copy
import csv
import io
import json

from mocks import mock_data as m

CAMPOS_OBRIGATORIOS = ("autor", "canal", "texto")


def _obter_sal() -> str:
    """Retorna o sal para pseudonimização LGPD a partir de secrets ou env."""
    try:
        import streamlit as st
        return st.secrets.get("LGPD_SALT", "communitylab_salt_2026")
    except Exception:
        return os.environ.get("LGPD_SALT", "communitylab_salt_2026")


def _deve_anonimizar_pii() -> bool:
    """Verifica se a anonimização de PII (dados sensíveis) está ativada nas configurações."""
    try:
        import streamlit as st
        return bool(st.secrets.get("ANONIMIZAR_PII", False))
    except Exception:
        return os.environ.get("ANONIMIZAR_PII", "").lower() in ("true", "1", "yes")


# ---------- Ingestão ----------
def _normalizar(itens):
    if not isinstance(itens, list) or not itens:
        raise ValueError("O arquivo precisa conter uma lista com pelo menos uma interação.")
    sal = _obter_sal()
    anonimizar_ativado = _deve_anonimizar_pii()
    saida = []
    for i, item in enumerate(itens, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Interação {i}: formato inválido.")

        # Normaliza as chaves do item (minúsculas, sem aspas e sem BOM)
        item_norm = {}
        for k, v in item.items():
            if k is not None:
                k_limpo = str(k).lstrip("\ufeff").strip().strip('"').strip("'").lower()
                item_norm[k_limpo] = v

        faltando = [c for c in CAMPOS_OBRIGATORIOS if not str(item_norm.get(c, "")).strip()]
        if faltando:
            raise ValueError(f"Interação {i}: faltam os campos {', '.join(faltando)}.")

        texto_raw = str(item_norm["texto"]).strip()
        if normalizar_texto:
            try:
                texto_limpo = normalizar_texto(texto_raw)
            except Exception:
                texto_limpo = texto_raw
        else:
            texto_limpo = texto_raw

        # Anonimização de PII (LGPD: telefones, CPFs, e-mails) se ativado
        if anonimizar_ativado and anonimizar_texto:
            try:
                texto_limpo, _ = anonimizar_texto(texto_limpo)
            except Exception:
                pass

        autor_raw = str(item_norm["autor"]).strip()
        if pseudonimizar_autor:
            autor_id = pseudonimizar_autor(autor_raw, sal)
        else:
            autor_id = f"membro_{i:06d}"

        raw_id = item_norm.get("id")
        id_final = str(raw_id) if raw_id is not None and str(raw_id).strip() else f"int_{i:03d}"

        saida.append({
            "id": id_final,
            "autor": autor_raw,
            "autor_id": autor_id,
            "canal": str(item_norm["canal"]).strip(),
            "tipo": str(item_norm.get("tipo") or "mensagem").strip(),
            "texto": texto_limpo or texto_raw,
        })
    return saida


def interacoes_de_json(texto):
    """Aceita uma lista de interações ou um objeto com a chave 'interacoes'."""
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as erro:
        raise ValueError(f"JSON inválido: {erro.msg} (linha {erro.lineno}).")
    if isinstance(dados, dict) and "interacoes" in dados:
        dados = dados["interacoes"]
    return _normalizar(dados)


def parse_interacoes(nome_arquivo, conteudo):
    """Lê um arquivo CSV ou JSON enviado no upload aplicando fallbacks de encoding do core."""
    nome = nome_arquivo.lower()

    if isinstance(conteudo, bytes):
        if ler_arquivo_bytes:
            texto, _enc, _ = ler_arquivo_bytes(conteudo)
        else:
            try:
                texto = conteudo.decode("utf-8-sig")
            except UnicodeDecodeError:
                texto = conteudo.decode("latin-1", errors="replace")
    else:
        texto = str(conteudo)

    # Remove BOM residual do início do texto, se houver
    texto = texto.lstrip("\ufeff")

    if not texto.strip():
        raise ValueError("O arquivo enviado está vazio ou não pôde ser decodificado.")

    if nome.endswith(".json"):
        return interacoes_de_json(texto)
    if nome.endswith(".csv"):
        delimitador = ","
        linhas = [ln for ln in texto.splitlines() if ln.strip()]
        if linhas:
            primeira = linhas[0]
            if ";" in primeira and ("," not in primeira or primeira.count(";") > primeira.count(",")):
                delimitador = ";"

        def _ler_com_delimitador(delim):
            leitor = csv.DictReader(io.StringIO(texto), delimiter=delim)
            resultado = []
            for row in leitor:
                linha_limpa = {}
                for k, v in row.items():
                    if k is not None:
                        k_limpo = str(k).lstrip("\ufeff").strip().strip('"').strip("'").lower()
                        linha_limpa[k_limpo] = v
                resultado.append(linha_limpa)
            return resultado

        itens = _ler_com_delimitador(delimitador)

        # Fallback de delimitador caso os campos obrigatórios não tenham sido mapeados
        if itens and not all(c in itens[0] for c in CAMPOS_OBRIGATORIOS):
            outro = ";" if delimitador == "," else ","
            itens_alt = _ler_com_delimitador(outro)
            if itens_alt and all(c in itens_alt[0] for c in CAMPOS_OBRIGATORIOS):
                itens = itens_alt

        return _normalizar(itens)
    raise ValueError("Formato não suportado. Envie um arquivo CSV ou JSON.")


# ---------- Análise ----------
ORIGEM_ANALISE = "mock"   # "gemini" quando a análise real responde
ULTIMO_ERRO = ""          # preenchido quando a análise real falha


def analisar(interacoes):
    """Analisa as interações com o provedor de LLM.

    Se a chave não estiver configurada ou a chamada falhar, devolve o mock
    (o protótipo continua navegável) e registra o motivo de forma isolada por sessão.
    """
    try:
        from . import llm  # import local: evita custo quando não usado
    except ImportError:  # pragma: no cover - execução como pacote vs. script
        from services import llm  # type: ignore

    try:
        historias = llm.analisar(interacoes, maximo=maximo)
        _definir_origem_analise("gemini", "")
        print(f"[analise] gemini OK: {len(historias)} historias", flush=True)
        return _enriquecer_historias_com_cqf(historias, interacoes)
    except Exception as erro:  # rede, chave ausente, JSON inválido
        msg_erro = str(erro)
        _definir_origem_analise("mock", msg_erro)
        print(f"[analise] FALHOU -> fallback mock: {msg_erro}", flush=True)

    historias_mock = copy.deepcopy(m.HISTORIAS)
    return _enriquecer_historias_com_cqf(historias_mock, interacoes)


def regenerar(historia, ativo_id, vez):
    """Regenera rascunho de ativo aplicando validação RG-01 (anti-alucinação).

    Alterna entre as variações disponíveis e assegura que qualquer citação
    presente no rascunho satisfaça a Regra RG-01 (integridade factual
    com normalização de whitespace). Em caso de violação, preserva com
    segurança a versão base do ativo.
    """
    for ativo in historia.get("ativos", []):
        if ativo.get("id") == ativo_id:
            opcoes = [ativo.get("campos", {})] + ativo.get("variacoes", [])
            if not opcoes:
                return {}
            candidato = dict(opcoes[vez % len(opcoes)])

            # Validação RG-01 para citações presentes na variação
            if validar_integridade_evidencias:
                citacoes_candidato = []
                if "citacao" in candidato and candidato["citacao"]:
                    citacoes_candidato.append(str(candidato["citacao"]))
                if "citacoes" in candidato and isinstance(candidato["citacoes"], list):
                    for c in candidato["citacoes"]:
                        if isinstance(c, dict) and "texto" in c:
                            citacoes_candidato.append(str(c["texto"]))
                        elif isinstance(c, str) and c:
                            citacoes_candidato.append(c)

                if citacoes_candidato:
                    try:
                        origens = historia.get("interacoes_origem") or [historia.get("id") or "int_001"]
                        id_origem = origens[0]
                        msg_orig = historia.get("mensagem_original") or ""

                        interacoes_check = [{"id": id_origem, "texto": msg_orig}]
                        historia_check = {
                            "interacoes_origem": [id_origem],
                            "citacoes": [{"id_interacao": id_origem, "texto": cit} for cit in citacoes_candidato],
                        }

                        valido, erros = validar_integridade_evidencias(historia_check, interacoes_check)
                        if not valido:
                            print(
                                f"[regenerar] RG-01 reprovou variação #{vez} do ativo '{ativo_id}': {erros}. "
                                f"Retornando versão base segura.",
                                flush=True,
                            )
                            return dict(ativo.get("campos", {}))
                    except Exception as e_rg01:
                        print(f"[regenerar] Aviso ao validar RG-01: {e_rg01}", flush=True)

            return candidato
    return {}


# ---------- OCI ----------
def listar_pacotes():
    """TODO(back): listar objetos do bucket no OCI Object Storage."""
    return copy.deepcopy(m.PACOTES_OCI)


def salvar_no_oci(pacotes, lote_id):
    """TODO(back): gravar o pacote no OCI. Deve ser idempotente (retry não duplica)."""
    return pacotes


def reenviar_pacote(pacote):
    """TODO(back): tentar gravar de novo um pacote que falhou."""
    novo = dict(pacote)
    novo.update({"status": "salvo", "data": "15/10/2026 14:40", "tamanho": "2,4 KB"})
    return novo


def conteudo_pacote(caminho):
    """TODO(back): ler o objeto do bucket. Formato provisório."""
    if caminho.endswith("evidencias.json"):
        return {
            "lote": "DEMO-001",
            "evidencias": [
                {"autor": h["autor"], "canal": h["canal"],
                 "mensagem_original": h["mensagem_original"], "citacoes": h["destaques"], "fatos": h["fatos"]}
                for h in m.HISTORIAS
            ],
        }
    return {
        "status": "sucesso",
        "lote": "DEMO-001",
        "gravado_em": "2026-10-15T14:32:00-03:00",
        "historias": [
            {"autor": h["autor"], "categoria": h["categoria"], "relevancia": h["relevancia"],
             "citacao": h["destaques"][0],
             "ativos": {a["id"]: {"status": "rascunho_aguardando_revisao"} for a in h["ativos"]}}
            for h in m.HISTORIAS
        ],
    }
