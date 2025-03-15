# app/models/medico.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .usuario import Base, TipoUsuario

class Medico(Base):
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    crm = Column(String, unique=True, nullable=False, index=True)
    especialidade = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    cpf = Column(String(11), unique=True, nullable=False)
    horario_inicio_atendimento = Column(String, nullable=False, default="08:00")
    horario_fim_atendimento = Column(String, nullable=False, default="18:00")
    dias_atendimento = Column(String, nullable=False, default="1,2,3,4,5")  # 0=Dom, 1=Seg, ..., 6=Sáb
    tempo_consulta = Column(Integer, nullable=False, default=30)  # em minutos
    data_criacao = Column(TIMESTAMP(timezone=True), server_default=func.now())
    data_atualizacao = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # Relacionamentos
    usuario = relationship("Usuario")
    consultas = relationship("Consulta", back_populates="medico")