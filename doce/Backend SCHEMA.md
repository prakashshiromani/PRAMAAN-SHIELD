# 🗄️ SCHEMA.md — PRAMAAN-SHIELD Backend Schema Specification

**Master Data Blueprint: MongoDB Collections, Redis Keys, Pydantic DTOs, Cryptographic Payloads & API Contracts**  
Version 1.0 · Team Black Ghost · SEBI TechSprint 2026

---

## 📌 Document Overview

This document defines the complete backend schema specification for **PRAMAAN-SHIELD**. It acts as the single source of truth for:
1. **MongoDB Collections** — Document structures, data types, indexes, and validation rules.
2. **Redis In-Memory Key Schema** — Caching, rate limiting, and real-time perceptual hash indexes.
3. **Pydantic Models (DTOs)** — Request/response schemas for FastAPI endpoints.
4. **Cryptographic Payloads** — PRAMAAN Seal QR code data layout & ECDSA signature structures.
5. **LLM Prompt & JSON Response Schemas** — Structured outputs for Gemini 1.5 Flash.

---

## 📂 Table of Contents

1. [MongoDB Database Schemas](#1-mongodb-database-schemas)
   - [1.1 `sebi_registry`](#11-sebi_registry)
   - [1.2 `seal_records`](#12-seal_records)
   - [1.3 `scan_history`](#13-scan_history)
   - [1.4 `flagged_content`](#14-flagged_content)
   - [1.5 `user_reports`](#15-user_reports)
   - [1.6 `audit_ledger`](#16-audit_ledger)
2. [Redis In-Memory Key Schemas](#2-redis-in-memory-key-schemas)
3. [Pydantic API DTO Schemas](#3-pydantic-api-dto-schemas)
   - [3.1 Core Enums & Shared Types](#31-core-enums--shared-types)
   - [3.2 `/api/scan` Endpoint Schemas](#32-apiscan-endpoint-schemas)
   - [3.3 `/api/verify` Endpoint Schemas](#33-apiverify-endpoint-schemas)
   - [3.4 `/api/seal/sign` Endpoint Schemas](#34-apisealsign-endpoint-schemas)
   - [3.5 `/api/report` Endpoint Schemas](#35-apireport-endpoint-schemas)
   - [3.6 `/api/dashboard/stats` Endpoint Schemas](#36-apidashboardstats-endpoint-schemas)
   - [3.7 Telegram Bot Webhook Schemas](#37-telegram-bot-webhook-schemas)
   - [3.8 Standard Error Response Schema](#38-standard-error-response-schema)
4. [Cryptographic Seal QR Payload Schema](#4-cryptographic-seal-qr-payload-schema)
5. [Gemini LLM JSON Response Schemas](#5-gemini-llm-json-response-schemas)
6. [MongoDB Validation Rules](#6-mongodb-validation-rules)
7. [Python Implementation (`app/schemas.py`)](#7-python-implementation-appschemaspy)

---

## 1. MongoDB Database Schemas

All collections reside in database: `pramaan_shield`.
For **MongoDB `jsonSchema` validation rules**, see [Section 6](#6-mongodb-validation-rules).

### 1.1 `sebi_registry`
*Purpose:* Stores official SEBI registered entities and their **Pinned Public Keys (Trust Anchors)**.

```json
{
  "_id": "ObjectId('66a01b2f8c12d4001a1b2c3d')",
  "entity_name": "Zerodha Broking Limited",
  "registration_number": "INZ000031633",
  "category": "Stock Broker",
  "sebi_registered": true,
  "official_domains": [
    "zerodha.com",
    "kite.zerodha.com",
    "console.zerodha.com"
  ],
  "official_emails": [
    "support@zerodha.com",
    "notice@zerodha.com"
  ],
  "official_public_key": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE7vX...==\n-----END PUBLIC KEY-----",
  "cert_fingerprint": "sha256:9f2c7a4b8e1d3f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a",
  "key_status": "active",
  "key_valid_from": "2026-01-01T00:00:00Z",
  "key_valid_to": "2027-01-01T00:00:00Z",
  "address": "153/154, 4th Cross, Dollars Colony, JP Nagar 4th Phase, Bengaluru, Karnataka 560078",
  "last_updated": "2026-07-01T00:00:00Z"
}
```

**Indexes:**
* `registration_number` → `UNIQUE INDEX`
* `entity_name` → `TEXT INDEX` (Candidate search)
* `official_domains` → `MULTIKEY INDEX`
* `key_status` → `INDEX`

---

### 1.2 `seal_records`
*Purpose:* Records every issued PRAMAAN Seal for verification & revocation lookup.

```json
{
  "_id": "ObjectId('66a01c3e8c12d4001a1b2c3e')",
  "seal_id": "PRMN-2026-SEBI-A3F2C",
  "entity_name": "SEBI",
  "registration_number": "REGULATOR",
  "content_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "signature": "MEQCID3k8Z1YxV2N...b3A1Wj9=",
  "signing_key_fingerprint": "sha256:9f2c7a4b8e1d3f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a",
  "timestamp": "2026-07-08T10:30:00Z",
  "not_before": "2026-07-08T10:30:00Z",
  "not_after": "2026-10-08T10:30:00Z",
  "content_type": "circular",
  "content_title": "Framework for Advisory Communications on Social Media Platforms",
  "qr_data": "eyJzZWFsX2lkIjoiUFJNTi0yMDI2LVNFQkktQTNGMkMiLCJwYXlsb2FkIjp7Li4ufX0=",
  "status": "active",
  "revoked_at": null,
  "revocation_reason": null,
  "signed_by_session": "sess_89f1a2b3c4d5",
  "created_at": "2026-07-08T10:30:00Z"
}
```

**Indexes:**
* `seal_id` → `UNIQUE INDEX`
* `content_hash` → `INDEX`
* `entity_name` + `timestamp` → `COMPOUND INDEX`
* `status` → `INDEX`

---

### 1.3 `scan_history`
*Purpose:* Stores non-sensitive scan logs, detected threats, trust scores, and explainability checks.

```json
{
  "_id": "ObjectId('66a01d4f8c12d4001a1b2c3f')",
  "scan_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "content_type": "text",
  "content_hash": "sha256:8f4b2c1a0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b",
  "perceptual_hash": null,
  "trust_score": 8,
  "verdict": "SUSPICIOUS",
  "checks": [
    {
      "module": "phishing",
      "status": "fail",
      "label": "AI-Generated Text Detected",
      "detail": "87% probability of LLM-generated content",
      "contribution": -30
    },
    {
      "module": "domain",
      "status": "fail",
      "label": "Typosquat Domain Detected",
      "detail": "serbi-gov.in (Levenshtein distance 1 from sebi.gov.in)",
      "contribution": -20
    },
    {
      "module": "registry",
      "status": "fail",
      "label": "SEBI Registry Check Failed",
      "detail": "Sender domain serbi-gov.in is not listed in SEBI registered entities",
      "contribution": -15
    }
  ],
  "source": "web",
  "language": "hi",
  "complaint_generated": true,
  "ip_hmac": "e3a8901c09b689a74c2d3b4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a",
  "created_at": "2026-07-23T14:30:00Z"
}
```

**Indexes:**
* `scan_id` → `UNIQUE INDEX`
* `content_hash` → `INDEX`
* `created_at` → `INDEX` (TTL 90 Days)
* `verdict` + `content_type` → `COMPOUND INDEX`

---

### 1.4 `flagged_content`
*Purpose:* Registry of known fakes and their auto-generated variant hash families.

```json
{
  "_id": "ObjectId('66a01e508c12d4001a1b2c40')",
  "perceptual_hash": "phash:a1b2c3d4e5f67890",
  "hash_family": [
    "phash:a1b2c3d4e5f67891",
    "phash:a1b2c3d4e5f67892",
    "phash:b1b2c3d4e5f67890",
    "phash:a1b2c3d4e5f67800"
  ],
  "content_type": "video",
  "description": "BSE CEO Deepfake Scam Video (Fake Stock Tips)",
  "first_flagged": "2026-01-15T09:00:00Z",
  "flagged_by": "SEBI",
  "source_reference": "SEBI Advisory 2026/01-BSE",
  "detection_count": 1420,
  "last_detected": "2026-07-23T14:15:00Z",
  "severity": "critical"
}
```

**Indexes:**
* `perceptual_hash` → `UNIQUE INDEX`
* `hash_family` → `MULTIKEY INDEX`

---

### 1.5 `user_reports`
*Purpose:* Stores generated complaint packages for SEBI SCORES 2.0 & Cyber Crime 1930 / Chakshu.

```json
{
  "_id": "ObjectId('66a01f618c12d4001a1b2c41')",
  "report_id": "rep_78a1b2c3d4e5",
  "scan_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "target_portals": ["sebi_scores", "cybercrime_1930"],
  "template_text_en": "FORMAL COMPLAINT TO SEBI SCORES 2.0...\nEvidence Hash: sha256:8f4b2c1a...",
  "template_text_hi": "सेबी स्कोर्स 2.0 पोर्टल हेतु औपचारिक शिकायत...\nप्रमाण हैश: sha256:8f4b2c1a...",
  "evidence_package": {
    "content_hash": "sha256:8f4b2c1a0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b",
    "trust_score": 8,
    "verdict": "SUSPICIOUS",
    "detected_typosquat": "serbi-gov.in",
    "ai_probability": 0.87,
    "timestamp": "2026-07-23T14:30:00Z"
  },
  "status": "generated",
  "created_at": "2026-07-23T14:30:05Z"
}
```

**Indexes:**
* `report_id` → `UNIQUE INDEX`
* `scan_id` → `INDEX`

---

### 1.6 `audit_ledger`
*Purpose:* Immutable log for regulatory tracking of all key signatures, registry updates, and flags.

**Allowed `action` values (enum):**

| Action | Triggered When |
| :--- | :--- |
| `SIGN_SEAL` | Entity signs a new PRAMAAN Seal |
| `REVOKE_SEAL` | Entity revokes an existing seal |
| `FLAG_CONTENT` | Verified entity flags content as fake |
| `REGISTRY_ADD` | New entity added to SEBI registry |
| `REGISTRY_UPDATE` | Entity registry record modified |
| `KEY_ROTATE` | Entity's public key is rotated |
| `KEY_REVOKE` | Entity's public key is revoked |

```json
{
  "_id": "ObjectId('66a020728c12d4001a1b2c42')",
  "audit_id": "aud_102030405060",
  "action": "SIGN_SEAL",
  "actor_entity": "SEBI",
  "actor_registration_number": "REGULATOR",
  "resource_id": "PRMN-2026-SEBI-A3F2C",
  "metadata": {
    "content_type": "circular",
    "content_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "ip_hmac": "e3a8901c09b689a74c2d3b4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a",
  "timestamp": "2026-07-08T10:30:00Z"
}
```

---

## 2. Redis In-Memory Key Schemas

| Key Pattern | Data Type | TTL | Purpose / Description |
| :--- | :--- | :--- | :--- |
| `hash:image:<phash_hex>` | String (JSON) | Infinite | Image perceptual hash index for fast lookup |
| `hash:video:<vhash_hex>` | String (JSON) | Infinite | Video perceptual hash index (<50ms lookup) |
| `hash:family:<parent_phash>` | Set | Infinite | Set of perceptual hash variants (cropped, mirrored) |
| `rate:<ip_hmac>` | String (Integer) | 60 Seconds | Rate limiter counter (Max 30 req/min) |
| `scan:cache:<content_hash>` | String (JSON) | 3600 Secs | Caches result of recent identical content scans |
| `stats:total_scans` | String (Integer) | Infinite | Real-time global scan counter for dashboard |
| `stats:fakes_detected` | String (Integer) | Infinite | Real-time global fakes counter for dashboard |

---

## 3. Pydantic API DTO Schemas

### 3.1 Core Enums & Shared Types

```python
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class ContentType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"

class VerdictStatus(str, Enum):
    VERIFIED = "VERIFIED"
    CAUTION = "EXERCISE CAUTION"
    SUSPICIOUS = "SUSPICIOUS"

class CheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"

class SealVerdict(str, Enum):
    VERIFIED = "VERIFIED"
    TAMPERED = "TAMPERED"
    FORGED = "FORGED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    UNVERIFIED = "UNVERIFIED"

class CheckResult(BaseModel):
    module: str = Field(..., description="Module key: hash, phishing, voice, video, domain, registry, seal")
    status: CheckStatus
    label: str = Field(..., description="Human readable summary label")
    detail: str = Field(..., description="Detailed technical reason")
    contribution: int = Field(..., description="Impact on trust score (-100 to +50)")
```

---

### 3.2 `/api/scan` Endpoint Schemas

**Request:** `POST /api/scan` (`multipart/form-data`)

> **Note:** This endpoint accepts both JSON (text-only scans) and `multipart/form-data` (file uploads for audio/video/image). FastAPI handles both via dependency injection.

```python
from fastapi import UploadFile, File, Form

# --- JSON body (text scans) ---
class ScanTextRequest(BaseModel):
    content_type: ContentType = ContentType.TEXT
    text_content: str = Field(..., max_length=10000, description="Pasted text, email body, SMS, or social post")
    language: str = Field("hi", description="Output language: 'hi' or 'en'")

# --- Multipart form (media uploads) ---
# Used as FastAPI route params, not a Pydantic model:
#   content_type: ContentType = Form(...)
#   language: str = Form("hi")
#   media_file: UploadFile = File(...)
#
# FastAPI route signature:
#   @router.post("/api/scan")
#   async def scan_content(
#       content_type: ContentType = Form(...),
#       language: str = Form("hi"),
#       text_content: Optional[str] = Form(None),
#       media_file: Optional[UploadFile] = File(None),
#   ):

# Internal unified model after parsing:
class ScanInput(BaseModel):
    """Internal model after request parsing — unifies text and media inputs."""
    content_type: ContentType
    text_content: Optional[str] = None
    media_path: Optional[str] = None  # Temp file path after saving upload
    media_original_name: Optional[str] = None
    language: str = "hi"
```

**Response:** `200 OK`
```python
class ActionButton(BaseModel):
    id: str
    label: str
    action_type: str  # "copy" | "download" | "navigate"
    url: Optional[str] = None

class ScanResponse(BaseModel):
    scan_id: str
    content_type: ContentType
    trust_score: int = Field(..., ge=0, le=100, description="Unified Trust Score (0-100)")
    verdict: VerdictStatus
    verdict_label_hi: str
    verdict_label_en: str
    checks: List[CheckResult]
    ai_generated_probability: Optional[float] = None
    typosquat_detected: Optional[str] = None
    evidence_summary: str
    recommended_actions: List[ActionButton]
    created_at: datetime
```

---

### 3.3 `/api/verify` Endpoint Schemas

**Request:** `POST /api/verify`
```python
class VerifySealRequest(BaseModel):
    seal_id: Optional[str] = Field(None, description="PRAMAAN Seal ID e.g. PRMN-2026-SEBI-A3F2C")
    qr_payload: Optional[str] = Field(None, description="Scanned QR raw payload string")
    presented_content_hash: Optional[str] = Field(None, description="SHA-256 of the presented document")
```

**Response:** `200 OK`
```python
class VerifySealResponse(BaseModel):
    verdict: SealVerdict
    is_valid: bool
    signer_entity_name: Optional[str] = None
    signer_registration_number: Optional[str] = None
    signed_at: Optional[datetime] = None
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None
    content_match: bool = False
    message_hi: str
    message_en: str
```

---

### 3.4 `/api/seal/sign` Endpoint Schemas

**Request:** `POST /api/seal/sign` (Authenticated)
```python
class IssueSealRequest(BaseModel):
    content_hash: str = Field(..., regex="^sha256:[a-fA-F0-9]{64}$")
    content_type: str = Field(..., example="circular")
    content_title: str = Field(..., example="F&O Margin Update July 2026")
    validity_days: int = Field(90, ge=1, le=365)
```

**Response:** `200 OK`
```python
class IssueSealResponse(BaseModel):
    seal_id: str
    entity_name: str
    registration_number: str
    content_hash: str
    signature: str
    not_before: datetime
    not_after: datetime
    qr_data_base64: str
    qr_image_url: str
```

---

### 3.5 `/api/report` Endpoint Schemas

**Request:** `POST /api/report`
```python
class GenerateReportRequest(BaseModel):
    scan_id: str
    target_portals: List[str] = Field(["sebi_scores", "cybercrime_1930"])
    language: str = Field("hi")
```

**Response:** `200 OK`
```python
class ComplaintTemplate(BaseModel):
    portal_id: str  # "sebi_scores" or "cybercrime_1930"
    portal_name: str
    subject: str
    body_text: str
    evidence_attached: Dict[str, Any]

class GenerateReportResponse(BaseModel):
    report_id: str
    scan_id: str
    templates: List[ComplaintTemplate]
    pdf_download_url: str
    created_at: datetime
```

---

### 3.6 `/api/dashboard/stats` Endpoint Schemas

**Response:** `GET /api/dashboard/stats`
```python
class DashboardStatsResponse(BaseModel):
    total_scans: int
    total_fakes_detected: int
    total_seals_verified: int
    reports_generated: int
    top_flagged_domains: List[Dict[str, int]]
    threat_distribution: Dict[str, int]
```

---

### 3.7 Telegram Bot Webhook Schemas

**Incoming:** Telegram sends `POST /webhook/telegram` with its Update object. We extract:
```python
class TelegramScanInput(BaseModel):
    """Extracted from Telegram Update after webhook secret validation."""
    chat_id: int
    message_id: int
    user_id: int
    username: Optional[str] = None
    text_content: Optional[str] = None
    media_file_id: Optional[str] = None
    media_type: Optional[ContentType] = None
    language: str = "hi"
```

**Outgoing:** Bot sends verdict back via `sendMessage`:
```python
class TelegramVerdictReply(BaseModel):
    """Shape of the verdict message sent back to the Telegram user."""
    chat_id: int
    reply_to_message_id: int
    trust_score: int = Field(..., ge=0, le=100)
    verdict: VerdictStatus
    verdict_emoji: str  # "🔴" | "🟡" | "🟢"
    summary_text: str  # Plain-text bilingual summary
    inline_keyboard: List[Dict[str, str]]  # [{"text": "Report SEBI SCORES", "url": "..."}]
```

---

### 3.8 Standard Error Response Schema

All API endpoints return this shape on failure:
```python
class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    """Standard error envelope for all 4xx / 5xx responses."""
    error: bool = True
    status_code: int  # 400, 404, 422, 429, 500
    error_type: str   # "validation_error" | "not_found" | "rate_limited" | "internal_error"
    message: str      # Human readable summary
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None
```

**HTTP Status Code Mapping:**

| Status | `error_type` | When |
| :--- | :--- | :--- |
| `400` | `validation_error` | Missing/invalid request fields |
| `404` | `not_found` | Seal ID / Scan ID not found |
| `413` | `payload_too_large` | Media file exceeds max upload size |
| `422` | `unprocessable_entity` | Content could not be parsed or analyzed |
| `429` | `rate_limited` | More than 30 requests/minute from same IP |
| `500` | `internal_error` | Unexpected server failure |

---

## 4. Cryptographic Seal QR Payload Schema

To prevent forgery, public keys are **NOT** stored inside the QR. The payload carries only content hash, identity pointers, and signature.

```json
{
  "seal_id": "PRMN-2026-SEBI-A3F2C",
  "payload": {
    "content_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "entity": "SEBI",
    "reg_no": "REGULATOR",
    "signed_at": "2026-07-08T10:30:00Z",
    "not_after": "2026-10-08T10:30:00Z",
    "version": "2.0"
  },
  "signature": "MEQCID3k8Z1YxV2N...b3A1Wj9="
}
```

---

## 5. Gemini LLM JSON Response Schemas

When FastAPI calls Gemini 1.5 Flash for NER, text classification, or complaint drafting, Gemini is enforced via structured system prompts to return JSON matching these schemas.

### 5.1 Text Phishing & NER Extraction Schema
```json
{
  "ai_generated_probability": 0.87,
  "perplexity_score": "low",
  "burstiness_score": "low",
  "urgency_score": 9,
  "extracted_entities": [
    {
      "entity_name": "SEBI",
      "claimed_registration": null,
      "category": "Regulator"
    }
  ],
  "social_engineering_triggers": [
    "account block",
    "24 hour deadline",
    "kyc update"
  ],
  "injection_attempt": false
}
```

### 5.2 Complaint Draft Generation Schema
```json
{
  "complaint_subject_en": "Report: Suspected Phishing Communication Impersonating SEBI",
  "complaint_subject_hi": "शिकायत: सेबी के नाम पर संदिग्ध फ़िशिंग संचार",
  "complaint_body_en": "I received a suspicious communication claiming to be from SEBI...",
  "complaint_body_hi": "मुझे सेबी के नाम से एक संदिग्ध संचार प्राप्त हुआ...",
  "evidence_summary_en": "Trust Score: 8/100. AI-generated text (87%), typosquat domain (serbi-gov.in), entity not registered.",
  "evidence_summary_hi": "विश्वास स्कोर: 8/100। AI-जनित पाठ (87%), टाइपोस्क्वाट डोमेन (serbi-gov.in), इकाई पंजीकृत नहीं है।",
  "recommended_category": "Fraudulent Communication / Phishing",
  "urgency_level": "high"
}
```

---

## 6. MongoDB Validation Rules

Apply these `jsonSchema` validators via `db.createCollection()` or `db.runCommand({collMod})` to enforce data integrity at database level.

### 6.1 `sebi_registry` Validator
```javascript
db.createCollection("sebi_registry", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["entity_name", "registration_number", "category", "sebi_registered",
                 "official_domains", "key_status", "last_updated"],
      properties: {
        entity_name:         { bsonType: "string", description: "Official entity name" },
        registration_number: { bsonType: "string", description: "SEBI registration ID (unique)" },
        category:            { bsonType: "string", enum: ["Stock Broker", "Depository Participant",
                              "Mutual Fund", "Portfolio Manager", "Investment Adviser",
                              "Research Analyst", "Registrar", "Exchange", "Regulator"] },
        sebi_registered:     { bsonType: "bool" },
        official_domains:    { bsonType: "array", items: { bsonType: "string" }, minItems: 1 },
        official_public_key: { bsonType: "string" },
        key_status:          { bsonType: "string", enum: ["active", "rotated", "revoked"] },
        key_valid_from:      { bsonType: "date" },
        key_valid_to:        { bsonType: "date" },
        last_updated:        { bsonType: "date" }
      }
    }
  }
});
```

### 6.2 `seal_records` Validator
```javascript
db.createCollection("seal_records", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["seal_id", "entity_name", "registration_number", "content_hash",
                 "signature", "signing_key_fingerprint", "timestamp",
                 "not_before", "not_after", "status", "created_at"],
      properties: {
        seal_id:                  { bsonType: "string" },
        entity_name:              { bsonType: "string" },
        registration_number:      { bsonType: "string" },
        content_hash:             { bsonType: "string", pattern: "^sha256:[a-fA-F0-9]{64}$" },
        signature:                { bsonType: "string" },
        signing_key_fingerprint:  { bsonType: "string" },
        status:                   { bsonType: "string", enum: ["active", "revoked"] },
        content_type:             { bsonType: "string", enum: ["circular", "press_release",
                                    "advisory", "video_statement", "notification"] },
        not_before:               { bsonType: "date" },
        not_after:                { bsonType: "date" },
        revoked_at:               { bsonType: ["date", "null"] },
        revocation_reason:        { bsonType: ["string", "null"] }
      }
    }
  }
});
```

### 6.3 `scan_history` Validator
```javascript
db.createCollection("scan_history", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["scan_id", "content_type", "content_hash", "trust_score",
                 "verdict", "checks", "source", "created_at"],
      properties: {
        scan_id:      { bsonType: "string" },
        content_type: { bsonType: "string", enum: ["text", "audio", "video", "image"] },
        content_hash: { bsonType: "string" },
        trust_score:  { bsonType: "int", minimum: 0, maximum: 100 },
        verdict:      { bsonType: "string", enum: ["VERIFIED", "EXERCISE CAUTION", "SUSPICIOUS"] },
        checks:       { bsonType: "array", items: {
          bsonType: "object",
          required: ["module", "status", "label", "detail", "contribution"],
          properties: {
            module:       { bsonType: "string" },
            status:       { bsonType: "string", enum: ["pass", "fail", "warn", "skip"] },
            label:        { bsonType: "string" },
            detail:       { bsonType: "string" },
            contribution: { bsonType: "int" }
          }
        }},
        source:       { bsonType: "string", enum: ["web", "telegram", "api"] },
        language:     { bsonType: "string", enum: ["hi", "en"] },
        ip_hmac:      { bsonType: "string", description: "Keyed HMAC-SHA256, NOT plain SHA256" },
        created_at:   { bsonType: "date" }
      }
    }
  }
});
```

### 6.4 `flagged_content` Validator
```javascript
db.createCollection("flagged_content", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["perceptual_hash", "content_type", "description",
                 "first_flagged", "flagged_by", "severity"],
      properties: {
        perceptual_hash: { bsonType: "string" },
        hash_family:     { bsonType: "array", items: { bsonType: "string" } },
        content_type:    { bsonType: "string", enum: ["video", "image", "audio"] },
        description:     { bsonType: "string" },
        first_flagged:   { bsonType: "date" },
        flagged_by:      { bsonType: "string" },
        source_reference:{ bsonType: "string" },
        detection_count: { bsonType: "int", minimum: 0 },
        last_detected:   { bsonType: "date" },
        severity:        { bsonType: "string", enum: ["critical", "high", "medium", "low"] }
      }
    }
  }
});
```

### 6.5 `user_reports` Validator
```javascript
db.createCollection("user_reports", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["report_id", "scan_id", "target_portals", "status", "created_at"],
      properties: {
        report_id:      { bsonType: "string" },
        scan_id:        { bsonType: "string" },
        target_portals: { bsonType: "array", items: {
          bsonType: "string", enum: ["sebi_scores", "cybercrime_1930"]
        }, minItems: 1 },
        template_text_en: { bsonType: "string" },
        template_text_hi: { bsonType: "string" },
        evidence_package: { bsonType: "object" },
        status:         { bsonType: "string", enum: ["generated", "copied", "downloaded"] },
        created_at:     { bsonType: "date" }
      }
    }
  }
});
```

### 6.6 `audit_ledger` Validator
```javascript
db.createCollection("audit_ledger", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["audit_id", "action", "actor_entity",
                 "actor_registration_number", "resource_id", "timestamp"],
      properties: {
        audit_id:                  { bsonType: "string" },
        action:                    { bsonType: "string", enum: [
          "SIGN_SEAL", "REVOKE_SEAL", "FLAG_CONTENT",
          "REGISTRY_ADD", "REGISTRY_UPDATE", "KEY_ROTATE", "KEY_REVOKE"
        ]},
        actor_entity:              { bsonType: "string" },
        actor_registration_number: { bsonType: "string" },
        resource_id:               { bsonType: "string" },
        metadata:                  { bsonType: "object" },
        ip_hmac:                   { bsonType: "string" },
        timestamp:                 { bsonType: "date" }
      }
    }
  }
});
```

---

## 7. Python Implementation (`app/schemas.py`)

Here is the complete production Python code ready to be placed in `backend/app/schemas.py`:

```python
"""
PRAMAAN-SHIELD FastAPI Schemas Module
File: app/schemas.py
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class ContentType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"


class VerdictStatus(str, Enum):
    VERIFIED = "VERIFIED"
    CAUTION = "EXERCISE CAUTION"
    SUSPICIOUS = "SUSPICIOUS"


class CheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


class SealVerdict(str, Enum):
    VERIFIED = "VERIFIED"
    TAMPERED = "TAMPERED"
    FORGED = "FORGED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    UNVERIFIED = "UNVERIFIED"


class CheckResult(BaseModel):
    module: str
    status: CheckStatus
    label: str
    detail: str
    contribution: int


class ScanTextRequest(BaseModel):
    content_type: ContentType = ContentType.TEXT
    text_content: str = Field(..., max_length=10000)
    language: str = "hi"


class ScanInput(BaseModel):
    """Internal unified model after request parsing."""
    content_type: ContentType
    text_content: Optional[str] = None
    media_path: Optional[str] = None
    media_original_name: Optional[str] = None
    language: str = "hi"


class ActionButton(BaseModel):
    id: str
    label: str
    action_type: str
    url: Optional[str] = None


class ScanResponse(BaseModel):
    scan_id: str
    content_type: ContentType
    trust_score: int = Field(..., ge=0, le=100)
    verdict: VerdictStatus
    verdict_label_hi: str
    verdict_label_en: str
    checks: List[CheckResult]
    ai_generated_probability: Optional[float] = None
    typosquat_detected: Optional[str] = None
    evidence_summary: str
    recommended_actions: List[ActionButton]
    created_at: datetime


class VerifySealRequest(BaseModel):
    seal_id: Optional[str] = None
    qr_payload: Optional[str] = None
    presented_content_hash: Optional[str] = None


class VerifySealResponse(BaseModel):
    verdict: SealVerdict
    is_valid: bool
    signer_entity_name: Optional[str] = None
    signer_registration_number: Optional[str] = None
    signed_at: Optional[datetime] = None
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None
    content_match: bool = False
    message_hi: str
    message_en: str


class IssueSealRequest(BaseModel):
    content_hash: str
    content_type: str
    content_title: str
    validity_days: int = 90


class IssueSealResponse(BaseModel):
    seal_id: str
    entity_name: str
    registration_number: str
    content_hash: str
    signature: str
    not_before: datetime
    not_after: datetime
    qr_data_base64: str
    qr_image_url: str


class GenerateReportRequest(BaseModel):
    scan_id: str
    target_portals: List[str] = ["sebi_scores", "cybercrime_1930"]
    language: str = "hi"


class ComplaintTemplate(BaseModel):
    portal_id: str
    portal_name: str
    subject: str
    body_text: str
    evidence_attached: Dict[str, Any]


class GenerateReportResponse(BaseModel):
    report_id: str
    scan_id: str
    templates: List[ComplaintTemplate]
    pdf_download_url: str
    created_at: datetime


class DashboardStatsResponse(BaseModel):
    total_scans: int
    total_fakes_detected: int
    total_seals_verified: int
    reports_generated: int
    top_flagged_domains: List[Dict[str, int]]
    threat_distribution: Dict[str, int]


# --- Telegram Bot Schemas ---

class TelegramScanInput(BaseModel):
    chat_id: int
    message_id: int
    user_id: int
    username: Optional[str] = None
    text_content: Optional[str] = None
    media_file_id: Optional[str] = None
    media_type: Optional[ContentType] = None
    language: str = "hi"


class TelegramVerdictReply(BaseModel):
    chat_id: int
    reply_to_message_id: int
    trust_score: int = Field(..., ge=0, le=100)
    verdict: VerdictStatus
    verdict_emoji: str
    summary_text: str
    inline_keyboard: List[Dict[str, str]]


# --- Standard Error Response ---

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    error: bool = True
    status_code: int
    error_type: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None
```
