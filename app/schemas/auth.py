# app/schemas/auth.py
from pydantic import BaseModel
from typing import Optional
from .usuario import Usuario, TipoUsuario

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    tipo: Optional[TipoUsuario] = None

class Login(BaseModel):
    email: str
    senha: str