"""
PRAMAAN-SHIELD — Database Seeder
File: backend/app/db/seed.py

Seeds:
1. sebi_registry: SEBI registered entities with generated SECP256R1 public keys
2. flagged_content + Redis: Known fake perceptual hashes (BSE CEO deepfake, etc.)
"""

asyncio_import = True
import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

from cryptography.hazmat.primitives import serialization
from app.db.mongodb import connect_to_mongo, get_db
from app.db.redis import connect_to_redis, get_redis, key_video_hash, key_image_hash, key_hash_family
from app.crypto.seal_engine import generate_entity_keypair, entity_api_key, api_key_hash
from app.services.audit_service import log_audit
from loguru import logger

SEBI_ENTITIES = [
    {
        "entity_name": "SEBI",
        "registration_number": "REGULATOR",
        "category": "Regulator",
        "sebi_registered": True,
        "official_domains": ["sebi.gov.in", "scores.gov.in"],
        "official_emails": ["sebi@sebi.gov.in", "complaints@sebi.gov.in"]
    },
    {
        "entity_name": "BSE Limited",
        "registration_number": "BSE",
        "category": "Exchange",
        "sebi_registered": True,
        "official_domains": ["bseindia.com", "bseplus.bseindia.com"],
        "official_emails": ["corp.relations@bseindia.com"]
    },
    {
        "entity_name": "National Stock Exchange of India Limited",
        "registration_number": "NSE",
        "category": "Exchange",
        "sebi_registered": True,
        "official_domains": ["nseindia.com", "nseindianow.com"],
        "official_emails": ["investorservicecell@nse.co.in"]
    },
    {
        "entity_name": "MCX — Multi Commodity Exchange of India",
        "registration_number": "MCX",
        "category": "Exchange",
        "sebi_registered": True,
        "official_domains": ["mcxindia.com"],
        "official_emails": ["info@mcxindia.com"]
    },
    {
        "entity_name": "Zerodha Broking Limited",
        "registration_number": "INZ000031633",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["zerodha.com", "kite.zerodha.com", "console.zerodha.com"],
        "official_emails": ["support@zerodha.com", "notice@zerodha.com"]
    },
    {
        "entity_name": "Groww Investments Private Limited",
        "registration_number": "INZ000177137",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["groww.in", "app.groww.in"],
        "official_emails": ["support@groww.in"]
    },
    {
        "entity_name": "Angel One Limited",
        "registration_number": "INZ000161534",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["angelone.in", "trade.angelone.in"],
        "official_emails": ["support@angelone.in"]
    },
    {
        "entity_name": "Upstox (RKSV Securities India Pvt Ltd)",
        "registration_number": "INZ000185137",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["upstox.com", "pro.upstox.com"],
        "official_emails": ["support@upstox.com"]
    },
    {
        "entity_name": "ICICI Securities Limited",
        "registration_number": "INZ000183631",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["icicidirect.com", "secure.icicidirect.com"],
        "official_emails": ["helpdesk@icicidirect.com"]
    },
    {
        "entity_name": "HDFC Securities Limited",
        "registration_number": "INZ000186937",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["hdfcsec.com", "trade.hdfcsec.com"],
        "official_emails": ["customercare@hdfcsec.com"]
    },
    {
        "entity_name": "Kotak Securities Limited",
        "registration_number": "INZ000200137",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["kotaksecurities.com", "kotakneo.com"],
        "official_emails": ["service.securities@kotak.com"]
    },
    {
        "entity_name": "5paisa Capital Limited",
        "registration_number": "INZ000010231",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["5paisa.com", "trade.5paisa.com"],
        "official_emails": ["support@5paisa.com"]
    },
    {
        "entity_name": "SBI Securities (SBI Cap Securities Ltd)",
        "registration_number": "INZ000200032",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["sbismart.com", "secure.sbismart.com"],
        "official_emails": ["helpdesk@sbicapsec.com"]
    },
    {
        "entity_name": "Motilal Oswal Financial Services Limited",
        "registration_number": "INZ000158836",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["motilaloswal.com", "trade.motilaloswal.com"],
        "official_emails": ["connect@motilaloswal.com"]
    },
    {
        "entity_name": "Sharekhan Limited",
        "registration_number": "INZ000171330",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["sharekhan.com", "trade.sharekhan.com"],
        "official_emails": ["myaccount@sharekhan.com"]
    },
    {
        "entity_name": "Paytm Money Limited",
        "registration_number": "INZ000240532",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["paytmmoney.com"],
        "official_emails": ["care@paytmmoney.com"]
    },
    {
        "entity_name": "India Infoline (IIFL Securities)",
        "registration_number": "INZ000164132",
        "category": "Stock Broker",
        "sebi_registered": True,
        "official_domains": ["indiainfoline.com", "iiflsecurities.com"],
        "official_emails": ["cs@iifl.com"]
    },
    {
        "entity_name": "CDSL — Central Depository Services (India) Ltd",
        "registration_number": "IN-DP-CDSL-00032",
        "category": "Depository Participant",
        "sebi_registered": True,
        "official_domains": ["cdslindia.com", "easi.cdslindia.com"],
        "official_emails": ["helpdesk@cdslindia.com"]
    },
    {
        "entity_name": "NSDL — National Securities Depository Limited",
        "registration_number": "IN-DP-NSDL-00001",
        "category": "Depository Participant",
        "sebi_registered": True,
        "official_domains": ["nsdl.co.in", "speed-e.in"],
        "official_emails": ["info@nsdl.co.in"]
    },
    {
        "entity_name": "SBI Mutual Fund",
        "registration_number": "MF-009",
        "category": "Mutual Fund",
        "sebi_registered": True,
        "official_domains": ["sbimf.com"],
        "official_emails": ["customercare@sbimf.com"]
    },
    {
        "entity_name": "HDFC Asset Management Company Limited",
        "registration_number": "MF-044",
        "category": "Mutual Fund",
        "sebi_registered": True,
        "official_domains": ["hdfcfund.com"],
        "official_emails": ["cliser@hdfcfund.com"]
    },
    {
        "entity_name": "ICICI Prudential Mutual Fund",
        "registration_number": "MF-012",
        "category": "Mutual Fund",
        "sebi_registered": True,
        "official_domains": ["icicipruamc.com"],
        "official_emails": ["enquiry@icicipruamc.com"]
    },
    {
        "entity_name": "Axis Mutual Fund",
        "registration_number": "MF-062",
        "category": "Mutual Fund",
        "sebi_registered": True,
        "official_domains": ["axismf.com"],
        "official_emails": ["customerservice@axismf.com"]
    },
    {
        "entity_name": "Nippon India Mutual Fund",
        "registration_number": "MF-013",
        "category": "Mutual Fund",
        "sebi_registered": True,
        "official_domains": ["nipponindiamf.com", "mf.nipponindiaim.com"],
        "official_emails": ["customercare@nipponindiaim.in"]
    },
    {
        "entity_name": "Bajaj Finserv Asset Management Ltd",
        "registration_number": "MF-082",
        "category": "Mutual Fund",
        "sebi_registered": True,
        "official_domains": ["bajajamc.com", "bajajfinservamc.com"],
        "official_emails": ["mf@bajajfinserv.in"]
    },
]

