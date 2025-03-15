# app/models/prontuario.py
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .usuario import Base

class Prontuario(Base):
    __tablename__ = "prontuarios"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    consulta_id = Column(Integer, ForeignKey("consultas.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("medicos.id"), nullable=False)
    diagnostico = Column(Text, nullable=True)
    tratamento = Column(Text, nullable=True)
    observacoes = Column(Text, nullable=True)
    data_criacao = Column(TIMESTAMP(timezone=True), server_default=func.now())
    data_atualizacao = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # Relacionamentos
    paciente = relationship("Paciente", back_populates="prontuarios")
    consulta = relationship("Consulta", back_populates="prontuario")
    medico = relationship("Medico")