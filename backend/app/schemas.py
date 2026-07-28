"""
PRAMAAN-SHIELD — Pydantic Schemas and Enums
File: backend/app/schemas.py

Single source of truth for all API contracts, internal DTOs, and system Enums.
Derived from Backend SCHEMA.md §3.1–§3.8 and §7.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── Core Enums ─────────────────────────────────────────────────────────────

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
    TAMPERED = "TAMPERED"    # Signature valid but content modified
    FORGED = "FORGED"        # Signature not from registered entity key
    REVOKED = "REVOKED"      # Seal explicitly revoked by issuer
    EXPIRED = "EXPIRED"      # Outside not_before / not_after window
    UNVERIFIED = "UNVERIFIED" # No Seal found / entity not in registry


# ── Shared Models ──────────────────────────────────────────────────────────

class CheckResult(BaseModel):
    module: str           # "baseline" | "hash" | "phishing" | "voice" | "video" | "domain" | "registry" | "seal" | "ai"
    status: CheckStatus
    label: str            # Human-readable summary e.g. "Known Fake Detected"
    detail: str           # Technical reason e.g. "Flagged Jan 15, detected 847 times"
    contribution: int     # Score impact: negative=deduction, positive=boost
    label_hi: Optional[str] = None    # Hindi twin of `label`
    detail_hi: Optional[str] = None   # Hindi twin of `detail`


class ActionButton(BaseModel):
    id: str
    label: str
    action_type: str      # "copy" | "download" | "navigate"
    url: Optional[str] = None


# ── /api/scan Models ───────────────────────────────────────────────────────

class ScanTextRequest(BaseModel):
    content_type: ContentType = ContentType.TEXT
    text_content: str = Field(..., max_length=10000)
    language: str = Field("hi", pattern="^(hi|en)$")


class ScanInput(BaseModel):
    """Internal unified model after request parsing."""
    content_type: ContentType
    text_content: Optional[str] = None
    media_path: Optional[str] = None
    media_original_name: Optional[str] = None
    language: str = "hi"


class ScanResponse(BaseModel):
    scan_id: str
    content_type: ContentType
    trust_score: int = Field(..., ge=0, le=100)
    verdict: VerdictStatus
    verdict_label_hi: str
    verdict_label_en: str
    checks: List[CheckResult]
    explainability_en: Optional[str] = None
    explainability_hi: Optional[str] = None
    ai_generated_probability: Optional[float] = None
    typosquat_detected: Optional[str] = None
    evidence_summary: str
    recommended_actions: List[ActionButton]
    created_at: datetime


# ── /api/verify Models ─────────────────────────────────────────────────────

class VerifySealRequest(BaseModel):
    seal_id: Optional[str] = None
    qr_payload: Optional[str] = None
    presented_content_hash: Optional[str] = Field(
        None,
        description="SHA-256 hex of the document the user is currently looking at"
    )


class VerifySealResponse(BaseModel):
    verdict: SealVerdict
    is_valid: bool
    seal_id: Optional[str] = None
    entity_name: Optional[str] = None
    registration_number: Optional[str] = None
    signer_entity_name: Optional[str] = None
    signer_registration_number: Optional[str] = None
    signed_at: Optional[str] = None
    not_before: Optional[str] = None
    not_after: Optional[str] = None
    content_match: bool = False
    message_hi: str
    message_en: str


# ── /api/seal/sign Models ──────────────────────────────────────────────────

class IssueSealRequest(BaseModel):
    # entity_name & reg_no come from authenticated session (SECURITY.md §5.1)
    content_hash: str = Field(..., pattern=r"^sha256:[a-fA-F0-9]{64}$")
    content_type: str = Field(..., examples=["circular", "press_release", "advisory", "video_statement"])
    content_title: str = Field(..., max_length=200)
    validity_days: int = Field(90, ge=1, le=365)


class IssueSealResponse(BaseModel):
    seal_id: str
    entity_name: str
    registration_number: str
    content_hash: str
    signature: str
    not_before: datetime
    not_after: datetime
    qr_data_base64: str     # Base64 encoded QR payload JSON
    qr_image_url: str       # URL to PNG QR code image


# ── /api/report Models ─────────────────────────────────────────────────────

class GenerateReportRequest(BaseModel):
    scan_id: str
    target_portals: List[str] = Field(
        ["sebi_scores", "cybercrime_1930"],
        description="One or both targets"
    )
    language: str = Field("hi", pattern="^(hi|en)$")


class ComplaintTemplate(BaseModel):
    portal_id: str           # "sebi_scores" | "cybercrime_1930"
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


# ── Dashboard & Telegram Models ────────────────────────────────────────────

class DashboardStatsResponse(BaseModel):
    total_scans: int
    total_fakes_detected: int
    total_seals_verified: int
    reports_generated: int
    top_flagged_domains: List[Dict[str, Any]]
    threat_distribution: Dict[str, int]


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
    verdict_emoji: str       # "🔴" | "🟡" | "🟢"
    summary_text: str
    inline_keyboard: List[Dict[str, str]]


# ── Error Response Models ──────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    error: bool = True
    status_code: int
    error_type: str      # "validation_error" | "not_found" | "rate_limited" | "internal_error"
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None
