"""
Unit and Integration Tests for Real-Time Analytics & Live Metrics Recording
File: backend/tests/test_analytics.py
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.services.analytics_service import get_analytics_service

client = TestClient(app)


def test_dashboard_stats_endpoint_baseline():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()

    assert data["total_scans"] >= 15420
    assert data["total_fakes_detected"] >= 4218
    assert data["total_seals_verified"] >= 892
    assert data["reports_generated"] >= 1256
    assert "threat_distribution" in data
    assert "top_flagged_domains" in data
    assert len(data["top_flagged_domains"]) > 0


@patch("app.routers.scan.get_db")
@patch("app.db.redis.get_redis")
def test_live_scan_increments_analytics(mock_redis, mock_db):
    mock_db_inst = AsyncMock()
    mock_db_inst.scan_history.insert_one = AsyncMock(return_value=True)
    mock_db_inst.sebi_registry.find_one = AsyncMock(return_value=None)
    mock_db.return_value = mock_db_inst

    mock_redis_inst = AsyncMock()
    mock_redis_inst.get = AsyncMock(return_value=None)
    mock_redis_inst.set = AsyncMock(return_value=True)
    mock_redis.return_value = mock_redis_inst

    # Check baseline stats
    resp_before = client.get("/api/dashboard/stats").json()
    scans_before = resp_before["total_scans"]
    fakes_before = resp_before["total_fakes_detected"]

    # Execute a live scan with suspicious content
    payload = {
        "content_type": "text",
        "text_content": "Urgent! Account suspended! Login serbi-gov.in immediately to unlock KYC!",
        "language": "hi"
    }
    scan_resp = client.post("/api/scan", data=payload)
    assert scan_resp.status_code == 200

    # Fetch dashboard stats again
    resp_after = client.get("/api/dashboard/stats").json()
    assert resp_after["total_scans"] == scans_before + 1
    assert resp_after["total_fakes_detected"] >= fakes_before + 1


@patch("app.routers.verify.verify_seal")
def test_live_seal_verification_increments_analytics(mock_verify_seal):
    mock_verify_seal.return_value = {
        "verdict": "VERIFIED",
        "is_valid": True,
        "signer_entity_name": "SEBI",
        "signer_registration_number": "REGULATOR",
        "content_match": True
    }

    resp_before = client.get("/api/dashboard/stats").json()
    seals_before = resp_before["total_seals_verified"]

    verify_payload = {
        "qr_payload": '{"seal_id":"PRMN-TEST-12345"}'
    }
    res = client.post("/api/verify", json=verify_payload)
    assert res.status_code == 200

    resp_after = client.get("/api/dashboard/stats").json()
    assert resp_after["total_seals_verified"] == seals_before + 1


@patch("app.routers.report.redressal_svc.generate_complaint_report")
def test_live_report_generation_increments_analytics(mock_gen_report):
    from datetime import datetime, timezone
    mock_gen_report.return_value = {
        "report_id": "REP-99999",
        "scan_id": "SCAN-99999",
        "templates": [],
        "pdf_download_url": "/api/report/REP-99999/pdf",
        "created_at": datetime.now(timezone.utc)
    }

    resp_before = client.get("/api/dashboard/stats").json()
    reports_before = resp_before["reports_generated"]

    report_payload = {
        "scan_id": "SCAN-99999",
        "target_portals": ["sebi_scores"],
        "language": "hi"
    }
    res = client.post("/api/report", json=report_payload)
    assert res.status_code == 200

    resp_after = client.get("/api/dashboard/stats").json()
    assert resp_after["reports_generated"] == reports_before + 1
