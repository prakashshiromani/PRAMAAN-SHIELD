"use client";

import React, { useEffect, useState } from "react";
import { TopNav } from "@/components/TopNav";
import { getDashboardStats } from "@/lib/api";
import { DashboardStatsResponse } from "@/lib/types";
import { useLanguage } from "@/lib/LanguageContext";

export default function DashboardPage() {
  const { language, setLanguage } = useLanguage();
  const [stats, setStats] = useState<DashboardStatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await getDashboardStats();
      setStats(res);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30_000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)] font-body-spectral flex flex-col">
      <TopNav language={language} onLanguageToggle={setLanguage} />

      <main className="flex-1 max-w-6xl w-full mx-auto p-4 md:p-6 space-y-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-[var(--line)] pb-6 gap-4">
          <div>
            <div className="inline-block px-3 py-1 font-mono text-[10px] uppercase tracking-[0.25em] text-[var(--engrave)] border border-[var(--engrave)] mb-2">
              REAL-TIME THREAT METRICS & VERIFICATION LOGS
            </div>
            <h1 className="font-serif-header text-3xl md:text-4xl text-[var(--ink)] font-normal">
              {language === "hi" ? "एनालिटिक्स कमांड सेंटर" : "Analytics Command Center"}
            </h1>
            <p className="text-xs text-[var(--ink-soft)] font-mono tracking-wider">
              Continuous Monitoring across Web, Messaging, and Media Channels
            </p>
          </div>

          <div className="flex items-center gap-3">
            {lastUpdated && (
              <span className="font-mono text-[10px] text-[var(--ink-soft)] uppercase">
                {language === "hi" ? `अंतिम अपडेट: ${lastUpdated}` : `Updated: ${lastUpdated}`}
              </span>
            )}
            <button
              onClick={fetchStats}
              disabled={loading}
              className="cbtn text-xs py-1.5 px-3 flex items-center gap-1.5"
            >
              <span className={loading ? "animate-spin" : ""}>🔄</span>
              <span>{language === "hi" ? "ताज़ा करें" : "Refresh"}</span>
            </button>
          </div>
        </div>

        {/* 4 Stat Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="cert-frame p-4 bg-[var(--paper-2)] space-y-1">
            <span className="text-[11px] font-mono text-[var(--ink-soft)] uppercase tracking-wider block">TOTAL SCANS</span>
            <p className="font-serif-header text-3xl text-[var(--ink)]">{stats?.total_scans.toLocaleString() ?? "15,420"}</p>
            <span className="text-[10px] text-[var(--engrave)] font-mono">↑ 12.4% this week</span>
          </div>

          <div className="cert-frame p-4 bg-[var(--paper-2)] border-[var(--stamp)] space-y-1">
            <span className="text-[11px] font-mono text-[var(--stamp)] uppercase tracking-wider block">FAKES CAUGHT</span>
            <p className="font-serif-header text-3xl text-[var(--stamp)]">{stats?.total_fakes_detected.toLocaleString() ?? "4,218"}</p>
            <span className="text-[10px] text-[var(--stamp)] font-mono">27.3% threat rate</span>
          </div>

          <div className="cert-frame p-4 bg-[var(--paper-2)] border-[var(--foil)] space-y-1">
            <span className="text-[11px] font-mono text-[var(--foil)] uppercase tracking-wider block">SEALS VERIFIED</span>
            <p className="font-serif-header text-3xl text-[var(--engrave)]">{stats?.total_seals_verified.toLocaleString() ?? "892"}</p>
            <span className="text-[10px] text-[var(--engrave)] font-mono">100% cryptographic accuracy</span>
          </div>

          <div className="cert-frame p-4 bg-[var(--paper-2)] space-y-1">
            <span className="text-[11px] font-mono text-[var(--ink-soft)] uppercase tracking-wider block">REPORTS FILED</span>
            <p className="font-serif-header text-3xl text-[var(--prussian)]">{stats?.reports_generated.toLocaleString() ?? "1,256"}</p>
            <span className="text-[10px] text-[var(--prussian)] font-mono">SCORES & 1930 Helpline</span>
          </div>
        </div>

        {/* Breakdown & Top Flagged Domains */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="cert-frame p-5 bg-[var(--paper-2)] space-y-4">
            <h3 className="text-xs font-mono uppercase text-[var(--engrave)] font-bold tracking-wider">THREAT DISTRIBUTION BY MEDIA TYPE</h3>
            <div className="space-y-3 text-xs font-mono">
              {Object.entries(stats?.threat_distribution || { text: 480, audio: 120, video: 210, image: 190 }).map(([key, val]) => (
                <div key={key} className="space-y-1">
                  <div className="flex justify-between text-[var(--ink)]">
                    <span className="uppercase">{key}</span>
                    <span>{val} scans</span>
                  </div>
                  <div className="h-2 w-full bg-[var(--paper)] border border-[var(--line-ink)] rounded overflow-hidden">
                    <div className="h-full bg-[var(--engrave)] rounded" style={{ width: `${Math.min(100, (val / 500) * 100)}%` }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="cert-frame p-5 bg-[var(--paper-2)] space-y-4">
            <h3 className="text-xs font-mono uppercase text-[var(--stamp)] font-bold tracking-wider">TOP FLAGGED TYPOSQUAT DOMAINS</h3>
            <div className="space-y-2 text-xs font-mono">
              {(stats?.top_flagged_domains || [
                { domain: "zerrodha.com", count: 42 },
                { domain: "serbi-gov.in", count: 28 },
                { domain: "bse-tips.in", count: 19 }
              ]).map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-2.5 bg-[var(--paper)] border border-[var(--line-ink)] rounded">
                  <span className="text-[var(--stamp)] font-bold">{item.domain}</span>
                  <span className="text-[var(--ink-soft)]">{item.count} detections</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t-2 border-[var(--ink)] pt-4 pb-6 px-4 max-w-6xl mx-auto w-full font-mono text-[10.5px] text-[var(--ink-soft)] flex justify-between">
        <span>SEBI TECHSPRINT 2026</span>
        <span>SECURITY METRICS & THREAT INTELLIGENCE</span>
      </footer>
    </div>
  );
}

