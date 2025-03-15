# app/schemas/usuario.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TipoUsuario(str, Enum):
    ADMINISTRADOR = "administrador"
    MEDICO = "medico"
    RECEPCIONISTA = "recepcionista"

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    tipo: TipoUsuario
    foto_perfil: Optional[str] = None
    ativo: bool = True

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    foto_perfil: Optional[str] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = None

class UsuarioInDB(UsuarioBase):
    id: int
    senha_hash: str
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None

    class Config:
        orm_mode = True

class Usuario(UsuarioBase):
    id: int
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None

    class Config:
        orm_mode = True