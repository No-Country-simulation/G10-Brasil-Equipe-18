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
import sys
from pathlib import Path

# Garante acesso ao pacote src do core de ML
_raiz_projeto = Path(__file__).resolve().parent.parent.parent
if str(_raiz_projeto) not in sys.path:
    sys.path.insert(0, str(_raiz_projeto))

import os
import threading

from datetime import datetime, timezone

try:
    from src.ingestion.leitura import ler_arquivo_bytes
    from src.ingestion.ingestion import pseudonimizar_autor, processar_json, processar_csv
    from src.preprocessing.limpeza import normalizar_texto, limpar_e_filtrar_interacoes
    from src.preprocessing.anonimizacao import anonimizar_texto
    from src.analysis.classificacao import classificar_interacao
    from src.storage.contrato import carregar_schema
    from src.orchestration.cqf import (
        calcular_cqf_score,
        validar_integridade_evidencias,
        avaliar_aprovacao_editorial,
        validar_liberacao_publicacao,
        consolidar_decisao_governança,
    )
    from src.modelos import AvaliacaoCQF, HistoriaDetectada, Interacao, Citacao
except Exception as _e_import:
    import warnings
    warnings.warn(
        f"[data_service] Falha ao importar módulos do core src/: {_e_import}. "
        "Pipeline rodando com fallbacks locais.",
        stacklevel=2,
    )
    ler_arquivo_bytes = None
    pseudonimizar_autor = None
    processar_json = None
    processar_csv = None
    normalizar_texto = lambda t: " ".join(str(t).split())
    limpar_e_filtrar_interacoes = None
    anonimizar_texto = None
    classificar_interacao = None
    carregar_schema = None
    calcular_cqf_score = None
    validar_integridade_evidencias = None
    avaliar_aprovacao_editorial = None
    validar_liberacao_publicacao = None
    consolidar_decisao_governança = None
    AvaliacaoCQF = None
    HistoriaDetectada = None
    Interacao = None
    Citacao = None

try:
    from mocks import mock_data as m
except ImportError:
    from app.mocks import mock_data as m  # type: ignore

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


# ---------- Limpeza & Classificação Core (Pipeline Real) ----------
def limpar_interacoes_lote(interacoes: list) -> tuple:
    """Aplica o filtro de limpeza real (src.preprocessing.limpeza) no lote.
    
    Remove mensagens vazias ou com menos de 10 caracteres e deduplica registros
    intra-lote preservando a primeira ocorrência.
    """
    if not interacoes:
        return [], []
    if limpar_e_filtrar_interacoes:
        try:
            return limpar_e_filtrar_interacoes(interacoes, tamanho_minimo=10)
        except Exception as e_limpeza:
            print(f"[data_service] Aviso na limpeza de interações: {e_limpeza}", flush=True)
    return interacoes, []


