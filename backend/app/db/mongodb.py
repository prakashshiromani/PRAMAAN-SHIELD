"""
PRAMAAN-SHIELD — MongoDB Connection & Schema Enforcement
File: backend/app/db/mongodb.py

Responsibilities:
1. Async connection via motor.motor_asyncio
2. Apply jsonSchema validators on startup (collMod) for all 6 collections
3. Create all required indexes (unique, text, multikey, compound, TTL)
"""

from typing import Optional
import motor.motor_asyncio
from loguru import logger
from app.config import get_settings

settings = get_settings()

client: motor.motor_asyncio.AsyncIOMotorClient = None
db: motor.motor_asyncio.AsyncIOMotorDatabase = None


# ── jsonSchema Definitions ──────────────────────────────────────────────────

SEBI_REGISTRY_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["entity_name", "registration_number", "category",
                     "sebi_registered", "official_domains", "key_status", "last_updated"],
        "properties": {
            "entity_name":          {"bsonType": "string"},
            "registration_number":  {"bsonType": "string"},
            "category":             {"bsonType": "string", "enum": [
                "Stock Broker", "Depository Participant", "Mutual Fund",
                "Portfolio Manager", "Investment Adviser", "Research Analyst",
                "Registrar", "Exchange", "Regulator"
            ]},
            "sebi_registered":      {"bsonType": "bool"},
            "official_domains":     {"bsonType": "array", "minItems": 1,
                                     "items": {"bsonType": "string"}},
            "official_emails":      {"bsonType": "array",
                                     "items": {"bsonType": "string"}},
            "official_public_key":  {"bsonType": "string"},  # PEM format
            "api_key_hash":         {"bsonType": "string"},  # sha256 of entity signing API key
            "cert_fingerprint":     {"bsonType": "string"},  # sha256:...
            "key_status":           {"bsonType": "string",
                                     "enum": ["active", "rotated", "revoked"]},
            "key_valid_from":       {"bsonType": "date"},
            "key_valid_to":         {"bsonType": "date"},
            "last_updated":         {"bsonType": "date"}
        }
    }
}

SEAL_RECORDS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["seal_id", "entity_name", "registration_number",
                     "content_hash", "signature", "signing_key_fingerprint",
                     "timestamp", "not_before", "not_after", "status", "created_at"],
        "properties": {
            "seal_id":                 {"bsonType": "string"},
            "entity_name":             {"bsonType": "string"},
            "registration_number":     {"bsonType": "string"},
            "content_hash":            {"bsonType": "string",
                                        "pattern": "^sha256:[a-fA-F0-9]{64}$"},
            "signature":               {"bsonType": "string"},  # base64 ECDSA sig
            "signing_key_fingerprint": {"bsonType": "string"},
            "timestamp":               {"bsonType": "date"},
            "not_before":              {"bsonType": "date"},
            "not_after":               {"bsonType": "date"},
            "content_type":            {"bsonType": "string", "enum": [
                "circular", "press_release", "advisory",
                "video_statement", "notification"
            ]},
            "content_title":           {"bsonType": "string"},
            "qr_data":                 {"bsonType": "string"},
            "signed_payload":          {"bsonType": "object"},
            "status":                  {"bsonType": "string", "enum": ["active", "revoked"]},
            "revoked_at":              {"bsonType": ["date", "null"]},
            "revocation_reason":       {"bsonType": ["string", "null"]},
            "signed_by_session":       {"bsonType": "string"},
            "created_at":              {"bsonType": "date"}
        }
    }
}

