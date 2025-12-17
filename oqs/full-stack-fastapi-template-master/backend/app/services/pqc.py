from __future__ import annotations

import base64
from dataclasses import dataclass

import oqs


def _b64encode(value: bytes) -> str:
    """Keep JSON payloads binary-safe."""
    return base64.b64encode(value).decode("ascii")


@dataclass(slots=True)
class KEMDetails:
    name: str
    claimed_nist_level: int
    is_classical_secured: bool
    length_public_key: int
    length_secret_key: int
    length_ciphertext: int
    length_shared_secret: int


@dataclass(slots=True)
class KEMHandshake:
    algorithm: str
    public_key: str
    ciphertext: str
    server_shared_secret: str
    client_shared_secret: str
    shared_secret_match: bool
    details: KEMDetails


class PQCService:
    """Thin wrapper around liboqs/oqs utilities used by the API."""

    def list_kem_algorithms(self) -> list[KEMDetails]:
        return [
            self._build_kem_details(algorithm)
            for algorithm in oqs.get_enabled_kem_mechanisms()
        ]

    def generate_kem_handshake(self, algorithm: str) -> KEMHandshake:
        details = self._build_kem_details(algorithm)
        with oqs.KeyEncapsulation(algorithm) as server:
            public_key = server.generate_keypair()
            with oqs.KeyEncapsulation(algorithm) as client:
                ciphertext, client_shared_secret = client.encap_secret(public_key)
            server_shared_secret = server.decap_secret(ciphertext)

        return KEMHandshake(
            algorithm=algorithm,
            public_key=_b64encode(public_key),
            ciphertext=_b64encode(ciphertext),
            server_shared_secret=_b64encode(server_shared_secret),
            client_shared_secret=_b64encode(client_shared_secret),
            shared_secret_match=server_shared_secret == client_shared_secret,
            details=details,
        )

    def _build_kem_details(self, algorithm: str) -> KEMDetails:
        details = oqs.get_kem_details(algorithm)
        return KEMDetails(
            name=algorithm,
            claimed_nist_level=details["claimed_nist_level"],
            is_classical_secured=details["is_classical_secured"],
            length_public_key=details["length_public_key"],
            length_secret_key=details["length_secret_key"],
            length_ciphertext=details["length_ciphertext"],
            length_shared_secret=details["length_shared_secret"],
        )
