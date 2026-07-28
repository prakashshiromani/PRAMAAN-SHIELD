"use client";

import React from "react";

export interface ToastMessage {
  id: string;
  type: "success" | "warning" | "error" | "info";
  text: string;
}

interface ToastProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastProps> = ({ toasts, onDismiss }) => {
  return (
    <div className="fixed top-20 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => {
        const borderColors = {
          success: "border-emerald-500 text-emerald-400",
          warning: "border-amber-500 text-amber-400",
          error: "border-rose-500 text-rose-400",
          info: "border-indigo-500 text-indigo-400",
        };

        const icons = {
          success: "✓",
          warning: "⚠",
          error: "✕",
          info: "ℹ",
        };

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-center gap-3 p-3.5 rounded-xl bg-[#111827] border-l-4 shadow-xl border ${borderColors[toast.type]} backdrop-blur-md transition-all duration-300 animate-slide-in`}
          >
            <span className="text-base font-bold">{icons[toast.type]}</span>
            <p className="text-xs text-gray-200 flex-1 leading-snug">{toast.text}</p>
            <button
              onClick={() => onDismiss(toast.id)}
              className="text-gray-400 hover:text-white text-sm px-1"
            >
              ✕
            </button>
          </div>
        );
      })}
    </div>
  );
};
