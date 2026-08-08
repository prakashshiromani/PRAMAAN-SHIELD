"use client";

import React, { useEffect, useRef, useMemo } from "react";
import { CheckItem } from "./ExplainabilityLedger";

interface TrustScoreDisplayProps {
  score: number;
  verdict: "VERIFIED" | "EXERCISE CAUTION" | "SUSPICIOUS";
  checks: CheckItem[];
  explainabilityEn?: string;
  explainabilityHi?: string;
  language: "hi" | "en";
  scanId?: string;
}

export const TrustScoreDisplay: React.FC<TrustScoreDisplayProps> = ({
  score,
  verdict,
  checks,
  explainabilityEn,
  explainabilityHi,
  language,
  scanId,
}) => {
  // ── Dynamic Certificate Number (unique per scan) ────────────────────────
  const certNumber = useMemo(() => {
    if (scanId) {
      // Use last 6 hex chars of scanId as serial
      const serial = scanId.replace(/-/g, "").slice(-6).toUpperCase();
      const now = new Date();
      return `PS-${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${serial}`;
    }
    // Fallback: timestamp-based unique number
    const now = new Date();
    const serial = String(now.getTime()).slice(-4);
    return `PS-${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${serial}`;
  }, [scanId]);

  // ── Smart certificate title based on detected signals ──────────────────
  const certTitle = useMemo(() => {
    if (verdict === "VERIFIED") {
      return {
        en: "Authenticated Communication",
        hi: "सत्यापित प्रमाण पत्र (Verified Certificate)"
      };
    }
    const labels = checks.map(c => c.label?.toLowerCase() || "");
    const hasTyposquat = labels.some(l => l.includes("typosquat"));
    const hasUrgency = labels.some(l => l.includes("urgency") || l.includes("panic") || l.includes("threat"));
    const hasInvestment = labels.some(l => l.includes("pump") || l.includes("investment") || l.includes("jackpot"));
    const hasHindi = (explainabilityEn || "").toLowerCase().includes("hindi") ||
                    (explainabilityHi || "").length > 0;

    if (verdict === "SUSPICIOUS") {
      if (hasTyposquat && hasUrgency) return { en: "Phishing Typosquat Scam", hi: "टाइपोस्क्वाट फिशिंग धोखाधड़ी" };
      if (hasTyposquat) return { en: "Domain Spoofing Attack", hi: "डोमेन स्पूफिंग हमला" };
      if (hasUrgency) return { en: "Urgency Threat Fraud", hi: "ब्लैकमेल / धमकी धोखाधड़ी" };
      if (hasInvestment) return { en: "Investment Pump-and-Dump Scam", hi: "पंप-एंड-डंप निवेश घोटाला" };
      return { en: "Phishing Fraud Communication", hi: "धोखाधड़ी चेतावनी प्रमाण पत्र" };
    }
    // CAUTION
    return { en: "Cautionary Content Analysis", hi: "सावधानी जांच प्रमाण पत्र" };
  }, [verdict, checks, explainabilityEn, explainabilityHi]);
  const topBandRef = useRef<HTMLCanvasElement>(null);
  const botBandRef = useRef<HTMLCanvasElement>(null);
  const foilSealRef = useRef<HTMLCanvasElement>(null);

  const isVerified = verdict === "VERIFIED";
  const isFraud = verdict === "SUSPICIOUS";

  // Draw Guilloche Bands & Foil Seal
  useEffect(() => {
    // Top & Bottom Guilloche bands
    [topBandRef.current, botBandRef.current].forEach((cv) => {
      if (!cv) return;
      const x = cv.getContext("2d");
      if (!x) return;
      const W = cv.width, H = cv.height;
      x.clearRect(0, 0, W, H);

      const col = isVerified ? "#9A7B2E" : "#116E5F";
      x.strokeStyle = col;
      x.globalAlpha = 0.8;
      x.lineWidth = 0.6;

      for (let L = 0; L < 4; L++) {
        x.beginPath();
        for (let px = 0; px <= W; px += 2) {
          const a = Math.sin(px / 26 + L * 0.5) * 9;
          const b = Math.sin(px / 9 + L * 1.1) * 4.2;
          const y = H / 2 + a + b;
          if (px === 0) x.moveTo(px, y);
          else x.lineTo(px, y);
        }
        x.stroke();
      }
    });

    // Foil Seal Canvas (for Verified result)
    if (isVerified && foilSealRef.current) {
      const cv = foilSealRef.current;
      const x = cv.getContext("2d");
      if (x) {
        const C = 66;
        x.clearRect(0, 0, 132, 132);

        const g = x.createRadialGradient(C, C - 18, 10, C, C, 120);
        g.addColorStop(0, "#E3CA83");
        g.addColorStop(0.5, "#CBA85A");
        g.addColorStop(1, "#9A7B2E");
        x.fillStyle = g;
        x.beginPath();
        x.arc(C, C, 60, 0, 7);
        x.fill();

        x.beginPath();
        x.arc(C, C, 56, 0, 7);
        x.strokeStyle = "#7c611f";
        x.lineWidth = 1.5;
        x.stroke();

        x.fillStyle = "#3a2d0e";
        x.textAlign = "center";
        x.textBaseline = "middle";
        x.font = '700 18px "DM Serif Display", serif';
        x.fillText("प्रमाण", C, C - 6);
        x.font = '600 8px "IBM Plex Mono", monospace';
        x.fillText("✓ AUTHENTIC", C, C + 14);
      }
    }
  }, [isVerified]);

  return (
    <article className={`cert-frame my-6 ${isVerified ? "border-[var(--foil)]" : ""}`}>
      {/* Top Guilloche Security Band */}
      <div className="h-8 relative overflow-hidden border-b border-[var(--line)]">
        <canvas ref={topBandRef} width="900" height="32" className="w-full h-full" />
      </div>

      {/* Certificate Frame Corner Accents */}
      <div className="cert-corner tl"></div>
      <div className="cert-corner tr"></div>
      <div className="cert-corner bl"></div>
      <div className="cert-corner br"></div>

      <div className="p-6 md:p-8 space-y-6">
        {/* Certificate Header */}
        <div className="flex flex-col md:flex-row items-start justify-between gap-4 border-b border-[var(--line)] pb-4">
          <div>
            <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--ink-soft)]">
              Certificate of Analysis · Signal Verification
            </span>
            <h2 className="font-serif-header text-2xl md:text-3xl text-[var(--ink)] mt-1">
              {language === "hi" ? certTitle.hi : certTitle.en}
            </h2>
            <span className="text-xs text-[var(--ink-soft)] font-mono block mt-1">
              {explainabilityEn || explainabilityHi}
            </span>
          </div>

          <div className="text-right font-mono text-[10.5px] text-[var(--ink-soft)] leading-tight flex-shrink-0">
            NO. <b className="text-[var(--ink)]">{certNumber}</b><br />
            VERDICT <b className={isVerified ? "text-[var(--engrave)]" : isFraud ? "text-[var(--stamp)]" : "text-amber-600"}>{verdict}</b><br />
            STATUS <b className="text-[var(--ink)]">CERTIFIED</b>
          </div>
        </div>

        {/* Certificate Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start relative">
          {/* Left Column: Big Score Readout + Rubber Stamp */}
          <div className="lg:col-span-6 relative space-y-4">
            <div className="flex items-baseline gap-4">
              <span
                className="font-serif-header text-7xl md:text-8xl leading-none font-bold tracking-tight"
                style={{ color: isVerified ? "var(--engrave)" : isFraud ? "var(--stamp)" : "var(--amber)" }}
              >
                {score.toString().padStart(2, "0")}
              </span>

              <div className="flex-1 space-y-2">
                <span className="font-mono text-xs text-[var(--ink-soft)] tracking-wider block">
                  TRUST INDEX / 100
                </span>
                <div className="h-2.5 border border-[var(--ink)] relative bg-gray-200 dark:bg-gray-800">
                  <div
                    className="absolute -top-1 w-1.5 h-4"
                    style={{
                      left: `${score}%`,
                      backgroundColor: isVerified ? "var(--engrave)" : isFraud ? "var(--stamp)" : "var(--amber)",
                    }}
                  />
                </div>
              </div>
            </div>

            <div
              className="font-serif-header text-2xl md:text-3xl leading-tight"
              style={{ color: isVerified ? "var(--engrave)" : isFraud ? "var(--stamp)" : "var(--amber)" }}
            >
              {isVerified
                ? "Verified — Signed Entity."
                : isFraud
                ? "Do not trust."
                : "Exercise Caution."}
              <span className="font-hindi text-sm block mt-1 text-[var(--ink-soft)]">
                {isVerified ? "प्रमाणित — पंजीकृत संस्था।" : isFraud ? "भरोसा मत करो।" : "सावधानी बरतें।"}
              </span>
            </div>

            <p className="text-xs text-[var(--ink-soft)] border-l-2 border-[var(--line)] pl-3 py-1 font-body-spectral leading-relaxed">
              {language === "hi"
                ? "यह प्रमाण पत्र क्रिप्टोग्राफिक हस्ताक्षर और 4-लेयर AI डिटेक्शन सिग्नल के आधार पर जारी किया गया है।"
                : "Deterministic registry and seal verification hold absolute authority; AI models contribute advisory liveness signals."}
            </p>

            {/* Rubber Stamp Badge (For Fraud / Suspicious) */}
            {isFraud && (
              <div className="stamp-box transform rotate-[-4deg] mt-4">
                🚫 FRAUD · REJECTED · PRAMAAN · अप्रमाणित
              </div>
            )}

            {/* Real Gold Seal Badge (ONLY when genuine cryptographic seal is verified) */}
            {(() => {
              const sealCheck = checks.find((c) => c.module === "seal");
              if (sealCheck && sealCheck.status === "pass") {
                return (
                  <div className="flex items-center gap-4 border border-[var(--foil)] p-3 bg-[var(--paper-2)] rounded mt-4">
                    <canvas ref={foilSealRef} width="132" height="132" className="w-16 h-16 flex-shrink-0" />
                    <div className="font-mono text-[11px] space-y-1">
                      <span className="text-[var(--engrave)] font-bold block">✓ AUTHENTIC PRAMAAN SEAL</span>
                      <span className="text-[var(--ink-soft)] block">{sealCheck.detail}</span>
                    </div>
                  </div>
                );
              }
              if (sealCheck && sealCheck.status === "fail") {
                return (
                  <div className="flex items-center gap-4 border border-red-500/50 p-3 bg-red-50 dark:bg-red-950/20 rounded mt-4 text-red-600">
                    <span className="text-2xl">🚨</span>
                    <div className="font-mono text-[11px] space-y-1">
                      <span className="font-bold block">⚠️ FORGED / TAMPERED CRYPTOGRAPHIC SEAL</span>
                      <span className="text-xs block">{sealCheck.detail}</span>
                    </div>
                  </div>
                );
              }
              if (isVerified) {
                return (
                  <div className="flex items-center gap-3 border border-[var(--engrave)]/30 p-3 bg-emerald-50/50 dark:bg-emerald-950/10 rounded mt-4">
                    <span className="text-xl text-[var(--engrave)]">🛡️</span>
                    <div className="font-mono text-[11px] space-y-0.5">
                      <span className="text-[var(--engrave)] font-bold block">✓ SEBI REGISTERED ENTITY MATCHED</span>
                      <span className="text-[var(--ink-soft)] text-[10px] block">Verified against official registry database</span>
                    </div>
                  </div>
                );
              }
              return null;
            })()}
          </div>

          {/* Right Column: Findings Ledger */}
          <div className="lg:col-span-6 space-y-3">
            <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-[var(--engrave)] border-b border-[var(--ink)] pb-1 flex justify-between">
              <span>{language === "hi" ? "सुरक्षा जांच ट्रेल" : "Security Trail"}</span>
              <span>{language === "hi" ? "स्कोर प्रभाव" : "Weight Impact"}</span>
            </div>

            <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
              {checks.map((item, idx) => {
                const displayLabel = language === "hi" ? (item.label_hi || item.label) : item.label;
                const displayDetail = language === "hi" ? (item.detail_hi || item.detail) : item.detail;
                const statusColor =
                  item.status === "pass"
                    ? "text-[var(--engrave)]"
                    : item.status === "fail"
                    ? "text-[var(--stamp)]"
                    : item.status === "warn"
                    ? "text-amber-600 dark:text-amber-400"
                    : "text-gray-500 dark:text-gray-400";

                return (
                  <div key={idx} className="flex items-center justify-between border-b border-[var(--line)] pb-2 text-xs">
                    <div className="space-y-0.5 max-w-[75%]">
                      <span className="font-bold text-[var(--ink)] block">{displayLabel}</span>
                      <span className="font-mono text-[10px] text-[var(--ink-soft)] block leading-tight">{displayDetail}</span>
                    </div>
                    <span className={`font-mono font-bold text-xs ${statusColor}`}>
                      {item.contribution === 0 ? "0" : item.contribution > 0 ? `+${item.contribution}` : item.contribution}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* 1-Click Redressal Action Buttons (Shown for Fraud/Suspicious or Caution scans) */}
        {!isVerified && (
          <div className="border-t border-[var(--line)] pt-4 space-y-2">
            <span className="font-mono text-[10px] uppercase tracking-wider text-[var(--stamp)] font-bold block">
              {language === "hi" ? "🚨 त्वरित शिकायत और निवारण (1-Click Redressal Actions):" : "🚨 RECOMMENDED 1-CLICK REDRESSAL ACTIONS:"}
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <a
                href={`/report?scan_id=${scanId || "demo"}`}
                className="cbtn solid-ok py-2.5 px-4 font-mono text-xs text-center font-bold bg-red-700 hover:bg-red-800 border-red-800 text-white flex items-center justify-center gap-2"
              >
                <span>🚨</span>
                <span>{language === "hi" ? "1930 साइबरक्राइम रिपोर्ट दर्ज करें" : "Cybercrime 1930 Helpline Report"}</span>
              </a>
              <a
                href={`/report?scan_id=${scanId || "demo"}`}
                className="cbtn solid-ok py-2.5 px-4 font-mono text-xs text-center font-bold bg-amber-700 hover:bg-amber-800 border-amber-800 text-white flex items-center justify-center gap-2"
              >
                <span>⚖️</span>
                <span>{language === "hi" ? "SEBI SCORES शिकायत ड्राफ्ट करें" : "SEBI SCORES Complaint"}</span>
              </a>
            </div>
          </div>
        )}

        {/* Certificate Footer */}
        <div className="border-t border-[var(--line)] pt-4 flex flex-col sm:flex-row items-center justify-between gap-4 font-mono text-[10.5px] text-[var(--ink-soft)]">
          <div>
            ISSUED BY: <b className="text-[var(--ink)]">PRAMAAN-SHIELD ENGINE</b> · SEBI TECHSPRINT
          </div>
          <div>
            DIGITAL CERTIFICATE · <span className="text-[var(--engrave)] font-semibold">VERIFIABLE PROOF</span>
          </div>
        </div>
      </div>

      {/* Bottom Guilloche Security Band */}
      <div className="h-8 relative overflow-hidden border-t border-[var(--line)]">
        <canvas ref={botBandRef} width="900" height="32" className="w-full h-full" />
      </div>
    </article>
  );
};
