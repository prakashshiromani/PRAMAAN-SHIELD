"use client";

import React, { useState } from "react";
import { TopNav } from "@/components/TopNav";
import { TrustScoreDisplay } from "@/components/TrustScoreDisplay";
import { ScanUploader, ContentType } from "@/components/ScanUploader";
import { ConsentModal } from "@/components/ConsentModal";
import { scanContent, scanFile, scanText } from "@/lib/api";
import { ScanResponse } from "@/lib/types";
import { useLanguage } from "@/lib/LanguageContext";

export default function ScanPage() {
  const { language, setLanguage } = useLanguage();
  const [textContent, setTextContent] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [contentType, setContentType] = useState<ContentType>("text");

  const [scanState, setScanState] = useState<"IDLE" | "SCANNING" | "REVEAL" | "RESULT" | "ERROR">("IDLE");
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  const handleScanSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!textContent && !selectedFile) return;

    try {
      setScanState("SCANNING");
      setErrorMessage("");

      let response: ScanResponse;
      if (contentType === "text") {
        response = await scanText(textContent, language);
      } else if (selectedFile && (contentType === "audio" || contentType === "video" || contentType === "image")) {
        response = await scanFile(selectedFile, contentType, language);
      } else {
        const formData = new FormData();
        formData.append("content_type", contentType);
        formData.append("language", language);
        if (selectedFile) formData.append("file", selectedFile);
        if (textContent) formData.append("text_content", textContent);
        response = await scanContent(formData);
      }

      setScanResult(response);
      setScanState("RESULT");
    } catch (err: any) {
      console.error("Scan error details:", err);
      const backendDetail = err.response?.data?.detail;
      const detailStr = typeof backendDetail === "string" ? backendDetail : (err.message || "Network error");
      setErrorMessage(
        language === "hi"
          ? `स्कैन विश्लेषण त्रुटि: ${detailStr}`
          : `Scan analysis error: ${detailStr}`
      );
      setScanState("ERROR");
    }
  };

  return (
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)] flex flex-col font-body-spectral">
      <TopNav language={language} onLanguageToggle={setLanguage} />

      <main className="flex-1 max-w-4xl w-full mx-auto p-4 md:p-8 space-y-8">
        <div className="text-center space-y-2 border-b border-[var(--line)] pb-6">
          <div className="inline-block px-3 py-1 font-mono text-[10px] uppercase tracking-[0.25em] text-[var(--engrave)] border border-[var(--engrave)]">
            MULTIMEDIA FRAUD & FAKE NOTICE DETECTION
          </div>
          <h1 className="font-serif-header text-3xl md:text-4xl text-[var(--ink)] font-normal">
            {language === "hi" ? "PRAMAAN-SHIELD स्कैन कंसोल" : "PRAMAAN-SHIELD Scan Console"}
          </h1>
          <p className="text-xs text-[var(--ink-soft)] font-mono tracking-wider max-w-xl mx-auto">
            {language === "hi"
              ? "टेक्स्ट, ऑडियो नोट्स, स्क्रीनशॉट या वीडियो में वित्तीय धोखाधड़ी की तुरंत पहचान करें।"
              : "Detect financial fraud, deepfakes, and spoofed domains across media channels."}
          </p>
        </div>

        {/* Modular ScanUploader Component */}
        <div className="cert-frame p-6 md:p-8 bg-[var(--paper-2)]">
          <div className="cert-corner tl"></div>
          <div className="cert-corner tr"></div>
          <div className="cert-corner bl"></div>
          <div className="cert-corner br"></div>

          <ScanUploader
            contentType={contentType}
            onContentTypeChange={setContentType}
            textContent={textContent}
            onTextChange={setTextContent}
            selectedFile={selectedFile}
            onFileSelect={setSelectedFile}
            onSubmit={handleScanSubmit}
            isScanning={scanState === "SCANNING"}
            language={language}
          />
        </div>

        {errorMessage && (
          <div className="stamp-box w-full text-center">
            ⚠️ {errorMessage}
          </div>
        )}

        {/* Modular TrustScoreDisplay Component */}
        {scanResult && scanState === "RESULT" && (
          <TrustScoreDisplay
            score={scanResult.trust_score}
            verdict={scanResult.verdict as any}
            checks={scanResult.checks as any}
            explainabilityEn={scanResult.explainability_en}
            explainabilityHi={scanResult.explainability_hi}
            language={language}
            scanId={scanResult.scan_id}
          />
        )}
      </main>

      <ConsentModal language={language} />

      <footer className="border-t-2 border-[var(--ink)] pt-4 pb-6 px-4 max-w-4xl mx-auto w-full font-mono text-[10.5px] text-[var(--ink-soft)] flex justify-between">
        <span>SEBI TECHSPRINT 2026</span>
        <span>PRAMAAN CERTIFICATE ANALYSIS ENGINE</span>
      </footer>
    </div>
  );
}

