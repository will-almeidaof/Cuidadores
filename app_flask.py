# app_flask.py — Backend Flask + SQLAlchemy
# Sistema de Rede de Cuidadores e Pacientes
# Fundamentos de Bancos de Dados 2026.1 — UFC
# Autor: Willyam de Sousa Almeida
#
# Execute com:  python app_flask.py
from sqlalchemy import text # Certifique-se de importar o text no topo do arquivo
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum as SAEnum
from urllib.parse import quote_plus
import enum

app = Flask(__name__)

# ── Configuração do banco ────────────────────────────────────
DB_USER     = "postgres"
DB_PASSWORD = "1234"   # ajuste se necessário
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "cuidadores_db"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# ── Models ───────────────────────────────────────────────────

class GravidadeEnum(enum.Enum):
    baixa = "baixa"
    media = "media"
    alta  = "alta"

class Usuario(db.Model):
    __tablename__ = "usuario"
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), nullable=False, unique=True)
    cuidador      = db.relationship("Cuidador",      back_populates="usuario", uselist=False, passive_deletes=True)
    administrador = db.relationship("Administrador", back_populates="usuario", uselist=False, passive_deletes=True)

class Cuidador(db.Model):
    __tablename__ = "cuidador"
    id_usuario  = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True)
    cpf         = db.Column(db.String(11), nullable=False, unique=True)
    usuario     = db.relationship("Usuario", back_populates="cuidador")
    telefones   = db.relationship("TelefoneCuidador", back_populates="cuidador", cascade="all, delete-orphan", passive_deletes=True)
    atividades  = db.relationship("Atividade",  back_populates="cuidador")
    ocorrencias = db.relationship("Ocorrencia", back_populates="cuidador")

class Administrador(db.Model):
    __tablename__ = "administrador"
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True)
    usuario    = db.relationship("Usuario", back_populates="administrador")

class TelefoneCuidador(db.Model):
    __tablename__ = "telefone_cuidador"
    id         = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("cuidador.id_usuario", ondelete="CASCADE"), nullable=False)
    telefone   = db.Column(db.String(20), nullable=False)
    cuidador   = db.relationship("Cuidador", back_populates="telefones")

class Paciente(db.Model):
    __tablename__ = "paciente"
    id_paciente     = db.Column(db.Integer, primary_key=True)
    nome            = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    historicos      = db.relationship("HistoricoMedico", back_populates="paciente", cascade="all, delete-orphan", passive_deletes=True)
    atividades      = db.relationship("Atividade",  back_populates="paciente")
    ocorrencias     = db.relationship("Ocorrencia", back_populates="paciente")

class HistoricoMedico(db.Model):
    __tablename__ = "historico_medico"
    id            = db.Column(db.Integer, primary_key=True)
    id_paciente   = db.Column(db.Integer, db.ForeignKey("paciente.id_paciente", ondelete="CASCADE"), nullable=False)
    descricao     = db.Column(db.Text, nullable=False)
    data_registro = db.Column(db.Date, nullable=False)
    paciente      = db.relationship("Paciente", back_populates="historicos")

class Atividade(db.Model):
    __tablename__ = "atividade"
    id_atividade = db.Column(db.Integer, primary_key=True)
    descricao    = db.Column(db.Text, nullable=False)
    data_hora    = db.Column(db.DateTime, nullable=False)
    tipo         = db.Column(db.String(80), nullable=False)
    id_cuidador  = db.Column(db.Integer, db.ForeignKey("cuidador.id_usuario"),  nullable=False)
    id_paciente  = db.Column(db.Integer, db.ForeignKey("paciente.id_paciente"), nullable=False)
    cuidador     = db.relationship("Cuidador", back_populates="atividades")
    paciente     = db.relationship("Paciente", back_populates="atividades")

class Ocorrencia(db.Model):
    __tablename__ = "ocorrencia"
    id_ocorrencia = db.Column(db.Integer, primary_key=True)
    descricao     = db.Column(db.Text, nullable=False)
    data_hora     = db.Column(db.DateTime, nullable=False)
    gravidade     = db.Column(SAEnum(GravidadeEnum), nullable=False)
    id_cuidador   = db.Column(db.Integer, db.ForeignKey("cuidador.id_usuario"),  nullable=False)
    id_paciente   = db.Column(db.Integer, db.ForeignKey("paciente.id_paciente"), nullable=False)
    cuidador      = db.relationship("Cuidador", back_populates="ocorrencias")
    paciente      = db.relationship("Paciente", back_populates="ocorrencias")

