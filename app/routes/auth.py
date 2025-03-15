# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..schemas.auth import Token, Login
from ..schemas.usuario import UsuarioCreate, Usuario
from ..models.usuario import Usuario as UsuarioModel, TipoUsuario
from ..auth import verify_password, create_access_token, get_password_hash
from ..config import settings

router = APIRouter(
    prefix="/auth",
    tags=["autenticação"]
)

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UsuarioModel).filter(UsuarioModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "tipo": user.tipo.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=Usuario)
def register_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar se o email já existe
    db_user = db.query(UsuarioModel).filter(UsuarioModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    # Criar o usuário
    hashed_password = get_password_hash(user.senha)
    db_user = UsuarioModel(
        nome=user.nome,
        email=user.email,
        senha_hash=hashed_password,
        tipo=TipoUsuario[user.tipo.name],
        foto_perfil=user.foto_perfil,
        ativo=user.ativo
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user