KNOWN_FAKE_HASHES = [
    {
        "perceptual_hash": "phash:a1b2c3d4e5f67890",
        "hash_family": [
            "phash:a1b2c3d4e5f67891",
            "phash:a1b2c3d4e5f67892",
            "phash:b1b2c3d4e5f67890",
            "phash:a1b2c3d4e5f67800",
        ],
        "content_type": "video",
        "description": "BSE CEO Deepfake Scam Video (Fake Stock Tips - Jan 2026)",
        "first_flagged": datetime(2026, 1, 15, 9, 0, 0, tzinfo=timezone.utc),
        "flagged_by": "SEBI",
        "source_reference": "SEBI Advisory 2026/01-BSE",
        "detection_count": 1420,
        "last_detected": datetime(2026, 3, 12, tzinfo=timezone.utc),
        "severity": "critical"
    },
    {
        "perceptual_hash": "phash:f8e7d6c5b4a39281",
        "hash_family": ["phash:f8e7d6c5b4a39282", "phash:f8e7d6c5b4a39280"],
        "content_type": "video",
        "description": "NSE Chairman Deepfake AI Voice Clone Trading App Promo",
        "first_flagged": datetime(2026, 2, 10, 11, 30, 0, tzinfo=timezone.utc),
        "flagged_by": "NSE",
        "source_reference": "NSE Circular 2026/02-CLONE",
        "detection_count": 890,
        "last_detected": datetime(2026, 4, 1, tzinfo=timezone.utc),
        "severity": "critical"
    },
    {
        "perceptual_hash": "phash:c9b8a79685746352",
        "hash_family": ["phash:c9b8a79685746353", "phash:d9b8a79685746352"],
        "content_type": "image",
        "description": "Fake SEBI Notice - Demat Account Freeze Letterhead Scam",
        "first_flagged": datetime(2026, 1, 28, 14, 15, 0, tzinfo=timezone.utc),
        "flagged_by": "SEBI",
        "source_reference": "SEBI Investor Alert 2026/03",
        "detection_count": 2340,
        "last_detected": datetime(2026, 4, 15, tzinfo=timezone.utc),
        "severity": "high"
    },
    {
        "perceptual_hash": "phash:1122334455667788",
        "hash_family": ["phash:1122334455667789", "phash:1122334455667780"],
        "content_type": "audio",
        "description": "Synthetic Voice Call Impersonating Zerodha Relationship Manager",
        "first_flagged": datetime(2026, 3, 5, 8, 45, 0, tzinfo=timezone.utc),
        "flagged_by": "Zerodha",
        "source_reference": "Zerodha Safety Alert #882",
        "detection_count": 670,
        "last_detected": datetime(2026, 4, 10, tzinfo=timezone.utc),
        "severity": "high"
    },
    {
        "perceptual_hash": "phash:9988776655443322",
        "hash_family": ["phash:9988776655443323"],
        "content_type": "image",
        "description": "Spoofed Groww App Cashback Banner Link Phishing Screenshot",
        "first_flagged": datetime(2026, 3, 14, 16, 20, 0, tzinfo=timezone.utc),
        "flagged_by": "Groww",
        "source_reference": "Groww Security Advisory 2026-03",
        "detection_count": 510,
        "last_detected": datetime(2026, 4, 2, tzinfo=timezone.utc),
        "severity": "medium"
    },
    {
        "perceptual_hash": "phash:aabbccddeeff0011",
        "hash_family": ["phash:aabbccddeeff0012", "phash:babbccddeeff0011"],
        "content_type": "video",
        "description": "Famous Investor Deepfake Promoting Unregistered Telegram VIP Channel",
        "first_flagged": datetime(2026, 2, 22, 10, 0, 0, tzinfo=timezone.utc),
        "flagged_by": "SEBI",
        "source_reference": "SEBI Press Release 2026/12",
        "detection_count": 3120,
        "last_detected": datetime(2026, 4, 18, tzinfo=timezone.utc),
        "severity": "critical"
    },
    {
        "perceptual_hash": "phash:1234567890abcdef",
        "hash_family": ["phash:1234567890abcdee"],
        "content_type": "image",
        "description": "Fake Guaranteed 500% Monthly Return Crypto Trading Certificate",
        "first_flagged": datetime(2026, 1, 10, 15, 30, 0, tzinfo=timezone.utc),
        "flagged_by": "Cybercrime 1930",
        "source_reference": "FIR-2026-DELHI-9982",
        "detection_count": 4500,
        "last_detected": datetime(2026, 4, 20, tzinfo=timezone.utc),
        "severity": "critical"
    },
    {
        "perceptual_hash": "phash:fedcba0987654321",
        "hash_family": ["phash:fedcba0987654322"],
        "content_type": "audio",
        "description": "AI Clone Voice of Prominent Analyst Claiming Insider Stock Tip",
        "first_flagged": datetime(2026, 3, 20, 19, 0, 0, tzinfo=timezone.utc),
        "flagged_by": "BSE",
        "source_reference": "BSE Advisory 2026/04",
        "detection_count": 930,
        "last_detected": datetime(2026, 4, 16, tzinfo=timezone.utc),
        "severity": "high"
    },
    {
        "perceptual_hash": "phash:445566778899aabb",
        "hash_family": ["phash:445566778899aabc"],
        "content_type": "image",
        "description": "Fake Angel One Profit Screenshot Used for WhatsApp Group Scam",
        "first_flagged": datetime(2026, 3, 1, 12, 10, 0, tzinfo=timezone.utc),
        "flagged_by": "Angel One",
        "source_reference": "Angel One Fraud Notice 404",
        "detection_count": 1840,
        "last_detected": datetime(2026, 4, 14, tzinfo=timezone.utc),
        "severity": "medium"
    },
    {
        "perceptual_hash": "phash:5566778899aabbcc",
        "hash_family": ["phash:5566778899aabbcd"],
        "content_type": "video",
        "description": "Fake IPO Allotment Guaranteed Trick Video with Synthetic Host",
        "first_flagged": datetime(2026, 3, 25, 14, 50, 0, tzinfo=timezone.utc),
        "flagged_by": "SEBI",
        "source_reference": "SEBI Advisory 2026/09",
        "detection_count": 760,
        "last_detected": datetime(2026, 4, 19, tzinfo=timezone.utc),
        "severity": "high"
    }
]


