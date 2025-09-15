# 🏥 Sistema de Gerenciamento de Consultas Médicas

## 📋 Visão Geral

Sistema completo de gerenciamento de consultas médicas desenvolvido com **FastAPI** e **PostgreSQL**. O sistema oferece funcionalidades completas para agendamento, gerenciamento de pacientes, médicos e prontuários médicos, com sistema de autenticação robusto e notificações por e-mail.

## 🎯 Funcionalidades Principais

### 👥 Gestão de Usuários

- **Sistema de Autenticação JWT** com diferentes níveis de acesso
- **Três tipos de usuários**: Administrador, Médico e Recepcionista
- **Controle de permissões** granular por funcionalidade
- **Gerenciamento de perfis** com foto e dados pessoais

### 🩺 Gestão de Médicos

- **Cadastro completo** com CRM, especialidade e dados pessoais
- **Configuração de horários** de atendimento personalizados
- **Dias da semana** de atendimento configuráveis
- **Tempo de consulta** personalizado por médico
- **Validação de CRM** e CPF únicos

### 👤 Gestão de Pacientes

- **Cadastro detalhado** com dados pessoais e de contato
- **Múltiplos tipos de contato** (celular, telefone fixo, WhatsApp)
- **Endereço completo** com CEP, cidade e estado
- **Validação de CPF** único no sistema

### 📅 Sistema de Consultas

- **Agendamento inteligente** com verificação de disponibilidade
- **Validação de conflitos** de horários automaticamente
- **Status de consulta** (Agendada, Confirmada, Cancelada, Concluída, Remarcada)
- **Notificações automáticas** por e-mail
- **Lembretes** de consultas
- **Consulta de disponibilidade** em tempo real

### 📋 Prontuários Médicos

- **Registro de diagnósticos** e tratamentos
- **Observações médicas** detalhadas
- **Histórico completo** de consultas por paciente
- **Vinculação** com médicos e consultas

### 📊 Dashboard e Relatórios

- **Visão geral** do sistema
- **Estatísticas** de consultas e pacientes
- **Relatórios** por período e médico
- **Métricas** de utilização

## 🛠️ Tecnologias Utilizadas

### Backend

- **FastAPI** - Framework web moderno e rápido para APIs
- **Python 3.8+** - Linguagem de programação
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL** - Banco de dados relacional
- **Pydantic** - Validação de dados e serialização
- **JWT** - Autenticação e autorização
- **Bcrypt** - Criptografia de senhas

### Segurança

- **OAuth2** com Bearer Token
- **JWT (JSON Web Tokens)** para autenticação
- **Bcrypt** para hash de senhas
- **Validação de dados** com Pydantic
- **Controle de acesso** baseado em roles

### Banco de Dados

- **PostgreSQL** - Banco de dados principal
- **SQLAlchemy** - ORM e migrações
- **Alembic** - Controle de versão do banco

### Comunicação

- **SMTP** - Envio de e-mails
- **FastAPI** - API REST com documentação automática

## 🏗️ Arquitetura do Sistema

### Estrutura de Pastas

```
app/
├── models/          # Modelos de dados (SQLAlchemy)
├── schemas/         # Schemas de validação (Pydantic)
├── routes/          # Endpoints da API
├── services/        # Lógica de negócio
├── utils/           # Utilitários e helpers
├── auth.py          # Sistema de autenticação
├── config.py        # Configurações
├── database.py      # Conexão com banco
└── main.py          # Aplicação principal
```

### Padrões de Design

- **Repository Pattern** - Separação entre dados e lógica
- **Dependency Injection** - Injeção de dependências do FastAPI
- **Service Layer** - Camada de serviços para lógica de negócio
- **Schema Validation** - Validação de dados com Pydantic
- **ORM Mapping** - Mapeamento objeto-relacional com SQLAlchemy

## 🚀 Como Executar

### Pré-requisitos

- Python 3.8 ou superior
- PostgreSQL 12 ou superior
- Docker e Docker Compose (opcional)

### Instalação Local

1. **Clone o repositório**

```bash
git clone <url-do-repositorio>
cd Sistema-Medico
```

2. **Crie um ambiente virtual**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
   Crie um arquivo `.env` na raiz do projeto:

```env
# Banco de dados
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=consultas_medicas

# Segurança
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# E-mail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app
EMAIL_FROM=seu-email@gmail.com
```

5. **Configure o banco de dados**

