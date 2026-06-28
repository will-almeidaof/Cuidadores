# app.py — Sistema de Rede de Cuidadores e Pacientes
# Fundamentos de Bancos de Dados 2026.1 - UFC
# Autor: Willyam de Sousa Almeida
#
# Execute com:  panel serve app.py --show

import panel as pn
import pandas as pd
from datetime import datetime
from db import (
    get_session, Usuario, Cuidador, TelefoneCuidador,
    Paciente, Atividade, Ocorrencia, GravidadeEnum
)

pn.extension("tabulator", sizing_mode="stretch_width")

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _cuidador_opts():
    s = get_session()
    try:
        rows = s.query(Cuidador).join(Usuario).order_by(Usuario.nome).all()
        return {f"{c.id_usuario} — {c.usuario.nome}": c.id_usuario for c in rows}
    finally:
        s.close()

def _paciente_opts():
    s = get_session()
    try:
        rows = s.query(Paciente).order_by(Paciente.nome).all()
        return {f"{p.id_paciente} — {p.nome}": p.id_paciente for p in rows}
    finally:
        s.close()

def ok(msg):  return f'<span style="color:#2e7d32;font-weight:bold">✅ {msg}</span>'
def err(msg): return f'<span style="color:#c62828;font-weight:bold">⚠️ {msg}</span>'

# ─────────────────────────────────────────────────────────────
# ABA 1 — PACIENTES
# ─────────────────────────────────────────────────────────────

p_nome  = pn.widgets.TextInput(name="Nome", placeholder="Nome completo")
p_nasc  = pn.widgets.DatePicker(name="Data de Nascimento")
p_sel   = pn.widgets.Select(name="Paciente (editar/remover)", options={})
p_msg   = pn.pane.HTML("")
p_grid  = pn.widgets.Tabulator(pd.DataFrame(), pagination="local", page_size=10,
                                 show_index=False, sizing_mode="stretch_width")

def pac_listar(e=None):
    s = get_session()
    try:
        rows = s.query(Paciente).order_by(Paciente.nome).all()
        p_grid.value = pd.DataFrame([
            {"ID": p.id_paciente, "Nome": p.nome, "Nascimento": str(p.data_nascimento)}
            for p in rows
        ])
        p_sel.options = {f"{p.id_paciente} — {p.nome}": p.id_paciente for p in rows}
    finally:
        s.close()

def pac_inserir(e):
    if not p_nome.value or not p_nasc.value:
        p_msg.object = err("Nome e data de nascimento são obrigatórios.")
        return
    s = get_session()
    try:
        s.add(Paciente(nome=p_nome.value, data_nascimento=p_nasc.value))
        s.commit()
        p_msg.object = ok("Paciente inserido.")
        p_nome.value = ""; p_nasc.value = None
        pac_listar()
    except Exception as ex:
        s.rollback(); p_msg.object = err(ex)
    finally:
        s.close()

def pac_carregar(e):
    pid = p_sel.value
    if not pid: return
    s = get_session()
    try:
        p = s.query(Paciente).get(pid)
        if p: p_nome.value = p.nome; p_nasc.value = p.data_nascimento
    finally:
        s.close()

def pac_editar(e):
    pid = p_sel.value
    if not pid: p_msg.object = err("Selecione um paciente."); return
    s = get_session()
    try:
        p = s.query(Paciente).get(pid)
        if p:
            if p_nome.value: p.nome = p_nome.value
            if p_nasc.value: p.data_nascimento = p_nasc.value
            s.commit(); p_msg.object = ok("Paciente atualizado.")
            pac_listar()
    except Exception as ex:
        s.rollback(); p_msg.object = err(ex)
    finally:
        s.close()

# --- confirmação de remoção de paciente ---
p_confirm_box = pn.Column(visible=False)
p_confirm_pid = [None]

