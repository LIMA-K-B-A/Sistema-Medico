# app/routes/medicos.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..database import get_db
from ..schemas.medico import Medico, MedicoCreate, MedicoUpdate, MedicoCompleto
from ..models.medico import Medico as MedicoModel
from ..models.usuario import Usuario as UsuarioModel, TipoUsuario
from ..auth import admin_required, medico_required, get_password_hash

router = APIRouter(
    prefix="/medicos",
    tags=["médicos"]
)

@router.get("/", response_model=List[MedicoCompleto])
def get_medicos(
    skip: int = 0, 
    limit: int = 100,
    nome: Optional[str] = None,
    especialidade: Optional[str] = None,
    crm: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(medico_required)
):
    query = db.query(MedicoModel).join(UsuarioModel)
    
    if nome:
        query = query.filter(UsuarioModel.nome.ilike(f"%{nome}%"))
    if especialidade:
        query = query.filter(MedicoModel.especialidade.ilike(f"%{especialidade}%"))
    if crm:
        query = query.filter(MedicoModel.crm.ilike(f"%{crm}%"))
    
    medicos = query.offset(skip).limit(limit).all()
    
    resultado = []
    for medico in medicos:
        medico_completo = {
            **medico.__dict__,
            "nome": medico.usuario.nome,
            "email": medico.usuario.email,
            "foto_perfil": medico.usuario.foto_perfil,
            "ativo": medico.usuario.ativo
        }
        resultado.append(medico_completo)
    
    return resultado

@router.get("/{medico_id}", response_model=MedicoCompleto)
def get_medico(
    medico_id: int, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(medico_required)
):
    medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()
    if medico is None:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == medico.usuario_id).first()
    
    medico_completo = {
        **medico.__dict__,
        "nome": usuario.nome,
        "email": usuario.email,
        "foto_perfil": usuario.foto_perfil,
        "ativo": usuario.ativo
    }
    
    return medico_completo

@router.post("/", response_model=MedicoCompleto)
def create_medico(
    medico_data: MedicoCreate, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    # Verificar se já existe um médico com esse CRM
    existing_medico = db.query(MedicoModel).filter(MedicoModel.crm == medico_data.crm).first()
    if existing_medico:
        raise HTTPException(status_code=400, detail="CRM já cadastrado")
    
    # Verificar se já existe um médico com esse CPF
    existing_medico = db.query(MedicoModel).filter(MedicoModel.cpf == medico_data.cpf).first()
    if existing_medico:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    # Verificar se o usuário existe
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == medico_data.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se o usuário já está atribuído a um médico
    existing_medico = db.query(MedicoModel).filter(MedicoModel.usuario_id == medico_data.usuario_id).first()
    if existing_medico:
        raise HTTPException(status_code=400, detail="Este usuário já está atribuído a um médico")
    
    # Verificar se o usuário é do tipo médico
    if usuario.tipo != TipoUsuario.MEDICO:
        raise HTTPException(status_code=400, detail="O usuário deve ser do tipo 'medico'")
    
    db_medico = MedicoModel(
        usuario_id=medico_data.usuario_id,
        crm=medico_data.crm,
        especialidade=medico_data.especialidade,
        telefone=medico_data.telefone,
        data_nascimento=medico_data.data_nascimento,
        cpf=medico_data.cpf,
        horario_inicio_atendimento=medico_data.horario_inicio_atendimento,
        horario_fim_atendimento=medico_data.horario_fim_atendimento,
        dias_atendimento=medico_data.dias_atendimento,
        tempo_consulta=medico_data.tempo_consulta
    )
    
    db.add(db_medico)
    db.commit()
    db.refresh(db_medico)
    
    medico_completo = {
        **db_medico.__dict__,
        "nome": usuario.nome,
        "email": usuario.email,
        "foto_perfil": usuario.foto_perfil,
        "ativo": usuario.ativo
    }
    
    return medico_completo

@router.put("/{medico_id}", response_model=MedicoCompleto)
def update_medico(
    medico_id: int,
    medico_data: MedicoUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    db_medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    if medico_data.crm is not None:
        # Verificar se o novo CRM já existe (exceto para o próprio médico)
        existing_medico = db.query(MedicoModel).filter(
            MedicoModel.crm == medico_data.crm,
            MedicoModel.id != medico_id
        ).first()
        if existing_medico:
            raise HTTPException(status_code=400, detail="CRM já cadastrado")
        db_medico.crm = medico_data.crm
    
    if medico_data.especialidade is not None:
        db_medico.especialidade = medico_data.especialidade
    
    if medico_data.telefone is not None:
        db_medico.telefone = medico_data.telefone
    
    if medico_data.horario_inicio_atendimento is not None:
        db_medico.horario_inicio_atendimento = medico_data.horario_inicio_atendimento
    
    if medico_data.horario_fim_atendimento is not None:
        db_medico.horario_fim_atendimento = medico_data.horario_fim_atendimento
    
    if medico_data.dias_atendimento is not None:
        db_medico.dias_atendimento = medico_data.dias_atendimento
    
    if medico_data.tempo_consulta is not None:
        db_medico.tempo_consulta = medico_data.tempo_consulta
    
    db.commit()
    db.refresh(db_medico)
    
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == db_medico.usuario_id).first()
    
    medico_completo = {
        **db_medico.__dict__,
        "nome": usuario.nome,
        "email": usuario.email,
        "foto_perfil": usuario.foto_perfil,
        "ativo": usuario.ativo
    }
    
    return medico_completo

@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medico(
    medico_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    db_medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Desativar o usuário associado ao médico
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == db_medico.usuario_id).first()
    if usuario:
        usuario.ativo = False
    
    # Em sistemas reais, você pode preferir não excluir os registros permanentemente
    db.delete(db_medico)
    db.commit()
    
    return {"detail": "Médico removido com sucesso"}