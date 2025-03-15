# app/schemas/consulta.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time, datetime
from enum import Enum

class StatusConsulta(str, Enum):
    AGENDADA = "agendada"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    CONCLUIDA = "concluida"
    REMARCADA = "remarcada"

class ConsultaBase(BaseModel):
    paciente_id: int
    medico_id: int
    data_consulta: date
    hora_consulta: time
    problema_saude: Optional[str] = None
    status: StatusConsulta = StatusConsulta.AGENDADA
    observacoes: Optional[str] = None

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaUpdate(BaseModel):
    data_consulta: Optional[date] = None
    hora_consulta: Optional[time] = None
    problema_saude: Optional[str] = None
    status: Optional[StatusConsulta] = None
    observacoes: Optional[str] = None

class Consulta(ConsultaBase):
    id: int
    notificacao_enviada: bool
    lembrete_enviado: bool
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None

    class Config:
        orm_mode = True

class ConsultaDetalhada(Consulta):
    paciente_nome: str
    paciente_cpf: str
    medico_nome: str
    medico_especialidade: str