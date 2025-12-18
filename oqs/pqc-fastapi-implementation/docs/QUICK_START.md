# 🚀 Guia de Início Rápido - PQC FastAPI

Este guia fornece instruções passo a passo para configurar e executar o sistema de autenticação pós-quântica.

---

## 📋 Pré-requisitos

### Obrigatórios

- **Docker**: 20.10 ou superior
- **Docker Compose**: 2.0 ou superior
- **Git**: Para clonar o repositório

### Opcionais (para desenvolvimento local)

- **Python**: 3.10 ou superior
- **liboqs-python**: Para executar o cliente demo localmente
- **Node.js**: 18+ (se for trabalhar com o frontend)

---

## 🏁 Configuração Inicial

### 1. Clone o Repositório

```bash
git clone https://github.com/Op-Quantum-Computing/grupo-op-comp-quantica.git
cd grupo-op-comp-quantica/oqs/pqc-fastapi-implementation
```

### 2. Configure as Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite conforme necessário
nano .env
```

**Variáveis importantes**:

```env
# Configurações do projeto
PROJECT_NAME="PQC FastAPI"
ENVIRONMENT=local

# Banco de dados
POSTGRES_SERVER=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis123
POSTGRES_DB=app

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 dias

# PQC Específico
DEFAULT_PQC_KEM=Kyber512
PQC_SESSION_TTL_MINUTES=5

# Usuário admin inicial
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis
```

### 3. Inicie os Containers

```bash
# Build e start dos serviços
docker-compose up -d

# Acompanhe os logs
docker-compose logs -f backend
```

**Primeira execução**: O build do liboqs leva aproximadamente 5-7 minutos.

### 4. Verifique a Instalação

```bash
# Health check da API
curl http://localhost:8000/api/v1/utils/health-check/

# Esperado: {"status":"ok"}
```

**URLs importantes**:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Frontend: http://localhost:5173 (se habilitado)
- Adminer (DB): http://localhost:8080

---

## 🔐 Testando a Autenticação PQC

### Opção 1: Cliente Demo Python (Recomendado)

#### Instalação Local do liboqs

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential git cmake libssl-dev
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs && mkdir build && cd build
cmake -DCMAKE_INSTALL_PREFIX=/usr/local ..
make && sudo make install

# Instale o binding Python
pip install liboqs-python
```

#### Execute o Demo

```bash
cd examples
python pqc_client_demo.py
```

**Saída esperada**:

```
============================================================
  DEMONSTRAÇÃO: Autenticação PQC (Post-Quantum Crypto)
============================================================

📧 1. Login JWT...
✅ JWT obtido: eyJhbGciOiJIUzI1NiIsInR5cCI6...

🔐 2. Listar algoritmos PQC...
✅ 12 algoritmos disponíveis:
   - Kyber512: NIST Level 1
   - Kyber768: NIST Level 3
   - Kyber1024: NIST Level 5

🤝 3. Handshake PQC (Kyber512)...
✅ Sessão PQC criada!

🔒 4. Trocar senha (operação protegida)...
✅ Operação protegida autenticada com sucesso!

⚠️  5. Testar sem sessão PQC (deve falhar)...
✅ Corretamente rejeitado! (falta X-PQC-Session)
```

### Opção 2: Usando cURL (Manual)

#### 1. Login JWT

```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" \
  | jq -r '.access_token')

echo "JWT Token: $TOKEN"
```

#### 2. Listar Algoritmos KEM

```bash
curl -X GET "http://localhost:8000/api/v1/pqc/kems" | jq
```

#### 3. Iniciar Handshake PQC

```bash
HANDSHAKE=$(curl -s -X POST "http://localhost:8000/api/v1/pqc/handshake/init" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"algorithm":"Kyber512"}')

HANDSHAKE_ID=$(echo $HANDSHAKE | jq -r '.handshake_id')
PUBLIC_KEY=$(echo $HANDSHAKE | jq -r '.public_key')

echo "Handshake ID: $HANDSHAKE_ID"
```

#### 4. Encapsular Segredo (Requer liboqs-python)

```python
import oqs
import base64

public_key = base64.b64decode("$PUBLIC_KEY")

with oqs.KeyEncapsulation('Kyber512') as client:
    ciphertext, shared_secret = client.encap_secret(public_key)

ciphertext_b64 = base64.b64encode(ciphertext).decode()
print(ciphertext_b64)
```

#### 5. Completar Handshake

```bash
SESSION=$(curl -s -X POST "http://localhost:8000/api/v1/pqc/handshake/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"handshake_id\":\"$HANDSHAKE_ID\",\"ciphertext\":\"$CIPHERTEXT_B64\"}")

SESSION_ID=$(echo $SESSION | jq -r '.session_id')
echo "PQC Session ID: $SESSION_ID"
```

#### 6. Testar Operação Protegida

```bash
# Com sessão PQC (deve funcionar)
curl -X PATCH "http://localhost:8000/api/v1/users/me/password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-PQC-Session: $SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"changethis","new_password":"newpassword123"}'

# Sem sessão PQC (deve falhar com 403)
curl -X PATCH "http://localhost:8000/api/v1/users/me/password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"changethis","new_password":"newpassword123"}'
```

