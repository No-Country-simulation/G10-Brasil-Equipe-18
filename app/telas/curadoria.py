"""Tela Curadoria - Revisão e decisão sobre rascunhos com controles separados."""
import streamlit as st

from services import data_service as svc
from state import campo, definir, historia_por_id, ir_para, valor
from styles import avatar, cabecalho, caixa, chip, destacar, esc, md, topbar

try:  # st.dialog existe a partir da 1.37; antes era experimental
    _dialogo = st.dialog
except AttributeError:  # pragma: no cover
    _dialogo = st.experimental_dialog


def _chave(hid, aid, nome_campo):
    return f"c:{hid}:{aid}:{nome_campo}"


def _aprovar(hid, aid):
    ss = st.session_state
    chave = f"{hid}:{aid}"
    ss.status_curadoria[chave] = "aprovado"
    ss.status_ativos[chave] = "aprovado"  # legado
    ss.toast = "Rascunho aprovado. Nenhum conteúdo foi publicado."


def _solicitar_ajustes(hid, aid, obs):
    ss = st.session_state
    chave = f"{hid}:{aid}"
    ss.status_curadoria[chave] = "ajustes"
    ss.observacoes[chave] = obs
    ss.toast = "Ajustes solicitados. Revise novamente após correções."


def _desfazer(hid, aid):
    ss = st.session_state
    chave = f"{hid}:{aid}"
    ss.status_curadoria[chave] = "rascunho"
    ss.status_ativos[chave] = "rascunho"  # legado
    ss.validacao_factual[chave] = "pendente"
    ss.autorizacao[chave] = "nao_registrada"
    ss.motivos.pop(chave, None)
    ss.observacoes.pop(chave, None)
    ss.toast = "Decisão desfeita. O ativo voltou para rascunho."


@_dialogo("Rejeitar este rascunho?")
def _dialogo_rejeitar(hid, aid, nome_ativo, autor):
    ss = st.session_state
    chave = f"{hid}:{aid}"
    st.write(f"O {nome_ativo.lower()} de {autor} será marcado como rejeitado e não ficará pronto para uso pelo time.")
    st.caption("A mensagem original e as evidências serão preservadas.")
    motivo = st.text_area("Motivo da rejeição (opcional)", placeholder="Conte por que este rascunho não deve ser usado.")
    c1, c2 = st.columns(2)
    if c1.button("Cancelar"):
        st.rerun()
    if c2.button("Confirmar rejeição", type="primary"):
        ss.status_curadoria[chave] = "rejeitado"
        ss.status_ativos[chave] = "rejeitado"  # legado
        ss.motivos[chave] = motivo.strip()
        ss.toast = "Rascunho rejeitado."
        st.rerun()


@_dialogo("Solicitar ajustes?")
def _dialogo_ajustes(hid, aid, nome_ativo):
    ss = st.session_state
    chave = f"{hid}:{aid}"
    st.write(f"O {nome_ativo.lower()} será marcado como 'Ajustes solicitados' e poderá ser revisado novamente.")
    obs = st.text_area("Observações sobre os ajustes necessários", 
                       placeholder="Descreva quais mudanças são necessárias...",
                       height=100)
    c1, c2 = st.columns(2)
    if c1.button("Cancelar"):
        st.rerun()
    if c2.button("Confirmar", type="primary"):
        _solicitar_ajustes(hid, aid, obs)
        st.rerun()


def _regenerar(hid, aid):
    ss = st.session_state
    h = historia_por_id(hid)
    n = ss.regen.get(f"{hid}:{aid}", 0) + 1
    ss.regen[f"{hid}:{aid}"] = n
    for nome_campo, texto in svc.regenerar(h, aid, n).items():
        definir(_chave(hid, aid, nome_campo), texto)
    # Resetar validação factual para "pendente" ao regenerar (requisito do review)
    chave = f"{hid}:{aid}"
    ss.validacao_factual[chave] = "pendente"
    ss.toast = "Novo rascunho gerado. Revise antes de aprovar."