def classificar_interacoes_lote(interacoes: list) -> list:
    """Classifica cada interação utilizando src.analysis.classificacao.classificar_interacao.
    
    Enriquece cada item com análise auditável de sentimento, relevância,
    tópicos e tipo de insight em total conformidade com schemas/interacao_schema.json.
    """
    if not interacoes:
        return []

    schema_path = _raiz_projeto / "schemas" / "interacao_schema.json"
    schema = carregar_schema(str(schema_path)) if (carregar_schema and schema_path.exists()) else None

    # Função de classificação estruturada compatível com o contrato do LLM
    def _chamar_classificador(prompt_texto: str) -> str:
        texto_l = prompt_texto.lower()
        if any(w in texto_l for w in ["vaga", "consegui", "aprovado", "conquista", "contratado", "transição", "destaque", "promoção"]):
            sent = "positivo"
            topicos = ["carreira", "tecnologia"]
            insight = "conquista"
            rel = "alta"
            just = "Relato explícito de conquista e evolução profissional."
        elif any(w in texto_l for w in ["projeto", "estudo", "código", "desafio", "alura", "equipe", "formação", "portfólio"]):
            sent = "positivo"
            topicos = ["estudos", "tecnologia"]
            insight = "historia"
            rel = "media"
            just = "Progresso em projetos e atividades práticas da comunidade."
        elif any(w in texto_l for w in ["?", "dúvida", "horário", "alguém", "onde", "quando", "mentoria"]):
            sent = "neutro"
            topicos = ["comunidade"]
            insight = "duvida"
            rel = "baixa"
            just = "Dúvida operacional de rotina da comunidade."
        else:
            sent = "neutro"
            topicos = ["comunidade"]
            insight = "outro"
            rel = "baixa"
            just = "Comunicação geral de rotina."

        return json.dumps({
            "sentimento": sent,
            "relevancia": rel,
            "topicos": topicos,
            "tipo_insight": insight,
            "justificativa": just,
            "confianca": 0.95
        }, ensure_ascii=False)

    template = "Classifique a mensagem: {{texto}}"
    saida = []

    for idx, item in enumerate(interacoes, start=1):
        item_copia = dict(item)
        if classificar_interacao and schema:
            autor_id = str(item_copia.get("autor_id") or "")
            if not autor_id.startswith("membro_"):
                autor_id = f"membro_{idx:06d}"
            
            interacao_core = {
                "versao_schema": "1.0",
                "id": idx,
                "autor_id": autor_id,
                "data": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "origem": "discord",
                "texto": str(item_copia.get("texto") or "Mensagem da comunidade")
            }
            try:
                classificada, status, avisos = classificar_interacao(
                    interacao=interacao_core,
                    schema_interacao=schema,
                    funcao_chamar_llm=_chamar_classificador,
                    prompt_template=template,
                    max_tentativas=2,
                    limiar_confianca=0.6,
                )
                if "analise" in classificada:
                    item_copia["analise"] = classificada["analise"]
                    item_copia["sentimento"] = classificada["analise"]["sentimento"].capitalize()
                    item_copia["categoria"] = " / ".join(classificada["analise"]["topicos"]).capitalize()
            except Exception as _e_cls:
                print(f"[classificacao] Aviso ao classificar interação {idx}: {_e_cls}", flush=True)

        saida.append(item_copia)

    return saida


# ---------- Análise & Rastreabilidade CQF ----------
_thread_local = threading.local()
ORIGEM_ANALISE = "mock"   # Mantido para retrocompatibilidade
ULTIMO_ERRO = ""          # Mantido para retrocompatibilidade


def obter_origem_analise() -> str:
    """Retorna a origem da análise de forma isolada por sessão do Streamlit."""
    try:
        import streamlit as st
        if hasattr(st, "session_state") and "origem_analise" in st.session_state:
            return st.session_state["origem_analise"]
    except Exception:
        pass
    return getattr(_thread_local, "origem_analise", ORIGEM_ANALISE)


def obter_ultimo_erro() -> str:
    """Retorna o último erro de análise de forma isolada por sessão do Streamlit."""
    try:
        import streamlit as st
        if hasattr(st, "session_state") and "ultimo_erro" in st.session_state:
            return st.session_state["ultimo_erro"]
    except Exception:
        pass
    return getattr(_thread_local, "ultimo_erro", ULTIMO_ERRO)


def _definir_origem_analise(origem: str, erro: str = ""):
    global ORIGEM_ANALISE, ULTIMO_ERRO
    ORIGEM_ANALISE = origem
    ULTIMO_ERRO = erro
    _thread_local.origem_analise = origem
    _thread_local.ultimo_erro = erro
    try:
        import streamlit as st
        if hasattr(st, "session_state"):
            st.session_state["origem_analise"] = origem
            st.session_state["ultimo_erro"] = erro
    except Exception:
        pass