def pac_remover(e):
    pid = p_sel.value
    if not pid: p_msg.object = err("Selecione um paciente."); return
    s = get_session()
    try:
        n_ativ = s.query(Atividade).filter_by(id_paciente=pid).count()
        n_ocor = s.query(Ocorrencia).filter_by(id_paciente=pid).count()
        if n_ativ > 0 or n_ocor > 0:
            p_confirm_pid[0] = pid
            aviso = (
                f"<b>Atenção!</b> Este paciente possui "
                f"<b>{n_ativ} atividade(s)</b> e <b>{n_ocor} ocorrência(s)</b> vinculadas.<br>"
                f"Tudo isso será apagado junto. Deseja continuar?"
            )
            btn_sim = pn.widgets.Button(name="✅ Sim, remover tudo", button_type="danger", width=200)
            btn_nao = pn.widgets.Button(name="❌ Cancelar",           button_type="default", width=130)
            btn_sim.on_click(_pac_confirmar_remover)
            btn_nao.on_click(_pac_cancelar_remover)
            p_confirm_box.objects = [
                pn.pane.HTML(f'<div style="background:#fff3cd;padding:10px;border-radius:6px">{aviso}</div>'),
                pn.Row(btn_sim, btn_nao),
            ]
            p_confirm_box.visible = True
            p_msg.object = ""
        else:
            _pac_deletar(pid)
    finally:
        s.close()

def _pac_deletar(pid):
    s = get_session()
    try:
        s.query(Atividade).filter_by(id_paciente=pid).delete()
        s.query(Ocorrencia).filter_by(id_paciente=pid).delete()
        p = s.query(Paciente).get(pid)
        if p: s.delete(p)
        s.commit()
        p_msg.object = ok("Paciente e todos os registros vinculados foram removidos.")
        pac_listar(); ati_listar(); oco_listar()
    except Exception as ex:
        s.rollback(); p_msg.object = err(ex)
    finally:
        s.close()

def _pac_confirmar_remover(e):
    pid = p_confirm_pid[0]
    p_confirm_box.visible = False
    p_confirm_box.objects = []
    if pid: _pac_deletar(pid)

def _pac_cancelar_remover(e):
    p_confirm_box.visible = False
    p_confirm_box.objects = []
    p_msg.object = '<span style="color:#555">Remoção cancelada.</span>'


btn = lambda label, tp: pn.widgets.Button(name=label, button_type=tp, width=130)
pb_ins = btn("➕ Inserir",  "success");  pb_ins.on_click(pac_inserir)
pb_lst = btn("🔄 Listar",   "primary");  pb_lst.on_click(pac_listar)
pb_car = btn("📥 Carregar", "default");  pb_car.on_click(pac_carregar)
pb_edi = btn("✏️ Editar",   "warning");  pb_edi.on_click(pac_editar)
pb_rem = btn("🗑️ Remover",  "danger");   pb_rem.on_click(pac_remover)

aba_pacientes = pn.Column(
    pn.pane.Markdown("### 👤 Pacientes"),
    pn.Row(p_nome, p_nasc),
    pn.Row(pb_ins, pb_lst),
    pn.layout.Divider(),
    p_sel, pn.Row(pb_car, pb_edi, pb_rem),
    p_confirm_box,
    p_msg, pn.layout.Divider(),
    p_grid,
)

# ─────────────────────────────────────────────────────────────
# ABA 2 — CUIDADORES
# ─────────────────────────────────────────────────────────────

c_nome  = pn.widgets.TextInput(name="Nome")
c_email = pn.widgets.TextInput(name="E-mail")
c_senha = pn.widgets.PasswordInput(name="Senha")
c_cpf   = pn.widgets.TextInput(name="CPF (só números)", max_length=11)
c_tel   = pn.widgets.TextInput(name="Telefone principal")
c_sel   = pn.widgets.Select(name="Cuidador (editar/remover)", options={})
c_msg   = pn.pane.HTML("")
c_grid  = pn.widgets.Tabulator(pd.DataFrame(), pagination="local", page_size=10,
                                 show_index=False, sizing_mode="stretch_width")

