"use client";

import React, { useState, useEffect } from "react";
import { TopNav } from "@/components/TopNav";
import { issueSeal, sha256Hex } from "@/lib/api";
import { IssueSealResponse } from "@/lib/types";
import { useLanguage } from "@/lib/LanguageContext";

export default function SealPortalPage() {
  const { language, setLanguage } = useLanguage();
  const [title, setTitle] = useState("Zerodha Official Security Advisory");
  const [messageText, setMessageText] = useState(
    "Official Advisory from Zerodha Broking Limited (SEBI Reg: INZ000031633). Please never share your password, OTP, or PIN with anyone. Always verify trading activity directly on zerodha.com or kite.zerodha.com."
  );
  const [contentHash, setContentHash] = useState("");
  const [loading, setLoading] = useState(false);
  const [issuedSeal, setIssuedSeal] = useState<IssueSealResponse | null>(null);
  const [copied, setCopied] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (messageText.trim()) {
      sha256Hex(messageText.trim()).then((h) => setContentHash(`sha256:${h}`));
    } else {
      setContentHash("");
    }
  }, [messageText]);

  const handleIssue = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !contentHash) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await issueSeal({
        content_hash: contentHash.startsWith("sha256:") ? contentHash : `sha256:${contentHash}`,
        content_type: "advisory",
        content_title: title,
        validity_days: 90,
      });
      setIssuedSeal(res);
    } catch (err: any) {
      console.error(err);
      const detail = err?.response?.data?.detail || err?.message || "Unknown error. Check backend server.";
      setErrorMsg(`Seal signing failed: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  const signedMessage = issuedSeal
    ? `${messageText.trim()}\n\n[PRAMAAN SEAL CERTIFICATE: ${issuedSeal.seal_id}]`
    : "";

  const handleCopy = () => {
    if (!signedMessage) return;
    navigator.clipboard.writeText(signedMessage);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)] font-body-spectral flex flex-col">
      <TopNav language={language} onLanguageToggle={setLanguage} />

      <main className="flex-1 max-w-3xl w-full mx-auto p-4 md:p-8 space-y-8">
        <div className="text-center space-y-2 border-b border-[var(--line)] pb-6">
          <div className="inline-block px-3 py-1 font-mono text-[10px] uppercase tracking-[0.25em] text-[var(--engrave)] border border-[var(--engrave)]">
            SEBI REGISTERED ENTITY PORTAL
          </div>
          <h1 className="font-serif-header text-3xl md:text-4xl text-[var(--ink)] font-normal">
            {language === "hi" ? "SEBI संस्था डिजिटल सील पोर्टल" : "Intermediary PRAMAAN Seal Signing Portal"}
          </h1>
          <p className="text-xs text-[var(--ink-soft)] font-mono tracking-wider uppercase">
            Issue SECP256R1 Cryptographically Signed Official Communications
          </p>
        </div>

        <form onSubmit={handleIssue} className="cert-frame p-6 md:p-8 bg-[var(--paper-2)] space-y-6">
          <div className="cert-corner tl"></div>
          <div className="cert-corner tr"></div>
          <div className="cert-corner bl"></div>
          <div className="cert-corner br"></div>

          <div className="space-y-2">
            <label className="cfield-label font-bold">1. Communication Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Official Advisory from Zerodha Broking Limited"
              className="cfield"
            />
          </div>

          <div className="space-y-2">
            <label className="cfield-label font-bold">2. Official Message / Advisory Text</label>
            <textarea
              rows={4}
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              placeholder="Paste official advisory text here..."
              className="cfield w-full"
            />
          </div>

          <div className="space-y-2">
            <label className="cfield-label font-bold text-[11px] text-[var(--engrave)]">
              Auto-Calculated Document SHA-256 Hash
            </label>
            <input
              type="text"
              readOnly
              value={contentHash}
              className="cfield bg-[var(--paper)] font-mono text-xs text-[var(--ink-soft)]"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !title || !contentHash}
            className="cbtn solid-ok w-full py-3.5 font-mono text-xs tracking-widest font-bold"
          >
            {loading ? "Signing Payload & Generating Seal..." : "Sign Document & Generate PRAMAAN Seal"}
          </button>

          {errorMsg && (
            <div className="p-3 bg-red-50 border border-red-300 rounded text-red-700 text-xs font-mono">
              ⚠ {errorMsg}
            </div>
          )}
        </form>

        {issuedSeal && (
          <div className="cert-frame p-6 bg-[var(--paper-2)] border-[var(--foil)] space-y-6 text-center flex flex-col items-center">
            <div className="cert-corner tl" style={{ borderColor: "var(--foil)" }}></div>
            <div className="cert-corner tr" style={{ borderColor: "var(--foil)" }}></div>
            <div className="cert-corner bl" style={{ borderColor: "var(--foil)" }}></div>
            <div className="cert-corner br" style={{ borderColor: "var(--foil)" }}></div>

            <div className="stamp-box ok font-bold text-sm">
              ✓ PRAMAAN SEAL ISSUED & CRYPTOGRAPHICALLY RECORDED
            </div>

            <div className="p-4 bg-white rounded shadow-inner border border-[var(--line)]">
              <img
                src={`data:image/png;base64,${issuedSeal.qr_data_base64}`}
                alt="PRAMAAN Seal QR Code"
                className="w-48 h-48"
              />
            </div>

            <div className="text-xs font-mono space-y-1 text-[var(--ink)]">
              <p>SEAL ID: <span className="text-[var(--engrave)] font-bold">{issuedSeal.seal_id}</span></p>
              <p>ISSUER: {issuedSeal.entity_name} ({issuedSeal.registration_number})</p>
            </div>

            <div className="w-full text-left space-y-2 border-t border-[var(--line)] pt-4">
              <label className="cfield-label font-bold text-xs">
                Copy Cryptographically Signed Message (Paste into Scan Console for 100/100 VERIFIED Score):
              </label>
              <textarea
                readOnly
                rows={5}
                value={signedMessage}
                className="cfield w-full font-mono text-xs bg-[var(--paper)] text-[var(--ink)]"
              />
              <button
                type="button"
                onClick={handleCopy}
                className="cbtn solid-ok w-full py-2.5 font-mono text-xs tracking-wider"
              >
                {copied ? "✓ COPIED TO CLIPBOARD!" : "📋 COPY SIGNED TEXT FOR SCAN CONSOLE"}
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t-2 border-[var(--ink)] pt-4 pb-6 px-4 max-w-3xl mx-auto w-full font-mono text-[10.5px] text-[var(--ink-soft)] flex justify-between">
        <span>SEBI TECHSPRINT 2026</span>
        <span>DIGITAL SEAL ISSUANCE ENGINE</span>
      </footer>
    </div>
  );
}
