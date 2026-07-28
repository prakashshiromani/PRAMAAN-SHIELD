"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

type Language = "hi" | "en";

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextType>({
  language: "hi",
  setLanguage: () => {},
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>("hi");

  useEffect(() => {
    const savedLang = localStorage.getItem("pramaan_language") as Language | null;
    if (savedLang === "hi" || savedLang === "en") {
      setLanguageState(savedLang);
      document.documentElement.setAttribute("lang", savedLang);
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem("pramaan_language", lang);
    document.documentElement.setAttribute("lang", lang);
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