def cui_listar(e=None):
    s = get_session()
    try:
        rows = s.query(Cuidador).join(Usuario).order_by(Usuario.nome).all()
        c_grid.value = pd.DataFrame([
            {"ID": c.id_usuario, "Nome": c.usuario.nome, "E-mail": c.usuario.email,
             "CPF": c.cpf, "Telefones": ", ".join(t.telefone for t in c.telefones)}
            for c in rows
        ])
        c_sel.options = {f"{c.id_usuario} — {c.usuario.nome}": c.id_usuario for c in rows}
    finally:
        s.close()

def cui_inserir(e):
    if not all([c_nome.value, c_email.value, c_senha.value, c_cpf.value]):
        c_msg.object = err("Nome, e-mail, senha e CPF são obrigatórios."); return
    s = get_session()
    try:
        u = Usuario(nome=c_nome.value, email=c_email.value, senha=c_senha.value)
        s.add(u); s.flush()
        s.add(Cuidador(id_usuario=u.id_usuario, cpf=c_cpf.value))
        if c_tel.value:
            s.add(TelefoneCuidador(id_usuario=u.id_usuario, telefone=c_tel.value))
        s.commit(); c_msg.object = ok("Cuidador inserido.")
        for w in [c_nome, c_email, c_senha, c_cpf, c_tel]: w.value = ""
        cui_listar()
    except Exception as ex:
        s.rollback(); c_msg.object = err(ex)
    finally:
        s.close()

def cui_carregar(e):
    cid = c_sel.value
    if not cid: return
    s = get_session()
    try:
        c = s.query(Cuidador).get(cid)
        if c:
            c_nome.value = c.usuario.nome; c_email.value = c.usuario.email
            c_cpf.value  = c.cpf
            c_tel.value  = c.telefones[0].telefone if c.telefones else ""
    finally:
        s.close()

def cui_editar(e):
    cid = c_sel.value
    if not cid: c_msg.object = err("Selecione um cuidador."); return
    s = get_session()
    try:
        c = s.query(Cuidador).get(cid)
        if c:
            if c_nome.value:  c.usuario.nome  = c_nome.value
            if c_email.value: c.usuario.email = c_email.value
            if c_cpf.value:   c.cpf           = c_cpf.value
            if c_tel.value and c.telefones: c.telefones[0].telefone = c_tel.value
            s.commit(); c_msg.object = ok("Cuidador atualizado."); cui_listar()
    except Exception as ex:
        s.rollback(); c_msg.object = err(ex)
    finally:
        s.close()

# --- confirmação de remoção de cuidador ---
c_confirm_box = pn.Column(visible=False)
c_confirm_cid = [None]  # guarda o id a remover

def cui_remover(e):
    cid = c_sel.value
    if not cid: c_msg.object = err("Selecione um cuidador."); return
    s = get_session()
    try:
        n_ativ = s.query(Atividade).filter_by(id_cuidador=cid).count()
        n_ocor = s.query(Ocorrencia).filter_by(id_cuidador=cid).count()
        if n_ativ > 0 or n_ocor > 0:
            c_confirm_cid[0] = cid
            aviso = (
                f"<b>Atenção!</b> Este cuidador possui "
                f"<b>{n_ativ} atividade(s)</b> e <b>{n_ocor} ocorrência(s)</b> vinculadas.<br>"
                f"Tudo isso será apagado junto. Deseja continuar?"
            )
            btn_sim = pn.widgets.Button(name="✅ Sim, remover tudo", button_type="danger", width=200)
            btn_nao = pn.widgets.Button(name="❌ Cancelar",           button_type="default", width=130)
            btn_sim.on_click(_cui_confirmar_remover)
            btn_nao.on_click(_cui_cancelar_remover)
            c_confirm_box.objects = [
                pn.pane.HTML(f'<div style="background:#fff3cd;padding:10px;border-radius:6px">{aviso}</div>'),
                pn.Row(btn_sim, btn_nao),
            ]
            c_confirm_box.visible = True
            c_msg.object = ""
        else:
            _cui_deletar(cid)
    finally:
        s.close()

