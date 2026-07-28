"""
Test DPDP Privacy Keyed HMAC IP Pseudonymization
File: backend/tests/test_privacy.py
"""

import hashlib
from app.utils.privacy import pseudonymize_ip


def test_pseudonymize_ip_returns_hex():
    result = pseudonymize_ip("203.0.113.42")
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)


def test_pseudonymize_ip_is_not_plain_sha256():
    ip = "203.0.113.42"
    plain_sha = hashlib.sha256(ip.encode()).hexdigest()
    hmac_result = pseudonymize_ip(ip)
    assert hmac_result != plain_sha, "SECURITY FAIL: output matches plain SHA-256 (no salt applied)"


def test_pseudonymize_ip_same_input_same_output():
    ip = "10.0.0.1"
    assert pseudonymize_ip(ip) == pseudonymize_ip(ip)


def test_pseudonymize_ip_different_ips_differ():
    assert pseudonymize_ip("1.1.1.1") != pseudonymize_ip("8.8.8.8")


def test_pseudonymize_ipv6():
    result = pseudonymize_ip("::1")
    assert len(result) == 64