class Cuida(db.Model):
    __tablename__ = "cuida"
    id_cuidador = db.Column(db.Integer, db.ForeignKey("cuidador.id_usuario", ondelete="CASCADE"), primary_key=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey("paciente.id_paciente", ondelete="CASCADE"), primary_key=True)
    data_inicio = db.Column(db.Date, primary_key=True, nullable=False)
    data_fim    = db.Column(db.Date, nullable=True)

    cuidador = db.relationship("Cuidador", backref=db.backref("vinculos", cascade="all, delete-orphan"))
    paciente = db.relationship("Paciente", backref=db.backref("vinculos", cascade="all, delete-orphan"))


# ── Helpers ──────────────────────────────────────────────────

def ok(data):  return jsonify({"ok": True,  "data": data})
def fail(msg): return jsonify({"ok": False, "error": msg}), 400


# ── Rota principal ───────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ══════════════════════════════════════════════════════════════
# API — PACIENTES
# ══════════════════════════════════════════════════════════════

@app.route("/api/pacientes", methods=["GET"])
def listar_pacientes():
    rows = Paciente.query.order_by(Paciente.nome).all()
    return ok([{
        "id": p.id_paciente, "nome": p.nome,
        "data_nascimento": str(p.data_nascimento),
        "n_atividades": len(p.atividades),
        "n_ocorrencias": len(p.ocorrencias),
    } for p in rows])

@app.route("/api/pacientes", methods=["POST"])
def criar_paciente():
    d = request.json
    if not d.get("nome") or not d.get("data_nascimento"):
        return fail("Nome e data de nascimento são obrigatórios.")
    try:
        from datetime import date
        p = Paciente(nome=d["nome"],
                     data_nascimento=date.fromisoformat(d["data_nascimento"]))
        db.session.add(p)
        db.session.commit()
        return ok({"id": p.id_paciente, "nome": p.nome})
    except Exception as e:
        db.session.rollback(); return fail(str(e))

@app.route("/api/pacientes/<int:pid>", methods=["PUT"])
def editar_paciente(pid):
    p = Paciente.query.get_or_404(pid)
    d = request.json
    try:
        from datetime import date
        if d.get("nome"):            p.nome = d["nome"]
        if d.get("data_nascimento"): p.data_nascimento = date.fromisoformat(d["data_nascimento"])
        db.session.commit()
        return ok({"id": p.id_paciente, "nome": p.nome})
    except Exception as e:
        db.session.rollback(); return fail(str(e))

@app.route("/api/pacientes/<int:pid>", methods=["DELETE"])
def remover_paciente(pid):
    p = Paciente.query.get_or_404(pid)
    force = request.args.get("force") == "1"
    n_a = len(p.atividades); n_o = len(p.ocorrencias)
    if (n_a > 0 or n_o > 0) and not force:
        return jsonify({"ok": False, "conflict": True,
                        "n_atividades": n_a, "n_ocorrencias": n_o}), 409
    try:
        Atividade.query.filter_by(id_paciente=pid).delete()
        Ocorrencia.query.filter_by(id_paciente=pid).delete()
        db.session.delete(p); db.session.commit()
        return ok("Paciente removido.")
    except Exception as e:
        db.session.rollback(); return fail(str(e))


# ══════════════════════════════════════════════════════════════
# API — CUIDADORES
# ══════════════════════════════════════════════════════════════

@app.route("/api/cuidadores", methods=["GET"])
def listar_cuidadores():
    rows = Cuidador.query.join(Usuario).order_by(Usuario.nome).all()
    return ok([{
        "id": c.id_usuario, "nome": c.usuario.nome,
        "email": c.usuario.email, "cpf": c.cpf,
        "telefones": [t.telefone for t in c.telefones],
        "n_atividades": len(c.atividades),
        "n_ocorrencias": len(c.ocorrencias),
    } for c in rows])

