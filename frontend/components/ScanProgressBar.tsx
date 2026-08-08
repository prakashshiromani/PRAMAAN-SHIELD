"use client";

import React, { useEffect, useState } from "react";

interface ScanProgressBarProps {
  isScanning: boolean;
  contentType: "text" | "audio" | "video" | "image" | "email";
  language: "hi" | "en";
}

export const ScanProgressBar: React.FC<ScanProgressBarProps> = ({
  isScanning,
  contentType,
  language,
}) => {
  const [progress, setProgress] = useState(0);
  const [stageIndex, setStageIndex] = useState(0);

  // Stages definition based on content type
  const stages = {
    video: [
      {
        pct: 18,
        en: "[STAGE 1/4] INGESTING VIDEO & DECODING SHA256 / pHASH DIGEST",
        hi: "[चरण 1/4] वीडियो प्रोसेसिंग और डिजिटल फ़िंगरप्रिंट निर्माण",
      },
      {
        pct: 42,
        en: "[STAGE 2/4] EXTRACTING KEYFRAMES & LOCATING PRIMARY FACIAL BOUNDING BOXES",
        hi: "[चरण 2/4] फ़्रेम निष्कर्षण एवं चेहरे की सीमाओं की पहचान",
      },
      {
        pct: 74,
        en: "[STAGE 3/4] RUNNING VISION TRANSFORMER (ViT) & 8x8 DCT BLOCK FORENSICS",
        hi: "[चरण 3/4] AI विज़न ट्रांसफॉर्मर और 8x8 स्पेक्ट्रल विश्लेषण",
      },
      {
        pct: 92,
        en: "[STAGE 4/4] EVALUATING rPPG CARDIAC PULSE & TEMPORAL FLICKER STABILITY",
        hi: "[चरण 4/4] जैविक पल्स धड़कन एवं समय-स्थिरता सत्यापन",
      },
    ],
    audio: [
      {
        pct: 25,
        en: "[STAGE 1/3] DECODING WAVEFORM & GENERATING ACOUSTIC SPECTROGRAM",
        hi: "[चरण 1/3] ऑडियो तरंग एवं स्पेक्ट्रोग्राम विश्लेषण",
      },
      {
        pct: 60,
        en: "[STAGE 2/3] EVALUATING AASIST GRAPH ATTENTION VOICE CLONE MARKERS",
        hi: "[चरण 2/3] AASIST एआई वॉयस क्लोनिंग पैटर्न पहचान",
      },
      {
        pct: 90,
        en: "[STAGE 3/3] RUNNING RAWNET2 RAW WAVEFORM ANTI-SPOOFING ENSEMBLE",
        hi: "[चरण 3/3] RawNet2 ऑडियो विश्वसनीयता सत्यापन",
      },
    ],
    text: [
      {
        pct: 35,
        en: "[STAGE 1/3] PARSING DOMAIN STRUCTURE & CHECKING TYPOSQUAT REGISTRY",
        hi: "[चरण 1/3] डोमेन संरचना एवं नकली लिंक सत्यापन",
      },
      {
        pct: 70,
        en: "[STAGE 2/3] EVALUATING PHISHING INTENT & URGENCY SCAM LANGUAGE",
        hi: "[चरण 2/3] धोखाधड़ी भाषा एवं तात्कालिकता दबाव विश्लेषण",
      },
      {
        pct: 94,
        en: "[STAGE 3/3] MATCHING OFFICIAL SEBI REGISTERED ENTITY DATABASES",
        hi: "[चरण 3/3] SEBI आधिकारिक पंजीकृत डेटाबेस से मिलान",
      },
    ],
    image: [
      {
        pct: 30,
        en: "[STAGE 1/3] GENERATING 64-BIT DCT PERCEPTUAL HASH (pHASH)",
        hi: "[चरण 1/3] 64-बिट pHASH फ़िंगरप्रिंट जनरेशन",
      },
      {
        pct: 65,
        en: "[STAGE 2/3] QUERYING KNOWN FAKE MEDIA IN-MEMORY REDIS DATABASE",
        hi: "[चरण 2/3] ज्ञात फर्जी मीडिया डेटाबेस में त्वरित खोज",
      },
      {
        pct: 92,
        en: "[STAGE 3/3] HAMMING DISTANCE NEAR-NEIGHBOR VARIANT MATCHING",
        hi: "[चरण 3/3] हैमिंग दूरी विकृत छवि तुलना",
      },
    ],
    email: [
      {
        pct: 25,
        en: "[STAGE 1/3] EXAMINING EML HEADERS FOR SPF, DKIM & DMARC CRYPTOGRAPHIC PROOF",
        hi: "[चरण 1/3] ई-मेल हेडर SPF, DKIM और DMARC सत्यापन",
      },
      {
        pct: 60,
        en: "[STAGE 2/3] ANALYZING EMBEDDED URL HYPERLINKS & SENDER SPOOFING",
        hi: "[चरण 2/3] निहित लिंक एवं प्रेषक धोखाधड़ी जांच",
      },
      {
        pct: 92,
        en: "[STAGE 3/3] CROSS-MATCHING SEBI ENTITY REGISTRY BINDING RULES",
        hi: "[चरण 3/3] SEBI पंजीकृत संस्था बाइंडिंग नियम जांच",
      },
    ],
  };

  const currentStages = stages[contentType] || stages.video;

  useEffect(() => {
    if (!isScanning) {
      setProgress(0);
      setStageIndex(0);
      return;
    }

    setProgress(4);
    setStageIndex(0);

    // Smooth logarithmic progress curve tuned to realistic ~5-7 sec video analysis
    const interval = setInterval(() => {
      setProgress((prev) => {
        let delta = 1;
        if (prev < 30) {
          delta = Math.random() * 1.8 + 1.2; // ~1.2% - 3.0% early phase
        } else if (prev < 60) {
          delta = Math.random() * 1.2 + 0.8; // ~0.8% - 2.0% heavy ML phase
        } else if (prev < 82) {
          delta = Math.random() * 0.8 + 0.4; // ~0.4% - 1.2% liveness phase
        } else if (prev < 97) {
          // Asymptotic crawl: continuously moves forward without ever getting stuck at 94%
          delta = Math.random() * 0.3 + 0.1; // ~0.1% - 0.4% fine finish crawl
        } else {
          return 97;
        }

        const next = Math.min(97, prev + delta);
        const roundedNext = Math.round(next * 10) / 10; // smooth 1-decimal float

        // Update stage index smoothly based on progress milestones
        if (roundedNext >= 80 && currentStages.length > 3) {
          setStageIndex(3);
        } else if (roundedNext >= 52 && currentStages.length > 2) {
          setStageIndex(2);
        } else if (roundedNext >= 25 && currentStages.length > 1) {
          setStageIndex(1);
        }

        return roundedNext;
      });
    }, 220);

    return () => clearInterval(interval);
  }, [isScanning, contentType]);

  if (!isScanning) return null;

  const activeStage = currentStages[stageIndex] || currentStages[0];
  const currentStageText = language === "hi" ? activeStage.hi : activeStage.en;
  
  // Calculate remaining time estimate
  const remainingSecs = Math.max(0.5, ((100 - progress) * 0.06)).toFixed(1);

  // Total 24 matrix dots
  const totalDots = 24;
  const litDots = Math.floor((progress / 100) * totalDots);

  return (
    <div className="w-full space-y-4 p-5 bg-[var(--field)] backdrop-blur-lg border border-[var(--engrave)]/40 rounded-xl shadow-2xl animate-fade-in font-mono">
      {/* Header Info Bar */}
      <div className="flex items-center justify-between text-xs border-b border-[var(--line-ink)] pb-3">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span className="font-bold text-[var(--engrave)] tracking-wider uppercase">
            {language === "hi" ? "फॉरेंसिक विश्लेषण जारी..." : "FORENSIC SIGNAL SCANNING"}
          </span>
        </div>
        <div className="text-[11px] text-[var(--ink-soft)] font-bold tracking-widest">
          {Math.floor(progress)}% <span className="text-[var(--ink-soft)]/60">({remainingSecs}s EST)</span>
        </div>
      </div>

      {/* Main Fluid Progress Bar */}
      <div className="relative w-full h-3 bg-[var(--line)] rounded-full overflow-hidden p-0.5 border border-[var(--line-ink)]">
        <div
          className="h-full bg-gradient-to-r from-emerald-600 via-teal-500 to-emerald-400 rounded-full transition-all duration-300 ease-out shadow-[0_0_12px_rgba(16,185,129,0.6)] relative overflow-hidden"
          style={{ width: `${progress}%` }}
        >
          {/* Animated pulse shimmer effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent animate-shimmer" />
        </div>
      </div>

      {/* Micro-Segmented LED Dot Matrix Indicator */}
      <div className="flex items-center justify-between px-1 py-1 gap-1">
        {Array.from({ length: totalDots }).map((_, i) => {
          const isLit = i < litDots;
          const isCurrent = i === litDots;
          return (
            <div
              key={i}
              className={`h-1.5 flex-1 rounded-sm transition-all duration-200 ${
                isLit
                  ? "bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.8)] scale-y-110"
                  : isCurrent
                  ? "bg-amber-400 animate-pulse scale-y-125 shadow-[0_0_8px_rgba(251,191,36,0.9)]"
                  : "bg-[var(--line-ink)]/40"
              }`}
            />
          );
        })}
      </div>

      {/* Live Telemetry Status Output */}
      <div className="bg-[var(--paper)]/60 border border-[var(--line-ink)]/50 p-2.5 rounded-lg text-[10.5px] text-[var(--ink)] flex items-center gap-2">
        <span className="animate-spin text-emerald-600">⚙️</span>
        <span className="font-semibold tracking-wide text-[var(--ink)] truncate">
          {currentStageText}
        </span>
      </div>
    </div>
  );
};
