# Integração de Criptografia Pós-Quântica

Este documento resume a integração do [Open Quantum Safe](https://openquantumsafe.org) (liboqs + `python-oqs`) ao backend FastAPI. O objetivo é oferecer uma base didática para explorar e demonstrar algoritmos de encapsulamento de chaves (KEM) resistentes a ataques com computadores quânticos.

## Visão Geral

1. **Dependência**: `oqs` foi adicionada em `pyproject.toml` para disponibilizar as bindings Python da liboqs.
2. **Configuração**: a variável `DEFAULT_PQC_KEM` no `Settings` define o algoritmo padrão usado nos fluxos de demonstração (valor inicial `Kyber512`).
3. **Camadas**:
   - `app/services/pqc.py`: wrapper orientado a serviço para listar algoritmos e executar handshakes.
   - `app/api/routes/pqc.py`: expõe duas rotas REST sob `/api/v1/pqc`.
   - `app/models.py`: modelos Pydantic/SQLModel descrevendo os payloads de requisição e resposta.

O fluxo mantém todos os artefatos binários (chave pública, ciphertext, segredos compartilhados) em Base64 para facilitar o consumo por clientes HTTP.

## Pré-requisitos

1. **liboqs instalada**: siga as instruções oficiais do Open Quantum Safe para o seu sistema operacional; o pacote Python espera encontrar a biblioteca nativa.
2. **Dependências Python**: no diretório `backend/`, rode `uv sync` (ou `pip install -r requirements.txt` se adaptar o projeto) para instalar `oqs` e demais pacotes.

```bash
cd backend
uv sync
```

Se estiver usando Docker, garanta que a imagem inclui liboqs antes de subir os contêineres.

## Endpoints Disponíveis

### 1. Listar algoritmos KEM

- **Rota**: `GET /api/v1/pqc/kems`
- **Resposta**:

```json
{
  "data": [
    {
      "name": "Kyber512",
      "claimed_nist_level": 1,
      "is_classical_secured": true,
      "length_public_key": 800,
      "length_secret_key": 1632,
      "length_ciphertext": 768,
      "length_shared_secret": 32
    },
    {
      "name": "Kyber768",
      "...": "..."
    }
  ]
}
```

Use esta rota para descobrir quais mecanismos estão habilitados no build atual da liboqs.

### 2. Executar um handshake KEM demonstrativo

- **Rota**: `POST /api/v1/pqc/kem/handshake`
- **Body opcional**:

```json
{
  "algorithm": "Kyber512"
}
```

Se o campo for omitido, o serviço usará `settings.DEFAULT_PQC_KEM`.

- **Resposta** (campos relevantes):

```json
{
  "algorithm": "Kyber512",
  "public_key": "BASE64...",
  "ciphertext": "BASE64...",
  "server_shared_secret": "BASE64...",
  "client_shared_secret": "BASE64...",
  "shared_secret_match": true,
  "details": {
    "name": "Kyber512",
    "claimed_nist_level": 1,
    "is_classical_secured": true,
    "length_public_key": 800,
    "length_secret_key": 1632,
    "length_ciphertext": 768,
    "length_shared_secret": 32
  }
}
```

O backend gera o par de chaves do “servidor”, encapsula o segredo no “cliente” e depois decapsula para confirmar que ambos chegam ao mesmo segredo compartilhado (`shared_secret_match`).

## Estrutura do Código

| Arquivo | Função |
| --- | --- |
| `app/services/pqc.py` | Implementa `PQCService`, com métodos para listar algoritmos habilitados e executar handshakes. |
| `app/api/routes/pqc.py` | Define o router FastAPI, instanciando o serviço e retornando modelos prontos para a API. |
| `app/models.py` | Contém `PQCKEMAlgorithm`, `PQCKEMAlgorithms`, `PQCKEMHandshakeRequest` e `PQCKEMHandshakeResponse`. |
| `app/core/config.py` | Acrescenta `DEFAULT_PQC_KEM` às configurações. |
| `backend/README.md` | Resumo de alto nível das novas rotas. |

## Personalizações e Próximos Passos

1. **Alterar o algoritmo padrão**: ajuste `DEFAULT_PQC_KEM` no `.env` ou nas variáveis de ambiente para alinhar com sua política interna.
2. **Persistir artefatos**: estenda o serviço para armazenar chaves/segredos em banco se precisar correlacionar sessões reais.
3. **Frontend**: consuma as rotas para demonstrar visualmente a derivação do segredo ou medir tempos de execução.
4. **Autenticação**: hoje as rotas são públicas; use as dependências padrão do projeto para restringir o acesso caso necessário.

Com essa base, você consegue iterar rapidamente na avaliação de algoritmos PQC e preparar o restante da stack para a transição pós-quântica.
