# app/schemas/medico.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime

class MedicoBase(BaseModel):
    usuario_id: int
    crm: str
    especialidade: str
    telefone: str
    data_nascimento: date
    cpf: str = Field(..., min_length=11, max_length=11)
    horario_inicio_atendimento: str = "08:00"
    horario_fim_atendimento: str = "18:00"
    dias_atendimento: str = "1,2,3,4,5"  # 0=Dom, 1=Seg, ..., 6=Sáb
    tempo_consulta: int = 30  # em minutos

class MedicoCreate(MedicoBase):
    pass

class MedicoUpdate(BaseModel):
    crm: Optional[str] = None
    especialidade: Optional[str] = None
    telefone: Optional[str] = None
    horario_inicio_atendimento: Optional[str] = None
    horario_fim_atendimento: Optional[str] = None
    dias_atendimento: Optional[str] = None
    tempo_consulta: Optional[int] = None

class Medico(MedicoBase):
    id: int
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None

    class Config:
        orm_mode = True

class MedicoCompleto(Medico):
    nome: str
    email: EmailStr
    foto_perfil: Optional[str] = None
    ativo: bool