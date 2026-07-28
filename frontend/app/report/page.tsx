"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { TopNav } from "@/components/TopNav";
import { ComplaintTemplate } from "@/components/ComplaintTemplate";
import { generateReport } from "@/lib/api";
import { GenerateReportResponse } from "@/lib/types";
import { useLanguage } from "@/lib/LanguageContext";

function ReportPageContent() {
  const { language, setLanguage } = useLanguage();
  const searchParams = useSearchParams();
  const queryScanId = searchParams.get("scan_id") || "";

  const [scanId, setScanId] = useState(queryScanId);
  const [loading, setLoading] = useState(false);
  const [reportResult, setReportResult] = useState<GenerateReportResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const triggerReport = async (targetId: string) => {
    if (!targetId.trim()) return;
    try {
      setLoading(true);
      setErrorMsg("");
      setReportResult(null);

      const response = await generateReport({
        scan_id: targetId.trim(),
        target_portals: ["sebi_scores", "cybercrime_1930"],
        language,
      });

      setReportResult(response);
    } catch (err: any) {
      setErrorMsg(
        language === "hi"
          ? "रिपोर्ट जनरेशन विफल: अमान्य Scan ID या नेटवर्क त्रुटि"
          : "Report generation failed: Invalid Scan ID or network error"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (queryScanId) {
      setScanId(queryScanId);
      triggerReport(queryScanId);
    }
  }, [queryScanId]);

  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    triggerReport(scanId);
  };

  return (
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)] flex flex-col font-body-spectral">
      <TopNav language={language} onLanguageToggle={setLanguage} />

      <main className="flex-1 max-w-4xl w-full mx-auto p-4 md:p-8 space-y-8">
        <div className="text-center space-y-2 border-b border-[var(--line)] pb-6">
          <div className="inline-block px-3 py-1 font-mono text-[10px] uppercase tracking-[0.25em] text-[var(--engrave)] border border-[var(--engrave)]">
            SEBI SCORES & 1930 CYBERCRIME DRAFTING ENGINE
          </div>
          <h1 className="font-serif-header text-3xl md:text-4xl text-[var(--ink)] font-normal">
            {language === "hi" ? "शिकायत और निवारण पोर्टल" : "Grievance & Redressal Portal"}
          </h1>
          <p className="text-xs text-[var(--ink-soft)] font-mono tracking-wider max-w-xl mx-auto">
            {language === "hi"
              ? "SEBI SCORES और 1930 साइबरक्राइम पोर्टल के लिए पहले से भरे हुए रिपोर्ट ड्राफ्ट तैयार करें।"
              : "Generate 1-click pre-filled complaint drafts and evidence packages for SEBI SCORES & 1930."}
          </p>
        </div>

        {/* Input Scan ID Form */}
        <div className="cert-frame p-6 md:p-8 bg-[var(--paper-2)] space-y-6">
          <div className="cert-corner tl"></div>
          <div className="cert-corner tr"></div>
          <div className="cert-corner bl"></div>
          <div className="cert-corner br"></div>

          <form onSubmit={handleGenerateReport} className="space-y-4">
            <div className="space-y-2">
              <label className="cfield-label">
                {language === "hi" ? "स्कैन आईडी (Scan ID) दर्ज करें:" : "Enter Scan ID from recent analysis:"}
              </label>
              <input
                type="text"
                value={scanId}
                onChange={(e) => setScanId(e.target.value)}
                placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000"
                className="cfield"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !scanId.trim()}
              className="cbtn solid-ok w-full py-3.5 font-mono text-xs tracking-widest font-bold"
            >
              {loading ? (
                <>
                  <div className="h-4 w-4 rounded-full border-2 border-current border-t-transparent animate-spin" />
                  <span>{language === "hi" ? "ड्राफ्ट तैयार हो रहा है..." : "Generating Complaint Drafts..."}</span>
                </>
              ) : (
                <>
                  <span>📝</span>
                  <span>{language === "hi" ? "शिकायत ड्राफ्ट तैयार करें" : "GENERATE COMPLAINT DRAFTS"}</span>
                </>
              )}
            </button>
          </form>
        </div>

        {errorMsg && (
          <div className="stamp-box w-full text-center">
            ⚠️ {errorMsg}
          </div>
        )}

        {/* Complaint Cards Grid */}
        {reportResult && reportResult.templates && (
          <div className="space-y-6">
            {reportResult.templates.map((tpl, idx) => (
              <ComplaintTemplate
                key={idx}
                portalName={tpl.portal_name}
                portalCode={(tpl.portal_code as any) || (idx === 0 ? "sebi_scores" : "cybercrime_1930")}
                subject={tpl.subject}
                bodyText={tpl.body_text}
                evidenceSummary={tpl.evidence_summary || tpl.subject}
                language={language}
              />
            ))}

            {/* PDF Evidence Package Action */}
            <div className="flex justify-center pt-4">
              <a
                href={`http://localhost:8000/api/report/${reportResult.report_id}/pdf`}
                target="_blank"
                rel="noreferrer"
                className="cbtn solid-ok py-3.5 px-6 font-mono text-xs tracking-widest font-bold flex items-center gap-2"
              >
                <span>📄</span>
                <span>
                  {language === "hi"
                    ? "पीडीएफ साक्ष्य पैकेज डाउनलोड करें (PDF Evidence Package)"
                    : "DOWNLOAD PDF EVIDENCE PACKAGE"}
                </span>
              </a>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t-2 border-[var(--ink)] pt-4 pb-6 px-4 max-w-4xl mx-auto w-full font-mono text-[10.5px] text-[var(--ink-soft)] flex justify-between">
        <span>SEBI TECHSPRINT 2026</span>
        <span>AUTOMATED COMPLAINT DRAFTING ENGINE</span>
      </footer>
    </div>
  );
}

export default function ReportPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[var(--paper)] flex items-center justify-center font-mono text-xs text-[var(--ink-soft)]">Loading Redressal Portal...</div>}>
      <ReportPageContent />
    </Suspense>
  );
}

