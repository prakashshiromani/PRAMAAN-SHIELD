import type { Config } from 'tailwindcss';

/**
 * PRAMAAN-SHIELD — Intaglio Security Certificate design tokens.
 *
 * Visual language: doce/mockup_pramaan_v2.html (pale safety-paper, guilloche
 * teal, rubber-stamp vermilion, embossed gold foil, serif typography).
 * Structural language (type scale, radii, elevation, motion): doce/DESIGN.md §4–§8.
 *
 * Colours resolve through the CSS custom properties declared in app/globals.css
 * so the light/dark ramp stays live without a Tailwind rebuild. Where a token
 * needs an alpha channel it is spelled out as rgba() instead of a var().
 *
 * NOTE: do not add a top-level `border` colour key here — it overrides the
 * `border-*` utility family and paints every bordered element one colour.
 */
const config: Config = {
  darkMode: ['class', '[data-theme="dark"]'],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        paper: {
          DEFAULT: 'var(--paper)',
          2: 'var(--paper-2)',
        },
        ink: {
          DEFAULT: 'var(--ink)',
          soft: 'var(--ink-soft)',
        },
        engrave: 'var(--engrave)',
        prussian: 'var(--prussian)',
        stamp: {
          DEFAULT: 'var(--stamp)',
          soft: 'var(--stamp-soft)',
        },
        foil: {
          DEFAULT: 'var(--foil)',
          lite: 'var(--foil-lite)',
        },
        amber: 'var(--amber)',
        line: {
          DEFAULT: 'var(--line)',
          ink: 'var(--line-ink)',
        },
        // Verdict aliases — semantic names for trust bands so pages never
        // hardcode a hex. Mirrors getVerdictBand() in lib/types.ts.
        verdict: {
          pass: 'var(--engrave)',
          warn: 'var(--amber)',
          fail: 'var(--stamp)',
          none: 'var(--line-ink)',
        },
      },

      fontFamily: {
        serif: ['var(--font-serif)', 'DM Serif Display', 'serif'],
        body: ['var(--font-body)', 'Spectral', 'serif'],
        dev: ['var(--font-dev)', 'Tiro Devanagari Hindi', 'serif'],
        mono: ['var(--font-mono)', 'IBM Plex Mono', 'monospace'],
      },

      // DESIGN.md §4 type scale, retuned onto the intaglio serif stack.
      // metric-xl carries the mobile step-down from DESIGN.md's mobile table.
      fontSize: {
        'metric-xl': ['clamp(48px, 8vw, 92px)', { lineHeight: '0.9', letterSpacing: '-0.02em' }],
        'metric-lg': ['clamp(24px, 4vw, 32px)', { lineHeight: '1' }],
        h1: ['clamp(34px, 4.6vw, 58px)', { lineHeight: '1.02', letterSpacing: '-0.01em' }],
        h2: ['clamp(18px, 2.4vw, 27px)', { lineHeight: '1.05' }],
        h3: ['clamp(16px, 1.8vw, 22px)', { lineHeight: '1.2' }],
        'body-base': ['15px', { lineHeight: '1.6' }],
        'label-sm': ['11px', { lineHeight: '1.3', letterSpacing: '0.05em' }],
        'mono-data': ['12px', { lineHeight: '1.4' }],
        micro: ['8.5px', { lineHeight: '1.2', letterSpacing: '0.32em' }],
      },

      // Intaglio print is a low-radius medium — a certificate has crisp edges.
      // DESIGN.md's 6/10/16/24 scale is compressed accordingly.
      borderRadius: {
        sm: '2px',
        md: '3px',
        lg: '4px',
        xl: '6px',
      },

      boxShadow: {
        'elev-1': '0 4px 12px -6px rgba(20,33,28,0.18)',
        'elev-2': '0 8px 24px -12px rgba(20,33,28,0.28)',
        'elev-3': '0 12px 36px -14px rgba(20,33,28,0.38)',
        cert: '0 24px 50px -34px rgba(20,33,28,0.55)',
        press: 'inset 0 1px 2px rgba(20,33,28,0.22)',
      },

      spacing: {
        // Console shell measurements from DESIGN.md §5.
        sidebar: '300px',
        telemetry: '360px',
        topbar: '64px',
        'topbar-sm': '56px',
        'actionbar': '64px',
      },

      keyframes: {
        // Scan lifecycle: teal sweep travelling down the analysis canvas.
        sweep: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '10%': { opacity: '1' },
          '90%': { opacity: '1' },
          '100%': { transform: 'translateY(100%)', opacity: '0' },
        },
        // REVEAL: findings rows slide in from the ledger edge.
        'stagger-in': {
          '0%': { opacity: '0', transform: 'translateX(12px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        // Signal chips scale up as they are pinned to the canvas.
        'chip-in': {
          '0%': { opacity: '0', transform: 'scale(0.8)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        // Rubber stamp striking the page.
        'stamp-in': {
          '0%': { opacity: '0', transform: 'scale(1.6) rotate(-14deg)' },
          '60%': { opacity: '1', transform: 'scale(0.96) rotate(-3deg)' },
          '100%': { opacity: '1', transform: 'scale(1) rotate(-4deg)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'pulse-ring': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.45' },
        },
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },

      animation: {
        sweep: 'sweep 1.6s linear infinite',
        'stagger-in': 'stagger-in 320ms cubic-bezier(.2,.7,.2,1) both',
        'chip-in': 'chip-in 260ms cubic-bezier(.2,.7,.2,1) both',
        'stamp-in': 'stamp-in 420ms cubic-bezier(.2,.7,.2,1) both',
        shimmer: 'shimmer 1.5s linear infinite',
        'pulse-ring': 'pulse-ring 1s ease-in-out infinite',
        'fade-up': 'fade-up 200ms ease-out both',
      },

      transitionTimingFunction: {
        odometer: 'cubic-bezier(.2,.7,.2,1)',
      },
    },
  },
  plugins: [],
};

export default config;
