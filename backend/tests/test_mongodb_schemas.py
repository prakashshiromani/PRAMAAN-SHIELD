"""
Test MongoDB Collection Schemas Validation
File: backend/tests/test_mongodb_schemas.py
"""

from app.db.mongodb import (
    SEBI_REGISTRY_SCHEMA,
    SEAL_RECORDS_SCHEMA,
    SCAN_HISTORY_SCHEMA,
    FLAGGED_CONTENT_SCHEMA,
    USER_REPORTS_SCHEMA,
    AUDIT_LEDGER_SCHEMA,
)


def test_mongodb_schemas_defined():
    schemas = [
        SEBI_REGISTRY_SCHEMA,
        SEAL_RECORDS_SCHEMA,
        SCAN_HISTORY_SCHEMA,
        FLAGGED_CONTENT_SCHEMA,
        USER_REPORTS_SCHEMA,
        AUDIT_LEDGER_SCHEMA,
    ]
    for schema in schemas:
        assert "$jsonSchema" in schema
        assert "required" in schema["$jsonSchema"]
        assert "properties" in schema["$jsonSchema"]
