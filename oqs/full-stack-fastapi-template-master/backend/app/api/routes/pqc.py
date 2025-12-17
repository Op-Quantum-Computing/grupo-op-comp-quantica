from fastapi import APIRouter, HTTPException, status

import oqs

from app.core.config import settings
from app.models import (
    PQCKEMAlgorithm,
    PQCKEMAlgorithms,
    PQCKEMHandshakeRequest,
    PQCKEMHandshakeResponse,
)
from app.services.pqc import PQCService

router = APIRouter(prefix="/pqc", tags=["pqc"])
service = PQCService()


@router.get("/kems", response_model=PQCKEMAlgorithms)
def list_kem_algorithms() -> PQCKEMAlgorithms:
    kems = [
        PQCKEMAlgorithm(**details.__dict__)
        for details in service.list_kem_algorithms()
    ]
    return PQCKEMAlgorithms(data=kems)


@router.post("/kem/handshake", response_model=PQCKEMHandshakeResponse)
def generate_kem_handshake(
    payload: PQCKEMHandshakeRequest | None = None,
) -> PQCKEMHandshakeResponse:
    algorithm = (
        payload.algorithm if payload and payload.algorithm else settings.DEFAULT_PQC_KEM
    )
    try:
        handshake = service.generate_kem_handshake(algorithm)
    except oqs.MechanismNotSupportedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"KEM algorithm '{algorithm}' is not available: {exc}",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to perform KEM handshake: {exc}",
        ) from exc

    details = PQCKEMAlgorithm(**handshake.details.__dict__)
    return PQCKEMHandshakeResponse(
        algorithm=handshake.algorithm,
        public_key=handshake.public_key,
        ciphertext=handshake.ciphertext,
        server_shared_secret=handshake.server_shared_secret,
        client_shared_secret=handshake.client_shared_secret,
        shared_secret_match=handshake.shared_secret_match,
        details=details,
    )