def _cui_deletar(cid):
    s = get_session()
    try:
        # remove atividades e ocorrencias vinculadas primeiro
        s.query(Atividade).filter_by(id_cuidador=cid).delete()
        s.query(Ocorrencia).filter_by(id_cuidador=cid).delete()
        u = s.query(Usuario).get(cid)
        if u: s.delete(u)
        s.commit()
        c_msg.object = ok("Cuidador e todos os registros vinculados foram removidos.")
        cui_listar(); ati_listar(); oco_listar()
    except Exception as ex:
        s.rollback(); c_msg.object = err(ex)
    finally:
        s.close()

def _cui_confirmar_remover(e):
    cid = c_confirm_cid[0]
    c_confirm_box.visible = False
    c_confirm_box.objects = []
    if cid: _cui_deletar(cid)

def _cui_cancelar_remover(e):
    c_confirm_box.visible = False
    c_confirm_box.objects = []
    c_msg.object = '<span style="color:#555">Remoção cancelada.</span>'


cb_ins = btn("➕ Inserir",  "success");  cb_ins.on_click(cui_inserir)
cb_lst = btn("🔄 Listar",   "primary");  cb_lst.on_click(cui_listar)
cb_car = btn("📥 Carregar", "default");  cb_car.on_click(cui_carregar)
cb_edi = btn("✏️ Editar",   "warning");  cb_edi.on_click(cui_editar)
cb_rem = btn("🗑️ Remover",  "danger");   cb_rem.on_click(cui_remover)

aba_cuidadores = pn.Column(
    pn.pane.Markdown("### 🩺 Cuidadores"),
    pn.Row(c_nome, c_email), pn.Row(c_senha, c_cpf, c_tel),
    pn.Row(cb_ins, cb_lst),
    pn.layout.Divider(),
    c_sel, pn.Row(cb_car, cb_edi, cb_rem),
    c_confirm_box,
    c_msg, pn.layout.Divider(), c_grid,
)

# ─────────────────────────────────────────────────────────────
# ABA 3 — ATIVIDADES
# ─────────────────────────────────────────────────────────────

a_desc  = pn.widgets.TextAreaInput(name="Descrição", height=80)
a_tipo  = pn.widgets.TextInput(name="Tipo")
a_dh    = pn.widgets.DatetimePicker(name="Data e Hora")
a_cui   = pn.widgets.Select(name="Cuidador", options=_cuidador_opts())
a_pac   = pn.widgets.Select(name="Paciente", options=_paciente_opts())
a_sel   = pn.widgets.Select(name="Atividade (editar/remover)", options={})
a_msg   = pn.pane.HTML("")
a_grid  = pn.widgets.Tabulator(pd.DataFrame(), pagination="local", page_size=10,
                                 show_index=False, sizing_mode="stretch_width")

def ati_listar(e=None):
    s = get_session()
    try:
        rows = s.query(Atividade).order_by(Atividade.data_hora.desc()).all()
        a_grid.value = pd.DataFrame([
            {"ID": a.id_atividade, "Tipo": a.tipo, "Data/Hora": str(a.data_hora),
             "Cuidador": a.cuidador.usuario.nome, "Paciente": a.paciente.nome,
             "Descrição": a.descricao[:60]}
            for a in rows
        ])
        a_sel.options = {f"{a.id_atividade} — {a.tipo}": a.id_atividade for a in rows}
        a_cui.options = _cuidador_opts(); a_pac.options = _paciente_opts()
    finally:
        s.close()