async def seed_entities():
    """Upsert SEBI entities with generated SECP256R1 keypairs."""
    db = await get_db()
    now = datetime.now(timezone.utc)
    key_valid_to = now + timedelta(days=365)

    for entity_data in SEBI_ENTITIES:
        reg_no = entity_data["registration_number"]

        try:
            _, public_key_pem = generate_entity_keypair(reg_no)
        except Exception:
            from app.crypto.seal_engine import load_entity_private_key
            private_key = load_entity_private_key(reg_no)
            public_key_pem = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode("utf-8")

        import hashlib
        spki_bytes = public_key_pem.encode()
        cert_fingerprint = "sha256:" + hashlib.sha256(spki_bytes).hexdigest()

        doc = {
            **entity_data,
            "api_key_hash": api_key_hash(entity_api_key(reg_no)),
            "official_public_key": public_key_pem,
            "cert_fingerprint": cert_fingerprint,
            "key_status": "active",
            "key_valid_from": now,
            "key_valid_to": key_valid_to,
            "last_updated": now
        }

        await db.sebi_registry.update_one(
            {"registration_number": reg_no},
            {"$set": doc},
            upsert=True
        )

        await log_audit(
            action="REGISTRY_ADD",
            actor_entity="PRAMAAN-SYSTEM",
            actor_reg_no="SYSTEM",
            resource_id=reg_no,
            metadata={"entity_name": entity_data["entity_name"], "source": "seed.py"},
            ip_address="127.0.0.1"
        )

    logger.info(f"Seeded {len(SEBI_ENTITIES)} SEBI entities with SECP256R1 keys")


