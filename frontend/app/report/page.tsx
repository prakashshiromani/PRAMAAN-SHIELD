"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { TopNav } from "@/components/TopNav";
import { ComplaintTemplate } from "@/components/ComplaintTemplate";
import { generateReport, API_BASE_URL } from "@/lib/api";
import { GenerateReportResponse } from "@/lib/types";
import { useLanguage } from "@/lib/LanguageContext";

function ReportPageContent() {
  const { language: globalLang, setLanguage: setGlobalLang } = useLanguage();
  const searchParams = useSearchParams();
  const queryScanId = searchParams.get("scan_id") || "";

  const [scanId, setScanId] = useState(queryScanId);
  const [reportLanguage, setReportLanguage] = useState<"hi" | "en">(globalLang);
  const [loading, setLoading] = useState(false);
  const [reportResult, setReportResult] = useState<GenerateReportResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const triggerReport = async (targetId: string, langToUse?: "hi" | "en") => {
    if (!targetId.trim()) return;
    const selectedLang = langToUse || reportLanguage;
    try {
      setLoading(true);
      setErrorMsg("");
      setReportResult(null);

      const response = await generateReport({
        scan_id: targetId.trim(),
        target_portals: ["sebi_scores", "cybercrime_1930"],
        language: selectedLang,
      });

      setReportResult(response);
    } catch (err: any) {
      setErrorMsg(
        selectedLang === "hi"
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

  const handleLangChange = (newLang: "hi" | "en") => {
    setReportLanguage(newLang);
    setGlobalLang(newLang);
    if (scanId.trim()) {
      triggerReport(scanId, newLang);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)] flex flex-col font-body-spectral">
      <TopNav language={reportLanguage} onLanguageToggle={handleLangChange} />

      <main className="flex-1 max-w-4xl w-full mx-auto p-4 md:p-8 space-y-8">
        <div className="text-center space-y-2 border-b border-[var(--line)] pb-6">
          <div className="inline-block px-3 py-1 font-mono text-[10px] uppercase tracking-[0.25em] text-[var(--engrave)] border border-[var(--engrave)]">
            SEBI SCORES & 1930 CYBERCRIME DRAFTING ENGINE
          </div>
          <h1 className="font-serif-header text-3xl md:text-4xl text-[var(--ink)] font-normal">
            {reportLanguage === "hi" ? "शिकायत और निवारण पोर्टल" : "Grievance & Redressal Portal"}
          </h1>
          <p className="text-xs text-[var(--ink-soft)] font-mono tracking-wider max-w-xl mx-auto">
            {reportLanguage === "hi"
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

          <form onSubmit={handleGenerateReport} className="space-y-5">
            {/* Language Selector Bar */}
            <div className="space-y-2">
              <label className="cfield-label font-bold text-xs uppercase tracking-wider text-[var(--engrave)]">
                {reportLanguage === "hi" ? "शिकायत ड्राफ्ट की भाषा चुनें (Select Report Language):" : "Select Report Language:"}
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => handleLangChange("hi")}
                  className={`flex-1 py-2.5 px-4 font-mono text-xs uppercase tracking-wider rounded-lg border transition-all flex items-center justify-center gap-2 ${
                    reportLanguage === "hi"
                      ? "bg-[var(--engrave)] text-white font-bold border-[var(--engrave)] shadow"
                      : "bg-[var(--field)] text-[var(--ink-soft)] border-[var(--line-ink)] hover:text-[var(--ink)]"
                  }`}
                >
                  <span>🇮🇳</span>
                  <span>हिंदी (Hindi Draft)</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleLangChange("en")}
                  className={`flex-1 py-2.5 px-4 font-mono text-xs uppercase tracking-wider rounded-lg border transition-all flex items-center justify-center gap-2 ${
                    reportLanguage === "en"
                      ? "bg-[var(--engrave)] text-white font-bold border-[var(--engrave)] shadow"
                      : "bg-[var(--field)] text-[var(--ink-soft)] border-[var(--line-ink)] hover:text-[var(--ink)]"
                  }`}
                >
                  <span>🇬🇧</span>
                  <span>English (English Draft)</span>
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <label className="cfield-label">
                {reportLanguage === "hi" ? "स्कैन आईडी (Scan ID) दर्ज करें:" : "Enter Scan ID from recent analysis:"}
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
                  <span>{reportLanguage === "hi" ? "ड्राफ्ट तैयार हो रहा है..." : "Generating Complaint Drafts..."}</span>
                </>
              ) : (
                <>
                  <span>📝</span>
                  <span>{reportLanguage === "hi" ? "शिकायत ड्राफ्ट तैयार करें" : "GENERATE COMPLAINT DRAFTS"}</span>
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
                language={reportLanguage}
              />
            ))}

            {/* PDF Evidence Package Action */}
            {reportResult.pdf_download_url && (
              <div className="flex justify-center pt-4">
                <a
                  href={`${API_BASE_URL}${reportResult.pdf_download_url}${reportResult.pdf_download_url.includes('?') ? '&' : '?'}lang=${reportLanguage}`}
                  target="_blank"
                  rel="noreferrer"
                  className="cbtn solid-ok py-3.5 px-6 font-mono text-xs tracking-widest font-bold flex items-center gap-2"
                >
                  <span>📄</span>
                  <span>
                    {reportLanguage === "hi"
                      ? "पीडीएफ साक्ष्य पैकेज डाउनलोड करें (PDF Evidence Package)"
                      : "DOWNLOAD PDF EVIDENCE PACKAGE"}
                  </span>
                </a>
              </div>
            )}
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