def ati_inserir(e):
    if not all([a_desc.value, a_tipo.value, a_dh.value, a_cui.value, a_pac.value]):
        a_msg.object = err("Preencha todos os campos."); return
    s = get_session()
    try:
        s.add(Atividade(descricao=a_desc.value, tipo=a_tipo.value, data_hora=a_dh.value,
                        id_cuidador=a_cui.value, id_paciente=a_pac.value))
        s.commit(); a_msg.object = ok("Atividade inserida.")
        a_desc.value = ""; a_tipo.value = ""; ati_listar()
    except Exception as ex:
        s.rollback(); a_msg.object = err(ex)
    finally:
        s.close()

def ati_carregar(e):
    aid = a_sel.value
    if not aid: return
    s = get_session()
    try:
        a = s.query(Atividade).get(aid)
        if a: a_desc.value = a.descricao; a_tipo.value = a.tipo; a_dh.value = a.data_hora
    finally:
        s.close()

def ati_editar(e):
    aid = a_sel.value
    if not aid: a_msg.object = err("Selecione uma atividade."); return
    s = get_session()
    try:
        a = s.query(Atividade).get(aid)
        if a:
            if a_desc.value: a.descricao = a_desc.value
            if a_tipo.value: a.tipo      = a_tipo.value
            if a_dh.value:   a.data_hora = a_dh.value
            s.commit(); a_msg.object = ok("Atividade atualizada."); ati_listar()
    except Exception as ex:
        s.rollback(); a_msg.object = err(ex)
    finally:
        s.close()

def ati_remover(e):
    aid = a_sel.value
    if not aid: a_msg.object = err("Selecione uma atividade."); return
    s = get_session()
    try:
        a = s.query(Atividade).get(aid)
        if a: s.delete(a); s.commit(); a_msg.object = ok("Atividade removida."); ati_listar()
    except Exception as ex:
        s.rollback(); a_msg.object = err(ex)
    finally:
        s.close()

ab_ins = btn("➕ Inserir",  "success");  ab_ins.on_click(ati_inserir)
ab_lst = btn("🔄 Listar",   "primary");  ab_lst.on_click(ati_listar)
ab_car = btn("📥 Carregar", "default");  ab_car.on_click(ati_carregar)
ab_edi = btn("✏️ Editar",   "warning");  ab_edi.on_click(ati_editar)
ab_rem = btn("🗑️ Remover",  "danger");   ab_rem.on_click(ati_remover)

aba_atividades = pn.Column(
    pn.pane.Markdown("### 📋 Atividades"),
    pn.Row(a_cui, a_pac), pn.Row(a_tipo, a_dh), a_desc,
    pn.Row(ab_ins, ab_lst),
    pn.layout.Divider(),
    a_sel, pn.Row(ab_car, ab_edi, ab_rem),
    a_msg, pn.layout.Divider(), a_grid,
)

# ─────────────────────────────────────────────────────────────
# ABA 4 — OCORRÊNCIAS
# ─────────────────────────────────────────────────────────────

o_desc  = pn.widgets.TextAreaInput(name="Descrição", height=80)
o_grav  = pn.widgets.Select(name="Gravidade", options=["baixa", "media", "alta"])
o_dh    = pn.widgets.DatetimePicker(name="Data e Hora")
o_cui   = pn.widgets.Select(name="Cuidador", options=_cuidador_opts())
o_pac   = pn.widgets.Select(name="Paciente", options=_paciente_opts())
o_sel   = pn.widgets.Select(name="Ocorrência (editar/remover)", options={})
o_msg   = pn.pane.HTML("")
o_grid  = pn.widgets.Tabulator(pd.DataFrame(), pagination="local", page_size=10,
                                 show_index=False, sizing_mode="stretch_width")

def oco_listar(e=None):
    s = get_session()
    try:
        rows = s.query(Ocorrencia).order_by(Ocorrencia.data_hora.desc()).all()
        o_grid.value = pd.DataFrame([
            {"ID": o.id_ocorrencia, "Gravidade": o.gravidade.value,
             "Data/Hora": str(o.data_hora),
             "Cuidador": o.cuidador.usuario.nome, "Paciente": o.paciente.nome,
             "Descrição": o.descricao[:60]}
            for o in rows
        ])
        o_sel.options = {f"{o.id_ocorrencia} — {o.gravidade.value}": o.id_ocorrencia for o in rows}
        o_cui.options = _cuidador_opts(); o_pac.options = _paciente_opts()
    finally:
        s.close()

