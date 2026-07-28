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
  const [isScanning, setIsScanning] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const codeReader = new BrowserMultiFormatReader();
    let controls: any = null;

    const startCamera = async () => {
      try {
        setIsScanning(true);
        if (videoRef.current) {
          controls = await codeReader.decodeFromVideoDevice(
            undefined,
            videoRef.current,
            (result, err) => {
              if (result) {
                onScan(result.getText());
              }
              if (err && !(err.name === "NotFoundException")) {
                if (onError) onError(err.message);
              }
            }
          );
        }
      } catch (err: any) {
        setErrorMessage(
          language === "hi"
            ? "कैमरा एक्सेस करने में त्रुटि: " + (err.message || "अनुमति नहीं मिली")
            : "Camera access error: " + (err.message || "Permission denied")
        );
        setIsScanning(false);
      }
    };

    startCamera();

    return () => {
      if (controls) {
        controls.stop();
      }
    };
  }, [onScan, onError, language]);

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

