"use client";

import React from "react";

export type ContentType = "text" | "audio" | "video" | "image";

interface ScanUploaderProps {
  contentType: ContentType;
  onContentTypeChange: (type: ContentType) => void;
  textContent: string;
  onTextChange: (text: string) => void;
  selectedFile: File | null;
  onFileSelect: (file: File | null) => void;
  onSubmit: (e: React.FormEvent) => void;
  isScanning: boolean;
  language: "hi" | "en";
}

export const ScanUploader: React.FC<ScanUploaderProps> = ({
  contentType,
  onContentTypeChange,
  textContent,
  onTextChange,
  selectedFile,
  onFileSelect,
  onSubmit,
  isScanning,
  language,
}) => {
  return (
    <form onSubmit={onSubmit} className="w-full space-y-6">
      {/* Content Type Selector Bar */}
      <div className="flex flex-wrap items-center justify-center gap-1.5 p-1.5 bg-[var(--field)] backdrop-blur-md border border-[var(--line-ink)] rounded-xl shadow-inner">
        {(["text", "audio", "video", "image"] as ContentType[]).map((type) => {
          const isActive = contentType === type;
          const labels: Record<ContentType, { en: string; hi: string; icon: string }> = {
            text: { en: "Text Message", hi: "टेक्स्ट मैसेज", icon: "💬" },
            audio: { en: "Voice Note", hi: "ऑडियो नोट", icon: "🎙️" },
            video: { en: "Video Clip", hi: "वीडियो क्लिप", icon: "🎥" },
            image: { en: "Image Screenshot", hi: "इमेज स्क्रीनशॉट", icon: "🖼️" },
          };

          return (
            <button
              key={type}
              type="button"
              onClick={() => onContentTypeChange(type)}
              className={`flex-1 min-w-[120px] py-2.5 px-3 text-xs font-mono tracking-wider uppercase transition-all rounded-lg flex items-center justify-center gap-2 ${
                isActive
                  ? "bg-gradient-to-r from-[var(--engrave)] to-[#0D584C] text-white font-bold shadow-md shadow-emerald-900/30 scale-[1.02]"
                  : "text-[var(--ink-soft)] hover:text-[var(--ink)] hover:bg-[var(--line)]"
              }`}
            >
              <span>{labels[type].icon}</span>
              <span>{language === "hi" ? labels[type].hi : labels[type].en}</span>
            </button>
          );
        })}
      </div>

      {/* Input Form Section */}
      {contentType === "text" ? (
        <div className="space-y-2">
          <textarea
            rows={5}
            value={textContent}
            onChange={(e) => onTextChange(e.target.value)}
            placeholder={
              language === "hi"
                ? "संदेहास्पद व्हाट्सएप मैसेज, टेलीग्राम पोस्ट या ईमेल कंटेंट यहाँ पेस्ट करें..."
                : "Paste suspicious WhatsApp message, Telegram post or email content here..."
            }
            className="w-full p-4 text-xs font-mono bg-[var(--field)] text-[var(--ink)] placeholder-[var(--ink-soft)] border border-[var(--line-ink)] rounded-xl shadow-inner focus:border-[var(--engrave)] focus:ring-2 focus:ring-[var(--engrave)]/30 outline-none resize-none transition-all"
          />
        </div>
      ) : (
        <div className="relative flex flex-col items-center justify-center p-8 bg-[var(--field)] rounded-xl border-2 border-dashed border-[var(--line-ink)] hover:border-[var(--engrave)] transition-colors group cursor-pointer shadow-inner">
          <input
            type="file"
            accept={
              contentType === "audio"
                ? "audio/*"
                : contentType === "video"
                ? "video/*"
                : "image/*"
            }
            onChange={(e) => onFileSelect(e.target.files?.[0] || null)}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">
            {contentType === "audio" ? "🎧" : contentType === "video" ? "📼" : "🖼️"}
          </div>
          <p className="text-xs font-mono font-medium text-[var(--ink)] text-center">
            {selectedFile ? (
              <span className="text-[var(--engrave)] font-bold">{selectedFile.name}</span>
            ) : language === "hi" ? (
              "फाइल चुनने के लिए क्लिक करें या ड्रैग-एंड-ड्रॉप करें"
            ) : (
              "Click or drag & drop media file to upload"
            )}
          </p>
          <span className="text-[10px] font-mono text-[var(--ink-soft)] mt-1 uppercase">
            {contentType.toUpperCase()} • Max 50MB (Zero-Retention Enforced)
          </span>
        </div>
      )}

      {/* Action Submit Button */}
      <button
        type="submit"
        disabled={isScanning || (!textContent && !selectedFile)}
        className="cbtn solid-ok w-full py-4 font-mono text-xs tracking-widest font-bold disabled:opacity-50 flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[var(--engrave)] via-[#15806F] to-[#0D584C] text-white shadow-lg shadow-emerald-900/30 hover:shadow-emerald-900/50 hover:brightness-110 active:scale-[0.99] transition-all"
      >
        {isScanning ? (
          <>
            <div className="h-4 w-4 rounded-full border-2 border-white/20 border-t-white animate-spin" />
            <span>{language === "hi" ? "स्कैनिंग जारी है..." : "ANALYZING SIGNALS..."}</span>
          </>
        ) : (
          <>
            <span>🛡️</span>
            <span>{language === "hi" ? "ट्रस्ट स्कोर जांचें" : "RUN CERTIFICATE SECURITY SCAN"}</span>
          </>
        )}
      </button>
    </form>
  );
};
