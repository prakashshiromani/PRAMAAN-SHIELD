"use client";

import React, { useState } from "react";

interface ComplaintTemplateProps {
  portalName: string;
  portalCode: "sebi_scores" | "cybercrime_1930";
  subject: string;
  bodyText: string;
  evidenceSummary: string;
  language: "hi" | "en";
}

export const ComplaintTemplate: React.FC<ComplaintTemplateProps> = ({
  portalName,
  portalCode,
  subject,
  bodyText,
  evidenceSummary,
  language,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const fullText = `SUBJECT: ${subject}\n\nEVIDENCE SUMMARY:\n${evidenceSummary}\n\nCOMPLAINT BODY:\n${bodyText}`;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="cert-frame p-6 bg-[var(--paper-2)] space-y-4">
      <div className="cert-corner tl"></div>
      <div className="cert-corner tr"></div>
      <div className="cert-corner bl"></div>
      <div className="cert-corner br"></div>

      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-[var(--line)] pb-4">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 border border-[var(--ink)] bg-[var(--paper)] flex items-center justify-center text-lg">
            {portalCode === "sebi_scores" ? "🏛️" : "🚨"}
          </div>
          <div>
            <h3 className="font-serif-header text-base text-[var(--ink)]">{portalName}</h3>
            <span className="text-[10px] text-[var(--engrave)] font-mono uppercase tracking-wider block">
              {portalCode === "sebi_scores" ? "SEBI SCORES Portal Format" : "1930 National Cybercrime Portal"}
            </span>
          </div>
        </div>

        <button
          onClick={handleCopy}
          className="cbtn text-xs"
        >
          <span>{copied ? "✓ Copied" : "📋 Copy Draft"}</span>
        </button>
      </div>

      {/* Subject Line */}
      <div className="space-y-1">
        <span className="text-[10px] uppercase tracking-wider text-[var(--ink-soft)] font-mono">
          {language === "hi" ? "विषय (Subject):" : "SUBJECT LINE:"}
        </span>
        <p className="text-xs font-mono text-[var(--ink)] bg-[var(--paper)] p-3 border border-[var(--line-ink)] rounded">
          {subject}
        </p>
      </div>

      {/* Body Content */}
      <div className="space-y-1">
        <span className="text-[10px] uppercase tracking-wider text-[var(--ink-soft)] font-mono">
          {language === "hi" ? "शिकायत का विवरण (Complaint Draft):" : "PRE-FILLED COMPLAINT TEXT:"}
        </span>
        <div className="text-xs text-[var(--ink)] bg-[var(--paper)] p-4 border border-[var(--line-ink)] rounded whitespace-pre-wrap leading-relaxed max-h-60 overflow-y-auto font-mono">
          {bodyText}
        </div>
      </div>
    </div>
  );
};