@app.route("/api/cuidadores", methods=["POST"])
def criar_cuidador():
    d = request.json
    if not all([d.get("nome"), d.get("email"), d.get("cpf")]):
        return fail("Nome, e-mail e CPF são obrigatórios.")
    try:
        u = Usuario(nome=d["nome"], email=d["email"])
        db.session.add(u); db.session.flush()
        c = Cuidador(id_usuario=u.id_usuario, cpf=d["cpf"])
        db.session.add(c)
        for tel in d.get("telefones", []):
            if tel.strip():
                db.session.add(TelefoneCuidador(id_usuario=u.id_usuario, telefone=tel.strip()))
        db.session.commit()
        return ok({"id": u.id_usuario, "nome": u.nome})
    except Exception as e:
        db.session.rollback(); return fail(str(e))

@app.route("/api/cuidadores/<int:cid>", methods=["PUT"])
def editar_cuidador(cid):
    c = Cuidador.query.get_or_404(cid)
    d = request.json
    try:
        if d.get("nome"):  c.usuario.nome  = d["nome"]
        if d.get("email"): c.usuario.email = d["email"]
        if d.get("cpf"):   c.cpf           = d["cpf"]
        if "telefones" in d:
            for t in c.telefones: db.session.delete(t)
            for tel in d["telefones"]:
                if tel.strip():
                    db.session.add(TelefoneCuidador(id_usuario=cid, telefone=tel.strip()))
        db.session.commit()
        return ok({"id": c.id_usuario, "nome": c.usuario.nome})
    except Exception as e:
        db.session.rollback(); return fail(str(e))

@app.route("/api/cuidadores/<int:cid>", methods=["DELETE"])
def remover_cuidador(cid):
    c = Cuidador.query.get_or_404(cid)
    force = request.args.get("force") == "1"
    n_a = len(c.atividades); n_o = len(c.ocorrencias)
    if (n_a > 0 or n_o > 0) and not force:
        return jsonify({"ok": False, "conflict": True,
                        "n_atividades": n_a, "n_ocorrencias": n_o}), 409
    try:
        Atividade.query.filter_by(id_cuidador=cid).delete()
        Ocorrencia.query.filter_by(id_cuidador=cid).delete()
        db.session.delete(c.usuario); db.session.commit()
        return ok("Cuidador removido.")
    except Exception as e:
        db.session.rollback(); return fail(str(e))


# ══════════════════════════════════════════════════════════════
# API — ATIVIDADES
# ══════════════════════════════════════════════════════════════

@app.route("/api/atividades", methods=["GET"])
def listar_atividades():
    rows = Atividade.query.order_by(Atividade.data_hora.desc()).all()
    return ok([{
        "id": a.id_atividade, "descricao": a.descricao, "tipo": a.tipo,
        "data_hora": a.data_hora.strftime("%Y-%m-%dT%H:%M"),
        "cuidador_id": a.id_cuidador, "cuidador_nome": a.cuidador.usuario.nome,
        "paciente_id": a.id_paciente, "paciente_nome": a.paciente.nome,
    } for a in rows])

@app.route("/api/atividades", methods=["POST"])
def criar_atividade():
    d = request.json
    if not all([d.get("descricao"), d.get("tipo"), d.get("data_hora"),
                d.get("id_cuidador"), d.get("id_paciente")]):
        return fail("Todos os campos são obrigatórios.")
    try:
        from datetime import datetime
        a = Atividade(descricao=d["descricao"], tipo=d["tipo"],
                      data_hora=datetime.fromisoformat(d["data_hora"]),
                      id_cuidador=d["id_cuidador"], id_paciente=d["id_paciente"])
        db.session.add(a); db.session.commit()
        return ok({"id": a.id_atividade})
    except Exception as e:
        db.session.rollback(); return fail(str(e))

@app.route("/api/atividades/<int:aid>", methods=["PUT"])
def editar_atividade(aid):
    a = Atividade.query.get_or_404(aid)
    d = request.json
    try:
        from datetime import datetime
        if d.get("descricao"): a.descricao = d["descricao"]
        if d.get("tipo"):      a.tipo      = d["tipo"]
        if d.get("data_hora"): a.data_hora = datetime.fromisoformat(d["data_hora"])
        if d.get("id_cuidador"): a.id_cuidador = d["id_cuidador"]
        if d.get("id_paciente"): a.id_paciente = d["id_paciente"]
        db.session.commit()
        return ok({"id": a.id_atividade})
    except Exception as e:
        db.session.rollback(); return fail(str(e))

