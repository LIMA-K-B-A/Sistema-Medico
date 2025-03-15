# app/models/consulta.py
from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
import enum
from .usuario import Base

class StatusConsulta(enum.Enum):
    AGENDADA = "agendada"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    CONCLUIDA = "concluida"
    REMARCADA = "remarcada"

class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("medicos.id"), nullable=False)
    data_consulta = Column(Date, nullable=False)
    hora_consulta = Column(Time, nullable=False)
    problema_saude = Column(Text, nullable=True)
    status = Column(Enum(StatusConsulta), default=StatusConsulta.AGENDADA, nullable=False)
    notificacao_enviada = Column(Boolean, default=False)
    lembrete_enviado = Column(Boolean, default=False)
    observacoes = Column(Text, nullable=True)
    data_criacao = Column(TIMESTAMP(timezone=True), server_default=func.now())
    data_atualizacao = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # Relacionamentos
    paciente = relationship("Paciente", back_populates="consultas")
    medico = relationship("Medico", back_populates="consultas")
    prontuario = relationship("Prontuario", back_populates="consulta", uselist=False)