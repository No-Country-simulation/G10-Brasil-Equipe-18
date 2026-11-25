"""Camada de dados do front.

Hoje: devolve dados fictícios (mocks).
Depois: cada função aqui vira uma chamada ao back (Python/n8n/OCI).
As telas só falam com este arquivo, então a troca não mexe nelas.

IMPORTANTE para combinar com o back: o formato dos dicionários abaixo é
PROVISÓRIO. Quem define o contrato oficial é o back.
"""
import csv
import io
import json
from datetime import datetime, timedelta, timezone

from mocks import mock_data as m
from services import cases as _cases
from services import conferencia_citacao as _conf

CAMPOS_OBRIGATORIOS = ("autor", "canal", "texto")

# Avisos e erros de validação de IDs (preenchidos em parse_interacoes)
AVISOS_IDS: list[str] = []
ERRO_IDS_DUPLICADOS: str = ""


def calcular_ids_efetivos(itens: list) -> tuple[list[int], list[str], str]:
    """Calcula IDs efetivos ANTES de qualquer filtro.
    
    Retorna: (ids_efetivos, avisos, erro_duplicados)
    - ids_efetivos: lista de IDs (inteiros >= 1)
    - avisos: mensagens sobre IDs inválidos que viraram posição
    - erro_duplicados: mensagem de erro se houver IDs repetidos (bloqueia importação)
    
    Regras:
    - ID explícito (inteiro >= 1): usa ele
    - ID inválido (0, negativo, texto, booleano, None): usa posição + gera aviso
    - IDs duplicados (inclusive colisão id explícito vs posição): rejeita o lote
    """
    ids_efetivos = []
    avisos = []
    vistos = {}  # {id: [(posicao, autor)]}
    
    for posicao, item in enumerate(itens, start=1):
        id_campo = item.get("id")
        autor = str(item.get("autor", "")).strip()[:30]  # limita para exibição
        
        # Valida se o ID é inteiro >= 1
        id_valido = isinstance(id_campo, int) and id_campo >= 1
        
        if not id_valido and id_campo is not None:
            # ID inválido: gera aviso e usa posição
            tipo_invalido = type(id_campo).__name__
            valor_str = str(id_campo) if not isinstance(id_campo, bool) else repr(id_campo)
            avisos.append(
                f'Interação {posicao} (autor: {autor}): ID inválido ({tipo_invalido}: {valor_str}). '
                f'Usando posição {posicao} como ID.'
            )
            id_efetivo = posicao
        elif id_valido:
            id_efetivo = id_campo
        else:
            # ID ausente: usa posição (sem aviso, é o comportamento normal)
            id_efetivo = posicao
        
        # Registra para detecção de duplicados
        if id_efetivo not in vistos:
            vistos[id_efetivo] = []
        vistos[id_efetivo].append((posicao, autor))
        ids_efetivos.append(id_efetivo)
    
    # Detecta duplicados
    duplicados = {id_: ocorrencias for id_, ocorrencias in vistos.items() if len(ocorrencias) > 1}
    
    if duplicados:
        partes = []
        for id_, ocorrencias in sorted(duplicados.items()):
            autores = ", ".join(f'posição {pos} ({autor})' for pos, autor in ocorrencias)
            partes.append(f'ID {id_}: {autores}')
        
        erro = (
            f'Lote rejeitado: IDs duplicados detectados.\n\n'
            f'Os seguintes IDs aparecem mais de uma vez:\n' +
            '\n'.join(f'• {parte}' for parte in partes) +
            '\n\nCada interação deve ter um ID único. '
            'Corrija o arquivo e tente novamente.'
        )
        return ids_efetivos, avisos, erro
    
    return ids_efetivos, avisos, ""


def id_interacao(interacao, posicao_1indexed):
    """Devolve o ID da interação: campo 'id' se for inteiro >= 1, senão a posição.
    
    Regra idêntica à do llm.py linha 220, centralizada para uso em todas as telas.
    """
    id_lote = interacao.get("id")
    return id_lote if isinstance(id_lote, int) and id_lote >= 1 else posicao_1indexed


