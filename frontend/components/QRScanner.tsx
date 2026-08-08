"use client";

import React, { useEffect, useRef, useState } from "react";
import { BrowserMultiFormatReader } from "@zxing/browser";

interface QRScannerProps {
  onScan: (data: string) => void;
  onError?: (error: string) => void;
  language: "hi" | "en";
}

export const QRScanner: React.FC<QRScannerProps> = ({ onScan, onError, language }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Keep the latest callbacks in refs so the effect below can mount the camera
  // exactly ONCE. Previously the inline onScan/onError props in the deps array
  // restarted the camera on every parent re-render (flash/blackout loop) and
  // duplicate-scanned the same held QR because there was no decode-once guard.
  const onScanRef = useRef(onScan);
  const onErrorRef = useRef(onError);
  onScanRef.current = onScan;
  onErrorRef.current = onError;

  const scannedRef = useRef(false);

  useEffect(() => {
    const codeReader = new BrowserMultiFormatReader();
    let controls: any = null;
    let disposed = false;

    const handleResult = (result: any, err: any) => {
      if (result) {
        if (!scannedRef.current) {
          scannedRef.current = true;
          try {
            controls?.stop(); // stop decode loop after first successful read
          } catch {
            /* already stopped */
          }
          onScanRef.current(result.getText());
        }
        return;
      }
      if (err && !(err.name === "NotFoundException")) {
        onErrorRef.current?.(err.message);
      }
    };

    const startCamera = async () => {
      try {
        if (videoRef.current && !disposed) {
          controls = await codeReader.decodeFromVideoDevice(
            undefined,
            videoRef.current,
            handleResult
          );
        }
      } catch (err: any) {
        if (disposed) return;
        setErrorMessage(
          language === "hi"
            ? "कैमरा एक्सेस करने में त्रुटि: " + (err.message || "अनुमति नहीं मिली")
            : "Camera access error: " + (err.message || "Permission denied")
        );
      }
    };

    startCamera();

    return () => {
      disposed = true;
      try {
        controls?.stop();
      } catch {
        /* ignore */
      }
      const videoEl = videoRef.current;
      if (videoEl && videoEl.srcObject) {
        const stream = videoEl.srcObject as MediaStream;
        stream.getTracks().forEach((t) => t.stop());
        videoEl.srcObject = null;
      }
    };
  }, []); // camera lifecycle decoupled from parent re-renders

  return (
    <div className="relative w-full max-w-sm mx-auto overflow-hidden cert-frame p-2 bg-[var(--paper-2)] border-[var(--ink)] shadow-2xl">
      <div className="relative aspect-square w-full overflow-hidden rounded bg-black">
        <video ref={videoRef} className="h-full w-full object-cover" />
        
        {/* Scanner Overlay Box */}
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div className="h-48 w-48 border-2 border-dashed border-[var(--engrave)] bg-[var(--wash-a)] shadow-[0_0_30px_rgba(17,110,95,0.3)] animate-pulse" />
        </div>

        {/* Scan Status Badge */}
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 rounded bg-[var(--paper)] px-3 py-1 font-mono text-xs text-[var(--ink)] border border-[var(--line-ink)]">
          {language === "hi" ? "QR कोड फ़्रेम में रखें..." : "Align QR within frame..."}
        </div>
      </div>

      {errorMessage && (
        <div className="mt-2 text-center text-xs font-mono text-[var(--stamp)] p-2 bg-[var(--paper)] rounded border border-[var(--stamp)]">
          {errorMessage}
        </div>
      )}
    </div>
  );
};

