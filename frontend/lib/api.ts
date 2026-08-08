import axios from 'axios';
import type {
  ScanResponse,
  VerifySealResponse,
  DashboardStatsResponse,
  ReportSubmitResponse,
  SealIssueResponse,
} from './types';

export const API_BASE_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'https://pramaan-shield-backend.onrender.com';

/** SHA-256 hex digest via Web Crypto (shared by verify & seal-portal pages). */
export async function sha256Hex(message: string): Promise<string> {
  const msgUint8 = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest("SHA-256", msgUint8);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

// For browser: use '' (same-origin via Next.js rewrites) to avoid CORS.
// For server-side / local dev: use the full backend URL.
const isBrowser = typeof window !== 'undefined';
const axiosBaseURL = isBrowser ? '' : API_BASE_URL;

const api = axios.create({
  baseURL: axiosBaseURL,
  timeout: 120_000,
});

/* ────────────────────────────────────────────────────
   PILLAR A — DETECT
──────────────────────────────────────────────────── */

/** Scan plain text content (phishing, URL, social) */
export async function scanText(
  textContent: string,
  language: 'hi' | 'en' = 'hi'
): Promise<ScanResponse> {
  const formData = new FormData();
  formData.append('content_type', 'text');
  formData.append('text_content', textContent);
  formData.append('language', language);

  const { data } = await api.post<ScanResponse>('/api/scan', formData, {
    timeout: 120_000,
  });
  return data;
}

/** Scan file — audio (voice clone), video (deepfake), image (perceptual hash) */
export async function scanFile(
  file: File,
  contentType: 'audio' | 'video' | 'image',
  language: 'hi' | 'en' = 'hi'
): Promise<ScanResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('content_type', contentType);
  formData.append('language', language);

  const { data } = await api.post<ScanResponse>('/api/scan', formData, {
    timeout: 120_000,
  });
  return data;
}

/** Scan email (.eml) — SPF/DKIM/DMARC header analysis + body phishing */
export async function scanEmail(
  file: File,
  language: 'hi' | 'en' = 'hi'
): Promise<ScanResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('content_type', 'email');
  formData.append('language', language);

  const { data } = await api.post<ScanResponse>('/api/scan', formData, {
    timeout: 120_000,
  });
  return data;
}

/** Scan content via FormData or hash lookup string */
export async function scanContent(
  input: FormData | string,
  language: 'hi' | 'en' = 'hi'
): Promise<ScanResponse> {
  if (input instanceof FormData) {
    const { data } = await api.post<ScanResponse>('/api/scan', input, {
      timeout: 90_000,
    });
    return data;
  }
  const formData = new FormData();
  formData.append('content_type', 'hash');
  formData.append('text_content', input);
  formData.append('language', language);

  const { data } = await api.post<ScanResponse>('/api/scan', formData, {
    headers: { 'Content-Type': undefined },
  });
  return data;
}

/* ────────────────────────────────────────────────────
   PILLAR B — AUTHENTICATE (PRAMAAN Seal)
──────────────────────────────────────────────────── */

/** Verify a PRAMAAN Seal by ID or QR payload and optional presented content hash */
export async function verifySeal(
  sealIdOrPayload: string | { seal_id: string; qr_payload?: string },
  qrPayload?: string,
  presentedContentHash?: string
): Promise<VerifySealResponse> {
  const seal_id = typeof sealIdOrPayload === 'string' ? sealIdOrPayload : sealIdOrPayload.seal_id;
  const qr_payload = typeof sealIdOrPayload === 'string' ? qrPayload : sealIdOrPayload.qr_payload;
  const { data } = await api.post<VerifySealResponse>('/api/verify', {
    seal_id,
    qr_payload,
    presented_content_hash: presentedContentHash,
  });
  return data;
}

/** Issue a new PRAMAAN Seal (SEBI/regulator use) */
export async function issueSeal(payload: {
  content_hash?: string;
  content_type?: string;
  content_title?: string;
  validity_days?: number;
}): Promise<SealIssueResponse> {
  // Match backend IssueSealRequest schema exactly:
  // content_hash: sha256:<hex64>  (required)
  // content_type: circular / advisory etc (required)
  // content_title: string (required)
  // validity_days: int 1–365 (optional, default 90)
  const body = {
    content_hash: payload.content_hash || '',
    content_type: payload.content_type || 'advisory',
    content_title: payload.content_title || 'Official Communication',
    validity_days: payload.validity_days || 90,
  };

  // Issuer key never enters the browser bundle. It lives server-side in the
  // Next.js route handler /app/api/issue-seal/route.ts (SEAL_API_KEY env) which
  // proxies to the backend with the X-API-Key header. Same-origin fetch — do NOT
  // use the axios instance (its baseURL is the backend, not the Next server).
  const res = await fetch('/api/issue-seal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.detail || `Seal issuance failed (${res.status})`);
  }
  return data as SealIssueResponse;
}

/* ────────────────────────────────────────────────────
   PILLAR C — REDRESSAL
──────────────────────────────────────────────────── */

/** Submit a fraud report → auto-populates SCORES + 1930 packets */
export async function generateReport(payload: {
  scan_id: string;
  complainant_name?: string;
  contact_email?: string;
  contact_phone?: string;
  incident_date?: string;
  additional_context?: string;
  consent_given?: boolean;
  target_portals?: string[];
  language?: 'hi' | 'en';
}): Promise<ReportSubmitResponse> {
  const { data } = await api.post<ReportSubmitResponse>('/api/report', payload);
  return data;
}

/* ────────────────────────────────────────────────────
   DASHBOARD / HEALTH
   ───────────────────────────────────────────────────── */

export async function getDashboardStats(): Promise<DashboardStatsResponse> {
  const { data } = await api.get<DashboardStatsResponse>('/api/dashboard/stats');
  return data;
}

export default api;
