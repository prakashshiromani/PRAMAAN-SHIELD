"use client";

import React, { useState, useEffect } from "react";

interface ConsentModalProps {
  language: "hi" | "en";
}

export const ConsentModal: React.FC<ConsentModalProps> = ({ language }) => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const consentGiven = localStorage.getItem("pramaan_dpdp_consent");
    if (!consentGiven) {
      setIsOpen(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem("pramaan_dpdp_consent", "true");
    setIsOpen(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="max-w-md w-full cert-frame p-6 bg-[var(--paper-2)] border-[var(--ink)] space-y-4 shadow-2xl">
        <div className="cert-corner tl"></div>
        <div className="cert-corner tr"></div>
        <div className="cert-corner bl"></div>
        <div className="cert-corner br"></div>

        <div className="flex items-center gap-3 border-b border-[var(--line)] pb-3">
          <div className="h-10 w-10 border border-[var(--ink)] bg-[var(--paper)] flex items-center justify-center text-xl">
            🔒
          </div>
          <div>
            <h3 className="text-lg font-serif-header text-[var(--ink)]">
              {language === "hi" ? "DPDP अधिनियम 2023 गोपनीयता सहमति" : "DPDP Act 2023 Privacy Disclosure"}
            </h3>
            <p className="text-xs text-[var(--engrave)] font-mono uppercase tracking-wider">
              PRAMAAN-SHIELD Zero-Retention Protocol
            </p>
          </div>
        </div>

        <div className="text-xs text-[var(--ink)] font-mono space-y-2 leading-relaxed bg-[var(--paper)] p-3 rounded border border-[var(--line-ink)]">
          {language === "hi" ? (
            <>
              <p>• <b>डेटा न्यूनीकरण:</b> आपकी अपलोड की गई मीडिया फ़ाइलों को 60 सेकंड के बाद स्वचालित रूप से हटा दिया जाता है।</p>
              <p>• <b>IP छद्मनामकरण:</b> आपका IP पता रिवर्सिबल नहीं है (Keyed HMAC-SHA256 सुरक्षित)।</p>
              <p>• <b>सामग्री प्रतिधारण:</b> केवल डिजिटल हैश और सुरक्षा निष्कर्ष सहेजे जाते हैं — मूल मीडिया नहीं।</p>
            </>
          ) : (
            <>
              <p>• <b>Data Minimization:</b> Uploaded media files are auto-deleted after 60 seconds.</p>
              <p>• <b>IP Pseudonymization:</b> Your IP address is hashed using keyed HMAC-SHA256 (DPDP compliant).</p>
              <p>• <b>Zero-Retention:</b> Only digital hashes and security metadata are stored — never your raw media.</p>
            </>
          )}
        </div>

        <button
          onClick={handleAccept}
          className="cbtn solid-ok w-full py-3 font-mono text-xs tracking-widest font-bold"
        >
          {language === "hi" ? "स्वीकार करें और जारी रखें" : "Accept & Proceed"}
        </button>
      </div>
    </div>
  );
};

