# db.py — Conexão e Models SQLAlchemy
# Sistema de Rede de Cuidadores e Pacientes
# Fundamentos de Bancos de Dados 2026.1 - UFC

from sqlalchemy import (
    create_engine, Column, Integer, String, Date, DateTime,
    Text, ForeignKey, Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import enum

# ── Configuração — ajuste usuário/senha/banco conforme seu ambiente ──────────
DB_USER     = "postgres"
DB_PASSWORD = "1234"
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "cuidadores_db"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine  = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base    = declarative_base()


# ── Enum Python para gravidade ────────────────────────────────────────────────
class GravidadeEnum(enum.Enum):
    baixa = "baixa"
    media = "media"
    alta  = "alta"


# ── Models ────────────────────────────────────────────────────────────────────

class Usuario(Base):
    __tablename__ = "usuario"
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nome       = Column(String(100), nullable=False)
    email      = Column(String(150), nullable=False, unique=True)
    senha      = Column(String(255), nullable=False)

    cuidador      = relationship("Cuidador",      back_populates="usuario", uselist=False)
    administrador = relationship("Administrador", back_populates="usuario", uselist=False)


class Cuidador(Base):
    __tablename__ = "cuidador"
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True)
    cpf        = Column(String(11), nullable=False, unique=True)

    usuario    = relationship("Usuario",    back_populates="cuidador")
    telefones  = relationship("TelefoneCuidador", back_populates="cuidador", cascade="all, delete-orphan")
    atividades = relationship("Atividade",  back_populates="cuidador")
    ocorrencias = relationship("Ocorrencia", back_populates="cuidador")


class Administrador(Base):
    __tablename__ = "administrador"
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True)
    usuario    = relationship("Usuario", back_populates="administrador")


class TelefoneCuidador(Base):
    __tablename__ = "telefone_cuidador"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("cuidador.id_usuario", ondelete="CASCADE"), nullable=False)
    telefone   = Column(String(20), nullable=False)
    cuidador   = relationship("Cuidador", back_populates="telefones")


class Paciente(Base):
    __tablename__ = "paciente"
    id_paciente     = Column(Integer, primary_key=True, autoincrement=True)
    nome            = Column(String(100), nullable=False)
    data_nascimento = Column(Date, nullable=False)

    historicos  = relationship("HistoricoMedico", back_populates="paciente", cascade="all, delete-orphan")
    atividades  = relationship("Atividade",       back_populates="paciente")
    ocorrencias = relationship("Ocorrencia",      back_populates="paciente")


class HistoricoMedico(Base):
    __tablename__ = "historico_medico"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    id_paciente   = Column(Integer, ForeignKey("paciente.id_paciente", ondelete="CASCADE"), nullable=False)
    descricao     = Column(Text, nullable=False)
    data_registro = Column(Date, nullable=False)

    paciente = relationship("Paciente", back_populates="historicos")


class Cuida(Base):
    __tablename__ = "cuida"
    id_cuidador = Column(Integer, ForeignKey("cuidador.id_usuario",    ondelete="CASCADE"), primary_key=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente",   ondelete="CASCADE"), primary_key=True)
    data_inicio = Column(Date, nullable=False, primary_key=True)
    data_fim    = Column(Date, nullable=True)


class Atividade(Base):
    __tablename__ = "atividade"
    id_atividade = Column(Integer, primary_key=True, autoincrement=True)
    descricao    = Column(Text, nullable=False)
    data_hora    = Column(DateTime, nullable=False)
    tipo         = Column(String(80), nullable=False)
    id_cuidador  = Column(Integer, ForeignKey("cuidador.id_usuario"),  nullable=False)
    id_paciente  = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)

    cuidador = relationship("Cuidador", back_populates="atividades")
    paciente = relationship("Paciente", back_populates="atividades")


class Ocorrencia(Base):
    __tablename__ = "ocorrencia"
    id_ocorrencia = Column(Integer, primary_key=True, autoincrement=True)
    descricao     = Column(Text, nullable=False)
    data_hora     = Column(DateTime, nullable=False)
    gravidade     = Column(SAEnum(GravidadeEnum), nullable=False)
    id_cuidador   = Column(Integer, ForeignKey("cuidador.id_usuario"),  nullable=False)
    id_paciente   = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)

    cuidador = relationship("Cuidador", back_populates="ocorrencias")
    paciente = relationship("Paciente", back_populates="ocorrencias")


def get_session():
    """Retorna uma nova sessão do banco."""
    return Session()