@app.route("/api/atividades/<int:aid>", methods=["DELETE"])
def remover_atividade(aid):
    a = Atividade.query.get_or_404(aid)
    try:
        db.session.delete(a); db.session.commit()
        return ok("Atividade removida.")
    except Exception as e:
        db.session.rollback(); return fail(str(e))


# ══════════════════════════════════════════════════════════════
# API — OCORRÊNCIAS
# ══════════════════════════════════════════════════════════════

@app.route("/api/ocorrencias", methods=["GET"])
def listar_ocorrencias():
    rows = Ocorrencia.query.order_by(Ocorrencia.data_hora.desc()).all()
    return ok([{
        "id": o.id_ocorrencia, "descricao": o.descricao,
        "gravidade": o.gravidade.value,
        "data_hora": o.data_hora.strftime("%Y-%m-%dT%H:%M"),
        "cuidador_id": o.id_cuidador, "cuidador_nome": o.cuidador.usuario.nome,
        "paciente_id": o.id_paciente, "paciente_nome": o.paciente.nome,
    } for o in rows])

@app.route("/api/ocorrencias", methods=["POST"])
def criar_ocorrencia():
    d = request.json
    if not all([d.get("descricao"), d.get("gravidade"), d.get("data_hora"),
                d.get("id_cuidador"), d.get("id_paciente")]):
        return fail("Todos os campos são obrigatórios.")
    try:
        from datetime import datetime
        o = Ocorrencia(descricao=d["descricao"],
                       gravidade=GravidadeEnum[d["gravidade"]],
                       data_hora=datetime.fromisoformat(d["data_hora"]),
                       id_cuidador=d["id_cuidador"], id_paciente=d["id_paciente"])
        db.session.add(o); db.session.commit()
        return ok({"id": o.id_ocorrencia})
    except Exception as e:
        db.session.rollback(); return fail(str(e))

@app.route("/api/ocorrencias/<int:oid>", methods=["PUT"])
def editar_ocorrencia(oid):
    o = Ocorrencia.query.get_or_404(oid)
    d = request.json
    try:
        from datetime import datetime
        if d.get("descricao"): o.descricao = d["descricao"]
        if d.get("gravidade"): o.gravidade = GravidadeEnum[d["gravidade"]]
        if d.get("data_hora"): o.data_hora = datetime.fromisoformat(d["data_hora"])
        if d.get("id_cuidador"): o.id_cuidador = d["id_cuidador"]
        if d.get("id_paciente"): o.id_paciente = d["id_paciente"]
        db.session.commit()
        return ok({"id": o.id_ocorrencia})
    except Exception as e:
        db.session.rollback(); return fail(str(e))

@app.route("/api/ocorrencias/<int:oid>", methods=["DELETE"])
def remover_ocorrencia(oid):
    o = Ocorrencia.query.get_or_404(oid)
    try:
        db.session.delete(o); db.session.commit()
        return ok("Ocorrência removida.")
    except Exception as e:
        db.session.rollback(); return fail(str(e))
    


@app.route('/api/vinculos', methods=['GET'])
def listar_vinculos():
    try:
        # Query idêntica à do seu arquivo 01_criacao.sql
        query = text("""
            SELECT 
                cuida.id, 
                cuida.id_cuidador, 
                cuida.id_paciente, 
                cuida.data_inicio, 
                cuida.data_fim,
                u.nome AS cuidador_nome,
                p.nome AS paciente_nome
            FROM cuida
            JOIN usuario u ON cuida.id_cuidador = u.id_usuario
            JOIN paciente p ON cuida.id_paciente = p.id_paciente
        """)
        
        # No SQLAlchemy executamos direto na sessão
        resultado = db.session.execute(query)
        
        vinculos = []
        for linha in resultado:
            # No SQLAlchemy, você pode acessar os campos por índice ou pelo nome da coluna
            d_inicio = linha.data_inicio.strftime('%Y-%m-%d') if hasattr(linha.data_inicio, 'strftime') else str(linha.data_inicio)
            
            if linha.data_fim:
                d_fim = linha.data_fim.strftime('%Y-%m-%d') if hasattr(linha.data_fim, 'strftime') else str(linha.data_fim)
            else:
                d_fim = 'Ativo'
            
            vinculos.append({
                'id': linha.id,
                'id_cuidador': linha.id_cuidador,
                'id_paciente': linha.id_paciente,
                'data_inicio': d_inicio,
                'data_fim': d_fim,
                'cuidador_nome': linha.cuidador_nome,
                'paciente_nome': linha.paciente_nome
            })

        return jsonify({'ok': True, 'data': vinculos})

    except Exception as err:
        print("Erro real no GET:", str(err))
        return jsonify({'ok': False, 'error': f"Erro interno: {str(err)}"}), 500
    
