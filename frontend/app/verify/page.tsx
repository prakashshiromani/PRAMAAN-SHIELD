"use client";

import React, { useState } from "react";
import { TopNav } from "@/components/TopNav";
import { QRScanner } from "@/components/QRScanner";
import { verifySeal, sha256Hex } from "@/lib/api";
import { SealVerifyResponse } from "@/lib/types";
import { useLanguage } from "@/lib/LanguageContext";

export default function VerifyPage() {
  const { language, setLanguage } = useLanguage();
  const [sealId, setSealId] = useState("");
  const [docText, setDocText] = useState("");
  const [showCameraScanner, setShowCameraScanner] = useState(false);

  const [loading, setLoading] = useState(false);
  const [verifyResult, setVerifyResult] = useState<SealVerifyResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const handleVerify = async (e?: React.FormEvent, targetSealId?: string) => {
    if (e) e.preventDefault();
    const queryId = targetSealId || sealId;
    if (!queryId.trim()) return;

    try {
      setLoading(true);
      setErrorMsg("");
      setVerifyResult(null);

      let contentHash = undefined;
      if (docText.trim()) {
        // Strip appended [PRAMAAN SEAL CERTIFICATE: ...] tag before computing SHA-256 hash
        const cleanText = docText.trim().replace(/\[PRAMAAN\s+SEAL\s+CERTIFICATE:.*?\]/gi, "").trim();
        const hash = await sha256Hex(cleanText);
        contentHash = `sha256:${hash}`;
      }

      const res = await verifySeal(queryId.trim(), undefined, contentHash);
      setVerifyResult(res);
    } catch (err: any) {
      setErrorMsg(
        language === "hi"
          ? "सील सत्यापन विफल: रिकॉर्ड नहीं मिला या अमान्य Signature"
          : "Seal verification failed: Record not found or invalid signature"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleCameraScanSuccess = (decodedData: string) => {
    setShowCameraScanner(false);
    let extractedSealId = decodedData;
    try {
      const parsed = JSON.parse(decodedData);
      if (parsed.seal_id) extractedSealId = parsed.seal_id;
    } catch (e) {
      // String seal_id directly
    }
    setSealId(extractedSealId);
    handleVerify(undefined, extractedSealId);
  };

  return (
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)] flex flex-col font-body-spectral">
      <TopNav language={language} onLanguageToggle={setLanguage} />

      <main className="flex-1 max-w-4xl w-full mx-auto p-4 md:p-8 space-y-8">
        <div className="text-center space-y-2 border-b border-[var(--line)] pb-6">
          <div className="inline-block px-3 py-1 font-mono text-[10px] uppercase tracking-[0.25em] text-[var(--engrave)] border border-[var(--engrave)]">
            SEBI DIGITAL SEAL VERIFICATION REGISTRY
          </div>
          <h1 className="font-serif-header text-3xl md:text-4xl text-[var(--ink)] font-normal">
            {language === "hi" ? "PRAMAAN Seal सत्यापन" : "PRAMAAN Seal Verification"}
          </h1>
          <p className="text-xs text-[var(--ink-soft)] font-mono tracking-wider max-w-xl mx-auto">
            {language === "hi"
              ? "SEBI पंजीकृत संस्थाओं द्वारा जारी आधिकारिक सूचनाओं के डिजिटल हस्ताक्षर और सत्यता की जांच करें।"
              : "Verify ECDSA SECP256R1 signatures and content integrity for SEBI registered communications."}
          </p>
        </div>

        {/* Input & Camera Scan Options */}
        <div className="cert-frame p-6 md:p-8 bg-[var(--paper-2)] space-y-6">
          <div className="cert-corner tl"></div>
          <div className="cert-corner tr"></div>
          <div className="cert-corner bl"></div>
          <div className="cert-corner br"></div>

          <div className="flex items-center justify-between border-b border-[var(--line)] pb-4">
            <span className="font-mono text-xs font-semibold text-[var(--engrave)] uppercase tracking-wider">
              {language === "hi" ? "सत्यापन विधि चुनें" : "SELECT VERIFICATION METHOD"}
            </span>

            <button
              onClick={() => setShowCameraScanner(!showCameraScanner)}
              className="cbtn text-xs"
            >
              <span>📷</span>
              <span>
                {showCameraScanner
                  ? language === "hi" ? "मैनुअल इनपुट पर जाएं" : "Switch to Manual Input"
                  : language === "hi" ? "कैमरा स्कैन शुरू करें" : "Scan via Camera"}
              </span>
            </button>
          </div>

          {showCameraScanner ? (
            <div className="py-4">
              <QRScanner
                language={language}
                onScan={handleCameraScanSuccess}
                onError={(err) => setErrorMsg(err)}
              />
            </div>
          ) : (
            <form onSubmit={handleVerify} className="space-y-4">
              <div className="space-y-2">
                <label className="cfield-label">
                  {language === "hi" ? "PRAMAAN Seal ID प्रविष्ट करें:" : "Enter PRAMAAN Seal ID:"}
                </label>
                <input
                  type="text"
                  value={sealId}
                  onChange={(e) => setSealId(e.target.value)}
                  placeholder="e.g. PRMN-2026-SEBI-A3F2C"
                  className="cfield"
                />
              </div>

              <div className="space-y-2">
                <label className="cfield-label">
                  {language === "hi" ? "दस्तावेज़ टेक्स्ट (वैकल्पिक, सामग्री अखंडता जांचने के लिए):" : "Document Text (Optional, to check content integrity):"}
                </label>
                <textarea
                  rows={3}
                  value={docText}
                  onChange={(e) => setDocText(e.target.value)}
                  placeholder={language === "hi" ? "सर्कुलर या नोटिस का टेक्स्ट यहाँ पेस्ट करें..." : "Paste circular or notice text here..."}
                  className="cfield w-full font-body-spectral"
                />
              </div>

              <button
                type="submit"
                disabled={loading || !sealId.trim()}
                className="cbtn solid-ok w-full py-3.5 font-mono text-xs tracking-widest font-bold"
              >
                {loading ? (
                  <>
                    <div className="h-4 w-4 rounded-full border-2 border-current border-t-transparent animate-spin" />
                    <span>{language === "hi" ? "जांच जारी है..." : "Verifying Cryptographic Proof..."}</span>
                  </>
                ) : (
                  <>
                    <span>🔍</span>
                    <span>{language === "hi" ? "सील सत्यापित करें" : "VERIFY SEAL SIGNATURE"}</span>
                  </>
                )}
              </button>
            </form>
          )}
        </div>

        {/* Error Feedback */}
        {errorMsg && (
          <div className="stamp-box w-full text-center">
            ⚠️ {errorMsg}
          </div>
        )}

        {/* Verification Result Card */}
        {verifyResult && (
          <div className={`cert-frame p-6 md:p-8 bg-[var(--paper-2)] space-y-6 ${
            verifyResult.verdict === "VERIFIED" ? "border-[var(--foil)]" : "border-[var(--stamp)]"
          }`}>
            <div className="cert-corner tl"></div>
            <div className="cert-corner tr"></div>
            <div className="cert-corner bl"></div>
            <div className="cert-corner br"></div>

            <div className="flex items-center justify-between border-b border-[var(--line)] pb-4">
              <div className="flex items-center gap-3">
                <div className={`stamp-box ${verifyResult.verdict === "VERIFIED" ? "ok" : ""}`}>
                  {verifyResult.verdict === "VERIFIED" ? "✓ AUTHENTIC" : "🚫 INVALID / FORGED"}
                </div>
                <div>
                  <h3 className="font-serif-header text-xl text-[var(--ink)]">
                    {verifyResult.verdict === "VERIFIED"
                      ? language === "hi" ? "आधिकारिक रूप से सत्यापित" : "OFFICIALLY VERIFIED SEAL"
                      : language === "hi" ? "अमान्य / फर्जी सील" : "FORGED / INVALID SEAL"}
                  </h3>
                  <span className="text-xs font-mono text-[var(--ink-soft)] block">
                    ID: {verifyResult.seal_id}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              <div className="p-3 bg-[var(--paper)] border border-[var(--line-ink)] rounded">
                <span className="text-[var(--ink-soft)] block text-[10px] uppercase">Entity Name:</span>
                <span className="text-[var(--ink)] font-bold">{verifyResult.entity_name || "N/A"}</span>
              </div>

              <div className="p-3 bg-[var(--paper)] border border-[var(--line-ink)] rounded">
                <span className="text-[var(--ink-soft)] block text-[10px] uppercase">Registration Number:</span>
                <span className="text-[var(--engrave)] font-bold">{verifyResult.registration_number || "N/A"}</span>
              </div>

              <div className="p-3 bg-[var(--paper)] border border-[var(--line-ink)] rounded">
                <span className="text-[var(--ink-soft)] block text-[10px] uppercase">Signed Timestamp:</span>
                <span className="text-[var(--ink)]">{verifyResult.signed_at || "N/A"}</span>
              </div>

              <div className="p-3 bg-[var(--paper)] border border-[var(--line-ink)] rounded">
                <span className="text-[var(--ink-soft)] block text-[10px] uppercase">Content SHA-256:</span>
                <span className="text-[var(--engrave)] truncate block">{verifyResult.content_hash || "Intact"}</span>
              </div>

              <div className="p-3 bg-[var(--paper)] border border-[var(--line-ink)] rounded col-span-2">
                <span className="text-[var(--ink-soft)] block text-[10px] uppercase">Content Verification Status:</span>
                <span className={`font-bold ${verifyResult.verdict === "TAMPERED" ? "text-[var(--stamp)]" : (verifyResult.content_match ? "text-[var(--engrave)]" : "text-[var(--ink)]")}`}>
                  {verifyResult.verdict === "TAMPERED"
                    ? (language === "hi" ? "🚫 सामग्री बदली गई है (TAMPERED) — छेड़छाड़!" : "🚫 Content Modified (TAMPERED) — Spoofed/Altered!")
                    : (verifyResult.content_match
                        ? (language === "hi" ? "✅ सामग्री अखंडित है — हस्ताक्षर के बाद कोई बदलाव नहीं किया गया।" : "✅ Content Intact — Matches the registered signature.")
                        : (language === "hi" ? "🔍 मूल सील सत्यापित (सामग्री टेक्स्ट प्रदान नहीं किया गया)" : "🔍 Seal Valid (No document text presented for content match)"))}
                </span>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t-2 border-[var(--ink)] pt-4 pb-6 px-4 max-w-4xl mx-auto w-full font-mono text-[10.5px] text-[var(--ink-soft)] flex justify-between">
        <span>SEBI TECHSPRINT 2026</span>
        <span>ECDSA SECP256R1 VERIFICATION ENGINE</span>
      </footer>
    </div>
  );
}

