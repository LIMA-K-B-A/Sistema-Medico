# app/schemas/paciente.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class Sexo(str, Enum):
    MASCULINO = "masculino"
    FEMININO = "feminino"
    OUTRO = "outro"

class TipoContato(str, Enum):
    CELULAR = "celular"
    TELEFONE_FIXO = "telefone_fixo"
    WHATSAPP = "whatsapp"
    OUTRO = "outro"

class PacienteBase(BaseModel):
    nome: str
    cpf: str = Field(..., min_length=11, max_length=11)
    data_nascimento: date
    sexo: Sexo
    telefone: str
    tipo_contato: TipoContato
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(BaseModel):
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    sexo: Optional[Sexo] = None
    telefone: Optional[str] = None
    tipo_contato: Optional[TipoContato] = None
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None

class Paciente(PacienteBase):
    id: int
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None

    class Config:
        orm_mode = True