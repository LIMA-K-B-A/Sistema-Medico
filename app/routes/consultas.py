from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date, time, datetime, timedelta
from ..database import get_db
from ..schemas.consulta import Consulta, ConsultaCreate, ConsultaUpdate, ConsultaDetalhada, StatusConsulta
from ..models.consulta import Consulta as ConsultaModel, StatusConsulta as StatusConsultaModel
from ..models.paciente import Paciente as PacienteModel
from ..models.medico import Medico as MedicoModel
from ..models.usuario import Usuario as UsuarioModel
from ..auth import recepcionista_or_above_required, medico_required
from ..services.email_service import enviar_notificacao_consulta, enviar_lembrete_consulta

router = APIRouter(
    prefix="/consultas",
    tags=["consultas"]
)

@router.get("/", response_model=List[ConsultaDetalhada])
def get_consultas(
    skip: int = 0, 
    limit: int = 100,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    medico_id: Optional[int] = None,
    paciente_id: Optional[int] = None,
    status: Optional[StatusConsulta] = None,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    query = db.query(ConsultaModel).\
        join(PacienteModel, ConsultaModel.paciente_id == PacienteModel.id).\
        join(MedicoModel, ConsultaModel.medico_id == MedicoModel.id).\
        join(UsuarioModel, MedicoModel.usuario_id == UsuarioModel.id)
    
    if data_inicio:
        query = query.filter(ConsultaModel.data_consulta >= data_inicio)
    
    if data_fim:
        query = query.filter(ConsultaModel.data_consulta <= data_fim)
    
    if medico_id:
        query = query.filter(ConsultaModel.medico_id == medico_id)
    
    if paciente_id:
        query = query.filter(ConsultaModel.paciente_id == paciente_id)
    
    if status:
        query = query.filter(ConsultaModel.status == status)
    
    consultas = query.offset(skip).limit(limit).all()
    
    resultado = []
    for consulta in consultas:
        paciente = db.query(PacienteModel).filter(PacienteModel.id == consulta.paciente_id).first()
        medico = db.query(MedicoModel).filter(MedicoModel.id == consulta.medico_id).first()
        usuario_medico = db.query(UsuarioModel).filter(UsuarioModel.id == medico.usuario_id).first()
        
        consulta_detalhada = {
            **consulta.__dict__,
            "paciente_nome": paciente.nome,
            "paciente_cpf": paciente.cpf,
            "medico_nome": usuario_medico.nome,
            "medico_especialidade": medico.especialidade
        }
        resultado.append(consulta_detalhada)
    
    return resultado

@router.get("/{consulta_id}", response_model=ConsultaDetalhada)
def get_consulta(
    consulta_id: int, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    consulta = db.query(ConsultaModel).filter(ConsultaModel.id == consulta_id).first()
    if consulta is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    paciente = db.query(PacienteModel).filter(PacienteModel.id == consulta.paciente_id).first()
    medico = db.query(MedicoModel).filter(MedicoModel.id == consulta.medico_id).first()
    usuario_medico = db.query(UsuarioModel).filter(UsuarioModel.id == medico.usuario_id).first()
    
    consulta_detalhada = {
        **consulta.__dict__,
        "paciente_nome": paciente.nome,
        "paciente_cpf": paciente.cpf,
        "medico_nome": usuario_medico.nome,
        "medico_especialidade": medico.especialidade
    }
    
    return consulta_detalhada

@router.post("/", response_model=ConsultaDetalhada)
def create_consulta(
    consulta_data: ConsultaCreate, 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    # Verificar se o paciente existe
    paciente = db.query(PacienteModel).filter(PacienteModel.id == consulta_data.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Verificar se o médico existe
    medico = db.query(MedicoModel).filter(MedicoModel.id == consulta_data.medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Verificar se o horário está disponível para o médico
    # Converter a string para um objeto time
    hora_inicio = consulta_data.hora_consulta
    hora_fim = (datetime.combine(datetime.today(), hora_inicio) + timedelta(minutes=medico.tempo_consulta)).time()
    
    # Verificar se há alguma consulta neste horário para este médico
    consulta_existente = db.query(ConsultaModel).filter(
        ConsultaModel.medico_id == consulta_data.medico_id,
        ConsultaModel.data_consulta == consulta_data.data_consulta,
        ConsultaModel.status != StatusConsultaModel.CANCELADA,
        ((ConsultaModel.hora_consulta <= hora_inicio) & 
         (datetime.combine(datetime.min, ConsultaModel.hora_consulta) + 
          timedelta(minutes=medico.tempo_consulta) > datetime.combine(datetime.min, hora_inicio))) |
        ((ConsultaModel.hora_consulta < hora_fim) & 
         (ConsultaModel.hora_consulta >= hora_inicio))
    ).first()
    
    if consulta_existente:
        raise HTTPException(status_code=400, detail="Horário não disponível para este médico")
    
    # Verificar se o dia da semana está disponível para o médico
    dia_semana = consulta_data.data_consulta.weekday()  # 0=Seg, 1=Ter, ..., 6=Dom
    dias_atendimento = [int(d) for d in medico.dias_atendimento.split(",")]
    
    if dia_semana not in dias_atendimento:
        raise HTTPException(status_code=400, detail="O médico não atende neste dia da semana")
    
    # Verificar se o horário está dentro do horário de atendimento do médico
    horario_inicio_medico = datetime.strptime(medico.horario_inicio_atendimento, "%H:%M").time()
    horario_fim_medico = datetime.strptime(medico.horario_fim_atendimento, "%H:%M").time()
    
    if hora_inicio < horario_inicio_medico or hora_fim > horario_fim_medico:
        raise HTTPException(
            status_code=400, 
            detail=f"Horário fora do período de atendimento do médico ({medico.horario_inicio_atendimento} - {medico.horario_fim_atendimento})"
        )
    
    # Criar a consulta
    db_consulta = ConsultaModel(
        paciente_id=consulta_data.paciente_id,
        medico_id=consulta_data.medico_id,
        data_consulta=consulta_data.data_consulta,
        hora_consulta=consulta_data.hora_consulta,
        problema_saude=consulta_data.problema_saude,
        status=consulta_data.status,
        observacoes=consulta_data.observacoes
    )
    
    db.add(db_consulta)
    db.commit()
    db.refresh(db_consulta)
    
    # Enviar e-mail de notificação para o paciente
    try:
        usuario_medico = db.query(UsuarioModel).filter(UsuarioModel.id == medico.usuario_id).first()
        enviar_notificacao_consulta(
            paciente.email,
            paciente.nome,
            usuario_medico.nome,
            medico.especialidade,
            db_consulta.data_consulta,
            db_consulta.hora_consulta
        )
        db_consulta.notificacao_enviada = True
        db.commit()
    except Exception as e:
        # Não falhar se o e-mail não puder ser enviado
        print(f"Erro ao enviar notificação: {e}")
    
    consulta_detalhada = {
        **db_consulta.__dict__,
        "paciente_nome": paciente.nome,
        "paciente_cpf": paciente.cpf,
        "medico_nome": usuario_medico.nome,
        "medico_especialidade": medico.especialidade
    }
    
    return consulta_detalhada

@router.put("/{consulta_id}", response_model=ConsultaDetalhada)
def update_consulta(
    consulta_id: int,
    consulta_data: ConsultaUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    db_consulta = db.query(ConsultaModel).filter(ConsultaModel.id == consulta_id).first()
    if db_consulta is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    # Se estamos alterando a data ou hora, precisamos verificar disponibilidade
    if consulta_data.data_consulta is not None or consulta_data.hora_consulta is not None:
        data_consulta = consulta_data.data_consulta or db_consulta.data_consulta
        hora_consulta = consulta_data.hora_consulta or db_consulta.hora_consulta
        
        medico = db.query(MedicoModel).filter(MedicoModel.id == db_consulta.medico_id).first()
        
        hora_fim = (datetime.combine(datetime.today(), hora_consulta) + timedelta(minutes=medico.tempo_consulta)).time()
        
        # Verificar se há alguma consulta neste horário para este médico (exceto a atual)
        consulta_existente = db.query(ConsultaModel).filter(
            ConsultaModel.id != consulta_id,
            ConsultaModel.medico_id == db_consulta.medico_id,
            ConsultaModel.data_consulta == data_consulta,
            ConsultaModel.status != StatusConsultaModel.CANCELADA,
            ((ConsultaModel.hora_consulta <= hora_consulta) & 
             (datetime.combine(datetime.min, ConsultaModel.hora_consulta) + 
              timedelta(minutes=medico.tempo_consulta) > datetime.combine(datetime.min, hora_consulta))) |
            ((ConsultaModel.hora_consulta < hora_fim) & 
             (ConsultaModel.hora_consulta >= hora_consulta))
        ).first()
        
        if consulta_existente:
            raise HTTPException(status_code=400, detail="Horário não disponível para este médico")
        
        # Verificar se o dia da semana está disponível para o médico
        dia_semana = data_consulta.weekday()
        dias_atendimento = [int(d) for d in medico.dias_atendimento.split(",")]
        
        if dia_semana not in dias_atendimento:
            raise HTTPException(status_code=400, detail="O médico não atende neste dia da semana")
        
        # Verificar se o horário está dentro do horário de atendimento do médico
        horario_inicio_medico = datetime.strptime(medico.horario_inicio_atendimento, "%H:%M").time()
        horario_fim_medico = datetime.strptime(medico.horario_fim_atendimento, "%H:%M").time()
        
        if hora_consulta < horario_inicio_medico or hora_fim > horario_fim_medico:
            raise HTTPException(
                status_code=400, 
                detail=f"Horário fora do período de atendimento do médico ({medico.horario_inicio_atendimento} - {medico.horario_fim_atendimento})"
            )
    
    # Atualizar os campos da consulta
    if consulta_data.paciente_id is not None:
        # Verificar se o paciente existe
        paciente = db.query(PacienteModel).filter(PacienteModel.id == consulta_data.paciente_id).first()
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        db_consulta.paciente_id = consulta_data.paciente_id
    
    if consulta_data.medico_id is not None:
        # Verificar se o médico existe
        medico = db.query(MedicoModel).filter(MedicoModel.id == consulta_data.medico_id).first()
        if not medico:
            raise HTTPException(status_code=404, detail="Médico não encontrado")
        db_consulta.medico_id = consulta_data.medico_id
    
    if consulta_data.data_consulta is not None:
        db_consulta.data_consulta = consulta_data.data_consulta
    
    if consulta_data.hora_consulta is not None:
        db_consulta.hora_consulta = consulta_data.hora_consulta
    
    if consulta_data.problema_saude is not None:
        db_consulta.problema_saude = consulta_data.problema_saude
    
    if consulta_data.status is not None:
        db_consulta.status = consulta_data.status
    
    if consulta_data.observacoes is not None:
        db_consulta.observacoes = consulta_data.observacoes
    
    db.commit()
    db.refresh(db_consulta)
    
    # Enviar notificação de atualização se o status mudou para CONFIRMADA
    if consulta_data.status == StatusConsultaModel.CONFIRMADA and not db_consulta.notificacao_enviada:
        try:
            paciente = db.query(PacienteModel).filter(PacienteModel.id == db_consulta.paciente_id).first()
            medico = db.query(MedicoModel).filter(MedicoModel.id == db_consulta.medico_id).first()
            usuario_medico = db.query(UsuarioModel).filter(UsuarioModel.id == medico.usuario_id).first()
            enviar_notificacao_consulta(
                paciente.email,
                paciente.nome,
                usuario_medico.nome,
                medico.especialidade,
                db_consulta.data_consulta,
                db_consulta.hora_consulta
            )
            db_consulta.notificacao_enviada = True
            db.commit()
        except Exception as e:
            # Não falhar se o e-mail não puder ser enviado
            print(f"Erro ao enviar notificação: {e}")
    
    # Buscar dados atualizados para o retorno
    paciente = db.query(PacienteModel).filter(PacienteModel.id == db_consulta.paciente_id).first()
    medico = db.query(MedicoModel).filter(MedicoModel.id == db_consulta.medico_id).first()
    usuario_medico = db.query(UsuarioModel).filter(UsuarioModel.id == medico.usuario_id).first()
    
    consulta_detalhada = {
        **db_consulta.__dict__,
        "paciente_nome": paciente.nome,
        "paciente_cpf": paciente.cpf,
        "medico_nome": usuario_medico.nome,
        "medico_especialidade": medico.especialidade
    }
    
    return consulta_detalhada

@router.delete("/{consulta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    db_consulta = db.query(ConsultaModel).filter(ConsultaModel.id == consulta_id).first()
    if db_consulta is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    # Em vez de excluir, marcamos como cancelada
    db_consulta.status = StatusConsultaModel.CANCELADA
    db.commit()
    
    return None

@router.patch("/{consulta_id}/status", response_model=ConsultaDetalhada)
def update_consulta_status(
    consulta_id: int,
    status: StatusConsulta,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    db_consulta = db.query(ConsultaModel).filter(ConsultaModel.id == consulta_id).first()
    if db_consulta is None:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    db_consulta.status = status
    db.commit()
    db.refresh(db_consulta)
    
    # Buscar dados para o retorno
    paciente = db.query(PacienteModel).filter(PacienteModel.id == db_consulta.paciente_id).first()
    medico = db.query(MedicoModel).filter(MedicoModel.id == db_consulta.medico_id).first()
    usuario_medico = db.query(UsuarioModel).filter(UsuarioModel.id == medico.usuario_id).first()
    
    consulta_detalhada = {
        **db_consulta.__dict__,
        "paciente_nome": paciente.nome,
        "paciente_cpf": paciente.cpf,
        "medico_nome": usuario_medico.nome,
        "medico_especialidade": medico.especialidade
    }
    
    return consulta_detalhada

@router.get("/medico/minhas-consultas", response_model=List[ConsultaDetalhada])
def get_consultas_medico(
    data_inicial: Optional[date] = None,
    data_final: Optional[date] = None,
    status: Optional[StatusConsulta] = None,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(medico_required)
):
    # Obter o ID do médico pelo usuário atual
    medico = db.query(MedicoModel).filter(MedicoModel.usuario_id == current_user.id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado para este usuário")
    
    query = db.query(ConsultaModel).filter(ConsultaModel.medico_id == medico.id)
    
    if data_inicial:
        query = query.filter(ConsultaModel.data_consulta >= data_inicial)
    
    if data_final:
        query = query.filter(ConsultaModel.data_consulta <= data_final)
    
    if status:
        query = query.filter(ConsultaModel.status == status)
    
    # Ordenar por data e hora
    query = query.order_by(ConsultaModel.data_consulta, ConsultaModel.hora_consulta)
    
    consultas = query.all()
    
    resultado = []
    for consulta in consultas:
        paciente = db.query(PacienteModel).filter(PacienteModel.id == consulta.paciente_id).first()
        
        consulta_detalhada = {
            **consulta.__dict__,
            "paciente_nome": paciente.nome,
            "paciente_cpf": paciente.cpf,
            "medico_nome": current_user.nome,
            "medico_especialidade": medico.especialidade
        }
        resultado.append(consulta_detalhada)
    
    return resultado

@router.get("/agenda/disponibilidade")
def get_disponibilidade_medico(
    medico_id: int,
    data_consulta: date,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    # Verificar se o médico existe
    medico = db.query(MedicoModel).filter(MedicoModel.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Verificar se o médico atende nesse dia da semana
    dia_semana = data_consulta.weekday()
    dias_atendimento = [int(d) for d in medico.dias_atendimento.split(",")]
    
    if dia_semana not in dias_atendimento:
        return {"disponibilidade": [], "mensagem": "O médico não atende neste dia da semana"}
    
    # Obter o horário de atendimento do médico
    horario_inicio = datetime.strptime(medico.horario_inicio_atendimento, "%H:%M").time()
    horario_fim = datetime.strptime(medico.horario_fim_atendimento, "%H:%M").time()
    tempo_consulta = medico.tempo_consulta
    
    # Obter todas as consultas do médico para a data especificada
    consultas = db.query(ConsultaModel).filter(
        ConsultaModel.medico_id == medico_id,
        ConsultaModel.data_consulta == data_consulta,
        ConsultaModel.status != StatusConsultaModel.CANCELADA
    ).all()
    
    # Calcular horários ocupados
    horarios_ocupados = []
    for consulta in consultas:
        hora_inicio = consulta.hora_consulta
        hora_fim = (datetime.combine(datetime.today(), hora_inicio) + timedelta(minutes=tempo_consulta)).time()
        horarios_ocupados.append((hora_inicio, hora_fim))
    
    # Calcular horários disponíveis
    horarios_disponiveis = []
    hora_atual = horario_inicio
    
    while hora_atual < horario_fim:
        # Verificar se o horário atual está disponível
        hora_fim_atual = (datetime.combine(datetime.today(), hora_atual) + timedelta(minutes=tempo_consulta)).time()
        
        # Se passar do horário final de atendimento, interromper
        if hora_fim_atual > horario_fim:
            break
        
        disponivel = True
        for inicio, fim in horarios_ocupados:
            # Verificar se há sobreposição
            if (hora_atual < fim and hora_fim_atual > inicio):
                disponivel = False
                break
        
        if disponivel:
            horarios_disponiveis.append({
                "hora_inicio": hora_atual.strftime("%H:%M"),
                "hora_fim": hora_fim_atual.strftime("%H:%M")
            })
        
        # Avançar para o próximo horário
        hora_atual = (datetime.combine(datetime.today(), hora_atual) + timedelta(minutes=tempo_consulta)).time()
    
    return {
        "medico_id": medico_id,
        "medico_nome": db.query(UsuarioModel).filter(UsuarioModel.id == medico.usuario_id).first().nome,
        "especialidade": medico.especialidade,
        "data_consulta": data_consulta.strftime("%Y-%m-%d"),
        "tempo_consulta": f"{tempo_consulta} minutos",
        "disponibilidade": horarios_disponiveis
    }

@router.post("/enviar-lembretes")
def enviar_lembretes_consultas(
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(recepcionista_or_above_required)
):
    # Buscar consultas para o dia seguinte que ainda não receberam lembrete
    amanha = datetime.now().date() + timedelta(days=1)
    consultas = db.query(ConsultaModel).filter(
        ConsultaModel.data_consulta == amanha,
        ConsultaModel.status == StatusConsultaModel.CONFIRMADA,
        ConsultaModel.lembrete_enviado == False
    ).all()
    
    resultados = {
        "total_consultas": len(consultas),
        "lembretes_enviados": 0,
        "erros": []
    }
    
    for consulta in consultas:
        paciente = db.query(PacienteModel).filter(PacienteModel.id == consulta.paciente_id).first()
        medico = db.query(MedicoModel).filter(MedicoModel.id == consulta.medico_id).first()
        usuario_medico = db.query(UsuarioModel).filter(UsuarioModel.id == medico.usuario_id).first()
        
        try:
            enviar_lembrete_consulta(
                paciente.email,
                paciente.nome,
                usuario_medico.nome,
                medico.especialidade,
                consulta.data_consulta,
                consulta.hora_consulta
            )
            consulta.lembrete_enviado = True
            resultados["lembretes_enviados"] += 1
        except Exception as e:
            resultados["erros"].append({
                "consulta_id": consulta.id,
                "paciente": paciente.nome,
                "erro": str(e)
            })
    
    db.commit()
    return resultados