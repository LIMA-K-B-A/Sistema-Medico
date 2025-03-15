# app/models/paciente.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
import enum
from .usuario import Base

class Sexo(enum.Enum):
    MASCULINO = "masculino"
    FEMININO = "feminino"
    OUTRO = "outro"

class TipoContato(enum.Enum):
    CELULAR = "celular"
    TELEFONE_FIXO = "telefone_fixo"
    WHATSAPP = "whatsapp"
    OUTRO = "outro"

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String(11), unique=True, nullable=False, index=True)
    data_nascimento = Column(Date, nullable=False)
    sexo = Column(Enum(Sexo), nullable=False)
    telefone = Column(String, nullable=False)
    tipo_contato = Column(Enum(TipoContato), nullable=False)
    email = Column(String, nullable=True)
    endereco = Column(String, nullable=True)
    cidade = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    cep = Column(String, nullable=True)
    data_criacao = Column(TIMESTAMP(timezone=True), server_default=func.now())
    data_atualizacao = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # Relacionamentos
    consultas = relationship("Consulta", back_populates="paciente")
    prontuarios = relationship("Prontuario", back_populates="paciente")