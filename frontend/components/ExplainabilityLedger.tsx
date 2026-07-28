"use client";

import React from "react";

export interface CheckItem {
  module: string;
  status: "pass" | "fail" | "warn" | "skip";
  label: string;
  detail: string;
  contribution: number;
  label_hi?: string;
  detail_hi?: string;
}

interface LedgerProps {
  checks: CheckItem[];
  language: "hi" | "en";
}

export const ExplainabilityLedger: React.FC<LedgerProps> = ({ checks, language }) => {
  return (
    <div className="space-y-2">
      <h4 className="text-xs font-mono uppercase tracking-wider text-[var(--engrave)] font-bold mb-3">
        {language === "hi" ? "सुरक्षा जांच खाता (Explainability Ledger)" : "SECURITY CHECKS LEDGER"}
      </h4>
      {checks.map((check, idx) => {
        const isPass = check.status === "pass";
        const isFail = check.status === "fail";
        const isWarn = check.status === "warn";

        const badgeColor = isPass
          ? "bg-[var(--paper)] text-[var(--engrave)] border-[var(--engrave)]"
          : isFail
          ? "bg-[var(--paper)] text-[var(--stamp)] border-[var(--stamp)]"
          : isWarn
          ? "bg-[var(--paper)] text-[var(--amber)] border-[var(--amber)]"
          : "bg-[var(--paper)] text-[var(--ink-soft)] border-[var(--line-ink)]";

        const icon = isPass ? "✓" : isFail ? "✕" : isWarn ? "⚠" : "○";

        return (
          <div
            key={idx}
            className={`p-3 rounded bg-[var(--paper)] border border-[var(--line-ink)] flex items-start justify-between gap-3 text-xs font-mono transition-all ${
              isFail ? "border-l-4 border-l-[var(--stamp)]" : isWarn ? "border-l-4 border-l-[var(--amber)]" : isPass ? "border-l-4 border-l-[var(--engrave)]" : ""
            }`}
          >
            <div className="flex items-start gap-2.5">
              <span className={`h-5 w-5 rounded-full border flex items-center justify-center font-bold text-[10px] ${badgeColor}`}>
                {icon}
              </span>
              <div>
                <p className="font-bold text-[var(--ink)]">{check.label}</p>
                <p className="text-[11px] text-[var(--ink-soft)] leading-normal mt-0.5">{check.detail}</p>
              </div>
            </div>
            <span className={`font-mono text-[10px] font-bold px-2 py-0.5 border uppercase ${badgeColor}`}>
              {check.status}
            </span>
          </div>
        );
      })}
    </div>
  );
};