def oco_inserir(e):
    if not all([o_desc.value, o_dh.value, o_cui.value, o_pac.value]):
        o_msg.object = err("Preencha todos os campos."); return
    s = get_session()
    try:
        s.add(Ocorrencia(descricao=o_desc.value, data_hora=o_dh.value,
                         gravidade=GravidadeEnum[o_grav.value],
                         id_cuidador=o_cui.value, id_paciente=o_pac.value))
        s.commit(); o_msg.object = ok("Ocorrência inserida.")
        o_desc.value = ""; oco_listar()
    except Exception as ex:
        s.rollback(); o_msg.object = err(ex)
    finally:
        s.close()

def oco_carregar(e):
    oid = o_sel.value
    if not oid: return
    s = get_session()
    try:
        o = s.query(Ocorrencia).get(oid)
        if o: o_desc.value = o.descricao; o_grav.value = o.gravidade.value; o_dh.value = o.data_hora
    finally:
        s.close()

def oco_editar(e):
    oid = o_sel.value
    if not oid: o_msg.object = err("Selecione uma ocorrência."); return
    s = get_session()
    try:
        o = s.query(Ocorrencia).get(oid)
        if o:
            if o_desc.value: o.descricao = o_desc.value
            if o_grav.value: o.gravidade = GravidadeEnum[o_grav.value]
            if o_dh.value:   o.data_hora = o_dh.value
            s.commit(); o_msg.object = ok("Ocorrência atualizada."); oco_listar()
    except Exception as ex:
        s.rollback(); o_msg.object = err(ex)
    finally:
        s.close()

def oco_remover(e):
    oid = o_sel.value
    if not oid: o_msg.object = err("Selecione uma ocorrência."); return
    s = get_session()
    try:
        o = s.query(Ocorrencia).get(oid)
        if o: s.delete(o); s.commit(); o_msg.object = ok("Ocorrência removida."); oco_listar()
    except Exception as ex:
        s.rollback(); o_msg.object = err(ex)
    finally:
        s.close()

ob_ins = btn("➕ Inserir",  "success");  ob_ins.on_click(oco_inserir)
ob_lst = btn("🔄 Listar",   "primary");  ob_lst.on_click(oco_listar)
ob_car = btn("📥 Carregar", "default");  ob_car.on_click(oco_carregar)
ob_edi = btn("✏️ Editar",   "warning");  ob_edi.on_click(oco_editar)
ob_rem = btn("🗑️ Remover",  "danger");   ob_rem.on_click(oco_remover)

aba_ocorrencias = pn.Column(
    pn.pane.Markdown("### 🚨 Ocorrências"),
    pn.Row(o_cui, o_pac), pn.Row(o_grav, o_dh), o_desc,
    pn.Row(ob_ins, ob_lst),
    pn.layout.Divider(),
    o_sel, pn.Row(ob_car, ob_edi, ob_rem),
    o_msg, pn.layout.Divider(), o_grid,
)

# ─────────────────────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────────────────────

# Carrega dados iniciais
pac_listar(); cui_listar(); ati_listar(); oco_listar()

app = pn.template.FastListTemplate(
    title="🏥 Sistema de Rede de Cuidadores e Pacientes",
    header_background="#4a4a8a",
    main=[
        pn.Tabs(
            ("👤 Pacientes",   aba_pacientes),
            ("🩺 Cuidadores",  aba_cuidadores),
            ("📋 Atividades",  aba_atividades),
            ("🚨 Ocorrências", aba_ocorrencias),
            dynamic=True,
        )
    ],
)

app.servable()
