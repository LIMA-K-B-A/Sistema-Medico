# app/routes/usuarios.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from ..models.usuario import Usuario as UsuarioModel
from ..auth import get_password_hash, admin_required

router = APIRouter(
    prefix="/usuarios",
    tags=["usuários"]
)

@router.get("/", response_model=List[Usuario])
def get_usuarios(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    usuarios = db.query(UsuarioModel).offset(skip).limit(limit).all()
    return usuarios

@router.get("/{usuario_id}", response_model=Usuario)
def get_usuario(
    usuario_id: int, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.post("/", response_model=Usuario)
def create_usuario(
    usuario: UsuarioCreate, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    hashed_password = get_password_hash(usuario.senha)
    db_usuario = UsuarioModel(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=hashed_password,
        tipo=usuario.tipo,
        foto_perfil=usuario.foto_perfil,
        ativo=usuario.ativo
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.put("/{usuario_id}", response_model=Usuario)
def update_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Atualizar os campos
    if usuario.email is not None:
        # Verificar se o novo email já existe (exceto para o próprio usuário)
        existing_user = db.query(UsuarioModel).filter(
            UsuarioModel.email == usuario.email,
            UsuarioModel.id != usuario_id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        db_usuario.email = usuario.email
    
    if usuario.nome is not None:
        db_usuario.nome = usuario.nome
    
    if usuario.foto_perfil is not None:
        db_usuario.foto_perfil = usuario.foto_perfil
    
    if usuario.ativo is not None:
        db_usuario.ativo = usuario.ativo
    
    if usuario.senha is not None:
        db_usuario.senha_hash = get_password_hash(usuario.senha)
    
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Em vez de deletar, marcar como inativo
    db_usuario.ativo = False
    db.commit()
    return {"detail": "Usuário removido com sucesso"}