### Opção 3: Swagger UI (Interativo)

1. Acesse http://localhost:8000/docs
2. Clique em **Authorize** e faça login
3. Navegue até os endpoints `/pqc/*`
4. Execute os endpoints na ordem:
   - `POST /pqc/handshake/init`
   - *(use liboqs localmente para encapsular)*
   - `POST /pqc/handshake/complete`
   - `PATCH /users/me/password` (adicione header `X-PQC-Session`)

---

## 🧪 Validação da Instalação

### Checklist de Validação

```bash
# ✅ Containers rodando
docker-compose ps

# ✅ Backend respondendo
curl http://localhost:8000/api/v1/utils/health-check/

# ✅ Liboqs instalado no container
docker-compose exec backend python -c "import oqs; print(oqs.get_enabled_kem_mechanisms()[:5])"

# ✅ Banco de dados conectado
docker-compose exec backend python -c "from app.core.db import engine; engine.connect()"

# ✅ Endpoints PQC disponíveis
curl http://localhost:8000/api/v1/pqc/kems | jq
```

### Testes Automatizados

```bash
# Entre no container
docker-compose exec backend bash

# Execute os testes
pytest tests/ -v

# Testes específicos de PQC (se existirem)
pytest tests/test_pqc.py -v
```

---

## 🐛 Troubleshooting

### Problema: Build do Docker falha

**Sintoma**: Erro ao compilar liboqs

**Solução**:
```bash
# Limpe o cache do Docker
docker-compose down -v
docker system prune -a

# Rebuild sem cache
docker-compose build --no-cache backend
```

### Problema: Erro "liboqs not found"

**Sintoma**: `ModuleNotFoundError: No module named 'oqs'`

**Solução**:
```bash
# Verifique se liboqs está instalado no container
docker-compose exec backend python -c "import oqs; print('OK')"

# Se falhar, rebuild o container
docker-compose build backend
```

### Problema: Handshake PQC expira

**Sintoma**: `404 Handshake not found or expired`

**Solução**:
- Handshakes pendentes expiram em **2 minutos**
- Inicie e complete o handshake rapidamente
- Aumente o TTL em `app/core/pqc_sessions.py` se necessário

### Problema: Sessão PQC inválida

**Sintoma**: `403 Valid PQC session required`

**Solução**:
- Sessões PQC expiram em **5 minutos** (padrão)
- Refaça o handshake
- Verifique se o header `X-PQC-Session` está presente

### Problema: Erro de conexão com banco

**Sintoma**: `Connection refused` ao PostgreSQL

**Solução**:
```bash
# Verifique se o container do DB está rodando
docker-compose ps db

# Veja os logs do banco
docker-compose logs db

# Reinicie os serviços
docker-compose restart
```

---

## 📊 Monitoramento

### Logs em Tempo Real

```bash
# Todos os serviços
docker-compose logs -f

# Apenas backend
docker-compose logs -f backend

# Últimas 100 linhas
docker-compose logs --tail=100 backend
```

### Estatísticas de Sessões PQC

```bash
curl -X GET "http://localhost:8000/api/v1/pqc/sessions/stats" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Resposta**:
```json
{
  "pending_handshakes": 2,
  "active_sessions": 5
}
```

### Métricas do Container

```bash
# Uso de recursos
docker stats

# Inspecionar container
docker-compose exec backend top
```

---

## 🔄 Operações Comuns

### Reiniciar Serviços

```bash
# Reiniciar tudo
docker-compose restart

# Apenas backend
docker-compose restart backend
```

### Atualizar Código

```bash
# Pull das mudanças
git pull origin main

# Rebuild e restart
docker-compose up -d --build
```

### Limpar Dados

```bash
# Remove volumes (⚠️ perde dados do DB)
docker-compose down -v

# Rebuild completo
docker-compose up -d --build
```

### Backup do Banco

```bash
# Export do banco
docker-compose exec db pg_dump -U postgres app > backup.sql

# Restore
docker-compose exec -T db psql -U postgres app < backup.sql
```

---

## 🎓 Próximos Passos

1. **Explore a API**: http://localhost:8000/docs
2. **Leia a documentação técnica**: [PQC_INTEGRATION.md](./PQC_INTEGRATION.md)
3. **Entenda a arquitetura**: [ARCHITECTURE.md](./ARCHITECTURE.md)
4. **Customize algoritmos**: Edite `DEFAULT_PQC_KEM` no `.env`
5. **Adicione mais rotas protegidas**: Use `PQCSecuredUser` dependency

---

## 📚 Recursos Adicionais

- [Documentação liboqs](https://github.com/open-quantum-safe/liboqs/wiki)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [NIST PQC Project](https://csrc.nist.gov/projects/post-quantum-cryptography)

---

**Dúvidas?** Abra uma issue no [GitHub](https://github.com/Op-Quantum-Computing/grupo-op-comp-quantica/issues)
