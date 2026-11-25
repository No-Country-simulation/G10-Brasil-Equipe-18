"""Módulo de ingestão de dados (CSV e JSON).

Responsável por receber o texto decodificado, validar formatos, aplicar 
a pseudonimização de autores e retornar interações estruturadas ou rejeições.
"""
import json
import csv
import io
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

def pseudonimizar_autor(autor_original: str, sal: str) -> str:
    """Gera pseudonimo HMAC de 20 digitos; preserva IDs numericos legados."""
    autor_str = str(autor_original or "").strip()
    if not autor_str:
        return "membro_000000"
    if autor_str.startswith("membro_") and autor_str[7:].isascii() and autor_str[7:].isdigit() and len(autor_str[7:]) >= 3:
        return autor_str
    digest = hmac.new(sal.encode("utf-8"), autor_str.encode("utf-8"), hashlib.sha256).digest()
    return f"membro_{int.from_bytes(digest, 'big') % 10**20:020d}"


def processar_json(conteudo_texto: str, sal: str, origem_padrao: str = "discord") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    """Processa conteúdo JSON (lista de interações ou objeto de lote)."""
    interacoes_validas = []
    rejeitadas = []
    avisos = []
    mapeamento_autores: Dict[str, str] = {}
    
    try:
        dados = json.loads(conteudo_texto)
    except json.JSONDecodeError as e:
        rejeitadas.append({"posicao": 0, "motivo": f"JSON inválido: {e}", "original": {}})
        return interacoes_validas, rejeitadas, avisos

    # Trata formato de lote ou lista direta
    if isinstance(dados, dict) and "interacoes" in dados:
        lista_bruta = dados["interacoes"]
    elif isinstance(dados, list):
        lista_bruta = dados
    else:
        rejeitadas.append({"posicao": 0, "motivo": "Estrutura JSON não reconhecida (esperada lista ou objeto com chave 'interacoes')", "original": dados})
        return interacoes_validas, rejeitadas, avisos

    for idx, item in enumerate(lista_bruta, start=1):
        if not isinstance(item, dict):
            rejeitadas.append({"posicao": idx, "motivo": "Item não é um dicionário válido", "original": item})
            continue
            
        texto = item.get("texto") or item.get("content")
        if not texto or not str(texto).strip():
            rejeitadas.append({"posicao": idx, "motivo": "Texto vazio ou ausente", "original": item})
            continue
            
        autor_bruto = str(item.get("autor") or item.get("autor_id") or "desconhecido").strip()
        autor_id = pseudonimizar_autor(autor_bruto, sal)
        
        # Detecta colisões dentro do lote
        if autor_id in mapeamento_autores and mapeamento_autores[autor_id] != autor_bruto:
            avisos.append(f"Detectada colisão de pseudonimização para o autor_id '{autor_id}' no lote.")
            rejeitadas.append({"posicao": 0, "motivo": "Lote bloqueado por colisao de pseudonimizacao", "original": {}})
            return [], rejeitadas, avisos
        else:
            mapeamento_autores[autor_id] = autor_bruto

        # Valida e converte id para inteiro >= 1
        id_bruto = item.get("id", idx)
        try:
            id_int = int(id_bruto)
            if id_int < 1:
                id_int = idx
        except (ValueError, TypeError):
            id_int = idx
        
        interacao_estruturada = {
            "versao_schema": "1.0",
            "id": id_int,
            "autor_id": autor_id,
            "data": item.get("data", datetime.now(timezone.utc).isoformat()),
            "origem": item.get("origem", origem_padrao),
            "texto": str(texto).strip(),
            "status_revisao": "pendente"
        }
        
        interacoes_validas.append(interacao_estruturada)
        
    return interacoes_validas, rejeitadas, avisos