SCAN_HISTORY_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["scan_id", "content_type", "content_hash",
                     "trust_score", "verdict", "checks", "source", "created_at"],
        "properties": {
            "scan_id":         {"bsonType": "string"},
            "content_type":    {"bsonType": "string",
                                "enum": ["text", "audio", "video", "image"]},
            "content_hash":    {"bsonType": "string"},
            "perceptual_hash": {"bsonType": ["string", "null"]},
            "trust_score":     {"bsonType": "int", "minimum": 0, "maximum": 100},
            "verdict":         {"bsonType": "string",
                                "enum": ["VERIFIED", "EXERCISE CAUTION", "SUSPICIOUS"]},
            "checks":          {"bsonType": "array", "items": {
                "bsonType": "object",
                "required": ["module", "status", "label", "detail", "contribution"],
                "properties": {
                    "module":       {"bsonType": "string"},
                    "status":       {"bsonType": "string",
                                     "enum": ["pass", "fail", "warn", "skip"]},
                    "label":        {"bsonType": "string"},
                    "detail":       {"bsonType": "string"},
                    "contribution": {"bsonType": "int"}
                }
            }},
            "source":          {"bsonType": "string",
                                "enum": ["web", "telegram", "api"]},
            "language":        {"bsonType": "string", "enum": ["hi", "en"]},
            "ip_hmac":         {"bsonType": "string"},
            "created_at":      {"bsonType": "date"}
        }
    }
}

FLAGGED_CONTENT_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["perceptual_hash", "content_type", "description",
                     "first_flagged", "flagged_by", "severity"],
        "properties": {
            "perceptual_hash": {"bsonType": "string"},
            "hash_family":     {"bsonType": "array",
                                "items": {"bsonType": "string"}},
            "content_type":    {"bsonType": "string",
                                "enum": ["video", "image", "audio"]},
            "description":     {"bsonType": "string"},
            "first_flagged":   {"bsonType": "date"},
            "flagged_by":      {"bsonType": "string"},
            "source_reference":{"bsonType": "string"},
            "detection_count": {"bsonType": "int", "minimum": 0},
            "last_detected":   {"bsonType": "date"},
            "severity":        {"bsonType": "string",
                                "enum": ["critical", "high", "medium", "low"]}
        }
    }
}

USER_REPORTS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["report_id", "scan_id", "target_portals", "status", "created_at"],
        "properties": {
            "report_id":        {"bsonType": "string"},
            "scan_id":          {"bsonType": "string"},
            "target_portals":   {"bsonType": "array", "minItems": 1,
                                  "items": {"bsonType": "string",
                                            "enum": ["sebi_scores", "cybercrime_1930"]}},
            "template_text_en": {"bsonType": "string"},
            "template_text_hi": {"bsonType": "string"},
            "evidence_package": {"bsonType": "object"},
            "status":           {"bsonType": "string",
                                  "enum": ["generated", "copied", "downloaded"]},
            "created_at":       {"bsonType": "date"}
        }
    }
}

AUDIT_LEDGER_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["audit_id", "action", "actor_entity",
                     "actor_registration_number", "resource_id", "timestamp"],
        "properties": {
            "audit_id":                  {"bsonType": "string"},
            "action":                    {"bsonType": "string", "enum": [
                "SIGN_SEAL", "REVOKE_SEAL", "FLAG_CONTENT",
                "REGISTRY_ADD", "REGISTRY_UPDATE", "KEY_ROTATE", "KEY_REVOKE"
            ]},
            "actor_entity":              {"bsonType": "string"},
            "actor_registration_number": {"bsonType": "string"},
            "resource_id":               {"bsonType": "string"},
            "metadata":                  {"bsonType": "object"},
            "ip_hmac":                   {"bsonType": "string"},
            "timestamp":                 {"bsonType": "date"}
        }
    }
}


# ── Database Functions ──────────────────────────────────────────────────────

db_connected = False


async def connect_to_mongo():
    global client, db, db_connected
    try:
        uri = settings.MONGO_URI
        # TLS certificate validation is STRICT in production. We only allow
        # insecure certs for obvious local-dev, non-TLS endpoints; never for
        # mongodb+srv / Atlas URIs (a self-signed "server" there = MITM / cred theft).
        is_local_dev = (
            uri.startswith("mongodb://127.0.0.1")
            or uri.startswith("mongodb://localhost")
        )
        is_tls_uri = "mongodb+srv" in uri
        kwargs = {
            "serverSelectionTimeoutMS": 5000,
            "connectTimeoutMS": 5000,
            "socketTimeoutMS": 10000,
            "appName": "pramaan-shield",
        }
        try:
            import certifi
            kwargs["tlsCAFile"] = certifi.where()
        except ImportError:
            pass

        client = motor.motor_asyncio.AsyncIOMotorClient(uri, **kwargs)
        await client.admin.command('ping')
        db = client[settings.DB_NAME]
        db_connected = True
        logger.info(f"Connected to MongoDB Atlas: {settings.DB_NAME}")
        await apply_schemas_and_indexes()
    except Exception as e:
        db_connected = False
        db = None
        logger.warning(f"MongoDB connection offline (demo mode active): {e}")


