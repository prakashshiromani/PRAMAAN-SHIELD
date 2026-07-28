"use client";

import React from "react";

interface LanguageToggleProps {
  language: "hi" | "en";
  onLanguageToggle: (lang: "hi" | "en") => void;
}

export const LanguageToggle: React.FC<LanguageToggleProps> = ({
  language,
  onLanguageToggle,
}) => {
  return (
    <div className="flex items-center bg-[var(--paper-2)] p-1 rounded-lg border border-[var(--line-ink)] font-mono text-xs shadow-inner">
      <button
        type="button"
        onClick={() => onLanguageToggle("hi")}
        className={`px-3 py-1.5 text-xs font-mono font-bold uppercase tracking-wider transition-all rounded-md ${
          language === "hi"
            ? "bg-gradient-to-r from-[var(--engrave)] to-[#0D584C] text-white shadow-sm shadow-emerald-900/30"
            : "text-[var(--ink-soft)] hover:text-[var(--ink)] hover:bg-[var(--line)]"
        }`}
      >
        हिं
      </button>
      <button
        type="button"
        onClick={() => onLanguageToggle("en")}
        className={`px-3 py-1.5 text-xs font-mono font-bold uppercase tracking-wider transition-all rounded-md ${
          language === "en"
            ? "bg-gradient-to-r from-[var(--engrave)] to-[#0D584C] text-white shadow-sm shadow-emerald-900/30"
            : "text-[var(--ink-soft)] hover:text-[var(--ink)] hover:bg-[var(--line)]"
        }`}
      >
        EN
      </button>
    </div>
  );
};

