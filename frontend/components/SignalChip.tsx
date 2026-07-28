"use client";

import React from "react";

interface SignalChipProps {
  label: string;
  type: "threat" | "warn" | "safe";
  icon?: string;
}

export const SignalChip: React.FC<SignalChipProps> = ({ label, type, icon }) => {
  const styles = {
    threat: "bg-rose-950/80 border-rose-500/50 text-rose-300 shadow-rose-900/30",
    warn: "bg-amber-950/80 border-amber-500/50 text-amber-300 shadow-amber-900/30",
    safe: "bg-emerald-950/80 border-emerald-500/50 text-emerald-300 shadow-emerald-900/30",
  };

  const defaultIcons = {
    threat: "⚡",
    warn: "⚠️",
    safe: "✓",
  };

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border backdrop-blur-md text-xs font-mono font-medium shadow-lg transition-transform hover:scale-105 ${styles[type]}`}
    >
      <span>{icon || defaultIcons[type]}</span>
      <span>{label}</span>
    </div>
  );
};