```bash
# Crie o banco de dados PostgreSQL
createdb consultas_medicas

# Execute as migrações (quando implementadas)
alembic upgrade head
```

6. **Execute a aplicação**

```bash
uvicorn app.main:app --reload
```

### Execução com Docker

1. **Execute com Docker Compose**

```bash
docker-compose up -d
```

2. **Acesse a aplicação**

- API: http://localhost:8000
- Documentação: http://localhost:8000/docs
- Banco: localhost:5432

## 📚 Documentação da API

### Endpoints Principais

#### Autenticação

- `POST /api/auth/login` - Login de usuário
- `POST /api/auth/register` - Registro de usuário

#### Usuários

- `GET /api/usuarios/` - Listar usuários
- `POST /api/usuarios/` - Criar usuário
- `GET /api/usuarios/{id}` - Obter usuário
- `PUT /api/usuarios/{id}` - Atualizar usuário
- `DELETE /api/usuarios/{id}` - Remover usuário

#### Médicos

- `GET /api/medicos/` - Listar médicos
- `POST /api/medicos/` - Criar médico
- `GET /api/medicos/{id}` - Obter médico
- `PUT /api/medicos/{id}` - Atualizar médico
- `DELETE /api/medicos/{id}` - Remover médico

#### Pacientes

- `GET /api/pacientes/` - Listar pacientes
- `POST /api/pacientes/` - Criar paciente
- `GET /api/pacientes/{id}` - Obter paciente
- `PUT /api/pacientes/{id}` - Atualizar paciente
- `DELETE /api/pacientes/{id}` - Remover paciente

#### Consultas

- `GET /api/consultas/` - Listar consultas
- `POST /api/consultas/` - Agendar consulta
- `GET /api/consultas/{id}` - Obter consulta
- `PUT /api/consultas/{id}` - Atualizar consulta
- `DELETE /api/consultas/{id}` - Cancelar consulta
- `PATCH /api/consultas/{id}/status` - Alterar status
- `GET /api/consultas/agenda/disponibilidade` - Verificar disponibilidade
- `POST /api/consultas/enviar-lembretes` - Enviar lembretes

### Documentação Interativa

Acesse `http://localhost:8000/docs` para a documentação interativa da API (Swagger UI).

## 🔐 Sistema de Autenticação

### Tipos de Usuário

1. **Administrador**: Acesso total ao sistema
2. **Médico**: Acesso a consultas e prontuários
3. **Recepcionista**: Acesso a agendamentos e pacientes

### Fluxo de Autenticação

1. Usuário faz login com email e senha
2. Sistema valida credenciais
3. JWT token é gerado e retornado
4. Token é usado em requisições subsequentes
5. Sistema valida token e permissões

## 📧 Sistema de Notificações

### Tipos de E-mail

- **Confirmação de agendamento**
- **Lembretes de consulta**
- **Cancelamentos**
- **Remarcações**

### Configuração

Configure as credenciais SMTP no arquivo `.env` para habilitar o envio de e-mails.

## 🗄️ Modelo de Dados

### Entidades Principais

- **Usuario**: Dados de login e perfil
- **Medico**: Informações profissionais
- **Paciente**: Dados pessoais e contato
- **Consulta**: Agendamentos e status
- **Prontuario**: Histórico médico

### Relacionamentos

- Usuario 1:1 Medico
- Medico 1:N Consulta
- Paciente 1:N Consulta
- Consulta 1:1 Prontuario
- Paciente 1:N Prontuario

## 🔧 Configurações

### Variáveis de Ambiente

- `SECRET_KEY`: Chave secreta para JWT
- `POSTGRES_*`: Configurações do banco
- `SMTP_*`: Configurações de e-mail
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Tempo de expiração do token

### Configurações do Médico

- Horários de atendimento
- Dias da semana
- Tempo de consulta
- Especialidade

## 🧪 Testes

### Executar Testes

```bash
pytest
```

### Cobertura de Testes

```bash
pytest --cov=app
```

## 🚀 Deploy

### Produção

1. Configure variáveis de ambiente de produção
2. Use um banco PostgreSQL em produção
3. Configure HTTPS
4. Use um servidor WSGI como Gunicorn

### Docker

```bash
docker build -t sistema-medico .
docker run -p 8000:8000 sistema-medico
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

Desenvolvido para a matéria de **Programação Web 1**.

## 📞 Suporte

Para dúvidas ou suporte, entre em contato através dos issues do GitHub.

---

**Sistema desenvolvido com ❤️ usando FastAPI e PostgreSQL**