def _alternar_copia():
    st.session_state.mostrar_copia = not st.session_state.mostrar_copia


def _preview_card(titulo, frase, autor):
    md(f'<div class="cl-cardativo"><div class="one">ONE<small>Oracle Next Education</small></div>'
       f'<div class="tit">{esc(titulo)}</div><div class="aut">{esc(autor)}</div>'
       f'<div style="margin-top:10px;">"{esc(frase)}"</div></div>')


def _coluna_rascunhos(h, ativo, status):
    hid, aid = h["id"], ativo["id"]
    editavel = status in ["rascunho", "ajustes"]
    if ativo["tipo"] == "texto":
        texto_inicial = (
            ativo["campos"].get("texto")
            or next(iter(ativo["campos"].values()), "")
        )
        campo(st.text_area, "Texto do case" if "Case" in ativo["nome"] else "Texto",
              _chave(hid, aid, "texto"), texto_inicial, height=240, disabled=not editavel)
        texto_atual = valor(_chave(hid, aid, "texto"), "")
        st.caption(f"{len(texto_atual)} caracteres")
        copiavel = texto_atual
    elif ativo["tipo"] == "testemunho":
        campo(st.text_input, "Título", _chave(hid, aid, "titulo"), ativo["campos"].get("titulo", ""), disabled=not editavel)
        campo(st.text_area, "Descrição", _chave(hid, aid, "descricao"), ativo["campos"].get("descricao", ""), height=100, disabled=not editavel)
        campo(st.text_area, "Citação", _chave(hid, aid, "citacao"), ativo["campos"].get("citacao", ""), height=60, disabled=not editavel)
        total = len(valor(_chave(hid, aid, "titulo"), "")) + len(valor(_chave(hid, aid, "descricao"), "")) + len(valor(_chave(hid, aid, "citacao"), ""))
        st.caption(f"{total} caracteres no total")
        copiavel = f"{valor(_chave(hid, aid, 'titulo'), '')}\n\n{valor(_chave(hid, aid, 'descricao'), '')}\n\n\"{valor(_chave(hid, aid, 'citacao'), '')}\""
    else:  # card (legado)
        titulo = valor(_chave(hid, aid, "titulo"), ativo["campos"].get("titulo", ""))
        frase = valor(_chave(hid, aid, "frase"), ativo["campos"].get("frase", ""))
        _preview_card(titulo, frase, h["autor"])
        campo(st.text_input, "Título", _chave(hid, aid, "titulo"), ativo["campos"].get("titulo", ""), disabled=not editavel)
        campo(st.text_input, "Frase de destaque", _chave(hid, aid, "frase"), ativo["campos"].get("frase", ""), disabled=not editavel)
        copiavel = f'{valor(_chave(hid, aid, "titulo"), "")}\n{valor(_chave(hid, aid, "frase"), "")}'
    md(chip("Rascunho gerado por IA", "purple"))
    return copiavel