@app.route('/api/vinculos', methods=['POST'])
def criar_vinculo():
    dados = request.get_json()
    id_cuidador = dados.get('id_cuidador')
    id_paciente = dados.get('id_paciente')
    data_inicio = dados.get('data_inicio')
    data_fim = dados.get('data_fim') or None # Transforma string vazia em None/NULL

    if not all([id_cuidador, id_paciente, data_inicio]):
        return jsonify({'ok': False, 'error': 'Cuidador, paciente e data de início são obrigatórios.'}), 400

    try:
        # Validação: Verifica se já existe esse vínculo ativo/aberto
        query_valida = text("""
            SELECT id FROM cuida
            WHERE id_cuidador = :id_cuidador AND id_paciente = :id_paciente AND data_fim IS NULL
        """)
        existente = db.session.execute(query_valida, {
            "id_cuidador": id_cuidador, "id_paciente": id_paciente
        }).fetchall()

        if existente:
            return jsonify({'ok': False, 'error': 'Este cuidador já possui um vínculo ativo com este paciente.'}), 400

        # Se passou, insere o novo registro
        query_insert = text("""
            INSERT INTO cuida (id_cuidador, id_paciente, data_inicio, data_fim)
            VALUES (:id_cuidador, :id_paciente, :data_inicio, :data_fim)
        """)
        db.session.execute(query_insert, {
            "id_cuidador": id_cuidador, "id_paciente": id_paciente,
            "data_inicio": data_inicio, "data_fim": data_fim
        })
        db.session.commit()

        return jsonify({'ok': True})
    except Exception as err:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(err)}), 500

@app.route('/api/vinculos/<int:id>', methods=['PUT'])
def editar_vinculo(id):
    dados = request.get_json()
    id_cuidador = dados.get('id_cuidador')
    id_paciente = dados.get('id_paciente')
    data_inicio = dados.get('data_inicio')
    data_fim = dados.get('data_fim') or None

    try:
        # Validação: Verifica se a alteração vai gerar duplicidade com OUTRO id existente
        query_valida = text("""
            SELECT id FROM cuida
            WHERE id_cuidador = :id_cuidador AND id_paciente = :id_paciente
              AND data_inicio = :data_inicio AND id != :id
        """)
        duplicado = db.session.execute(query_valida, {
            "id_cuidador": id_cuidador, "id_paciente": id_paciente,
            "data_inicio": data_inicio, "id": id
        }).fetchall()

        if duplicado:
            return jsonify({'ok': False, 'error': 'Já existe um registro idêntico com essa mesma data de início.'}), 400

        # Atualiza liberando a troca de cuidador, paciente e datas
        query_update = text("""
            UPDATE cuida
            SET id_cuidador = :id_cuidador, id_paciente = :id_paciente,
                data_inicio = :data_inicio, data_fim = :data_fim
            WHERE id = :id
        """)
        resultado = db.session.execute(query_update, {
            "id_cuidador": id_cuidador, "id_paciente": id_paciente,
            "data_inicio": data_inicio, "data_fim": data_fim, "id": id
        })
        db.session.commit()

        if resultado.rowcount == 0:
            return jsonify({'ok': False, 'error': 'Vínculo não encontrado.'}), 404

        return jsonify({'ok': True})
    except Exception as err:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(err)}), 500
    
@app.route('/api/vinculos/<int:id>', methods=['DELETE'])
def deletar_vinculo(id):
    try:
        # Executa a remoção direta pelo ID único da tabela cuida
        query_delete = text("DELETE FROM cuida WHERE id = :id")
        resultado = db.session.execute(query_delete, {"id": id})
        db.session.commit()

        # Verifica se algum registro foi realmente afetado/deletado
        if resultado.rowcount == 0:
            return jsonify({'ok': False, 'error': 'Vínculo não encontrado.'}), 404

        return jsonify({'ok': True})
    except Exception as err:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(err)}), 500


# ── Iniciar ──────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)