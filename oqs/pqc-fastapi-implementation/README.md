# 🔐 PQC FastAPI Implementation

> Sistema de autenticação híbrido com criptografia pós-quântica usando liboqs

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![liboqs](https://img.shields.io/badge/liboqs-latest-blue.svg)](https://openquantumsafe.org/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

---

## 📖 Sobre

Este projeto implementa **autenticação resistente a computadores quânticos** combinando:

- **JWT tradicional** para controle de acesso
- **Sessões PQC** baseadas em KEMs (Key Encapsulation Mechanisms) para operações críticas

### Características

✅ Algoritmos NIST: Kyber512/768/1024
✅ Step-up security: PQC apenas quando necessário
✅ Docker-ready com liboqs compilado
✅ API REST completa e documentada
✅ Cliente demo Python incluído

---

## 🚀 Início Rápido

### 1. Pré-requisitos

- Docker & Docker Compose
- Python 3.10+ (para cliente demo)

### 2. Inicie os Serviços

```bash
# Clone e navegue até o diretório
git clone https://github.com/Op-Quantum-Computing/grupo-op-comp-quantica.git
cd grupo-op-comp-quantica/oqs/pqc-fastapi-implementation

# Configure variáveis de ambiente
cp .env.example .env

# Inicie com Docker Compose
docker-compose up -d
```

### 3. Verifique a Instalação

```bash
# Health check
curl http://localhost:8000/api/v1/utils/health-check/

# Documentação interativa
open http://localhost:8000/docs
```

### 4. Execute o Cliente Demo

```bash
# Instale liboqs-python localmente
pip install liboqs-python

# Execute o demo
cd examples
python pqc_client_demo.py
```

**Saída esperada**: Demonstração completa do fluxo JWT + PQC

---

## 📚 Documentação

### Guias Principais

| Documento | Descrição |
|-----------|-----------|
| **[README Principal](../README.md)** | 👈 Visão geral completa do projeto |
| **[QUICK_START.md](./docs/QUICK_START.md)** | Tutorial passo a passo |
| **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** | Arquitetura técnica detalhada |
| **[PQC_INTEGRATION.md](./docs/PQC_INTEGRATION.md)** | Guia de integração |

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🏗️ Estrutura do Projeto

```
pqc-fastapi-implementation/
├── backend/                # API FastAPI
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── pqc.py        # 🔐 Endpoints PQC
│   │   │   │   └── users.py      # Rotas protegidas
│   │   │   └── deps.py           # Dependencies (validate_pqc_session)
│   │   ├── services/
│   │   │   └── pqc.py            # 🔑 PQCService (liboqs wrapper)
│   │   ├── core/
│   │   │   ├── pqc_sessions.py   # Gerenciador de sessões
│   │   │   └── config.py         # Configurações
│   │   └── models.py             # Schemas Pydantic
│   ├── Dockerfile                # 🐳 Build com liboqs
│   └── pyproject.toml
│
├── frontend/               # Interface React (opcional)
│
├── docs/                   # 📖 Documentação técnica
│   ├── QUICK_START.md
│   ├── ARCHITECTURE.md
│   └── PQC_INTEGRATION.md
│
├── examples/               # 💡 Exemplos
│   └── pqc_client_demo.py
│
├── docker-compose.yml
└── README.md              # 👈 Você está aqui
```

---

## 🔐 Como Funciona

### Fluxo de Autenticação

```
1. Login JWT
   └─> POST /api/v1/login/access-token

2. Handshake PQC - Init
   └─> POST /api/v1/pqc/handshake/init
       ├─ Servidor gera par de chaves KEM
       └─ Retorna: handshake_id + public_key

3. Cliente Encapsula (Local)
   └─ Usa liboqs para criar ciphertext + shared_secret

4. Handshake PQC - Complete
   └─> POST /api/v1/pqc/handshake/complete
       ├─ Servidor decapsula com chave privada
       └─ Retorna: session_id

5. Operação Protegida
   └─> Headers: Authorization + X-PQC-Session
   └─> Exemplo: PATCH /users/me/password
```

### Endpoints PQC

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | `/pqc/kems` | ❌ | Lista algoritmos KEM |
| POST | `/pqc/handshake/init` | JWT | Inicia handshake |
| POST | `/pqc/handshake/complete` | JWT | Completa handshake |
| DELETE | `/pqc/session/{id}` | JWT | Revoga sessão |
| GET | `/pqc/sessions/stats` | JWT | Estatísticas |

### Rotas Protegidas com PQC

- `PATCH /api/v1/users/me/password` - Troca de senha
- `DELETE /api/v1/users/me` - Exclusão de conta

**Requer**: `Authorization` + `X-PQC-Session`

---

## 🛠️ Tecnologias

| Componente | Tecnologia |
|------------|------------|
| Framework | FastAPI 0.115+ |
| Criptografia | liboqs (Open Quantum Safe) |
| Algoritmo KEM | Kyber512/768/1024 (NIST) |
| Banco de dados | PostgreSQL 17 |
| ORM | SQLModel |
| Containerização | Docker + Docker Compose |

---

## 🧪 Desenvolvimento

### Executar Localmente (sem Docker)

```bash
cd backend

# Instale liboqs (veja docs/QUICK_START.md)

# Instale dependências Python
pip install -r requirements.txt

# Configure .env
cp .env.example .env

# Inicie o servidor
uvicorn app.main:app --reload
```

### Executar Testes

```bash
# Entre no container
docker-compose exec backend bash

# Execute pytest
pytest tests/ -v
```

### Acessar o Banco de Dados

```bash
# Via Adminer (web)
open http://localhost:8080

# Via psql
docker-compose exec db psql -U postgres app
```

---

## 📊 Status do Projeto

### Implementado

- ✅ Autenticação JWT tradicional
- ✅ Handshake PQC em 2 etapas
- ✅ Gerenciamento de sessões in-memory
- ✅ Rotas protegidas com PQC
- ✅ Cliente demo Python
- ✅ Docker com liboqs
- ✅ Documentação completa

### Roadmap

- [ ] Migração para Redis (multi-instância)
- [ ] Rate limiting nos endpoints PQC
- [ ] Métricas e monitoramento
- [ ] Suporte a Dilithium (assinaturas)
- [ ] TLS híbrido (clássico + PQC)
- [ ] Testes de carga

---

## 👥 Equipe

Desenvolvido por:

- **Ever**
- **Gabriel Pelinsari**
- **Leandro**
- **Paula**
- **Rodrigo**

**Instituição**: Grupo de Pesquisa em Computação Quântica - Op-Quantum-Computing

---

## 📚 Referências

### Open Quantum Safe

- [Site oficial](https://openquantumsafe.org/)
- [GitHub liboqs](https://github.com/open-quantum-safe/liboqs)
- [liboqs-python](https://github.com/open-quantum-safe/liboqs-python)

### NIST PQC

- [NIST PQC Project](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Kyber Specification](https://pq-crystals.org/kyber/)

---

## 📝 Licença

MIT License - veja [LICENSE](./LICENSE) para detalhes.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](./CONTRIBUTING.md) para diretrizes.

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/Op-Quantum-Computing/grupo-op-comp-quantica/issues)
- **Documentação**: Veja [`docs/`](./docs/)

---

<div align="center">

**Desenvolvido com 💜 pelo Grupo de Computação Quântica**

[⬆ Voltar ao README Principal](../README.md)

</div>