async def seed_known_fakes():
    """Seed flagged_content MongoDB collection and Redis hash indexes."""
    db = await get_db()
    redis = await get_redis()

    for fake in KNOWN_FAKE_HASHES:
        await db.flagged_content.update_one(
            {"perceptual_hash": fake["perceptual_hash"]},
            {"$set": fake},
            upsert=True
        )

        redis_payload = json.dumps({
            "description": fake["description"],
            "first_flagged": fake["first_flagged"].isoformat(),
            "flagged_by": fake["flagged_by"],
            "detection_count": fake["detection_count"],
            "severity": fake["severity"]
        })
        if fake.get("content_type") == "image":
            key = key_image_hash(fake["perceptual_hash"].replace("phash:", ""))
        else:
            key = key_video_hash(fake["perceptual_hash"].replace("phash:", ""))
        await redis.set(key, redis_payload)

        if fake.get("hash_family"):
            family_key = key_hash_family(fake["perceptual_hash"].replace("phash:", ""))
            await redis.sadd(family_key, *[h.replace("phash:", "") for h in fake["hash_family"]])

    logger.info(f"Seeded {len(KNOWN_FAKE_HASHES)} known fake hashes in MongoDB + Redis")


async def seed_all():
    await connect_to_mongo()
    await connect_to_redis()
    await seed_entities()
    await seed_known_fakes()
    logger.success("Database seeding complete!")


if __name__ == "__main__":
    # NOTE: No issuer keys are written to disk here. Keys are derived in-app from
    # ENTITIES_API_KEYS_V1 (env/secret). Minting a tangible secrets file was removed —
    # a plaintext copy on disk is itself the leak (audit Issue 02).
    asyncio.run(seed_all())