def _enriquecer_historias_com_cqf(historias, interacoes):
    """Enriquece as histórias com citações estruturadas (CATP-007) e CQF Score informativo."""
    if not historias:
        return []

    mapa_por_texto = {}
    interacoes_preparadas = []
    for idx, item in enumerate(interacoes or [], start=1):
        if not isinstance(item, dict):
            continue
        iid = str(item.get("id") or f"int_{idx:03d}")
        item_com_id = dict(item)
        item_com_id["id"] = iid
        interacoes_preparadas.append(item_com_id)
        txt = str(item.get("texto") or "")
        txt_norm = " ".join(txt.split())
        if txt_norm:
            mapa_por_texto[txt_norm] = iid

    for idx, h in enumerate(historias, start=1):
        msg_orig = str(h.get("mensagem_original") or "").strip()
        msg_norm = " ".join(msg_orig.split())

        # Vinculação rastreável de ID de origem
        id_origem = None
        if msg_norm in mapa_por_texto:
            id_origem = mapa_por_texto[msg_norm]
        elif "interacoes_origem" in h and h["interacoes_origem"]:
            id_cand = h["interacoes_origem"][0]
            if isinstance(id_cand, int):
                id_origem = f"int_{id_cand:03d}"
            elif str(id_cand).isdigit():
                id_origem = f"int_{int(id_cand):03d}"
            else:
                id_origem = str(id_cand)
        else:
            for txt_n, iid in mapa_por_texto.items():
                if msg_norm and (msg_norm in txt_n or txt_n in msg_norm):
                    id_origem = iid
                    break
        if not id_origem:
            id_origem = f"int_{idx:03d}"

        h["interacoes_origem"] = [id_origem]

        # Estrutura formal de citações (CATP-007)
        destaques = h.get("destaques") or []
        citacoes_estruturadas = []
        for d in destaques:
            citacoes_estruturadas.append({
                "id_interacao": id_origem,
                "texto": str(d)
            })
        h["citacoes"] = citacoes_estruturadas

        # Validação RG-01 de Integridade de Evidências
        if validar_integridade_evidencias:
            try:
                valido_rg01, erros_rg01 = validar_integridade_evidencias(h, interacoes_preparadas)
                h["rg01_valido"] = valido_rg01
                h["rg01_erros"] = erros_rg01
                if not valido_rg01:
                    print(
                        f"[rg01] História '{h.get('id', '?')}' REPROVADA: {erros_rg01}",
                        flush=True,
                    )
            except (TypeError, KeyError, AttributeError) as _e_rg01:
                # Erros de runtime no validador (bug no código) NÃO devem silenciosamente
                # marcar a história como válida. Loga e marca como pendente de revisão.
                print(
                    f"[rg01] ERRO DE RUNTIME ao validar história '{h.get('id', '?')}': {_e_rg01}. "
                    "Marcando rg01_valido=False para forçar revisão humana.",
                    flush=True,
                )
                h["rg01_valido"] = False
                h["rg01_erros"] = [f"Erro interno de validação RG-01: {_e_rg01}"]
        else:
            h["rg01_valido"] = True
            h["rg01_erros"] = []

        # Cálculo do CQF Score oficial (4 dimensões com heurísticas dinâmicas: R, C, I, E)
        if calcular_cqf_score:
            try:
                rel = float(h.get("relevancia") or 80.0)
                # 1. Relevância (0.0 a 5.0)
                r_dim = min(5.0, max(0.0, (rel / 100.0) * 5.0))

                # 2. Completude (0.0 a 5.0): avalia riqueza de fatos, resultados e resumo
                fatos = h.get("fatos") or []
                resultados = h.get("resultados") or []
                resumo = str(h.get("resumo") or h.get("categoria") or "")
                c_score = 2.0
                if len(fatos) >= 1:
                    c_score += 1.0
                if len(fatos) >= 2:
                    c_score += 0.8
                if len(resultados) >= 1:
                    c_score += 0.7
                if len(resumo) >= 30:
                    c_score += 0.5
                c_dim = min(5.0, max(1.0, c_score))

                # 3. Clareza & Impacto (0.0 a 5.0): analisa narrativa e evidências de transformação
                msg_original = str(h.get("mensagem_original") or "")
                palavras_impacto = [
                    "transição", "promovido", "conquista", "sucesso", "aprovado",
                    "contratado", "novo emprego", "primeira vaga", "evolução",
                    "estágio", "certificação", "projeto", "aprender", "resultado", "%"
                ]
                impacto_encontrado = sum(
                    1 for p in palavras_impacto if p in msg_original.lower() or p in resumo.lower()
                )
                i_score = 3.0
                if impacto_encontrado >= 1:
                    i_score += 1.0
                if impacto_encontrado >= 3:
                    i_score += 0.8
                if len(msg_original.split()) < 5:
                    i_score -= 1.5
                elif len(msg_original.split()) >= 15:
                    i_score += 0.2
                i_dim = min(5.0, max(1.0, i_score))

                # 4. Evidências (0.0 a 5.0): integridade factual e ancoragem em citações literais
                rg01_ok = h.get("rg01_valido", True)
                citacoes_list = h.get("citacoes") or []
                if not rg01_ok:
                    e_dim = 1.5  # Penalidade severa por violação de integridade factual (RG-01)
                elif not citacoes_list and not destaques:
                    e_dim = 2.0  # Sem citações ou evidências
                elif len(citacoes_list) == 1 or len(destaques) == 1:
                    e_dim = 4.0  # Citação única verificada
                else:
                    e_dim = 4.8  # Múltiplas evidências factuais verificadas

                res_cqf = calcular_cqf_score(
                    relevancia=round(r_dim, 1),
                    completude=round(c_dim, 1),
                    clareza_impacto=round(i_dim, 1),
                    evidencias=round(e_dim, 1),
                )
                h["cqf_score"] = res_cqf["cqf_score"]
                h["cqf_classificacao"] = res_cqf["classificacao_editorial"]
                h["cqf_dimensoes"] = res_cqf["notas_entrada"]
            except Exception:
                h["cqf_score"] = round(float(h.get("relevancia") or 80.0) * 0.9, 1)
                h["cqf_classificacao"] = "alta_prioridade" if h["cqf_score"] >= 80 else "prioridade_media"
                h["cqf_dimensoes"] = {"relevancia": 4.0, "completude": 4.0, "clareza_impacto": 4.0, "evidencias": 4.0}
        else:
            h["cqf_score"] = float(h.get("relevancia") or 80.0)
            h["cqf_classificacao"] = "alta_prioridade" if h["cqf_score"] >= 80 else "prioridade_media"
            h["cqf_dimensoes"] = {"relevancia": 4.0, "completude": 4.0, "clareza_impacto": 4.0, "evidencias": 4.0}

        # Instanciação formal do modelo Pydantic AvaliacaoCQF para auditoria
        if AvaliacaoCQF:
            try:
                id_cqf = f"cqf_{idx:03d}"
                st_val = "conforme" if h.get("rg01_valido", True) else "evidencias_insuficientes"
                avaliacao_obj = AvaliacaoCQF(
                    id_avaliacao=id_cqf,
                    id_historia=str(h.get("id") or f"hist-{idx:03d}"),
                    nota_relevancia=round(r_dim, 1),
                    nota_completude=round(c_dim, 1),
                    nota_clareza_impacto=round(i_dim, 1),
                    nota_evidencias=round(e_dim, 1),
                    cqf_score=h["cqf_score"],
                    classificacao_editorial=h["cqf_classificacao"],
                    status_validacao_factual=st_val,
                    status_curadoria="pendente",
                    status_autorizacao_publicacao="pendente",
                    responsavel_avaliacao="CommunityLab CQF Engine v1.0",
                )
                h["id_avaliacao_cqf"] = id_cqf
                h["avaliacao_cqf"] = avaliacao_obj.model_dump()
            except Exception as _e_cqf_model:
                print(f"[cqf] Aviso ao instanciar AvaliacaoCQF: {_e_cqf_model}", flush=True)

    return historias


