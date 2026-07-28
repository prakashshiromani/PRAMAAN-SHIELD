"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LanguageToggle } from "./LanguageToggle";
import { useLanguage } from "@/lib/LanguageContext";

interface TopNavProps {
  language?: "hi" | "en";
  onLanguageToggle?: (lang: "hi" | "en") => void;
}

export const TopNav: React.FC<TopNavProps> = ({ language: propLang, onLanguageToggle }) => {
  const pathname = usePathname();
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const { language: globalLang, setLanguage: setGlobalLang } = useLanguage();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const language = propLang ?? globalLang;
  const handleLangToggle = (lang: "hi" | "en") => {
    if (onLanguageToggle) {
      onLanguageToggle(lang);
    }
    setGlobalLang(lang);
  };

  const toggleTheme = () => {
    const nextTheme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);
    document.documentElement.setAttribute("data-theme", nextTheme);
  };

  // Draw Guilloche Rosette Logo on Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, 48, 48);

    // Rosette Hypotrochoid drawing
    const cx = 24, cy = 24, R = 18, r = 7, d = 11, steps = 800;
    const k = (R - r) / r;

    ctx.save();
    ctx.lineWidth = 0.6;
    ctx.strokeStyle = "#116E5F";
    ctx.globalAlpha = 0.9;

    ctx.beginPath();
    for (let i = 0; i <= steps; i++) {
      const t = (i / steps) * Math.PI * 2 * 11;
      const x = cx + (R - r) * Math.cos(t) + d * Math.cos(k * t);
      const y = cy + (R - r) * Math.sin(t) - d * Math.sin(k * t);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.restore();

    // Border rings
    ctx.beginPath(); ctx.arc(cx, cy, 22, 0, 7); ctx.strokeStyle = "#14211C"; ctx.lineWidth = 1.2; ctx.stroke();
    ctx.beginPath(); ctx.arc(cx, cy, 20, 0, 7); ctx.strokeStyle = "#116E5F"; ctx.lineWidth = 0.6; ctx.stroke();
  }, []);

  const navItems = [
    { href: "/scan", label_en: "Scan Console", label_hi: "स्कैन कंसोल" },
    { href: "/verify", label_en: "Verify Seal", label_hi: "सील सत्यापित करें" },
    { href: "/report", label_en: "Report Scam", label_hi: "रिपोर्ट दर्ज करें" },
    { href: "/dashboard", label_en: "Analytics", label_hi: "डैशबोर्ड" },
    { href: "/seal-portal", label_en: "Entity Portal", label_hi: "इकाई पोर्टल" },
  ];

  return (
    <header className="sticky top-0 z-40 w-full bg-[var(--paper-2)] backdrop-blur-md border-b border-[var(--line-ink)] pt-4 pb-3 px-4 md:px-8 shadow-md">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Left: Organization Intaglio Letterhead */}
        <Link href="/" className="flex items-center gap-3.5 group">
          <canvas ref={canvasRef} width="48" height="48" className="w-12 h-12 flex-shrink-0 filter drop-shadow" />
          <div className="flex flex-col">
            <span className="font-mono text-[9.5px] uppercase tracking-[0.32em] text-[var(--engrave)]">
              प्रमाण · AUTHENTICATION AUTHORITY
            </span>
            <span className="font-serif-header text-2xl tracking-tight text-[var(--ink)] leading-none mt-0.5">
              PRAMAAN·<b className="italic font-normal text-[var(--engrave)]">SHIELD</b>
            </span>
          </div>
        </Link>

        {/* Center: Guilloche Nav Links */}
        <nav className="flex flex-wrap items-center justify-center gap-1 border border-[var(--line-ink)] p-1 rounded-lg bg-[var(--field)] backdrop-blur-md shadow-inner">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3.5 py-1.5 text-xs font-mono tracking-wider uppercase transition-all rounded-md ${
                  isActive
                    ? "bg-gradient-to-r from-[var(--engrave)] to-[#0D584C] text-white font-bold shadow-md shadow-emerald-900/30 scale-[1.02]"
                    : "text-[var(--ink-soft)] hover:text-[var(--ink)] hover:bg-[var(--line)]"
                }`}
              >
                {language === "hi" ? item.label_hi : item.label_en}
              </Link>
            );
          })}
        </nav>

        {/* Right: Bilingual Switcher & Theme Control */}
        <div className="flex items-center gap-3">
          <LanguageToggle language={language} onLanguageToggle={handleLangToggle} />

          <button
            onClick={toggleTheme}
            aria-label="Toggle Security Mode"
            className="font-mono text-xs px-3 py-1.5 border border-[var(--line-ink)] bg-[var(--field)] backdrop-blur-md text-[var(--ink)] hover:bg-[var(--ink)] hover:text-[var(--paper)] transition-all uppercase rounded"
          >
            {theme === "light" ? "🌙 Dark" : "☀️ Light"}
          </button>
        </div>
      </div>

      {/* Microtext Security Border Line */}
      <div className="max-w-6xl mx-auto mt-3 pt-2 border-t border-[var(--line)] flex items-center justify-between text-[8.5px] font-mono text-[var(--line-ink)] tracking-[0.3em] uppercase overflow-hidden whitespace-nowrap">
        <span>SEBI TECHSPRINT 2026 · TEAM BLACK GHOST</span>
        <span>प्रमाण·PROOF·AUTHENTIC·PRAMAAN·SEBI</span>
        <span>ISSUE 2026 · REF PS/PS-1/2026</span>
      </div>
    </header>
  );
};
