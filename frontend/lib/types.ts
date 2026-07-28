export type ContentType = 'text' | 'audio' | 'video' | 'image';

export type VerdictStatus = 'VERIFIED' | 'EXERCISE CAUTION' | 'SUSPICIOUS';

export type CheckStatus = 'pass' | 'fail' | 'warn' | 'skip';

export type SealVerdict =
  | 'VERIFIED'
  | 'TAMPERED'
  | 'FORGED'
  | 'REVOKED'
  | 'EXPIRED'
  | 'UNVERIFIED';

export interface CheckResult {
  module: string;
  status: CheckStatus;
  label: string;
  detail: string;
  contribution: number;
  label_hi?: string;
  detail_hi?: string;
}

export interface ActionButton {
  id: string;
  label: string;
  action_type: 'copy' | 'download' | 'navigate';
  url?: string;
}

export interface ScanResponse {
  scan_id: string;
  content_type: ContentType;
  trust_score: number;
  verdict: VerdictStatus;
  verdict_label_hi: string;
  verdict_label_en: string;
  checks: CheckResult[];
  explainability_en?: string;
  explainability_hi?: string;
  ai_generated_probability?: number;
  typosquat_detected?: string;
  evidence_summary: string;
  recommended_actions: ActionButton[];
  created_at: string;
}

export interface VerifySealResponse {
  seal_id?: string;
  verdict: SealVerdict;
  is_valid: boolean;
  signer_entity_name?: string;
  signer_registration_number?: string;
  entity_name?: string;
  registration_number?: string;
  content_hash?: string;
  signed_at?: string;
  not_before?: string;
  not_after?: string;
  content_match: boolean;
  message_hi: string;
  message_en: string;
}

export type SealVerifyResponse = VerifySealResponse;

export interface DashboardStatsResponse {
  total_scans: number;
  total_fakes_detected: number;
  total_seals_verified: number;
  reports_generated: number;
  top_flagged_domains: Record<string, number>[];
  threat_distribution: Record<string, number>;
}

export interface ComplaintTemplate {
  portal_name: string;
  portal_code?: string;
  subject: string;
  body_text: string;
  evidence_summary?: string;
}

export interface GenerateReportResponse {
  report_id: string;
  status: 'SUBMITTED' | 'PROCESSING' | 'COMPLETED';
  templates: ComplaintTemplate[];
  scores_packet_url?: string;
  cybercrime_1930_url?: string;
  created_at: string;
}

export type ReportSubmitResponse = GenerateReportResponse;

export interface SealIssueResponse {
  seal_id: string;
  seal_token?: string;
  qr_data?: string;
  qr_data_base64?: string;
  qr_image_url?: string;
  issued_at?: string;
  not_after?: string;
  issuer_did?: string;
  entity_name?: string;
  registration_number?: string;
  content_sha256?: string;
  content_hash?: string;
}

export type IssueSealResponse = SealIssueResponse;

export interface ErrorResponse {
  error: true;
  status_code: number;
  error_type: string;
  message: string;
  request_id?: string;
}

export function getTrustScoreColor(score: number): string {
  if (score >= 70) return '#22c55e';
  if (score >= 30) return '#eab308';
  return '#ef4444';
}

export function getTrustScoreEmoji(score: number): string {
  if (score >= 70) return '🟢';
  if (score >= 30) return '🟡';
  return '🔴';
}
