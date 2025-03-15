# app/models/usuario.py
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
import enum

Base = declarative_base()

class TipoUsuario(enum.Enum):
    ADMINISTRADOR = "administrador"
    MEDICO = "medico"
    RECEPCIONISTA = "recepcionista"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    senha_hash = Column(String, nullable=False)
    tipo = Column(Enum(TipoUsuario), nullable=False)
    foto_perfil = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
    data_criacao = Column(TIMESTAMP(timezone=True), server_default=func.now())
    data_atualizacao = Column(TIMESTAMP(timezone=True), onupdate=func.now())
