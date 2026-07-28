"""
Test Cryptographic Engine & PRAMAAN Seal Generation/Verification
File: backend/tests/test_seal_engine.py
"""

import json
from datetime import datetime, timezone, timedelta
from app.crypto.seal_engine import (
    generate_entity_keypair,
    compute_public_key_fingerprint,
    build_canonical_payload,
)


def test_keypair_generation_and_fingerprint():
    private_key, public_key_pem = generate_entity_keypair("TEST_REG_123")
    assert "BEGIN PUBLIC KEY" in public_key_pem
    fingerprint = compute_public_key_fingerprint(private_key)
    assert fingerprint.startswith("sha256:")
    assert len(fingerprint) == 71


def test_qr_payload_does_not_contain_public_key():
    payload = build_canonical_payload(
        content_hash="sha256:" + "a" * 64,
        entity_name="SEBI",
        reg_no="REGULATOR",
        signed_at=datetime.now(timezone.utc),
        not_after=datetime.now(timezone.utc) + timedelta(days=90)
    )
    qr_payload = {"seal_id": "PRMN-TEST", "payload": payload, "signature": "sig"}
    qr_json = json.dumps(qr_payload)

    assert "public_key" not in qr_json
    assert "BEGIN PUBLIC KEY" not in qr_json
    assert "official_public_key" not in qr_json


def test_canonical_payload_has_sorted_keys():
    now = datetime.now(timezone.utc)
    payload = build_canonical_payload(
        content_hash="sha256:" + "b" * 64,
        entity_name="NSE",
        reg_no="NSE",
        signed_at=now,
        not_after=now + timedelta(days=90)
    )
    keys = list(payload.keys())
    assert keys == sorted(keys)
    assert all(k in payload for k in ["content_hash", "entity", "not_after", "reg_no", "signed_at", "version"])
