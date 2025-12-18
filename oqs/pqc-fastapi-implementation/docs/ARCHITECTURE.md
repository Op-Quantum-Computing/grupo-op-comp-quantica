# 🏗️ Arquitetura do Sistema PQC FastAPI

Este documento descreve a arquitetura técnica detalhada do sistema de autenticação pós-quântica.

---

## 📐 Visão Geral da Arquitetura

### Diagrama de Alto Nível

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTE                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │  HTTP Client │◄────►│ liboqs-python│◄────►│  Aplicação   │  │
│  │  (requests)  │      │    (KEM)     │      │   Cliente    │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                      │                      │          │
└─────────┼──────────────────────┼──────────────────────┼──────────┘
          │                      │                      │
          │ HTTP/REST            │ Criptografia         │
          │                      │ Local                │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVIDOR (Docker)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    BACKEND (FastAPI)                        │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │                                                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │
│  │  │   API Routes │  │  Middleware  │  │  Dependencies│     │ │
│  │  │   /pqc/*     │  │   (CORS,     │  │  (Auth, PQC) │     │ │
│  │  │   /users/*   │  │   Security)  │  │              │     │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │ │
│  │         │                  │                  │             │ │
│  │         ▼                  ▼                  ▼             │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │              CAMADA DE SERVIÇOS                      │  │ │
│  │  ├─────────────────────────────────────────────────────┤  │ │
│  │  │                                                       │  │ │
│  │  │  ┌───────────────┐      ┌───────────────────────┐   │  │ │
│  │  │  │  PQCService   │      │ PQCSessionManager     │   │  │ │
│  │  │  │               │      │                       │   │  │ │
│  │  │  │ - list_kems() │      │ - create_handshake()  │   │  │ │
│  │  │  │ - gen_keypair │      │ - complete_handshake()│   │  │ │
│  │  │  │ - encapsulate │      │ - validate_session()  │   │  │ │
│  │  │  │ - decapsulate │      │ - revoke_session()    │   │  │ │
│  │  │  └───────┬───────┘      └───────────┬───────────┘   │  │ │
│  │  │          │                           │               │  │ │
│  │  │          ▼                           ▼               │  │ │
│  │  │  ┌───────────────┐      ┌───────────────────────┐   │  │ │
│  │  │  │    liboqs     │      │   In-Memory Store     │   │  │ │
│  │  │  │   (C library) │      │   (Dict/Redis-ready)  │   │  │ │
│  │  │  └───────────────┘      └───────────────────────┘   │  │ │
│  │  │                                                       │  │ │
│  │  └───────────────────────────────────────────────────────┘  │ │
│  │                                                              │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │            CAMADA DE DADOS (SQLModel)               │  │ │
│  │  ├─────────────────────────────────────────────────────┤  │ │
│  │  │  User, Item, Token Models                            │  │ │
│  │  └────────────────────┬─────────────────────────────────┘  │ │
│  │                       │                                     │ │
│  └───────────────────────┼─────────────────────────────────────┘ │
│                          │                                       │
│  ┌───────────────────────▼─────────────────────────────────┐   │
│  │                  POSTGRESQL 17                           │   │
│  │  (Usuários, Items, Configurações)                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Camada Criptográfica

### Fluxo de Key Encapsulation Mechanism (KEM)

```
CLIENTE                                    SERVIDOR
   │                                          │
   │  1. POST /handshake/init                │
   ├─────────────────────────────────────────►│
   │                                          │ gen_keypair()
   │                                          ├──────────►┌──────────┐
   │                                          │            │  liboqs  │
   │                                          │            │  Kyber   │
   │                                          │◄──────────┤          │
   │                                          │ pk + sk    └──────────┘
   │  handshake_id, pk (Base64)              │
   │◄─────────────────────────────────────────┤ Armazena sk temporariamente
   │                                          │
   │                                          │
   │  Encapsulamento LOCAL                   │
   ├──────►┌──────────┐                      │
   │       │  liboqs  │                      │
   │       │  Kyber   │                      │
   │◄──────┤          │                      │
   │  ct + ss         └──────────┘           │
   │                                          │
   │  2. POST /handshake/complete            │
   │     {handshake_id, ct (Base64)}         │
   ├─────────────────────────────────────────►│
   │                                          │ Recupera sk
   │                                          │ decapsulate(sk, ct)
   │                                          ├──────────►┌──────────┐
   │                                          │            │  liboqs  │
   │                                          │            │  Kyber   │
   │                                          │◄──────────┤          │
   │                                          │ ss         └──────────┘
   │                                          │
   │                                          │ hash(ss) = session_hash
   │                                          │ Cria PQCSession
   │                                          │ Descarta sk
   │                                          │
   │  session_id, expires_at                 │
   │◄─────────────────────────────────────────┤
   │                                          │
   │  SESSÃO PQC ESTABELECIDA                │
   │  (ambos têm ss, mas nunca trafegou)     │
   │                                          │
```

### Propriedades de Segurança do KEM

| Propriedade | Descrição | Implementação |
|-------------|-----------|---------------|
| **IND-CCA2** | Indistinguível sob ataque de texto cifrado adaptativo | ✅ Kyber garante |
| **Forward Secrecy** | Comprometimento de chaves futuras não afeta sessões passadas | ✅ TTL curto (5 min) |
| **Quantum Resistance** | Resistente ao algoritmo de Shor | ✅ Baseado em lattices |
| **Secret Never Sent** | Shared secret nunca trafega na rede | ✅ Apenas ciphertext |

---

## 🗄️ Gerenciamento de Sessões PQC

### Estrutura de Dados

#### PendingHandshake (Temporário - 2 minutos)

```python
@dataclass
class PendingHandshake:
    handshake_id: str           # Token seguro (32 bytes)
    user_id: uuid.UUID          # Vínculo com usuário JWT
    algorithm: str              # "Kyber512", "Kyber768", etc.
    secret_key: bytes           # Chave privada KEM (⚠️ temporária)
    public_key: bytes           # Chave pública KEM
    created_at: datetime        # Timestamp de criação
    expires_at: datetime        # created_at + 2 minutos
```

**Armazenamento**: `Dict[str, PendingHandshake]` (em memória)

**Limpeza**: Automática na validação (método `_cleanup_expired_handshakes()`)

#### PQCSession (Ativa - 5 minutos)

```python
@dataclass
class PQCSession:
    session_id: str             # Token seguro (32 bytes)
    user_id: uuid.UUID          # Vínculo com usuário JWT
    algorithm: str              # Algoritmo usado
    shared_secret_hash: str     # SHA-256 do shared secret (🔒 não o segredo)
    created_at: datetime        # Timestamp de criação
    expires_at: datetime        # created_at + 5 minutos
```

**Armazenamento**: `Dict[str, PQCSession]` (em memória)

**Limpeza**: Automática na validação (método `_cleanup_expired_sessions()`)

### Por que In-Memory?

**Vantagens**:
- ⚡ Performance: Validação em O(1)
- 🔒 Segurança: Dados não persistidos em disco
- 🧹 Auto-limpeza: TTL gerenciado automaticamente

**Desvantagens**:
- 🔄 Não compartilhado entre instâncias
- 💾 Perde sessões ao reiniciar

**Migração para Produção**: Use Redis para multi-instância:

```python
# Exemplo de integração com Redis
import redis

class RedisPQCSessionManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    def create_session(self, session: PQCSession):
        key = f"pqc:session:{session.session_id}"
        ttl = int((session.expires_at - session.created_at).total_seconds())
        self.redis.setex(
            key,
            ttl,
            json.dumps(asdict(session))
        )
```

---

## 🛡️ Camada de Autenticação

### Fluxo de Dependency Injection

```python
# 1. JWT Tradicional
CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_user(session: SessionDep, token: TokenDep) -> User:
    # Valida JWT
    # Retorna User do banco
    ...

# 2. JWT + PQC (Step-up Security)
PQCSecuredUser = Annotated[User, Depends(validate_pqc_session)]

def validate_pqc_session(
    current_user: CurrentUser,                    # ✓ Valida JWT primeiro
    x_pqc_session: str = Header(...),            # ✓ Extrai header
) -> User:
    if not pqc_session_manager.validate_session(  # ✓ Valida sessão PQC
        x_pqc_session,
        current_user.id
    ):
        raise HTTPException(status_code=403, ...)
    return current_user
```

### Matriz de Controle de Acesso

| Operação | JWT | PQC | Rota |
|----------|-----|-----|------|
| Listar KEMs | ❌ | ❌ | `GET /pqc/kems` |
| Iniciar Handshake | ✅ | ❌ | `POST /pqc/handshake/init` |
| Completar Handshake | ✅ | ❌ | `POST /pqc/handshake/complete` |
| Ver perfil | ✅ | ❌ | `GET /users/me` |
| **Trocar senha** | ✅ | ✅ | `PATCH /users/me/password` |
| **Deletar conta** | ✅ | ✅ | `DELETE /users/me` |
| Criar item | ✅ | ❌ | `POST /items` |
| Listar items | ✅ | ❌ | `GET /items` |

---

## 📦 Estrutura de Módulos

### Backend (`backend/app/`)

```
app/
├── api/                      # Camada de API REST
│   ├── deps.py               # Dependencies (get_current_user, validate_pqc_session)
│   ├── main.py               # Router principal
│   └── routes/
│       ├── pqc.py            # 🔐 Endpoints PQC
│       ├── users.py          # Endpoints de usuário (com PQCSecuredUser)
│       ├── items.py          # CRUD de items
│       ├── login.py          # Login JWT
│       └── utils.py          # Health checks
│
├── core/                     # Núcleo do sistema
│   ├── config.py             # Settings (DEFAULT_PQC_KEM, PQC_SESSION_TTL_MINUTES)
│   ├── db.py                 # Configuração SQLModel/PostgreSQL
│   ├── security.py           # Hash de senhas, JWT
│   └── pqc_sessions.py       # 🔑 PQCSessionManager
│
├── models.py                 # Modelos Pydantic/SQLModel
│   ├── User, Item            # Modelos de banco
│   └── PQC*                  # Schemas PQC (Request/Response)
│
├── services/                 # Camada de serviços
│   └── pqc.py                # 🔐 PQCService (wrapper liboqs)
│
├── crud.py                   # Operações CRUD genéricas
└── main.py                   # App FastAPI principal
```

### Responsabilidades dos Módulos

#### `services/pqc.py` - PQCService

**Responsabilidade**: Wrapper para liboqs, abstrai operações KEM

**Métodos principais**:

```python
class PQCService:
    def list_kem_algorithms() -> list[KEMDetails]
        """Lista algoritmos KEM disponíveis."""

    def generate_keypair(algorithm: str) -> KEMKeyPair
        """Gera par de chaves (pk, sk)."""

    def encapsulate_secret(algorithm: str, public_key_b64: str) -> tuple[bytes, bytes]
        """Cliente: Encapsula segredo → (ciphertext, shared_secret)."""

    def decapsulate_secret(algorithm: str, secret_key: bytes, ciphertext: bytes) -> bytes
        """Servidor: Decapsula ciphertext → shared_secret."""
```

**Dependências**: `oqs` (liboqs-python)

#### `core/pqc_sessions.py` - PQCSessionManager

**Responsabilidade**: Gerenciar ciclo de vida de handshakes e sessões

**Métodos principais**:

```python
class PQCSessionManager:
    def create_pending_handshake(...) -> PendingHandshake
        """Cria handshake pendente (TTL 2 min)."""

    def get_pending_handshake(handshake_id: str) -> PendingHandshake | None
        """Recupera handshake (com limpeza de expirados)."""

    def complete_handshake(handshake_id: str, shared_secret: bytes) -> PQCSession
        """Completa handshake → cria sessão PQC (TTL 5 min)."""

    def validate_session(session_id: str, user_id: UUID) -> bool
        """Valida sessão PQC ativa."""

    def revoke_session(session_id: str) -> bool
        """Revoga sessão (logout PQC)."""
```

**Armazenamento**: In-memory (Dict)

#### `api/routes/pqc.py` - Endpoints REST

**Responsabilidade**: Expor operações PQC via HTTP

**Endpoints**:

| Método | Rota | Autenticação | Descrição |
|--------|------|--------------|-----------|
| GET | `/pqc/kems` | ❌ | Lista algoritmos |
| POST | `/pqc/handshake/init` | JWT | Inicia handshake |
| POST | `/pqc/handshake/complete` | JWT | Completa handshake |
| DELETE | `/pqc/session/{id}` | JWT | Revoga sessão |
| GET | `/pqc/sessions/stats` | JWT | Estatísticas |
| POST | `/pqc/kem/handshake` | ❌ | ⚠️ Demo apenas |

---

## 🐳 Docker e Build Pipeline

### Multi-stage Dockerfile

```dockerfile
FROM python:3.10

# 1. Instala dependências do sistema
RUN apt-get update && \
    apt-get install -y build-essential git cmake libssl-dev

# 2. Build liboqs C library
RUN git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs /tmp/liboqs && \
    cmake -S /tmp/liboqs -B /tmp/liboqs/build \
        -DBUILD_SHARED_LIBS=ON \
        -DOQS_ENABLE_SIG_STFL_LMS=ON \
        -DOQS_ENABLE_SIG_STFL_XMSS=ON && \
    cmake --build /tmp/liboqs/build --parallel 4 && \
    cmake --build /tmp/liboqs/build --target install && \
    rm -rf /tmp/liboqs

# 3. Configura LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

# 4. Instala uv (gerenciador de pacotes rápido)
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# 5. Instala dependências Python (incluindo liboqs-python)
RUN uv sync

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
```

### Docker Compose

```yaml
services:
  backend:
    build:
      context: ./backend
    environment:
      - DEFAULT_PQC_KEM=Kyber512
      - PQC_SESSION_TTL_MINUTES=5
      - POSTGRES_SERVER=db
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/utils/health-check/"]

  db:
    image: postgres:17
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
```

---

## 🔒 Considerações de Segurança

### Ameaças Mitigadas

| Ameaça | Mitigação | Status |
|--------|-----------|--------|
| **Token JWT roubado** | Sessão PQC exigida para ops críticas | ✅ |
| **Replay attack** | TTL curto (5 min) + session_id único | ✅ |
| **MITM (Man-in-the-Middle)** | TLS + Segredo nunca enviado | ✅ |
| **Ataques quânticos futuros** | Kyber (resistente a Shor) | ✅ |
| **Brute force de sessão** | Token criptograficamente seguro (32 bytes) | ✅ |

### Ameaças NÃO Mitigadas (Escopo Futuro)

| Ameaça | Solução Proposta |
|--------|------------------|
| **Sessões perdidas ao reiniciar** | Migrar para Redis |
| **Multi-instância** | Redis com TTL distribuído |
| **Side-channel attacks** | Implementação constant-time (liboqs já faz) |
| **DoS em handshakes** | Rate limiting |

---

## 📊 Performance

### Benchmarks (Kyber512)

| Operação | Tempo Médio | Tamanho |
|----------|-------------|---------|
| **Geração de chaves** | ~0.05ms | pk: 800B, sk: 1632B |
| **Encapsulamento** | ~0.07ms | ct: 768B, ss: 32B |
| **Decapsulamento** | ~0.08ms | ss: 32B |
| **Handshake completo** | ~0.2ms | Total: ~2.5KB trafegado |

**Comparação com RSA-2048**:
- Kyber512 é **5-10x mais rápido**
- Chaves **menores** que RSA-4096
- **Resistente a ataques quânticos**

---

## 🔮 Roadmap Futuro

### Fase 1: Produção-Ready
- [ ] Migrar sessões para Redis
- [ ] Adicionar rate limiting
- [ ] Implementar métricas (Prometheus)
- [ ] Testes de carga

### Fase 2: Segurança Avançada
- [ ] Dilithium para assinaturas digitais
- [ ] TLS híbrido (clássico + PQC)
- [ ] Audit log de sessões PQC
- [ ] Rotação automática de chaves

### Fase 3: Escalabilidade
- [ ] Kubernetes deployment
- [ ] Multi-região com sincronização
- [ ] Cache distribuído
- [ ] Monitoramento centralizado

---

## 📚 Referências Técnicas

### Algoritmos

- **Kyber**: [CRYSTALS-Kyber Specification (NIST Round 3)](https://pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf)
- **NIST PQC**: [Post-Quantum Cryptography Standardization](https://csrc.nist.gov/projects/post-quantum-cryptography)

### Implementação

- **liboqs**: [Open Quantum Safe Library](https://github.com/open-quantum-safe/liboqs)
- **liboqs-python**: [Python Bindings](https://github.com/open-quantum-safe/liboqs-python)

### Teoria

- **Lattice-based Crypto**: [Introduction to Lattice-based Cryptography](https://www.youtube.com/watch?v=...)
- **KEM vs PKE**: [Key Encapsulation vs Public Key Encryption](https://en.wikipedia.org/wiki/Key_encapsulation_mechanism)

---

**Mantido por**: Grupo de Computação Quântica (Ever, Gabriel Pelinsari, Leandro, Paula, Rodrigo)
