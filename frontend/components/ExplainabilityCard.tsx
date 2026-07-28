"use client";

import React from "react";

interface ExplainabilityCardProps {
  module: string;
  status: "pass" | "fail" | "warn" | "skip";
  label: string;
  detail: string;
  contribution: number;
}

export const ExplainabilityCard: React.FC<ExplainabilityCardProps> = ({
  module,
  status,
  label,
  detail,
  contribution,
}) => {
  const isPass = status === "pass";
  const isFail = status === "fail";

  const borderColor = isPass ? "border-[var(--engrave)]" : isFail ? "border-[var(--stamp)]" : "border-[var(--amber)]";
  const textColor = isPass ? "text-[var(--engrave)]" : isFail ? "text-[var(--stamp)]" : "text-[var(--amber)]";
  const icon = isPass ? "✓" : isFail ? "✕" : "⚠️";

  return (
    <div className={`flex items-start justify-between p-3.5 rounded bg-[var(--paper)] border ${borderColor} transition-all font-mono`}>
      <div className="flex items-start gap-3">
        <div className={`h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold ${textColor} border ${borderColor} bg-[var(--paper-2)]`}>
          {icon}
        </div>
        <div className="space-y-0.5">
          <h4 className="text-xs font-bold text-[var(--ink)]">{label}</h4>
          <p className="text-[11px] text-[var(--ink-soft)] font-mono">{detail}</p>
        </div>
      </div>

      <div className="text-right">
        <span className={`text-xs font-mono font-bold ${textColor}`}>
          {contribution > 0 ? `+${contribution}` : contribution} PTS
        </span>
        <span className="block text-[9px] uppercase tracking-wider text-[var(--ink-soft)] font-mono">
          {module}
        </span>
      </div>
    </div>
  );
};

