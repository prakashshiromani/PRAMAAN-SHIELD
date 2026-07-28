"""
PRAMAAN-SHIELD — Cryptographic Key Manager
File: backend/app/crypto/key_manager.py

Manages ECDSA SECP256R1 keypairs for registered entities.
Provides dedicated key generation, loading, and public key fingerprint computing.
"""

import hashlib
from pathlib import Path
from typing import Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from loguru import logger

from app.config import get_settings

settings = get_settings()


class KeyManager:
    """Dedicated Key Manager for Entity ECDSA Certificate & Key Handling."""

    def __init__(self, keys_dir: str = None):
        self.keys_dir = Path(keys_dir or settings.ENTITY_KEYS_DIR)
        self.keys_dir.mkdir(parents=True, exist_ok=True)

    def generate_entity_keypair(self, reg_no: str) -> Tuple[ec.EllipticCurvePrivateKey, str]:
        """
        Generate a SECP256R1 keypair for an entity and persist the private key.
        Returns (private_key, public_key_pem_string).
        """
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        key_path = self.keys_dir / f"{reg_no}.pem"

        pem_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        key_path.write_bytes(pem_bytes)
        try:
            key_path.chmod(0o600)
        except Exception:
            pass

        public_key_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("utf-8")

        logger.info(f"KeyManager: Generated SECP256R1 keypair for entity: {reg_no}")
        return private_key, public_key_pem

    def load_entity_private_key(self, reg_no: str) -> ec.EllipticCurvePrivateKey:
        """Load an entity's private key from disk."""
        key_path = self.keys_dir / f"{reg_no}.pem"
        if not key_path.exists():
            raise FileNotFoundError(f"No private key found for entity: {reg_no}")

        pem_bytes = key_path.read_bytes()
        return serialization.load_pem_private_key(pem_bytes, password=None, backend=default_backend())

    @staticmethod
    def compute_public_key_fingerprint(private_key: ec.EllipticCurvePrivateKey) -> str:
        """Compute SHA-256 fingerprint of the SubjectPublicKeyInfo (SPKI) bytes."""
        spki_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return "sha256:" + hashlib.sha256(spki_bytes).hexdigest()
