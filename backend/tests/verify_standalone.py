"""
Standalone Verification Script (Windows encoding safe)
File: backend/tests/verify_standalone.py
"""

import sys
import os
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend directory to sys.path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def run_standalone_tests():
    print("--- PRAMAAN-SHIELD Standalone Verification Suite ---")

    # 1. Config Test
    from app.config import get_settings
    settings = get_settings()
    assert settings.DB_NAME == "pramaan_shield"
    assert settings.MAX_UPLOAD_BYTES == 52428800
    print("[PASS] Config Test")

    # 2. Privacy Test (HMAC IP Pseudonymization)
    from app.utils.privacy import pseudonymize_ip
    ip_hmac = pseudonymize_ip("203.0.113.42")
    assert len(ip_hmac) == 64
    assert ip_hmac != pseudonymize_ip("192.168.1.1")
    print("[PASS] DPDP IP Pseudonymization Test")

    # 3. Crypto & Seal Engine Test
    from app.crypto.seal_engine import generate_entity_keypair, compute_public_key_fingerprint, build_canonical_payload
    from datetime import datetime, timezone, timedelta
    priv, pub_pem = generate_entity_keypair("VERIFY_ENTITY_123")
    assert "BEGIN PUBLIC KEY" in pub_pem
    fp = compute_public_key_fingerprint(priv)
    assert fp.startswith("sha256:")
    print("[PASS] SECP256R1 ECDSA Key Generation Test")

    # 4. Social Coordination Module Test
    import asyncio
    from app.services.social_service import SocialService
    async def _test_social():
        svc = SocialService()
        res = await svc.analyze_coordination("BUY NOW! Target 2000% guaranteed upper circuit multibagger tip! Join t.me/scam_group")
        assert res.coordination_score >= 50
        assert res.is_coordinated_scam is True
    asyncio.run(_test_social())
    print("[PASS] Social Pump-and-Dump Coordination (Module A5) Test")

    # 5. Typosquatting Levenshtein Test
    from app.utils.levenshtein import check_typosquatting
    typos = check_typosquatting(["zerrodha.com", "kite.zerodha.com"])
    assert len(typos) > 0
    assert typos[0]["suspicious_domain"] == "zerrodha.com"
    print("[PASS] Typosquatting Levenshtein Test")

    print("\nALL STANDALONE VERIFICATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_standalone_tests()
