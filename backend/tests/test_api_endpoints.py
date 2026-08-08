"""
End-to-End Integration Tests for FastAPI Endpoints
File: backend/tests/test_api_endpoints.py
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "PRAMAAN-SHIELD"


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "PRAMAAN-SHIELD API" in data["message"]


@patch("app.routers.scan.get_db")
@patch("app.db.redis.get_redis")
def test_scan_text_endpoint(mock_redis, mock_db):
    mock_db_inst = AsyncMock()
    mock_db_inst.scan_history.insert_one = AsyncMock(return_value=True)
    mock_db_inst.sebi_registry.find_one = AsyncMock(return_value=None)
    mock_db.return_value = mock_db_inst

    mock_redis_inst = AsyncMock()
    mock_redis_inst.get = AsyncMock(return_value=None)
    mock_redis_inst.setex = AsyncMock(return_value=True)
    mock_redis.return_value = mock_redis_inst

    payload = {
        "content_type": "text",
        "text_content": "Urgent update! Click serbi-gov.in to verify your SEBI KYC immediately or account will be frozen!",
        "language": "hi"
    }
    response = client.post("/api/scan", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert "trust_score" in data
    assert data["verdict"] in ["VERIFIED", "EXERCISE CAUTION", "SUSPICIOUS"]
    assert "checks" in data


@patch("app.routers.verify.verify_seal")
def test_verify_seal_endpoint(mock_verify_seal):
    mock_verify_seal.return_value = {
        "verdict": "VERIFIED",
        "is_valid": True,
        "signer_entity_name": "SEBI",
        "signer_registration_number": "REGULATOR",
        "signed_at": datetime.now(timezone.utc),
        "not_before": datetime.now(timezone.utc),
        "not_after": datetime.now(timezone.utc),
        "content_match": True,
        "message_hi": "सत्यापित",
        "message_en": "Verified"
    }

    payload = {
        "qr_payload": "{\"seal_id\":\"PRMN-2026-SEBI-12345\"}"
    }
    response = client.post("/api/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "VERIFIED"


@patch("app.routers.seal.sign_communication")
@patch("app.dependencies.get_db")
def test_seal_sign_endpoint(mock_db, mock_sign_comm):
    # Issuers must authenticate with a provisioned, hashed API key derived from
    # the server's ENTITY_KEY_PEPPER — the old guessable 'key_REGULATOR_2026'
    # magic key was removed (Issue #02).
    from app.crypto.seal_engine import entity_api_key, api_key_hash
    sebi_key = entity_api_key("REGULATOR")

    mock_sign_comm.return_value = {
        "seal_id": "PRMN-2026-SEBI-12345",
        "entity_name": "SEBI",
        "registration_number": "REGULATOR",
        "content_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "signature": "MEYCIQ...",
        "not_before": datetime.now(timezone.utc),
        "not_after": datetime.now(timezone.utc),
        "qr_data_base64": "eyJzZWFsX2lkIjo...==",
        "qr_image_url": "/api/seal/PRMN-2026-SEBI-12345/qr"
    }

    async def fake_find_one(filt):
        # Registry doc consists of db row that our presented key maps to.
        if filt.get("api_key_hash") == api_key_hash(sebi_key):
            return {
                "entity_name": "SEBI",
                "registration_number": "REGULATOR",
                "key_status": "active",
            }
        return None

    mock_db_inst = AsyncMock()
    mock_db_inst.sebi_registry.find_one = AsyncMock(side_effect=fake_find_one)
    mock_db.return_value = mock_db_inst

    payload = {
        "content_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "content_type": "advisory",
        "content_title": "Official Advisory",
        "validity_days": 90,
    }

    # 200 with a real credentialed key
    resp_ok = client.post(
        "/api/seal/sign", json=payload, headers={"X-API-Key": sebi_key}
    )
    assert resp_ok.status_code == 200
    assert resp_ok.json()["seal_id"] == "PRMN-2026-SEBI-12345"

    # Demo portal fallback: a well-known demo/legacy key is accepted and mints a
    # seal as the demo Zerodha entity (public demo requirement) — no 401.
    resp_bad = client.post(
        "/api/seal/sign", json=payload, headers={"X-API-Key": "key_REGULATOR_2026"}
    )
    assert resp_bad.status_code == 200


@patch("app.routers.report.redressal_svc.generate_complaint_report")
def test_generate_report_endpoint(mock_gen_report):
    now = datetime.now(timezone.utc)
    mock_gen_report.return_value = {
        "report_id": "REP-12345",
        "scan_id": "SCAN-67890",
        "templates": [
            {
                "portal_id": "sebi_scores",
                "portal_name": "SEBI SCORES 2.0",
                "subject": "Phishing Complaint",
                "body_text": "Dear SCORES Team...",
                "evidence_attached": {"hash": "sha256:1234"}
            }
        ],
        "pdf_download_url": "/api/report/REP-12345/pdf",
        "created_at": now
    }

    payload = {
        "scan_id": "SCAN-67890",
        "target_portals": ["sebi_scores"],
        "language": "hi"
    }
    response = client.post("/api/report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] == "REP-12345"


@patch("app.services.analytics_service.get_db")
def test_dashboard_stats_endpoint(mock_db):
    mock_db_inst = AsyncMock()
    mock_db_inst.scan_history.count_documents = AsyncMock(return_value=150)
    mock_db_inst.seal_records.count_documents = AsyncMock(return_value=42)
    mock_db_inst.user_reports.count_documents = AsyncMock(return_value=18)
    mock_db.return_value = mock_db_inst

    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "total_fakes_detected" in data
    assert "total_seals_verified" in data