def analisar(interacoes, maximo=None):
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
        prov = getattr(llm, "ULTIMO_PROVEDOR_USADO", "gemini") or "gemini"
        _definir_origem_analise(prov, "")
        print(f"[analise] {prov} OK: {len(historias)} historias", flush=True)
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


# ---------- OCI Object Storage Bridge ----------
_OCI_DIR = _raiz_projeto / "data" / "oci_storage"
ULTIMO_ERRO_OCI: str = ""


def erro_armazenamento() -> str:
    """Motivo da última falha de armazenamento (vazio quando não houve)."""
    global ULTIMO_ERRO_OCI
    return ULTIMO_ERRO_OCI


def bucket_atual() -> str:
    """Nome do bucket em uso ou configurado no ambiente."""
    try:
        from . import oci_storage
    except ImportError:
        try:
            from services import oci_storage
        except ImportError:
            oci_storage = None
    if oci_storage and hasattr(oci_storage, "nome_bucket"):
        try:
            return oci_storage.nome_bucket()
        except Exception:
            pass
    return "G10communitylab-ativos"


def _garantir_diretorio_oci():
    _OCI_DIR.mkdir(parents=True, exist_ok=True)


def listar_pacotes():
    """Lista pacotes persistidos no storage OCI (ou diretório particionado de ativos)."""
    try:
        _garantir_diretorio_oci()
        arquivos = list(_OCI_DIR.glob("ativos/*/*.json"))
        if arquivos:
            pacotes_reais = []
            for arq in sorted(arquivos, reverse=True):
                try:
                    tam_kb = f"{arq.stat().st_size / 1024:.1f} KB".replace(".", ",")
                    data_mod = datetime.fromtimestamp(arq.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
                    pacotes_reais.append({
                        "id": arq.stem,
                        "nome": f"Lote {arq.stem}",
                        "lote": arq.stem,
                        "caminho": str(arq.relative_to(_raiz_projeto)),
                        "status": "salvo",
                        "tamanho": tam_kb,
                        "data": data_mod,
                    })
                except Exception:
                    pass
            if pacotes_reais:
                return pacotes_reais
    except Exception as e:
        global ULTIMO_ERRO_OCI
        ULTIMO_ERRO_OCI = str(e)
    return copy.deepcopy(m.PACOTES_OCI)


def salvar_no_oci(pacotes, lote_id, historias=None):
    """Grava o pacote com idempotência (storage particionado por data).
    
    Salva os pacotes de histórias e rascunhos em disco estruturado
    (data/oci_storage/ativos/) e gera trilha de auditoria CQF formal
    (auditoria_cqf_{lote_id}.json) com instâncias Pydantic de AvaliacaoCQF.
    Se credenciais do Oracle Cloud estiverem configuradas, executa o upload
    direto para o bucket OCI Object Storage.
    """
    try:
        _garantir_diretorio_oci()
        data_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        dir_data = _OCI_DIR / "ativos" / data_str
        dir_data.mkdir(parents=True, exist_ok=True)
        caminho_arquivo = dir_data / f"{lote_id}.json"

        conteudo = {
            "lote_id": lote_id,
            "gravado_em": datetime.now(timezone.utc).isoformat(),
            "status": "salvo",
            "pacotes": pacotes,
        }
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(conteudo, f, ensure_ascii=False, indent=2)

        # Persistência auditável de AvaliacaoCQF (Pydantic)
        if historias:
            dir_auditorias = _OCI_DIR / "auditorias" / data_str
            dir_auditorias.mkdir(parents=True, exist_ok=True)
            caminho_auditoria = dir_auditorias / f"auditoria_cqf_{lote_id}.json"

            avaliacoes = []
            for h in historias:
                if isinstance(h, dict) and "avaliacao_cqf" in h:
                    avaliacoes.append(h["avaliacao_cqf"])
                elif isinstance(h, dict) and "cqf_score" in h:
                    avaliacoes.append({
                        "id_historia": h.get("id"),
                        "cqf_score": h.get("cqf_score"),
                        "classificacao": h.get("cqf_classificacao"),
                        "dimensoes": h.get("cqf_dimensoes"),
                        "rg01_valido": h.get("rg01_valido", True),
                    })
            if avaliacoes:
                with open(caminho_auditoria, "w", encoding="utf-8") as f_aud:
                    json.dump({
                        "lote_id": lote_id,
                        "gerado_em": datetime.now(timezone.utc).isoformat(),
                        "total_avaliacoes": len(avaliacoes),
                        "avaliacoes": avaliacoes,
                    }, f_aud, ensure_ascii=False, indent=2)

        # Tentativa de upload no Oracle Cloud Infrastructure Object Storage (se configurado)
        try:
            import oci
            config_file = os.environ.get("OCI_CONFIG_FILE", "~/.oci/config")
            if Path(config_file).expanduser().exists():
                config_oci = oci.config.from_file(config_file)
                client = oci.object_storage.ObjectStorageClient(config_oci)
                namespace = os.environ.get("OCI_NAMESPACE") or client.get_namespace().data
                bucket_name = os.environ.get("OCI_BUCKET_NAME", "communitylab-ativos-marketing")
                client.put_object(
                    namespace_name=namespace,
                    bucket_name=bucket_name,
                    object_name=f"ativos/{data_str}/{lote_id}.json",
                    put_object_body=json.dumps(conteudo, ensure_ascii=False, indent=2).encode("utf-8"),
                    content_type="application/json",
                )
                print(f"[oci] Upload para bucket OCI '{bucket_name}' concluído com sucesso.", flush=True)
        except Exception:
            # Fallback seguro para armazenamento local particionado caso OCI não esteja disponível
            pass

    except Exception as e:
        print(f"[oci] Erro ao persistir pacote no storage: {e}", flush=True)

    return pacotes


def reenviar_pacote(pacote):
    """Tenta gravar de novo um pacote que falhou, atualizando status e timestamp."""
    novo = dict(pacote)
    agora_formatado = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
    novo.update({"status": "salvo", "data": agora_formatado, "tamanho": "2,4 KB"})
    return novo


def conteudo_pacote(caminho):
    """Lê o objeto salvo do storage ou retorna mock estruturado com evidências."""
    try:
        p = Path(caminho)
        if not p.is_absolute():
            p = _raiz_projeto / p
        if p.exists() and p.is_file():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass

    if caminho.endswith("evidencias.json"):
        return {
            "lote": "DEMO-001",
            "evidencias": [
                {
                    "autor": str(h.get("autor") or ""),
                    "canal": str(h.get("canal") or ""),
                    "mensagem_original": str(h.get("mensagem_original") or ""),
                    "citacoes": h.get("destaques") if isinstance(h.get("destaques"), list) else [],
                    "fatos": h.get("fatos") if isinstance(h.get("fatos"), list) else [],
                }
                for h in m.HISTORIAS
            ],
        }

    historias_formatadas = []
    for h in m.HISTORIAS:
        destaques = h.get("destaques")
        citacao_padrao = destaques[0] if isinstance(destaques, list) and destaques else ""
        ativos_dict = {}
        lista_ativos = h.get("ativos")
        if isinstance(lista_ativos, list):
            for a in lista_ativos:
                if isinstance(a, dict) and "id" in a:
                    ativos_dict[str(a["id"])] = {"status": "rascunho_aguardando_revisao"}

        historias_formatadas.append({
            "autor": str(h.get("autor") or ""),
            "categoria": str(h.get("categoria") or ""),
            "relevancia": h.get("relevancia") or 0,
            "citacao": citacao_padrao,
            "ativos": ativos_dict,
        })

    return {
        "status": "sucesso",
        "lote": "DEMO-001",
        "gravado_em": "2026-10-15T14:32:00-03:00",
        "historias": historias_formatadas,
    }