def processar_csv(conteudo_texto: str, sal: str, origem_padrao: str = "discord") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    """Processa conteúdo CSV detectando separador (',' ou ';') e colunas padrão."""
    interacoes_validas = []
    rejeitadas = []
    avisos = []
    mapeamento_autores: Dict[str, str] = {}
    
    f = io.StringIO(conteudo_texto)
    try:
        # Detecta o dialeto do CSV (delimitador vírgula ou ponto e vírgula)
        amostra = f.read(2048)
        f.seek(0)
        try:
            dialecto = csv.Sniffer().sniff(amostra, delimiters=",;")
        except csv.Error:
            dialecto = csv.excel
            dialecto.delimiter = ","
            avisos.append("Não foi possível detectar o delimitador com precisão; assumida a vírgula.")

        leitor = csv.DictReader(f, dialect=dialecto)
        
        if not leitor.fieldnames:
            rejeitadas.append({"posicao": 0, "motivo": "CSV sem cabeçalho válido", "original": {}})
            return interacoes_validas, rejeitadas, avisos

        for idx, linha in enumerate(leitor, start=1):
            texto = linha.get("texto") or linha.get("content")
            if not texto or not str(texto).strip():
                rejeitadas.append({"posicao": idx, "motivo": "Campo texto vazio ou ausente", "original": linha})
                continue
                
            autor_bruto = str(linha.get("autor") or linha.get("autor_id") or "desconhecido").strip()
            autor_id = pseudonimizar_autor(autor_bruto, sal)
            
            # Detecta colisões dentro do lote
            if autor_id in mapeamento_autores and mapeamento_autores[autor_id] != autor_bruto:
                avisos.append(f"Detectada colisão de pseudonimização para o autor_id '{autor_id}' no lote.")
                rejeitadas.append({"posicao": 0, "motivo": "Lote bloqueado por colisao de pseudonimizacao", "original": {}})
                return [], rejeitadas, avisos
            else:
                mapeamento_autores[autor_id] = autor_bruto
            
            # Tenta converter ID para inteiro >= 1
            try:
                id_int = int(linha.get("id", idx))
                if id_int < 1:
                    id_int = idx
            except (ValueError, TypeError):
                id_int = idx

            interacao_estruturada = {
                "versao_schema": "1.0",
                "id": id_int,
                "autor_id": autor_id,
                "data": linha.get("data", datetime.now(timezone.utc).isoformat()),
                "origem": linha.get("origem", origem_padrao),
                "texto": str(texto).strip(),
                "status_revisao": "pendente"
            }
            
            interacoes_validas.append(interacao_estruturada)
            
    except Exception as e:
        rejeitadas.append({"posicao": 0, "motivo": f"Erro ao processar CSV: {e}", "original": {}})
        
    return interacoes_validas, rejeitadas, avisos

def processar_dataframe(
    df: Any, 
    sal: str, 
    origem_padrao: str = "discord"
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    """Processa um pandas DataFrame contendo interações brutas de comunidades.
    
    Espera colunas como 'texto' (ou 'content'), 'autor' (ou 'autor_id'), e opcionalmente 'id', 'data', 'origem'.
    """
    import pandas as pd
    if not isinstance(df, pd.DataFrame):
        raise TypeError("O parâmetro 'df' deve ser uma instância de pandas.DataFrame.")
        
    interacoes_validas = []
    rejeitadas = []
    avisos = []
    mapeamento_autores: Dict[str, str] = {}

    for idx, row in df.iterrows():
        pos = idx + 1 if isinstance(idx, int) else 1
        dicionario = row.to_dict()
        
        texto = dicionario.get("texto") or dicionario.get("content")
        if pd.isna(texto) or not str(texto).strip():
            rejeitadas.append({"posicao": pos, "motivo": "Campo texto vazio ou ausente", "original": dicionario})
            continue

        autor_bruto = str(dicionario.get("autor") or dicionario.get("autor_id") or "desconhecido").strip()
        autor_id = pseudonimizar_autor(autor_bruto, sal)

        if autor_id in mapeamento_autores and mapeamento_autores[autor_id] != autor_bruto:
            avisos.append(f"Detectada colisão de pseudonimização para o autor_id '{autor_id}' no lote.")
            rejeitadas.append({"posicao": 0, "motivo": "Lote bloqueado por colisao de pseudonimizacao", "original": {}})
            return [], rejeitadas, avisos
        else:
            mapeamento_autores[autor_id] = autor_bruto

        id_raw = dicionario.get("id", pos)
        try:
            id_int = int(id_raw)
            if id_int < 1:
                id_int = pos
        except (ValueError, TypeError):
            id_int = pos

        data_raw = dicionario.get("data")
        data_str = str(data_raw) if not pd.isna(data_raw) and str(data_raw).strip() else datetime.now(timezone.utc).isoformat()
        origem_str = str(dicionario.get("origem") or origem_padrao).strip()

        interacao_estruturada = {
            "versao_schema": "1.0",
            "id": id_int,
            "autor_id": autor_id,
            "data": data_str,
            "origem": origem_str,
            "texto": str(texto).strip(),
            "status_revisao": "pendente"
        }
        interacoes_validas.append(interacao_estruturada)

    return interacoes_validas, rejeitadas, avisos

def interacoes_para_dataframe(interacoes: List[Dict[str, Any]]) -> Any:
    """Converte uma lista de interações estruturadas em um pandas DataFrame para análise e manipulação tabular."""
    import pandas as pd
    if not interacoes:
        return pd.DataFrame(columns=["versao_schema", "id", "autor_id", "data", "origem", "texto", "status_revisao"])
    
    # Achata análise caso presente
    linhas = []
    for item in interacoes:
        linha = item.copy()
        analise = linha.pop("analise", None)
        if analise and isinstance(analise, dict):
            for k, v in analise.items():
                linha[f"analise_{k}"] = v
        linhas.append(linha)
        
    return pd.DataFrame(linhas)