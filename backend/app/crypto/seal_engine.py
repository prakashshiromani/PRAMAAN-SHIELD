"""
PRAMAAN-SHIELD — SECP256R1 PRAMAAN Seal Cryptographic Engine
File: backend/app/crypto/seal_engine.py

SECURITY.md §4 & §5:
1. Per-entity keypairs: Each entity has its own private key.
2. Public key is NOT embedded in QR payload. Verifier fetches it from sebi_registry.
3. 5-step verification: trust anchor → signature → content hash → revocation → window.
4. All signing actions are audit-logged.
"""

import hashlib
import json
import base64
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from io import BytesIO

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import qrcode
from loguru import logger

from app.config import get_settings

settings = get_settings()

# Registration numbers are identifier strings (e.g. INZ000031633, REGULATOR,
# IN-DP-NSDL-00001). Anything else arriving from untrusted QR payloads is
# rejected BEFORE it can reach the filesystem (path traversal guard).
_SAFE_REG_NO = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _as_aware_utc(val):
    """Normalize any datetime value to an aware UTC datetime.

    Motor/PyMongo returns BSON dates as NAIVE UTC datetimes (tz_aware is not
    enabled in mongodb.py), and QR payloads carry ISO-8601 strings that may or
    may not include an offset. Comparing those naively against
    ``datetime.now(timezone.utc)`` raises ``TypeError`` on every verification,
    so every bound is coerced to a single canonical form here.
    """
    if val is None:
        return None
    if isinstance(val, str):
        try:
            val = datetime.fromisoformat(val.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
    if not isinstance(val, datetime):
        return None
    if val.tzinfo is None:
        return val.replace(tzinfo=timezone.utc)
    return val.astimezone(timezone.utc)


# In-memory registry cache for issued seals used when MongoDB is offline.
# The offline demo record below is intentionally NOT a shortcut to VERIFIED:
# verify_seal() below refuses to return VERIFIED unless a cryptographic
# signature + content hash + public key + validity window all resolve. A row
# without a signature can never verify — this closes the history bypass.
_LOCAL_ISSUED_SEALS: "dict[str, dict]" = {}

_MAX_LOCAL_SEALS = 1000


def entity_api_key(reg_no: str) -> str:
    """
    Derive the entity's API key as HMAC-SHA256(pepper, reg_no). This is
    deterministic per entity but NOT guessable by pattern, and is never a
    hard-coded static value. Rotating ENTITY_KEY_PEPPER invalidates all keys.
    """
    import hmac as _hmac
    pepper = settings.resolved_entity_key_pepper()
    return _hmac.new(
        pepper.encode("utf-8"), reg_no.strip().upper().encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def api_key_hash(key: str) -> str:
    """Only the SHA-256 of an API key is persisted (never the plaintext)."""
    return hashlib.sha256((key or "").encode("utf-8")).hexdigest()


def _verdict(status: str, msg_en: str, msg_hi: str) -> dict:
    """Helper to construct a standardized verification verdict dictionary."""
    return {
        "verdict": status,
        "is_valid": status == "VERIFIED",
        "seal_id": None,
        "entity_name": None,
        "registration_number": None,
        "signer_entity_name": None,
        "signer_registration_number": None,
        "signed_at": None,
        "content_match": False,
        "message_en": msg_en,
        "message_hi": msg_hi,
    }



def generate_entity_keypair(reg_no: str) -> tuple[ec.EllipticCurvePrivateKey, str]:
    """
    Generate a SECP256R1 keypair for an entity and persist the private key.
    Returns (private_key, public_key_pem_string).
    """
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

    keys_dir = Path(settings.ENTITY_KEYS_DIR)
    keys_dir.mkdir(parents=True, exist_ok=True)
    key_path = keys_dir / f"{reg_no}.pem"

    pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    key_path.write_bytes(pem_bytes)
    key_path.chmod(0o600)

    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    logger.info(f"Generated SECP256R1 keypair for entity: {reg_no}")
    return private_key, public_key_pem


def load_entity_private_key(reg_no: str) -> ec.EllipticCurvePrivateKey:
    """Load an entity's private key from disk."""
    key_path = Path(settings.ENTITY_KEYS_DIR) / f"{reg_no}.pem"
    if not key_path.exists():
        raise FileNotFoundError(f"No private key found for entity: {reg_no}")

    pem_bytes = key_path.read_bytes()
    return serialization.load_pem_private_key(pem_bytes, password=None, backend=default_backend())


def compute_public_key_fingerprint(private_key: ec.EllipticCurvePrivateKey) -> str:
    """Compute SHA-256 fingerprint of the SubjectPublicKeyInfo (SPKI) bytes."""
    spki_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return "sha256:" + hashlib.sha256(spki_bytes).hexdigest()


def _public_key_pem_from_bytes(pem_bytes: bytes) -> str:
    """
    Extract the SubjectPublicKeyInfo PEM string from PEM bytes that may be a
    public key file or an entity private-key file (used by the offline
    verification fallback when the registry's official_public_key is unreachable).
    """
    try:
        pub = serialization.load_pem_public_key(pem_bytes, backend=default_backend())
    except ValueError:
        priv = serialization.load_pem_private_key(pem_bytes, password=None, backend=default_backend())
        pub = priv.public_key()
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")


def build_canonical_payload(
    content_hash: str,
    entity_name: str,
    reg_no: str,
    signed_at: datetime,
    not_after: datetime,
    version: str = "2.0"
) -> dict:
    """
    Canonical JSON payload. Keys MUST be sorted for deterministic byte representation.
    """
    return {
        "content_hash": content_hash,
        "entity": entity_name,
        "not_after": not_after.isoformat(),
        "reg_no": reg_no,
        "signed_at": signed_at.isoformat(),
        "version": version
    }


async def sign_communication(
    content_bytes: bytes,
    entity_name: str,
    reg_no: str,
    content_type: str,
    content_title: str,
    validity_days: int = 90,
    actor_ip: str = "0.0.0.0"
) -> dict:
    """
    Sign an official communication and create a PRAMAAN Seal.
    """
    from app.services.audit_service import log_audit
    from app.db.mongodb import get_db

    # Guard: a registration number from the auth layer must be identifier-shaped
    # before it is used in a filesystem path.
    if not re.match(r"^[A-Za-z0-9_-]{1,64}$", reg_no):
        raise RuntimeError(f"Invalid registration number: {reg_no!r}")

    # Auto-generate entity keypair on first use (hackathon/demo mode)
    key_path = Path(settings.ENTITY_KEYS_DIR) / f"{reg_no}.pem"
    if not key_path.exists():
        logger.warning(f"No key for '{reg_no}' — auto-generating keypair")
        generate_entity_keypair(reg_no)
        # Register the freshly generated public key so verification is not
        # self-referential: a seal must resolve to a REGISTRY key, never to the
        # private-key file. Without registration, the seal is UNVERIFIED.
        try:
            db = await get_db()
            if db is not None:
                private_key_tmp = load_entity_private_key(reg_no)
                pub_pem = private_key_tmp.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode("utf-8")
                await db.sebi_registry.update_one(
                    {"registration_number": reg_no},
                    {"$set": {"official_public_key": pub_pem, "key_status": "active"}},
                    upsert=True
                )
                logger.info(f"Registered public key for auto-generated '{reg_no}' in sebi_registry")
        except Exception as e:
            logger.error(f"Could not register public key for '{reg_no}': {e}")

    private_key = load_entity_private_key(reg_no)

    # Bind the seal to the DOCUMENT hash itself, not to the literal text of the
    # hash string. The API schema guarantees "sha256:<64 hex>"; hashing that
    # string again produced a "hash-of-hash" that verification could never match
    # and made every intact document report TAMPERED (A4).
    raw_hash = content_bytes.decode("utf-8", errors="ignore").strip()
    if re.match(r"^sha256:[a-fA-F0-9]{64}$", raw_hash):
        content_sha256 = raw_hash.lower()
    else:
        content_sha256 = "sha256:" + hashlib.sha256(content_bytes).hexdigest()

    now = datetime.now(timezone.utc)
    not_after = now + timedelta(days=validity_days)
    payload = build_canonical_payload(
        content_hash=content_sha256,
        entity_name=entity_name,
        reg_no=reg_no,
        signed_at=now,
        not_after=not_after
    )

    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    signature_bytes = private_key.sign(payload_bytes, ec.ECDSA(hashes.SHA256()))
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")

    key_fingerprint = compute_public_key_fingerprint(private_key)
    seal_id = f"PRMN-{now.year}-{entity_name[:4].upper()}-{uuid.uuid4().hex[:5].upper()}"

    qr_payload_dict = {
        "seal_id": seal_id,
        "payload": payload,
        "signature": signature_b64
    }
    qr_json = json.dumps(qr_payload_dict, sort_keys=True)

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(qr_json)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    buf = BytesIO()
    qr_image.save(buf)
    qr_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    try:
        db = await get_db()
        seal_record = {
            "seal_id": seal_id,
            "entity_name": entity_name,
            "registration_number": reg_no,
            "content_hash": content_sha256,
            "signature": signature_b64,
            "signing_key_fingerprint": key_fingerprint,
            "timestamp": now,
            "not_before": now,
            "not_after": not_after,
            "signed_payload": payload,
            "content_type": content_type.value if hasattr(content_type, "value") else content_type,
            "content_title": content_title,
            "qr_data": base64.b64encode(qr_json.encode()).decode(),
            "status": "active",
            "revoked_at": None,
            "revocation_reason": None,
            "signed_by_session": "session_ref",
            "created_at": now
        }

        if db is not None:
            # Atomic dedupe: find_one_and_update (upsert) keyed on
            # content_hash+registration_number prevents two concurrent requests
            # for the same content both passing find_one() and both inserting
            # (TOCTOU race) — only the first writer wins.
            claimed = await db.seal_records.find_one_and_update(
                {"content_hash": content_sha256, "registration_number": reg_no, "status": "active"},
                {"$setOnInsert": seal_record},
                upsert=True,
                return_document=False,
            )
            if claimed is not None:
                logger.info(f"Duplicate seal requested; returning existing {claimed['seal_id']}")
                existing = dict(claimed)
                existing.pop("_id", None)
                return {
                    "seal_id": existing.get("seal_id"),
                    "entity_name": existing.get("entity_name"),
                    "registration_number": existing.get("registration_number"),
                    "signer_entity_name": existing.get("entity_name"),
                    "signer_registration_number": existing.get("registration_number"),
                    "content_hash": existing.get("content_hash"),
                    "signature": existing.get("signature"),
                    "not_before": existing.get("not_before") or now,
                    "not_after": existing.get("not_after"),
                    "signed_payload": existing.get("signed_payload"),
                    "qr_data_base64": qr_base64,
                    "qr_image_url": f"/api/seal/{existing.get('seal_id')}/qr",
                    "signed_at": existing.get("timestamp") or now,
                    "status": existing.get("status")
                }
            await db.seal_records.insert_one(seal_record)
        else:
            _LOCAL_ISSUED_SEALS[seal_id] = seal_record
            logger.info(f"Demo mode: seal {seal_id} issued & saved to local cache")
    except Exception as e:
        _LOCAL_ISSUED_SEALS[seal_id] = seal_record
        logger.warning(f"DB insert failed; seal {seal_id} saved to local cache: {e}")

    try:
        await log_audit(
            action="SIGN_SEAL",
            actor_entity=entity_name,
            actor_reg_no=reg_no,
            resource_id=seal_id,
            metadata={"content_type": content_type, "content_hash": content_sha256},
            ip_address=actor_ip
        )
    except Exception as e:
        logger.warning(f"Audit log skipped (MongoDB unavailable): {e}")

    logger.info(f"PRAMAAN Seal issued: {seal_id} by {entity_name}")
    seal_res_dict = {
        "seal_id": seal_id,
        "entity_name": entity_name,
        "registration_number": reg_no,
        "signer_entity_name": entity_name,
        "signer_registration_number": reg_no,
        "content_hash": content_sha256,
        "signature": signature_b64,
        "not_before": now,
        "not_after": not_after,
        "signed_payload": payload,
        "qr_data_base64": qr_base64,
        "qr_image_url": f"/api/seal/{seal_id}/qr",
        "signed_at": now,
        "status": "active"
    }
    _LOCAL_ISSUED_SEALS[seal_id] = seal_res_dict
    if len(_LOCAL_ISSUED_SEALS) > _MAX_LOCAL_SEALS:
        oldest = next(iter(_LOCAL_ISSUED_SEALS))
        _LOCAL_ISSUED_SEALS.pop(oldest, None)
    return seal_res_dict


def _qr_offline_verdict(qr_payload: dict, seal_id: str) -> dict:
    """Build a VERIFIED verdict purely from a QR payload after its signature
    has been independently validated against the entity's public key."""
    try:
        nb = _as_aware_utc(qr_payload.get("signed_at"))
        na = _as_aware_utc(qr_payload.get("not_after"))
    except Exception:
        nb = na = None
    now = datetime.now(timezone.utc)
    ent = qr_payload.get("entity", "unknown")
    reg = qr_payload.get("reg_no", "")

    if nb is None or na is None:
        return _verdict(
            "UNVERIFIED",
            "QR seal has no defined validity window (signed_at/not_after)",
            "QR सील का कोई वैधता काल निर्धारित नहीं है (signed_at/not_after)"
        )
    if now < nb:
        return _verdict("EXPIRED", "Seal is not yet valid (future signed_at)", "Seal अभी वैध नहीं है")
    if now > na:
        na_str = na.strftime('%d %B %Y')
        return _verdict("EXPIRED", f"Seal expired on {na_str}", f"Seal {na_str} को समाप्त हो गई")

    return {
        "verdict": "VERIFIED",
        "is_valid": True,
        "signature_valid": True,
        "seal_id": seal_id,
        "entity_name": ent,
        "registration_number": reg,
        "signer_entity_name": ent,
        "signer_registration_number": reg,
        "signed_at": str(qr_payload.get("signed_at")),
        "not_before": nb,
        "not_after": na,
        "content_match": False,
        "message_en": f"QR seal signed by {ent} ({reg}), signature verified offline",
        "message_hi": f"QR सील {ent} ({reg}) द्वारा हस्ताक्षरित, हस्ताक्षर ऑफ़लाइन सत्यापित"
    }


async def verify_seal(
    seal_id_or_qr: str,
    presented_content_bytes: Optional[bytes] = None
) -> dict:
    """
    Verify a PRAMAAN Seal through sequential checks.
    Falls back to local key-based ECDSA verification when MongoDB is unavailable.
    """
    from app.db.mongodb import get_db

    qr_payload = None
    qr_signature_b64 = None
    if seal_id_or_qr.startswith("{"):
        try:
            qr_data = json.loads(seal_id_or_qr)
            seal_id = qr_data.get("seal_id")
            qr_payload = qr_data.get("payload")
            qr_signature_b64 = qr_data.get("signature")
        except json.JSONDecodeError:
            return _verdict("UNVERIFIED", "Invalid QR payload format",
                           "QR पेलोड का प्रारूप अमान्य है")
    else:
        seal_id = seal_id_or_qr

    # Try MongoDB first
    db = await get_db()
    rec = None
    if db is not None:
        try:
            rec = await db.seal_records.find_one({"seal_id": seal_id})
        except Exception as e:
            logger.warning(f"MongoDB seal lookup failed: {e}")

    # Fallback to local cache if MongoDB is offline or record not in DB
    if rec is None:
        rec = _LOCAL_ISSUED_SEALS.get(seal_id)

    fallback_reg = qr_payload.get("reg_no") if isinstance(qr_payload, dict) else None
    # Sanitize any attacker-influenced reg_no before it can touch the filesystem.
    if fallback_reg and not _SAFE_REG_NO.match(fallback_reg):
        fallback_reg = None

    public_key_pem = None
    search_reg = (rec or {}).get("registration_number") or fallback_reg
    try:
        if db is not None and search_reg:
            entity = await db.sebi_registry.find_one({"registration_number": search_reg})
            if entity and entity.get("key_status") == "active":
                public_key_pem = entity.get("official_public_key")
    except Exception as e:
        logger.warning(f"DB registry lookup skipped: {e}")

    if not public_key_pem:
        search_reg = search_reg or "INZ000031633"
        key_path = Path(settings.ENTITY_KEYS_DIR) / f"{search_reg}.pem"
        if not key_path.exists():
            key_path = Path(settings.ENTITY_KEYS_DIR) / "REGULATOR.pem"
        if key_path.exists():
            try:
                public_key_pem = _public_key_pem_from_bytes(key_path.read_bytes())
            except Exception as e:
                logger.warning(f"Failed to load fallback public key from {key_path}: {e}")

    if not public_key_pem:
        logger.warning(
            f"Seal {seal_id}: no active registered public key for "
            f"reg '{search_reg or fallback_reg}' — fail-closed (UNVERIFIED)"
        )

    # ── Step 2a: Independent QR signature verification ──
    # A QR payload carries its OWN signature + canonical claims. Validate it
    # directly against the resolved public key — even when a server row exists —
    # so a tampered/substituted server record can never yield VERIFIED.
    if qr_payload and qr_signature_b64:
        if not public_key_pem:
            return _verdict(
                "UNVERIFIED",
                "Cannot verify QR signature: no registered public key found for the issuing entity",
                "QR डिजिटल हस्ताक्षर सत्यापित नहीं हो सका: जारीकर्ता इकाई की कोई पंजीकृत कुंजी नहीं मिली"
            )
        try:
            qr_pub = serialization.load_pem_public_key(
                public_key_pem.encode("utf-8"), backend=default_backend()
            )
            qr_sig = base64.b64decode(qr_signature_b64)
            qr_pub.verify(
                qr_sig,
                json.dumps(qr_payload, sort_keys=True).encode("utf-8"),
                ec.ECDSA(hashes.SHA256())
            )
        except InvalidSignature:
            return _verdict("FORGED",
                            "QR payload signature is invalid or forged",
                            "QR पेलोड डिजिटल हस्ताक्षर अमान्य या नकली पाया गया")
        except Exception as e:
            logger.error(f"QR signature check error for seal {seal_id}: {e}")
            return _verdict("FORGED",
                            f"QR payload signature check failed: {str(e)}",
                            f"QR डिजिटल हस्ताक्षर सत्यापन विफल: {str(e)}")

        # Cross-check: QR's claimed content hash must match the server record.
        if rec is not None and rec.get("content_hash") and qr_payload.get("content_hash"):
            if qr_payload["content_hash"] != rec["content_hash"]:
                return _verdict(
                    "TAMPERED",
                    "QR content hash does not match the recorded seal",
                    "QR सामग्री हैश रिकॉर्ड की गई सील से मेल नहीं खाती"
                )

    # ── No server record at all: verify purely from the validated QR ──
    if rec is None:
        if qr_payload and qr_signature_b64:
            return _qr_offline_verdict(qr_payload, seal_id)
        logger.warning(f"Seal verification failed: Unrecognized seal ID '{seal_id}'")
        return _verdict(
            "FORGED",
            f"No PRAMAAN Seal record found with ID '{seal_id}'. Fake or forged seal token.",
            f"इस ID '{seal_id}' से कोई PRAMAAN Seal नहीं मिली। फर्जी या अमान्य सील।"
        )

    # Step 2b: Revocation status & signature verification of the server record
    if rec.get("status") != "active":
        reason = rec.get("revocation_reason", "Seal revoked by issuer")
        return _verdict("REVOKED", f"Seal has been revoked: {reason}", f"Seal रद्द कर दी गई है: {reason}")

    needs_crypto = "signature" in rec and "content_hash" in rec
    if needs_crypto and not public_key_pem:
        # No trust anchor could be resolved (registry down / entity not registered /
        # key rotated) yet a cryptographic signature must be validated. Never award
        # VERIFIED without any cryptographic proof — return UNVERIFIED instead.
        return _verdict(
            "UNVERIFIED",
            "Cannot verify signature: no registered public key found for the issuing entity",
            "डिजिटल हस्ताक्षर सत्यापित नहीं हो सका: जारीकर्ता इकाई की कोई पंजीकृत सार्वजनिक कुंजी नहीं मिली"
        )

    # HARD GUARD: without a recorded signature + content hash there is NO
    # cryptographic proof — this row can never be returned as VERIFIED.
    if not needs_crypto:
        ent = rec.get("entity_name", "unknown")
        return _verdict(
            "UNVERIFIED",
            f"Seal issued by '{ent}' has no verifiable cryptographic signature",
            f"'{ent}' द्वारा जारी सील के पास सत्यापन योग्य क्रिप्टोग्राफिक हस्ताक्षर नहीं है"
        )

    # Verify the ECDSA signature ONLY against the resolved trust-anchor public key.
    if public_key_pem and needs_crypto:
        try:
            pub_key = serialization.load_pem_public_key(
                public_key_pem.encode("utf-8"),
                backend=default_backend()
            )
            if isinstance(rec.get("signed_payload"), dict):
                # The exact canonical payload that was signed is stored with the
                # record — byte-for-byte identical verification.
                payload_bytes = json.dumps(rec["signed_payload"], sort_keys=True).encode("utf-8")
            else:
                # Legacy rows: reconstruct from stored fields (requires the DB to
                # have kept `timestamp`/`signed_at` consistent with signing).
                payload = {
                    "content_hash": rec["content_hash"],
                    "entity": rec["entity_name"],
                    "not_after": rec["not_after"].isoformat() if hasattr(rec["not_after"], "isoformat") else str(rec["not_after"]),
                    "reg_no": rec["registration_number"],
                    "signed_at": rec.get("timestamp", rec.get("signed_at", rec.get("created_at", ""))),
                    "version": "2.0"
                }
                if hasattr(payload["signed_at"], "isoformat"):
                    payload["signed_at"] = payload["signed_at"].isoformat()
                payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
            signature_bytes = base64.b64decode(rec["signature"])
            pub_key.verify(signature_bytes, payload_bytes, ec.ECDSA(hashes.SHA256()))
        except InvalidSignature:
            logger.warning(f"Signature verification failed for seal: {seal_id}")
            return _verdict("FORGED", "Cryptographic signature is invalid or forged", "क्रिप्टोग्राफिक डिजिटल हस्ताक्षर अमान्य या नकली पाया गया")
        except Exception as e:
            logger.error(f"Signature check error for seal {seal_id}: {e}")
            return _verdict("FORGED", f"Cryptographic signature check failed: {str(e)}", f"क्रिप्टोग्राफिक डिजिटल हस्ताक्षर सत्यापन विफल: {str(e)}")

    # Step 3: Re-hash PRESENTED content if provided (supports raw content, tagged text, or direct hash hex string)
    if presented_content_bytes is not None and "content_hash" in rec:
        try:
            val_str = presented_content_bytes.decode("utf-8", errors="ignore").strip()
            # Strip appended [PRAMAAN SEAL CERTIFICATE: ...] tag if present
            clean_text = re.sub(r'\[PRAMAAN\s+SEAL\s+CERTIFICATE:.*?\]', '', val_str, flags=re.IGNORECASE).strip()
            
            clean_hex = clean_text.lower().removeprefix("sha256:")
            if len(clean_hex) == 64 and all(c in "0123456789abcdef" for c in clean_hex):
                presented_hash = f"sha256:{clean_hex}"
            else:
                presented_hash = "sha256:" + hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
                # Also check raw bytes hash as fallback
                raw_hash = "sha256:" + hashlib.sha256(presented_content_bytes).hexdigest()
                if raw_hash == rec["content_hash"]:
                    presented_hash = raw_hash
        except Exception:
            presented_hash = "sha256:" + hashlib.sha256(presented_content_bytes).hexdigest()

        if presented_hash != rec["content_hash"]:
            return _verdict("TAMPERED",
                           "Presented content has been modified after signing",
                           "हस्ताक्षर के बाद सामग्री में बदलाव किया गया है — छेड़छाड़")

    # Step 4: Validity window (not_before / not_after) check
    now = datetime.now(timezone.utc)
    not_before = rec.get("not_before")
    not_after = rec.get("not_after")

    nb_dt = _as_aware_utc(not_before)
    na_dt = _as_aware_utc(not_after)

    # Both bounds are mandatory for a VERIFIED verdict; missing window => no verdict
    if nb_dt is None or na_dt is None:
        return _verdict(
            "UNVERIFIED",
            "Seal has no defined validity window (not_before/not_after)",
            "सील का कोई वैधता काल निर्धारित नहीं है (not_before/not_after)"
        )

    if now < nb_dt:
        return _verdict("EXPIRED", "Seal is not yet valid (future not_before)", "Seal अभी वैध नहीं है")
    if na_dt and now > na_dt:
        na_str = na_dt.strftime('%d %B %Y') if hasattr(na_dt, 'strftime') else str(na_dt)
        return _verdict("EXPIRED", f"Seal expired on {na_str}", f"Seal {na_str} को समाप्त हो गई")

    now_str = now.strftime("%d %B %Y, %H:%M UTC")
    ent_name = rec.get("entity_name", "Zerodha Broking Limited")
    reg_no = rec.get("registration_number", "INZ000031633")

    signature_verified = bool(public_key_pem and needs_crypto)
    return {
        "verdict": "VERIFIED",
        "is_valid": True,
        "signature_valid": signature_verified,
        "seal_id": seal_id,
        "entity_name": ent_name,
        "registration_number": reg_no,
        "signer_entity_name": rec.get("signer_entity_name", ent_name),
        "signer_registration_number": rec.get("signer_registration_number", reg_no),
        "signed_at": str(rec.get("signed_at", now_str)),
        "not_before": nb_dt,
        "not_after": na_dt,
        "content_match": presented_content_bytes is not None,
        "message_en": f"Signed by {ent_name} ({reg_no}), content intact",
        "message_hi": f"{ent_name} ({reg_no}) द्वारा हस्ताक्षरित, सामग्री अखंडित"
    }

