# app/routes/pacientes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas.paciente import Paciente, PacienteCreate, PacienteUpdate
from ..models.paciente import Paciente as PacienteModel
from ..models.usuario import Usuario as UsuarioModel
from ..auth import recepcionista_or_above_required

router = APIRouter(
    prefix="/pacientes",
    tags=["pacientes"]
)

@router.get("/", response_model=List[Paciente])
def get_pacientes(
    skip: int = 0, 
    limit: int = 100,
    nome: Optional[str] = None,
    cpf: Optional[str] = None,
    email: Optional[str] = None,
    telefone: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    query = db.query(PacienteModel)
    
    if nome:
        query = query.filter(PacienteModel.nome.ilike(f"%{nome}%"))
    if cpf:
        query = query.filter(PacienteModel.cpf.ilike(f"%{cpf}%"))
    if email:
        query = query.filter(PacienteModel.email.ilike(f"%{email}%"))
    if telefone:
        query = query.filter(PacienteModel.telefone.ilike(f"%{telefone}%"))
    
    pacientes = query.offset(skip).limit(limit).all()
    return pacientes

@router.get("/{paciente_id}", response_model=Paciente)
def get_paciente(
    paciente_id: int, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    paciente = db.query(PacienteModel).filter(PacienteModel.id == paciente_id).first()
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente

@router.post("/", response_model=Paciente)
def create_paciente(
    paciente: PacienteCreate, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    # Verificar se já existe um paciente com esse CPF
    db_paciente = db.query(PacienteModel).filter(PacienteModel.cpf == paciente.cpf).first()
    if db_paciente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    db_paciente = PacienteModel(
        nome=paciente.nome,
        cpf=paciente.cpf,
        data_nascimento=paciente.data_nascimento,
        sexo=paciente.sexo,
        telefone=paciente.telefone,
        tipo_contato=paciente.tipo_contato,
        email=paciente.email,
        endereco=paciente.endereco,
        cidade=paciente.cidade,
        estado=paciente.estado,
        cep=paciente.cep
    )
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

@router.put("/{paciente_id}", response_model=Paciente)
def update_paciente(
    paciente_id: int,
    paciente: PacienteUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    db_paciente = db.query(PacienteModel).filter(PacienteModel.id == paciente_id).first()
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Atualizar os campos
    if paciente.nome is not None:
        db_paciente.nome = paciente.nome
    
    if paciente.data_nascimento is not None:
        db_paciente.data_nascimento = paciente.data_nascimento
    
    if paciente.sexo is not None:
        db_paciente.sexo = paciente.sexo
    
    if paciente.telefone is not None:
        db_paciente.telefone = paciente.telefone
    
    if paciente.tipo_contato is not None:
        db_paciente.tipo_contato = paciente.tipo_contato
    
    if paciente.email is not None:
        db_paciente.email = paciente.email
    
    if paciente.endereco is not None:
        db_paciente.endereco = paciente.endereco
    
    if paciente.cidade is not None:
        db_paciente.cidade = paciente.cidade
    
    if paciente.estado is not None:
        db_paciente.estado = paciente.estado
    
    if paciente.cep is not None:
        db_paciente.cep = paciente.cep
    
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    db_paciente = db.query(PacienteModel).filter(PacienteModel.id == paciente_id).first()
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Em sistemas reais de saúde, geralmente não excluímos registros de pacientes permanentemente
    # Em vez disso, podemos implementar algum tipo de marcação como "inativo"
    # Para este exemplo, vamos excluir o registro
    db.delete(db_paciente)
    db.commit()
    
    return {"detail": "Paciente removido com sucesso"}