# ---------- Conferência de citação ----------
# A regra fica em services/conferencia_citacao.py. Aqui só resolvemos qual
# interação é a origem, para as telas não importarem o módulo direto.
MOTIVO_LITERAL = _conf.MOTIVO_LITERAL
MOTIVO_ANONIMIZADO = _conf.MOTIVO_ANONIMIZADO
MOTIVO_SEM_ID = "ID não informado"
MOTIVO_INDISPONIVEL = "Conferência indisponível"
MOTIVO_VARIAS_ORIGENS = "Conferência indisponível (mais de uma origem)"


def _id_valido(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor >= 1


def conferencia_da_citacao(citacao, interacoes):
    """Confere uma citação contra o texto da interação indicada pelo seu id_interacao.

    Devolve (confere, motivo, id_interacao). confere é True ou False quando a
    conferência rodou, e None quando não deu para conferir (sem ID válido ou
    interação fora do lote). None nunca deve ser exibido como conferido.
    """
    id_int = (citacao or {}).get("id_interacao")
    if not _id_valido(id_int):
        return None, MOTIVO_SEM_ID, None
    original = next(
        (i.get("texto", "") for i in (interacoes or []) if i.get("_id_efetivo") == id_int),
        None,
    )
    if original is None:
        return None, MOTIVO_INDISPONIVEL, id_int
    confere, motivo = _conf.conferir_citacao(citacao.get("texto", ""), original)
    return confere, motivo, id_int


def conferencia_da_citacao_do_ativo(texto, historia, interacoes):
    """Confere a citação editável de um ativo, que não traz id_interacao próprio.

    A origem é interacoes_origem da história. Com mais de uma origem não há
    como saber contra qual conferir, então o resultado fica indisponível.
    """
    origens = (historia or {}).get("interacoes_origem") or []
    if len(origens) > 1:
        return None, MOTIVO_VARIAS_ORIGENS, None
    id_int = origens[0] if origens else None
    return conferencia_da_citacao({"texto": texto, "id_interacao": id_int}, interacoes)


MOTIVO_CASE_LITERAL = "Texto composto só por trechos da mensagem original"
MOTIVO_CASE_FORA_DA_FONTE = "Há trechos que não estão na mensagem original"
MOTIVO_CASE_TEXTO_VAZIO = "Texto vazio"


def conferencia_do_texto_case(texto, fonte):
    """Confere o texto editado do case com a regra do preparar_case.

    Cada parágrafo precisa ser um trecho literal da fonte, na ordem. A fonte é
    a mensagem original da história (a mesma que o preparar_case usou).
    Devolve (confere, motivo); confere é None quando não há fonte para conferir
    ou quando o texto está vazio (nada a conferir nunca vira "confere").
    """
    if not (texto or "").strip():
        return None, MOTIVO_CASE_TEXTO_VAZIO
    if not (fonte or "").strip():
        return None, MOTIVO_INDISPONIVEL
    paragrafos = _cases.dividir_paragrafos(texto or "")
    if _cases.paragrafos_literais_em_ordem(paragrafos, fonte):
        return True, MOTIVO_CASE_LITERAL
    return False, MOTIVO_CASE_FORA_DA_FONTE


# ---------- Ingestão ----------
def _normalizar(itens):
    global AVISOS_IDS, ERRO_IDS_DUPLICADOS
    AVISOS_IDS = []
    ERRO_IDS_DUPLICADOS = ""
    
    if not isinstance(itens, list) or not itens:
        raise ValueError("O arquivo precisa conter uma lista com pelo menos uma interação.")
    
    # Calcula IDs efetivos ANTES de qualquer validação (regra B)
    ids_efetivos, avisos, erro_duplicados = calcular_ids_efetivos(itens)
    AVISOS_IDS = avisos
    ERRO_IDS_DUPLICADOS = erro_duplicados
    
    # Se houver IDs duplicados, rejeita o lote inteiro
    if erro_duplicados:
        raise ValueError(erro_duplicados)
    
    saida = []
    for i, item in enumerate(itens, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Interação {i}: formato inválido.")
        faltando = [c for c in CAMPOS_OBRIGATORIOS if not str(item.get(c, "")).strip()]
        if faltando:
            raise ValueError(f"Interação {i}: faltam os campos {', '.join(faltando)}.")
        normalizado = {
            "autor": str(item["autor"]).strip(),
            "canal": str(item["canal"]).strip(),
            "tipo": str(item.get("tipo") or "mensagem").strip(),
            "texto": str(item["texto"]).strip(),
        }
        # Preserva o campo id se for inteiro >= 1
        if "id" in item and isinstance(item["id"], int) and item["id"] >= 1:
            normalizado["id"] = item["id"]
        # Adiciona _id_efetivo para uso interno (preservado em filtros)
        normalizado["_id_efetivo"] = ids_efetivos[i - 1]
        saida.append(normalizado)
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


def interacoes_demo_json():
    """Devolve o JSON demonstrativo para a tela de importação."""
    return json.dumps(m.INTERACOES, ensure_ascii=False, indent=2)


def parse_interacoes(nome_arquivo, conteudo):
    """Lê um arquivo CSV ou JSON enviado no upload."""
    nome = nome_arquivo.lower()
    try:
        texto = conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("Não foi possível ler o arquivo. Salve-o em UTF-8.")
    if nome.endswith(".json"):
        return interacoes_de_json(texto)
    if nome.endswith(".csv"):
        return _normalizar(list(csv.DictReader(io.StringIO(texto))))
    raise ValueError("Formato não suportado. Envie um arquivo CSV ou JSON.")


def avisos_validacao_ids():
    """Retorna lista de avisos sobre IDs inválidos detectados na última importação."""
    return AVISOS_IDS.copy()


# ---------- Análise ----------
ORIGEM_ANALISE = "mock"   # "gemini" quando a análise real responde
ULTIMO_ERRO = ""          # preenchido quando a análise real falha
ULTIMO_ERRO_TRUNCADO = False  # True quando a falha foi corte por limite de saída


ULTIMO_ERRO_OCI = ""


def _storage():
    """Importa o modulo de storage; None quando indisponivel."""
    global ULTIMO_ERRO_OCI
    try:
        from . import oci_storage  # import local: evita custo quando nao usado
    except ImportError:
        try:
            from services import oci_storage  # type: ignore
        except ImportError:
            return None
    if not oci_storage.disponivel():
        motivo = ""
        if hasattr(oci_storage, "motivo_indisponivel"):
            motivo = oci_storage.motivo_indisponivel()
        ULTIMO_ERRO_OCI = motivo or "OCI indisponivel: credencial nao configurada"
        return None
    return oci_storage


def _registrar_erro_oci(erro):
    global ULTIMO_ERRO_OCI
    ULTIMO_ERRO_OCI = str(erro)
    print(f"[oci] falhou: {ULTIMO_ERRO_OCI}", flush=True)


def _fuso_brasil():
    """Fuso de São Paulo, com queda para UTC-3 fixo.

    Desde 2019 o Brasil não tem horário de verão, então UTC-3 é o valor
    correto o ano inteiro. O fallback existe para imagem sem base de fusos,
    como alguns containers mínimos.
    """
    try:
        from zoneinfo import ZoneInfo

        return ZoneInfo("America/Sao_Paulo")
    except Exception:  # pragma: no cover - depende da imagem
        return timezone(timedelta(hours=-3))


def _data_br(iso: str) -> str:
    """Converte o instante ISO para o fuso de São Paulo: 22/10/2026 01:05.

    Aceita offset explícito, sufixo Z e data sem fuso (tratada como UTC, que é
    como o bucket grava). Se o texto não for um instante válido, devolve o que
    veio, só com a formatação antiga, sem levantar erro.
    """
    texto = (iso or "").strip()
    if not texto:
        return ""
    try:
        from datetime import datetime

        momento = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        momento = None

    if momento is not None:
        if momento.tzinfo is None:
            momento = momento.replace(tzinfo=timezone.utc)
        return momento.astimezone(_fuso_brasil()).strftime("%d/%m/%Y %H:%M")

    legivel = texto.replace("T", " ")
    if len(legivel) < 16:
        return legivel
    data, hora = legivel[:10], legivel[11:16]
    partes = data.split("-")
    if len(partes) != 3:
        return legivel
    return f"{partes[2]}/{partes[1]}/{partes[0]} {hora}"


def analisar(interacoes):
    """Analisa o lote com o provedor de LLM; falhas não viram histórias fictícias."""
    global ORIGEM_ANALISE, ULTIMO_ERRO, ULTIMO_ERRO_TRUNCADO
    try:
        from . import llm  # import local: evita custo quando não usado
    except ImportError:  # pragma: no cover - execução como pacote vs. script
        from services import llm  # type: ignore

    try:
        historias = llm.analisar(interacoes)
        ORIGEM_ANALISE = llm.ULTIMO_PROVEDOR or "gemini"
        ULTIMO_ERRO = ""
        ULTIMO_ERRO_TRUNCADO = False
        print(f"[analise] concluída: {len(historias)} histórias", flush=True)
        return historias
    except Exception as erro:  # rede, chave ausente, JSON inválido
        ULTIMO_ERRO = str(erro)
        ORIGEM_ANALISE = "erro"
        ULTIMO_ERRO_TRUNCADO = isinstance(erro, getattr(llm, "ErroRespostaTruncada", ()))
        print(f"[analise] FALHOU: {ULTIMO_ERRO}", flush=True)
        raise RuntimeError(f"Análise real falhou: {erro}") from erro


def regenerar(historia, ativo_id, vez):
    """TODO(back): pedir um novo rascunho. Aqui alterna entre as variações já fornecidas; sem variações, devolve {} e nada muda."""
    for ativo in historia["ativos"]:
        if ativo["id"] == ativo_id:
            variacoes = ativo.get("variacoes") or []
            if not variacoes:
                return {}
            opcoes = [ativo["campos"]] + variacoes
            return dict(opcoes[vez % len(opcoes)])
    return {}


# ---------- OCI ----------
def erro_armazenamento():
    """Motivo da ultima falha de armazenamento (vazio quando nao houve)."""
    return ULTIMO_ERRO_OCI


def bucket_atual():
    """Nome do bucket em uso. Vazio quando nao ha acesso a OCI."""
    armazenamento = _storage()
    if armazenamento is None:
        return ""
    try:
        return armazenamento.nome_bucket()
    except Exception:
        return ""


def pacotes_do_lote(lote_id):
    """Arquivos que este lote precisa gravar no bucket."""
    from . import oci_storage  # import local, como em _storage()

    return [
        {"caminho": oci_storage.caminho_do_lote(lote_id, "pacote-distribuicao.json")},
        {"caminho": oci_storage.caminho_do_lote(lote_id, "evidencias.json")},
    ]

def listar_pacotes():
    """Lista os pacotes realmente salvos no bucket.

    Sem credencial nao existe persistencia: a lista volta vazia, em vez de
    mostrar objetos ficticios como se estivessem gravados.
    """
    global ULTIMO_ERRO_OCI
    armazenamento = _storage()
    if armazenamento is None:
        ULTIMO_ERRO_OCI = ULTIMO_ERRO_OCI or "OCI indisponivel: credencial nao configurada"
        return []
    ULTIMO_ERRO_OCI = ""
    try:
        itens = armazenamento.listar_pacotes()
    except Exception as erro:
        # Falha operacional fica visivel: lista vazia + motivo registrado.
        _registrar_erro_oci(erro)
        return []
    return [
        {
            "caminho": item["caminho"],
            "lote": item["lote"],
            "data": _data_br(item.get("salvo_em")),
            "tamanho": item.get("tamanho"),
            "status": "salvo",
            "persistencia": "real",
	    "salvo_em": item.get("salvo_em"),
        }
        for item in itens
    ]


NATUREZAS_DADOS = ("ficticios", "reais", "nao_informado")
NATUREZA_DADOS_PADRAO = "nao_informado"


def normalizar_natureza_dados(valor):
    """Devolve a natureza declarada, ou o padrao quando ausente/invalida.

    A ausencia nao e erro: lote antigo, gravado antes deste campo, e lido como
    "nao informado" — o mesmo que a tela mostra. Valor fora da lista tambem cai
    no padrao, porque o selo so pode afirmar o que foi declarado.
    """
    texto = str(valor or "").strip().lower()
    return texto if texto in NATUREZAS_DADOS else NATUREZA_DADOS_PADRAO


def salvar_no_oci(pacotes, lote_id, historias=None, natureza_dados=None, *, origem_analise=None):
    """Grava os pacotes do lote no bucket.

    O caminho e montado pelo backend a partir do lote e do nome do arquivo,
    entao repetir a gravacao sobrescreve em vez de duplicar (idempotente).
    Sem credencial, nada e gravado: o item volta como falha de simulacao.
    Sem conteudo, nada e gravado: o item volta como falha, para nao salvar
    um arquivo apenas com metadados.

    `natureza_dados` e a declaracao feita na importacao (ficticios, reais ou
    nao_informado). Ausente ou invalida, entra o padrao `nao_informado`: o selo
    so afirma o que foi declarado, nunca deduz do autor, do texto ou do provedor.
    """
    if historias is None:
        return [
            {
                **dict(pacote),
                "status": "falhou",
                "persistencia": "nenhuma",
                "motivo": "Sem conteudo para gravar: a analise nao foi informada",
                "data": None,
                "tamanho": None,
            }
            for pacote in pacotes
        ]

    if not isinstance(historias, (list, tuple)):
        return [
            {
                **dict(pacote),
                "status": "falhou",
                "persistencia": "nenhuma",
                "motivo": "Conteudo em formato invalido: esperada uma lista de historias",
                "data": None,
                "tamanho": None,
            }
            for pacote in pacotes
        ]

    # lista vazia e resultado valido: o lote foi processado e nao havia
    # historias elegiveis. Nao e falha tecnica.
    historias = list(historias)

    conteudo = {
        "versao_schema": "1.1",
        "lote": lote_id,
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "origem_analise": str(origem_analise or "nao_informado"),
        "natureza_dados": normalizar_natureza_dados(natureza_dados),
        "historias": historias,
        "evidencias": [
            {"id_interacao": c.get("id_interacao"), "texto": c.get("texto")}
            for h in historias
            for c in (h.get("citacoes") or [])
        ],
    }

    armazenamento = _storage()
    if armazenamento is None:
        return [
            {
                **dict(pacote),
                "status": "falhou",
                "persistencia": "simulada",
                "motivo": ULTIMO_ERRO_OCI or "OCI indisponivel: credencial nao configurada",
                "data": None,
                "tamanho": None,
            }
            for pacote in pacotes
        ]

    atualizados = []
    for pacote in pacotes:
        caminho = armazenamento.caminho_do_lote(lote_id, pacote.get("caminho"))
        try:
            if "evidencia" in caminho:
                dados = {
                    "versao_schema": "1.0",
                    "lote": lote_id,
                    "gerado_em": conteudo["gerado_em"],
                    "evidencias": conteudo["evidencias"],
                }
            else:
                dados = conteudo
            resultado = armazenamento.salvar_objeto(caminho, dados)
            novo = dict(pacote)
            novo.update(
                {
                    "caminho": caminho,
                    "lote": lote_id,
                    "data": _data_br(resultado.get("salvo_em")),
                    "tamanho": resultado.get("tamanho"),
                    "status": "salvo",
                    "persistencia": "real",
                    "motivo": None,
                }
            )
        except Exception as erro:
            _registrar_erro_oci(erro)
            novo = dict(pacote)
            novo.update(
                {
                    "caminho": caminho,
                    "lote": lote_id,
                    "status": "falhou",
                    "persistencia": "real",
                    "motivo": str(erro),
                    "data": None,
                    "tamanho": None,
                }
            )
        atualizados.append(novo)
    return atualizados


def reenviar_pacote(pacote):
    """Tenta gravar de novo um pacote que falhou."""
    armazenamento = _storage()
    if armazenamento is None:
        novo = dict(pacote)
        novo.update(
            {
                "status": "falhou",
                "persistencia": "simulada",
                "motivo": ULTIMO_ERRO_OCI or "OCI indisponivel: credencial nao configurada",
                "data": None,
                "tamanho": None,
            }
        )
        return novo

    lote = pacote.get("lote") or ""
    caminho = armazenamento.caminho_do_lote(lote, pacote.get("caminho"))
    try:
        resultado = armazenamento.salvar_objeto(caminho, pacote)
    except Exception as erro:
        _registrar_erro_oci(erro)
        novo = dict(pacote)
        novo.update({"status": "falhou", "persistencia": "real", "motivo": str(erro)})
        return novo
    novo = dict(pacote)
    novo.update(
        {
            "caminho": caminho,
            "status": "salvo",
            "persistencia": "real",
            "motivo": None,
            "data": _data_br(resultado.get("salvo_em")),
            "tamanho": resultado.get("tamanho"),
        }
    )
    return novo


def conteudo_pacote(caminho):
    """Le o JSON de um objeto do bucket.

    Devolve None quando o objeto nao existe ou a leitura falha -- nunca um
    conteudo ficticio com aparencia de sucesso.
    """
    armazenamento = _storage()
    if armazenamento is None:
        global ULTIMO_ERRO_OCI
        ULTIMO_ERRO_OCI = ULTIMO_ERRO_OCI or "OCI indisponivel: credencial nao configurada"
        return None
    try:
        return armazenamento.ler_objeto(str(caminho))
    except Exception as erro:
        _registrar_erro_oci(erro)
        return None


CAMINHO_CURSOR_DISCORD = "discord/cursor.json"
MARCADOR_ULTIMO_ID_DISCORD = "__ultimo_id_discord__:"


def campo_do_parecer(status):
    """Campo do estado que guarda o parecer vigente deste status editorial.

    O envelope do Card 05 tem um campo só para o parecer, mas a Curadoria
    grava textos em dois: observação de ajuste e motivo de rejeição. Devolver
    None quer dizer que o status atual não tem parecer pendente a registrar.
    """
    return {"ajustes": "observacoes", "rejeitado": "motivos"}.get(status)


def parecer_do_estado(status, chave, observacoes, motivos):
    """Parecer do ativo escolhido pelo status, nunca pela ordem dos campos.

    Antes valia a primeira chave preenchida (`observacoes or motivos`): depois
    de "Solicitar ajustes", a rejeição gravava o motivo em `motivos` mas o
    pacote saía com a observação antiga. O texto que vale é o do estado atual.
    """
    campo = campo_do_parecer(status)
    if campo is None:
        return ""
    origem = observacoes if campo == "observacoes" else motivos
    return str(origem.get(chave) or "").strip()


def montar_bloco_curadoria(lote_id, historias, estado):
    """Monta as decisões de Curadoria no formato do envelope do Card 05.

    Cada linha liga um ativo às três dimensões independentes — validação
    factual, status editorial e autorização — mais o parecer escrito pelo
    curador. As dimensões não se misturam: aprovado não é autorizado, e
    validado não é aprovado.
    """
    observacoes = estado.get("observacoes") or {}
    motivos = estado.get("motivos") or {}
    validacao = estado.get("validacao_factual") or {}
    status_editorial = estado.get("status_curadoria") or {}
    autorizacao = estado.get("autorizacao") or {}

    linhas = []
    for historia in historias or []:
        id_historia = historia.get("id")
        for ativo in historia.get("ativos") or []:
            id_ativo = ativo.get("id")
            if id_historia is None or id_ativo is None:
                continue
            chave = f"{id_historia}:{id_ativo}"
            status_ativo = status_editorial.get(chave, "rascunho")
            linhas.append(
                {
                    "lote": lote_id,
                    "id_historia": str(id_historia),
                    "id_ativo": str(id_ativo),
                    "validacao_factual": validacao.get(chave, "pendente"),
                    "status_curadoria": status_ativo,
                    "autorizacao": autorizacao.get(chave, "nao_registrada"),
                    "parecer": parecer_do_estado(status_ativo, chave, observacoes, motivos),
                }
            )
    return linhas


def decisoes_do_bloco(conteudo):
    """Decisões de um pacote, por chave "historia:ativo".

    Pacote gravado antes deste bloco devolve vazio, em vez de erro: é o caso
    de todo lote anterior a esta mudança.
    """
    if not isinstance(conteudo, dict):
        return {}
    bloco = conteudo.get("curadoria")
    if not isinstance(bloco, list):
        return {}
    decisoes = {}
    for linha in bloco:
        if not isinstance(linha, dict):
            continue
        id_historia = linha.get("id_historia")
        id_ativo = linha.get("id_ativo")
        if id_historia is None or id_ativo is None:
            continue
        decisoes[f"{id_historia}:{id_ativo}"] = {
            "validacao_factual": linha.get("validacao_factual", "pendente"),
            "status_curadoria": linha.get("status_curadoria", "rascunho"),
            "autorizacao": linha.get("autorizacao", "nao_registrada"),
            "parecer": linha.get("parecer", ""),
        }
    return decisoes


def ler_decisoes(caminho):
    """Decisões guardadas no pacote; vazio quando não há bloco ou a leitura falha."""
    return decisoes_do_bloco(conteudo_pacote(caminho))


def _eh_pacote_principal(caminho):
    return bool(caminho) and "evidencia" not in str(caminho)


def _pasta_do_lote(caminho):
    partes = str(caminho).split("/")
    return partes[1] if len(partes) >= 2 else ""


def _historia_no_formato_do_app(historia):
    """Mínimo que as telas exigem: dict com "id" e "ativos" em lista."""
    return (
        isinstance(historia, dict)
        and historia.get("id") not in (None, "")
        and isinstance(historia.get("ativos"), list)
    )


def recuperar_lote(caminho):
    """Lê um lote salvo no bucket e devolve o que a sessão precisa para reabri-lo.

    Só lê: nunca chama a IA nem grava. O pacote não guarda as interações
    originais, então elas não voltam. Lote antigo (1.0), sem natureza ou sem
    bloco de curadoria, abre com os padrões e um aviso, sem inventar dados.
    Falha vira {"ok": False, "motivo": ...}.
    """
    falha = lambda motivo: {"ok": False, "motivo": motivo}  # noqa: E731

    if not _eh_pacote_principal(caminho):
        return falha("Este objeto não é o pacote principal do lote.")

    avisos = []
    # O caminho é fixo por lote; se mesmo assim houver mais de um pacote
    # principal na pasta, vale o mais recente.
    pasta = _pasta_do_lote(caminho)
    irmaos = [
        p for p in listar_pacotes()
        if p.get("status") == "salvo" and _pasta_do_lote(p.get("caminho")) == pasta
    ]
    principais = [p for p in irmaos if _eh_pacote_principal(p.get("caminho"))]
    if len(principais) > 1:
        escolhido = max(principais, key=lambda p: p.get("salvo_em") or "")
        if escolhido["caminho"] != caminho:
            caminho = escolhido["caminho"]
        avisos.append("Há mais de um pacote deste lote; foi aberto o mais recente.")

    conteudo = conteudo_pacote(caminho)
    if conteudo is None:
        return falha(ULTIMO_ERRO_OCI or "Não foi possível ler o pacote no bucket.")
    if not isinstance(conteudo, dict) or not isinstance(conteudo.get("historias"), list):
        return falha("O pacote está em formato inesperado: não há lista de histórias.")

    # Recusa o pacote inteiro se alguma história não tem o formato do app: as
    # telas usam "id" e "ativos", e descartar histórias aqui as apagaria do
    # bucket na próxima decisão (salvar_decisoes regrava a lista inteira).
    invalidas = [h for h in conteudo["historias"] if not _historia_no_formato_do_app(h)]
    if invalidas:
        total = len(conteudo["historias"])
        if len(invalidas) == total:
            return falha("Este pacote não tem histórias no formato do app e não pode ser reaberto.")
        return falha(
            f"Este pacote tem {len(invalidas)} de {total} histórias fora do formato do app "
            "e não pode ser reaberto."
        )

    decisoes = decisoes_do_bloco(conteudo)
    if not decisoes:
        avisos.append(
            "Este lote não tem decisões de curadoria gravadas. "
            "Tudo abre como pendente, em rascunho e sem autorização."
        )
    versao = str(conteudo.get("versao_schema") or "")
    pacotes = [
        {"caminho": p["caminho"], "lote": p.get("lote"), "data": p.get("data"),
         "tamanho": p.get("tamanho"), "status": "salvo", "persistencia": "real",
         "salvo_em": p.get("salvo_em")}
        for p in irmaos
        if p["caminho"] == caminho or not _eh_pacote_principal(p["caminho"])
    ]
    if not any(p["caminho"] == caminho for p in pacotes):
        pacotes.insert(0, {"caminho": caminho, "lote": pasta, "status": "salvo", "persistencia": "real"})
    return {
        "ok": True,
        "motivo": None,
        "lote_id": str(conteudo.get("lote") or pasta),
        "versao_schema": versao,
        "origem_analise": str(conteudo.get("origem_analise") or ""),
        "natureza_dados": normalizar_natureza_dados(conteudo.get("natureza_dados")),
        "historias": conteudo["historias"],
        "decisoes": decisoes,
        "pacotes": pacotes,
        "avisos": avisos,
    }


def aplicar_edicoes(historias, edicoes):
    """Devolve as histórias com os campos editados na sessão aplicados.

    As edições vivem na sessão, em chaves `c:<historia>:<ativo>:<campo>`. O
    envelope do Card 05 (§4.6) pede os campos estruturados preservados, então
    o pacote passa a guardar o texto como o curador deixou — sem isso, reabrir
    um lote devolveria o texto da IA e perderia a revisão.
    """
    edicoes = edicoes or {}
    resultado = []
    for historia in historias or []:
        nova = dict(historia)
        id_historia = historia.get("id")
        ativos = []
        for ativo in historia.get("ativos") or []:
            novo_ativo = dict(ativo)
            id_ativo = ativo.get("id")
            campos = dict(ativo.get("campos") or {})
            editado = False
            for nome_campo in list(campos):
                chave = f"c:{id_historia}:{id_ativo}:{nome_campo}"
                if chave in edicoes and edicoes[chave] is not None:
                    campos[nome_campo] = str(edicoes[chave])
                    editado = True
            # Só mexe no formato quando havia campos ou quando houve edição:
            # ativo sem campos continua sem o bloco, em vez de ganhar um vazio.
            if "campos" in ativo or editado:
                novo_ativo["campos"] = campos
            ativos.append(novo_ativo)
        nova["ativos"] = ativos
        resultado.append(nova)
    return resultado


def salvar_decisoes(lote_id, caminho, historias, estado, edicoes=None):
    """Acrescenta o bloco de curadoria ao pacote gravado e regrava no mesmo caminho.

    Lê o pacote antes de escrever, em vez de remontar o conteúdo a partir da
    tela: assim um lote gravado antes deste bloco também aceita decisão nova, e
    o risco de apagar histórias cai. Também grava os campos com as edições do
    curador, para a revisão não se perder ao reabrir o lote.
    Devolve {"ok", "motivo", "data"}.
    """
    armazenamento = _storage()
    if armazenamento is None:
        return {
            "ok": False,
            "motivo": ULTIMO_ERRO_OCI or "OCI indisponivel: credencial nao configurada",
            "data": None,
        }

    try:
        atual = armazenamento.ler_objeto(str(caminho))
    except Exception as erro:
        _registrar_erro_oci(erro)
        return {"ok": False, "motivo": str(erro), "data": None}

    if not isinstance(atual, dict) or not atual:
        return {"ok": False, "motivo": "Pacote não encontrado no bucket: nada foi gravado", "data": None}

    atual["historias"] = aplicar_edicoes(historias, edicoes)
    atual["curadoria"] = montar_bloco_curadoria(lote_id, historias, estado)
    try:
        resultado = armazenamento.salvar_objeto(str(caminho), atual)
    except Exception as erro:
        _registrar_erro_oci(erro)
        return {"ok": False, "motivo": str(erro), "data": None}

    return {"ok": True, "motivo": None, "data": _data_br(resultado.get("salvo_em"))}


def buscar_mensagens_discord(canal_id=None, after_id=None, limite=50):
    """Busca mensagens no Discord usando o contrato do serviço de ingestão."""
    from src.ingestion.discord_load import buscar_mensagens_discord as buscar

    return buscar(limite=limite, canal_id=canal_id, after_id=after_id)


def after_id_discord(avisos):
    """Extrai dos avisos o cursor mais recente devolvido pela ingestão."""
    for aviso in avisos or []:
        if isinstance(aviso, str) and aviso.startswith(MARCADOR_ULTIMO_ID_DISCORD):
            valor = aviso[len(MARCADOR_ULTIMO_ID_DISCORD):]
            return valor or None
    return None


def carregar_cursor_discord():
    """Lê o último ID do Discord salvo no OCI; None se ainda não existir."""
    armazenamento = _storage()
    if armazenamento is None:
        raise RuntimeError(ULTIMO_ERRO_OCI or "OCI indisponível.")
    try:
        cursor = armazenamento.ler_objeto(CAMINHO_CURSOR_DISCORD)
    except Exception as erro:
        _registrar_erro_oci(erro)
        raise RuntimeError(str(erro)) from erro

    if cursor is None:
        return None
    if not isinstance(cursor, dict):
        raise RuntimeError("O cursor do Discord no OCI está em formato inválido.")

    after_id = cursor.get("after_id")
    return str(after_id) if after_id else None


def salvar_cursor_discord(after_id):
    """Salva o último ID importado em discord/cursor.json."""
    if not after_id:
        raise ValueError("after_id é obrigatório para salvar o cursor do Discord.")

    armazenamento = _storage()
    if armazenamento is None:
        raise RuntimeError(ULTIMO_ERRO_OCI or "OCI indisponível.")
    try:
        return armazenamento.salvar_objeto(
            CAMINHO_CURSOR_DISCORD,
            {"after_id": str(after_id)},
        )
    except Exception as erro:
        _registrar_erro_oci(erro)
        raise RuntimeError(str(erro)) from erro
