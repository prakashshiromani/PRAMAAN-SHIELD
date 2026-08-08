import type { Metadata, Viewport } from 'next';
import './globals.css';
import { LanguageProvider } from '@/lib/LanguageContext';

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0B0F19',
};

export const metadata: Metadata = {
  title: 'PRAMAAN-SHIELD — Three-Pillar Trust Engine',
  description:
    'Detect AI fraud. Authenticate what\'s real. Report instantly. SEBI TechSprint 2026.',
  keywords: [
    'SEBI', 'fraud detection', 'deepfake', 'phishing', 'PRAMAAN Seal', 'ECDSA',
    'voice clone', 'financial fraud', 'SCORES', 'Black Ghost',
  ],
  icons: { icon: '/favicon.ico' },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="hi" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="bg-[var(--paper)] text-[var(--ink)] antialiased min-h-screen">
        <LanguageProvider>
          <main className="min-h-screen">
            {children}
          </main>
        </LanguageProvider>
      </body>
    </html>
  );
}
