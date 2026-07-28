'use client';

import React, { useEffect, useRef } from 'react';
import Link from 'next/link';
import { TopNav } from '@/components/TopNav';
import { useLanguage } from '@/lib/LanguageContext';

export default function Home() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)] font-body-spectral flex flex-col">
      <TopNav language={language} onLanguageToggle={setLanguage} />

      <main className="max-w-6xl w-full mx-auto px-4 md:px-8 py-10 space-y-12 flex-1">
        {/* ── Thesis Banner ── */}
        <section className="border-b border-[var(--line)] pb-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-end">
          <div className="lg:col-span-8 space-y-4">
            <div className="inline-block px-3 py-1 font-mono text-[10px] uppercase tracking-[0.25em] text-[var(--engrave)] border border-[var(--engrave)]">
              SEBI SECURITIES MARKET TECHSPRINT 2026 · PROBLEM STATEMENT 1
            </div>

            <h1 className="font-serif-header text-4xl sm:text-5xl lg:text-6xl font-normal leading-[1.05] tracking-tight text-[var(--ink)]">
              Every verdict is issued as a <em className="italic text-[var(--engrave)] font-normal">certificate of proof.</em>
              <span className="font-hindi text-xl block mt-2 text-[var(--prussian)] font-normal">
                भरोसे का प्रमाण-पत्र।
              </span>
            </h1>
          </div>

          <div className="lg:col-span-4 space-y-4 lg:text-right">
            <div className="stamp-box">not a dashboard</div>
            <p className="text-sm text-[var(--ink-soft)] leading-relaxed">
              A scam gets stamped like a rejected document. A genuine SEBI notice carries an embossed seal you can verify. The interface is itself the security instrument.
            </p>

            <div className="flex flex-wrap gap-3 lg:justify-end pt-2">
              <Link href="/scan" className="cbtn solid-ok">
                🔍 Scan Content →
              </Link>
              <Link href="/verify" className="cbtn">
                🔏 Verify Seal
              </Link>
            </div>
          </div>
        </section>

        {/* ── Certificate Preview Section EX-01 & EX-02 ── */}
        <section className="space-y-8">
          <div className="flex items-center gap-4">
            <span className="font-mono text-xs text-[var(--engrave)] tracking-widest uppercase">EX·01</span>
            <h2 className="font-serif-header text-xl text-[var(--ink)]">Inbound content — flagged fraud vs authenticated circular</h2>
            <div className="flex-1 h-px bg-[var(--line)]" />
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Card 1: Fraud Certificate Sample */}
            <div className="cert-frame p-6 space-y-6">
              <div className="cert-corner tl"></div><div className="cert-corner tr"></div>
              <div className="cert-corner bl"></div><div className="cert-corner br"></div>

              <div className="border-b border-[var(--line)] pb-3 flex justify-between items-start font-mono text-[10px]">
                <div>
                  <span className="text-[var(--ink-soft)] block uppercase">Certificate of Analysis</span>
                  <span className="font-bold text-sm text-[var(--ink)] font-serif-header block mt-0.5">Phishing Communication</span>
                </div>
                <div className="text-right text-[var(--stamp)] font-bold">
                  NO. PS-2026-07-4471<br />FRAUD / REJECTED
                </div>
              </div>

              <div className="flex items-baseline gap-4">
                <span className="font-serif-header text-7xl font-bold text-[var(--stamp)] leading-none">08</span>
                <div className="flex-1">
                  <span className="font-mono text-[10px] text-[var(--ink-soft)] uppercase block mb-1">Trust Index / 100</span>
                  <div className="h-2 border border-[var(--ink)] relative bg-[var(--line)]">
                    <div className="absolute -top-1 left-[8%] w-1.5 h-4 bg-[var(--stamp)]" />
                  </div>
                </div>
              </div>

              <div className="stamp-box">
                🚫 FRAUD · REJECTED · PRAMAAN · 08/100
              </div>

              <p className="text-xs text-[var(--ink-soft)] font-mono leading-relaxed border-l-2 border-[var(--stamp)] pl-3">
                Four independent checks failed. Content carries fingerprints of automated impersonation campaign.
              </p>

              <Link href="/scan" className="cbtn solid block text-center">
                Run Live Scan →
              </Link>
            </div>

            {/* Card 2: Verified Certificate Sample */}
            <div className="cert-frame p-6 space-y-6 border-[var(--foil)]">
              <div className="cert-corner tl" style={{ borderColor: 'var(--foil)' }}></div>
              <div className="cert-corner tr" style={{ borderColor: 'var(--foil)' }}></div>
              <div className="cert-corner bl" style={{ borderColor: 'var(--foil)' }}></div>
              <div className="cert-corner br" style={{ borderColor: 'var(--foil)' }}></div>

              <div className="border-b border-[var(--line)] pb-3 flex justify-between items-start font-mono text-[10px]">
                <div>
                  <span className="text-[var(--ink-soft)] block uppercase">Certificate of Authenticity</span>
                  <span className="font-bold text-sm text-[var(--ink)] font-serif-header block mt-0.5">SEBI — F&O Margin Update</span>
                </div>
                <div className="text-right text-[var(--engrave)] font-bold">
                  SEAL PRMN-2026-SEBI-A3F2C<br />AUTHENTICATED
                </div>
              </div>

              <div className="flex items-baseline gap-4">
                <span className="font-serif-header text-7xl font-bold text-[var(--engrave)] leading-none">98</span>
                <div className="flex-1">
                  <span className="font-mono text-[10px] text-[var(--ink-soft)] uppercase block mb-1">Trust Index / 100</span>
                  <div className="h-2 border border-[var(--ink)] relative bg-[var(--line)]">
                    <div className="absolute -top-1 left-[96%] w-1.5 h-4 bg-[var(--engrave)]" />
                  </div>
                </div>
              </div>

              <div className="stamp-box ok">
                ✓ AUTHENTIC · PRAMAAN SEAL VERIFIED
              </div>

              <p className="text-xs text-[var(--ink-soft)] font-mono leading-relaxed border-l-2 border-[var(--engrave)] pl-3">
                Cryptographic signature valid under SEBI registry pinned key. Content SHA-256 intact.
              </p>

              <Link href="/verify" className="cbtn solid-ok block text-center">
                Verify PRAMAAN Seal →
              </Link>
            </div>
          </div>
        </section>

        {/* ── Footer ── */}
        <footer className="border-t-2 border-[var(--ink)] pt-6 pb-10 font-mono text-[10.5px] text-[var(--ink-soft)] flex flex-col sm:flex-row justify-between gap-4">
          <span>PRAMAAN·SHIELD — CERTIFICATE ENGINE</span>
          <span>SEBI TECHSPRINT 2026 · TEAM BLACK GHOST</span>
        </footer>
      </main>
    </div>
  );
}
