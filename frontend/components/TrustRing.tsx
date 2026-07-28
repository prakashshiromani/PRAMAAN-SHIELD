"use client";

import React, { useEffect, useState } from "react";

interface TrustRingProps {
  score: number;
  verdict: "VERIFIED" | "EXERCISE CAUTION" | "SUSPICIOUS";
  language: "hi" | "en";
}

export const TrustRing: React.FC<TrustRingProps> = ({ score, verdict, language }) => {
  // Animate from 0 to target score on mount
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    // Trigger CSS transition after mount — drives the 900ms ring fill animation
    const raf = requestAnimationFrame(() => setAnimatedScore(score));
    return () => cancelAnimationFrame(raf);
  }, [score]);

  // ── Color selection using Intaglio CSS variables ────────────────────────
  let ringColor = "var(--engrave)";       // teal — VERIFIED
  let ringHex   = "#116E5F";              // needed for inline style alpha
  let verdictText = language === "hi" ? "सत्यापित / सुरक्षित" : "VERIFIED";

  if (score < 30) {
    ringColor = "var(--stamp)";           // vermilion — SUSPICIOUS
    ringHex   = "#B2231F";
    verdictText = language === "hi" ? "संदिग्ध / खतरा" : "SUSPICIOUS";
  } else if (score < 70) {
    ringColor = "var(--amber)";           // amber — EXERCISE CAUTION
    ringHex   = "#B07A18";
    verdictText = language === "hi" ? "सावधान रहें" : "EXERCISE CAUTION";
  }

  // ── 270-degree arc SVG math ─────────────────────────────────────────────
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedScore / 100) * (circumference * 0.75);

  return (
    <div className="relative flex flex-col items-center justify-center p-4">
      <svg className="w-48 h-48 transform -rotate-135" viewBox="0 0 160 160">
        {/* Background Arc — uses design-system line color */}
        <circle
          cx="80"
          cy="80"
          r={radius}
          stroke="var(--line-ink)"
          strokeWidth="10"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={circumference * 0.25}
          strokeLinecap="round"
          opacity={0.4}
        />
        {/* Animated Score Arc — 900ms ease-out per Day 36 spec */}
        <circle
          cx="80"
          cy="80"
          r={radius}
          stroke={ringColor}
          strokeWidth="10"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 900ms cubic-bezier(0.22, 1, 0.36, 1)" }}
        />
      </svg>

      {/* Center Readout — uses --ink and --ink-soft for theme compatibility */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="text-4xl font-bold font-mono text-[var(--ink)] tracking-tight">
          {score.toString().padStart(2, "0")}
        </span>
        <span className="text-[10px] font-mono text-[var(--ink-soft)] uppercase tracking-widest">
          / 100 INDEX
        </span>
        <div
          className="mt-2 px-3 py-0.5 rounded-full text-[11px] font-semibold border shadow-sm"
          style={{
            borderColor: ringHex,
            color: ringHex,
            backgroundColor: `${ringHex}15`,
          }}
        >
          {verdictText}
        </div>
      </div>
    </div>
  );
};
