# app/schemas/prontuario.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProntuarioBase(BaseModel):
    paciente_id: int
    consulta_id: int
    medico_id: int
    diagnostico: Optional[str] = None
    tratamento: Optional[str] = None
    observacoes: Optional[str] = None

class ProntuarioCreate(ProntuarioBase):
    pass

class ProntuarioUpdate(BaseModel):
    diagnostico: Optional[str] = None
    tratamento: Optional[str] = None
    observacoes: Optional[str] = None

class Prontuario(ProntuarioBase):
    id: int
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None

    class Config:
        orm_mode = True