def render():
    ss = st.session_state
    hid = ss.historia_atual or ss.historias[0]["id"]
    h = historia_por_id(hid)
    topbar()
    cabecalho("Etapa 4 de 4 · Decidir", "Curadoria", "Revise, valide e decida sobre cada rascunho antes de qualquer publicação.")
    st.button("← Voltar para histórias", on_click=ir_para, args=("historias",))

    with st.container(border=True):
        a, b, c = st.columns([3, 3, 1.5])
        a.markdown(compactar_avatar(h), unsafe_allow_html=True)
        b.markdown(chip(h["categoria"]) + chip(f'Sentimento {h["sentimento"].lower()}', "green"), unsafe_allow_html=True)
        c.markdown(f'<div style="text-align:right;"><span class="cl-muted">Relevância</span> '
                   f'<span style="font-size:22px;">{h["relevancia"]}</span> <span class="cl-muted">/ 100</span></div>',
                   unsafe_allow_html=True)

    esq, dir_ = st.columns([2, 1])
    nomes = [a_["nome"] for a_ in h["ativos"]]
    with esq:
        with st.container(border=True):
            md('<b style="font-size:20px;">Rascunho para revisão</b><br><span class="cl-muted">Confira o conteúdo antes de decidir.</span>')
            escolhido = campo(st.radio, "Tipo de ativo", f"aba:{hid}", nomes[0], options=nomes,
                              horizontal=True, label_visibility="collapsed")
            ativo = next(a_ for a_ in h["ativos"] if a_["nome"] == escolhido)
            aid = ativo["id"]
            chave = f"{hid}:{aid}"
            
            # Status atual dos três controles
            validacao = ss.validacao_factual.get(chave, "pendente")
            status_cur = ss.status_curadoria.get(chave, "rascunho")
            autorizacao = ss.autorizacao.get(chave, "nao_registrada")
            
            copiavel = _coluna_rascunhos(h, ativo, status_cur)
            
            st.divider()
            
            # Três controles independentes
            md('<b style="font-size:16px;">Controles de decisão</b>')
            md('<span class="cl-muted">Três dimensões independentes de avaliação</span>')
            
            # 1. Validação factual
            md('<b style="font-size:14px; margin-top:16px;">1. Validação factual</b>')
            opcoes_validacao = ["Pendente", "Validada", "Evidências insuficientes", "Contradição não resolvida"]
            map_validacao = {"Pendente": "pendente", "Validada": "validada", 
                            "Evidências insuficientes": "insuficiente", "Contradição não resolvida": "contradicao"}
            validacao_label = {v: k for k, v in map_validacao.items()}[validacao]
            nova_validacao = st.selectbox("Status da validação", opcoes_validacao, 
                                         index=opcoes_validacao.index(validacao_label),
                                         key=f"validacao_{chave}",
                                         disabled=status_cur not in ["rascunho", "ajustes"])
            if map_validacao[nova_validacao] != validacao:
                ss.validacao_factual[chave] = map_validacao[nova_validacao]
                st.rerun()
            
            if validacao == "contradicao":
                caixa("red", "<b>RG-02:</b> Contradição não resolvida. O botão Aprovar ficará desabilitado até que as evidências sejam corrigidas ou a validação seja alterada.")
            
            # 2. Curadoria editorial
            md('<b style="font-size:14px; margin-top:16px;">2. Curadoria editorial</b>')
            status_chip = {"rascunho": ("Rascunho", "yellow"), "ajustes": ("Ajustes solicitados", "yellow"),
                          "aprovado": ("Aprovado", "green"), "rejeitado": ("Rejeitado", "red")}
            label, cor = status_chip[status_cur]
            md(f'<span class="cl-muted">Status atual:</span> {chip(label, cor)}')
            
            # Campo de observações para ajustes
            if status_cur == "ajustes":
                obs = ss.observacoes.get(chave, "")
                if obs:
                    st.info(f"**Observações:** {obs}")
            
            # Motivo de rejeição
            if status_cur == "rejeitado":
                motivo = ss.motivos.get(chave, "")
                if motivo:
                    st.caption(f"Motivo da rejeição: {motivo}")
            
            # 3. Autorização de publicação
            md('<b style="font-size:14px; margin-top:16px;">3. Autorização de publicação</b>')
            md('<span class="cl-muted">Este conteúdo identifica uma pessoa. A autorização NÃO bloqueia a aprovação editorial.</span>')
            
            autorizado = st.checkbox("Autorização da participante registrada", 
                                    value=(autorizacao == "registrada"),
                                    key=f"aut_{chave}",
                                    disabled=status_cur not in ["rascunho", "ajustes"])
            if autorizado != (autorizacao == "registrada"):
                ss.autorizacao[chave] = "registrada" if autorizado else "nao_registrada"
                st.rerun()
            
            # Indicador "Liberado para publicação" (RG-03)
            st.divider()
            liberado = (validacao == "validada" and status_cur == "aprovado" and autorizacao == "registrada")
            if liberado:
                caixa("green", "✓ <b>Liberado para publicação (RG-03)</b><br>"
                      "Este ativo está validado, aprovado e com autorização registrada. "
                      "O sistema não publica automaticamente - a decisão final é do seu time.")
            elif status_cur == "aprovado":
                if validacao != "validada":
                    caixa("yellow", "⚠ <b>Aprovado, mas validação factual pendente</b><br>Complete a validação para liberar para publicação.")
                elif autorizacao != "registrada":
                    caixa("yellow", "⚠ <b>Aprovado, mas autorização não registrada</b><br>Registre a autorização para liberar para publicação.")
            
    with dir_:
        with st.container(border=True):
            md('<b style="font-size:18px;">Evidências</b><br><b style="font-size:14px;">Mensagem original</b>'
               f'<div class="cl-quote" style="margin:8px 0;">"{destacar(h["mensagem_original"], h["destaques"])}"</div>'
               f'<div class="cl-kv"><span>Canal</span><span>{esc(h["canal"])}</span></div>'
               f'<div class="cl-kv"><span>Autor</span><span>{esc(h["autor"])}</span></div>'
               f'<div class="cl-kv"><span>Lote</span><span>{esc(ss.lote_id)}</span></div>'
               + chip("Mensagem fictícia"))
        with st.container(border=True):
            fatos = "".join(f'<div style="margin:8px 0;"><span style="color:#10B981;">✓</span> {esc(f)}<br>'
                            f'<span class="cl-muted" style="margin-left:18px;font-size:12px;">Vem da mensagem original</span></div>'
                            for f in h["fatos"])
            md(f'<b style="font-size:18px;">Fatos extraídos</b>{fatos}')

    st.divider()
    
    # Botões de ação
    b1, b2, b3, b4, b5 = st.columns([1.1, 1.2, 1.2, 1.8, 2.2])
    
    if status_cur in ["rascunho", "ajustes"]:
        # Botão Rejeitar
        if b1.button("Rejeitar"):
            _dialogo_rejeitar(hid, aid, ativo["nome"], h["autor"])
        
        # Botão Regenerar
        b2.button("↻ Regenerar", on_click=_regenerar, args=(hid, aid))
        
        # Botão Copiar
        b3.button("Copiar", on_click=_alternar_copia)
        
        # Botão Solicitar ajustes
        if b4.button("Solicitar ajustes"):
            _dialogo_ajustes(hid, aid, ativo["nome"])
        
        # Botão Aprovar - RG-01: só permite aprovação com validação "validada" + RG-02: bloqueia com contradição
        pode_aprovar = (validacao == "validada")
        razao_bloqueio = ""
        if validacao == "contradicao":
            razao_bloqueio = "Resolva a contradição"
        elif validacao == "pendente":
            razao_bloqueio = "Valide as evidências"
        elif validacao == "insuficiente":
            razao_bloqueio = "Evidências insuficientes"
        
        if not pode_aprovar:
            b5.markdown(f'<div class="cl-muted" style="text-align:right;padding-top:8px;font-size:12px;">{razao_bloqueio}</div>',
                       unsafe_allow_html=True)
        b5.button("✓ Aprovar", type="primary", disabled=not pode_aprovar, on_click=_aprovar, args=(hid, aid))
    else:
        # Após decisão
        b1.button("Desfazer", on_click=_desfazer, args=(hid, aid))
        b3.button("Copiar", on_click=_alternar_copia)
        if status_cur == "aprovado":
            b5.button("→ Ir para Histórico", type="primary", on_click=ir_para, args=("historico",))
        else:
            b5.button("→ Voltar", type="primary", on_click=ir_para, args=("historias",))
    
    st.caption("Aprovar não publica. O conteúdo só fica liberado para publicação quando: Validada + Aprovado + Autorização registrada (RG-03).")
    
    if ss.mostrar_copia:
        st.code(copiavel, language=None)
        st.caption("Use o ícone no canto do bloco para copiar.")


def compactar_avatar(h):
    return (f'{avatar(h["iniciais"])}<b>{esc(h["autor"])}</b><br>'
            f'<span class="cl-muted" style="margin-left:46px;">{esc(h["canal"])} · {esc(h["origem"])}</span>')