async def close_mongo_connection():
    global client, db_connected
    if client:
        client.close()
        db_connected = False
        logger.info("MongoDB connection closed")


_last_mongo_retry = 0.0

async def get_db() -> Optional[motor.motor_asyncio.AsyncIOMotorDatabase]:
    global db, db_connected, _last_mongo_retry
    if db is not None and db_connected:
        return db

    # Cooldown check: only retry reconnect every 60 seconds to avoid blocking requests
    import time
    now = time.time()
    if now - _last_mongo_retry < 60.0:
        return None

    _last_mongo_retry = now

    # Lazy best-effort reconnect: if the connection dropped since startup, try
    # once to re-establish it so the app can recover without a full restart.
    try:
        if client is None:
            await connect_to_mongo()
        elif not db_connected:
            await client.admin.command('ping')
            db = client[settings.DB_NAME]
            db_connected = True
            logger.info("MongoDB lazily reconnected after startup failure")
    except Exception as e:
        logger.warning(f"MongoDB unreachable ({e}); staying in degraded mode")

    if not db_connected or db is None:
        return None
    return db


async def create_indexes():
    """Create all required indexes per Backend SCHEMA.md §1.x"""
    # sebi_registry
    await db.sebi_registry.create_index("registration_number", unique=True)
    await db.sebi_registry.create_index([("entity_name", "text")])
    await db.sebi_registry.create_index("official_domains")
    await db.sebi_registry.create_index("key_status")

    # seal_records
    await db.seal_records.create_index("seal_id", unique=True)
    await db.seal_records.create_index("content_hash")
    await db.seal_records.create_index([("entity_name", 1), ("timestamp", -1)])
    await db.seal_records.create_index("status")

    # scan_history
    await db.scan_history.create_index("scan_id", unique=True)
    await db.scan_history.create_index("content_hash")
    await db.scan_history.create_index(
        "created_at",
        expireAfterSeconds=7_776_000  # 90 days TTL
    )
    await db.scan_history.create_index([("verdict", 1), ("content_type", 1)])

    # flagged_content
    await db.flagged_content.create_index("perceptual_hash", unique=True)
    await db.flagged_content.create_index("hash_family")

    # user_reports
    await db.user_reports.create_index("report_id", unique=True)
    await db.user_reports.create_index("scan_id")

    # audit_ledger
    await db.audit_ledger.create_index("audit_id", unique=True)
    await db.audit_ledger.create_index("action")
    await db.audit_ledger.create_index("timestamp")

    logger.info("All MongoDB indexes created successfully")


async def apply_schemas_and_indexes():
    """
    Apply jsonSchema validators to all collections.
    Uses collMod for existing collections, create_collection for new ones.
    """
    SCHEMAS = {
        "sebi_registry":  SEBI_REGISTRY_SCHEMA,
        "seal_records":   SEAL_RECORDS_SCHEMA,
        "scan_history":   SCAN_HISTORY_SCHEMA,
        "flagged_content": FLAGGED_CONTENT_SCHEMA,
        "user_reports":   USER_REPORTS_SCHEMA,
        "audit_ledger":   AUDIT_LEDGER_SCHEMA,
    }

    existing = await db.list_collection_names()
    for name, schema in SCHEMAS.items():
        if name not in existing:
            await db.create_collection(name, validator=schema, validationAction="error")
            logger.info(f"Created collection with schema: {name}")
        else:
            try:
                await db.command("collMod", name, validator=schema, validationAction="error")
                logger.info(f"Applied schema to existing collection: {name}")
            except Exception as e:
                logger.debug(f"Skipped collMod for {name}: {e}")

    await create_indexes()
