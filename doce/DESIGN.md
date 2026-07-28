# 🎨 DESIGN.md — PRAMAAN-SHIELD Design System

**Single visual source:** A premium clinical cryptographic console for cybersecurity verification, threat detection, and market trust.
Version 4.0 · Team Black Ghost · SEBI TechSprint 2026

> One reference, one system. Every token below is derived from the **Clinical Cryptographic Console** look (inspired by the sleek, data-dense styling of Airlume.ai and Hospity) — utilizing deep obsidian backdrops, translucent glass panels, floating threat-annotation chips, and a glowing holographic Trust Shield.
> Format follows `awesome-design-md`: **tokens → themes → components → blueprints**.

---

## Table of Contents
1. [What We're Building From](#1-what-were-building-from)
2. [Design Principles](#2-design-principles)
3. [Color System — Light & Dark](#3-color-system--light--dark)
4. [Typography](#4-typography)
5. [Spacing, Grid & Radius](#5-spacing-grid--radius)
6. [Elevation & Borders](#6-elevation--borders)
7. [Data-Viz Language](#7-data-viz-language)
8. [Motion & Lifecycle](#8-motion--lifecycle)
9. [Signature Element](#9-signature-element)
10. [Component Specs](#10-component-specs)
11. [Screen Blueprints](#11-screen-blueprints)
12. [Theming Implementation](#12-theming-implementation)
13. [Accessibility](#13-accessibility)
14. [Voice & Microcopy](#14-voice--microcopy)
15. [Do / Don't](#15-do--dont)

---

## 1. What We're Building From

The reference is a **security verification terminal**: scanned messages, documents, emails, or certificates are loaded into a central canvas. Pinned live to the scanned file are translucent alert chips showing authenticity indicators, while the left sidebar holds the case metrics, and the right panel displays the threat breakdown and the core Trust Index gauge.

**We map the cryptographic console 1:1 onto PRAMAAN-SHIELD:**

| Component | specification |
| :--- | :--- |
| **Analysis Stage** | Central preview area where the message/email is rendered in a translucent glass container |
| **Holographic Trust Shield** | Pulsing crystalline geometric shield in the header or beside the result indicating system status |
| **Signal Chips** | Floating glassmorphic cards connected by 1px indicator lines pointing to specific threat locations (e.g. *AI-text 87%*, *Typosquat domain*) |
| **Left Sidebar** | Case profile, telemetry dials, and general scanning controls |
| **Right Sidebar** | Trust Index gauge (`08/100` for threat, `98/100` for safe), explainability ledger of checks, and complaint submission CTAs |
| **Status Badges** | Green "VERIFIED" / Amber "EXERCISE CAUTION" / Crimson "SUSPICIOUS" pills |

---

## 2. Design Principles

1. **Obsidian Canvas.** Deep, low-fatigue dark themes as default to evoke an authoritative command center atmosphere.
2. **Precision Glassmorphism.** Translucent panels with fine `1px` border glows suggest a sophisticated, layered analytical environment.
3. **Data Density.** Information is presented concisely. Numbers are large near-white numerals sitting under tiny UPPERCASE labels.
4. **State-Driven Colors.** Royal Indigo and Neon Cyan are used for active branding/telemetry; Emerald, Amber, and Crimson are strictly reserved for verdicts and security status.
5. **Compliance & Trust.** High contrast typography, bilingual English/Hindi support, and clear compliance references.
6. **Mobile-First.** All layouts designed for 360px-first, scaling up to 1440px. Touch-friendly targets, thumb-zone-aware placement.

---

## 3. Color System — Light & Dark

Dark mode is the default primary aesthetic; Light mode is the clean, report-like equivalent.

### 3.1 Dark Theme (Default Console)

```css
[data-theme="dark"] {
  /* canvas */
  --bg:            #0B0F19;   /* Obsidian Navy app background */
  --bg-dot:        rgba(99, 102, 241, 0.04); /* Indigo dot-grid texture */
  --surface:       #111827;   /* Translucent glass surfaces */
  --surface-2:     #1F2937;   /* Nested tiles, inputs, mini-viz bg */
  --glass:         rgba(17, 24, 39, 0.7); /* Frosted glass */
  --glass-border:  rgba(99, 102, 241, 0.15); /* Indigo glowing border */

  /* ink */
  --text:          #F3F4F6;   /* Near-white headings + big metrics */
  --text-muted:    #9CA3AF;   /* Labels, subtitles */
  --text-faint:    #6B7280;   /* Hints, axis labels */

  /* lines */
  --border:        #374151;   /* Fine dark dividers */
  --border-strong: #4B5563;

  /* brand & telemetry */
  --primary:       #4F46E5;   --primary-press: #4338CA;  --on-primary: #FFFFFF;
  --primary-soft:  rgba(79, 70, 229, 0.15);  --primary-ring: rgba(79, 70, 229, 0.4);
  --secondary:     #06B6D4;   --secondary-soft: rgba(6, 182, 212, 0.15); /* Neon Cyan */
  --grad-a:        #4F46E5;   --grad-b: #06B6D4;         /* Progress bar gradient */

  /* status / verdict pills */
  --ok:            #10B981;   --ok-soft: rgba(16, 185, 129, 0.15);     /* VERIFIED */
  --warn:          #F59E0B;   --warn-soft: rgba(245, 158, 11, 0.15);    /* EXERCISE CAUTION */
  --bad:           #EF4444;   --bad-soft: rgba(239, 68, 68, 0.15);      /* SUSPICIOUS */

  /* skeleton loading */
  --skeleton-base: #1F2937;
  --skeleton-shine: #374151;

  --shadow-color:  0 0% 0%;
}
```

#### Dot Grid Pattern
Applied to the `<body>` background to create the subtle command-center texture:
```css
body[data-theme="dark"] {
  background-color: var(--bg);
  background-image: radial-gradient(var(--bg-dot) 1px, transparent 1px);
  background-size: 24px 24px;
}
```

### 3.2 Light Theme (Report Mode)

```css
[data-theme="light"] {
  /* canvas */
  --bg:            #F4F7FC;   /* Cool Ice Blue app background */
  --bg-dot:        rgba(29, 78, 216, 0.03);
  --surface:       #FFFFFF;   /* Crisp white cards */
  --surface-2:     #EBF0F6;   /* Input tiles */
  --glass:         rgba(255, 255, 255, 0.7);
  --glass-border:  rgba(29, 78, 216, 0.08);

  /* ink */
  --text:          #111827;   /* Dark charcoal text */
  --text-muted:    #4B5563;
  --text-faint:    #9CA3AF;

  /* lines */
  --border:        #E5E7EB;   /* Light dividers */
  --border-strong: #D1D5DB;

  /* brand & telemetry */
  --primary:       #1D4ED8;   --primary-press: #1E40AF;  --on-primary: #FFFFFF;
  --primary-soft:  #EFF6FF;   --primary-ring: rgba(29, 78, 216, 0.2);
  --secondary:     #0EA5E9;   --secondary-soft: #F0F9FF;
  --grad-a:        #1D4ED8;   --grad-b: #0EA5E9;

  /* status / verdict pills */
  --ok:            #10B981;   --ok-soft: #D1FAE5;
  --warn:          #D97706;   --warn-soft: #FEF3C7;
  --bad:           #DC2626;   --bad-soft: #FEE2E2;

  /* skeleton loading */
  --skeleton-base: #E5E7EB;
  --skeleton-shine: #F3F4F6;

  --shadow-color:  220 40% 20%;
}
```

---

## 4. Typography

We use **Outfit** for display headers to project modern authority, **Inter** or **Geist** for standard UI elements, and **Geist Mono** for cryptographic metrics, hashes, and threat logs.

| Role | Family | Source | Use |
| :--- | :--- | :--- | :--- |
| **Display / Headings** | **Outfit** (500/600/700) | Google Fonts | H1, H2, H3, Trust Index, brand headers |
| **Body & UI** | **Inter** (400/500/600) | Google Fonts | Paragraphs, tables, navigation items |
| **Technical Data** | **Geist Mono** (400/500) | Google Fonts | Hashes, parameters, threat indicators, numbers |

```
Google Fonts: Outfit, Inter, Geist Mono
```

### 4.1 Type Scale
| Token | Size / Line | Weight | Use |
| :--- | :--- | :--- | :--- |
| `metric-xl` | 64px / 0.95 | 700 Outfit | Hero Trust Index scores ("08", "98") |
| `metric-lg` | 32px / 1.00 | 600 Outfit | Major panel metrics ("87%", "9/10") |
| `h1` | 28px / 1.20 | 700 Outfit | Page titles |
| `h2` | 20px / 1.30 | 600 Outfit | Card and block titles |
| `body` | 15px / 1.50 | 400 Inter | Standard content |
| `label-sm` | 11px / 1.30 | 600 Inter | Upper case grey labels (letter-spacing: +0.05em) |
| `mono-data` | 12px / 1.40 | 500 Geist Mono | Serials, hash tags, IP logs, timers |

### 4.2 Mobile Type Adjustments
| Token | Desktop | Mobile (< 768px) |
| :--- | :--- | :--- |
| `metric-xl` | 64px | 48px |
| `metric-lg` | 32px | 24px |
| `h1` | 28px | 22px |
| `h2` | 20px | 18px |

---

## 5. Spacing, Grid & Radius

*   **Grid:** 12-column Grid on Desktop (gutter `24px`), collapsing to a single fluid column on Mobile (margins `16px`).
*   **Shell Spacing:** Top Bar (`64px` height, `56px` on mobile) + 3-Panel Console shell: **Left Sidebar (300px) · Center Workspace (Fluid) · Right Sidebar (360px)**.
*   **Mobile Shell:** Top Bar → Full-width stacked content → Sticky bottom action bar (`64px` height).
*   **Rhythm Scale:** `4px` base unit. Standard margins use `16px` / `24px`. Section spacing uses `32px`.
*   **Radius:**
    *   `r-sm` (6px): Small buttons, tags, chips.
    *   `r-md` (10px): Inputs, table rows.
    *   `r-lg` (16px): Main dashboard cards, inner workspaces.
    *   `r-xl` (24px): Main application panels.
    *   `r-full` (999px): Toggle buttons, arc rings, avatars.

---

## 6. Elevation & Borders

*   **Elevation:**
    *   `--elev-1` (Resting): `0 4px 12px rgba(0,0,0,0.08)`
    *   `--elev-2` (Hover): `0 8px 24px rgba(0,0,0,0.14)`
    *   `--elev-3` (Toast/Modal): `0 12px 36px rgba(0,0,0,0.20)`
*   **Borders:** Fine `1px` borders are mandatory on all cards. 
    *   *Dark Mode:* `1px solid var(--glass-border)` (gives the glowing edges effect).
    *   *Light Mode:* `1px solid var(--border)`.
*   **Focus Ring (Accessibility):**
    *   `--focus-ring: 0 0 0 3px var(--primary-ring);`
    *   Applied via `box-shadow: var(--focus-ring)` on `:focus-visible` for all interactive elements.
    *   Never removed — outline is set to `transparent` (not `none`) so Windows High Contrast mode still works.

---

## 7. Data-Viz Language

### 7.1 Trust Index Ring

270° progress arc (`10px` stroke). Color is determined by **score range**, with the big Outfit metric centered.

| Score Range | Color Token | Ring Color | Verdict Label |
| :--- | :--- | :--- | :--- |
| **0 – 29** | `--bad` | Crimson (`#EF4444`) | `SUSPICIOUS` / संदिग्ध |
| **30 – 69** | `--warn` | Amber (`#F59E0B`) | `EXERCISE CAUTION` / चेतावनी |
| **70 – 100** | `--ok` | Emerald (`#10B981`) | `VERIFIED` / सत्यापित |

### 7.2 Explainability Ledger

Checklist format where passing checks are represented by Green tick badges and failing checks use Red alert tags. A failing row is styled with a subtle `2px` left border tint of Crimson.

| Check Status | Icon | Badge Color | Border |
| :--- | :--- | :--- | :--- |
| `pass` | ✓ | `--ok-soft` text `--ok` | None |
| `fail` | ✕ | `--bad-soft` text `--bad` | `2px` left `--bad` |
| `warn` | ⚠ | `--warn-soft` text `--warn` | `2px` left `--warn` |
| `skip` | ○ | `--surface-2` text `--text-faint` | None (dimmed row) |

### 7.3 Sparklines
*   **Stroke:** `1.5px`, color `var(--secondary)` at `40%` opacity.
*   **Fill:** None (line-only).
*   **Usage:** Placed inside telemetry cards in the Left Sidebar.
*   **Data represented:** Historical trend of the metric shown in the card (e.g. AI probability trend across recent scans, urgency score distribution).
*   **Dimensions:** `120px × 32px` container, no axes, no labels — pure shape.

---

## 8. Motion & Lifecycle

### 8.1 Scan Lifecycle Sequence

The scan workspace transitions through 4 distinct visual states:

```
  IDLE ──────► SCANNING ──────► REVEAL ──────► RESULT
  (paste zone)  (sweep anim)    (verdict pop)   (full display)
  
  ├─ 0ms       ├─ 0ms          ├─ 0ms          ├─ permanent
  │             │ duration:     │ duration:     │
  │             │ until API     │ 900ms         │
  │             │ returns       │               │
```

| State | Visual Treatment | Duration |
| :--- | :--- | :--- |
| **IDLE** | Paste zone visible with dashed border. Center workspace is empty with faint helper text: "Paste, upload, or type content to scan". Signal chips and Trust Ring hidden. | Persistent until user action |
| **SCANNING** | Paste zone content locked (non-editable, slight dim to `0.6` opacity). Neon cyan scan sweep line animates vertically across the content. Left sidebar shows pulsing skeleton cards. Right sidebar shows Trust Ring outline at `10%` opacity with `--` placeholder digits. | Until API response (typically 2–10s) |
| **REVEAL** | Scan sweep stops. Trust Ring animates from `0` → target score (900ms ease). Score digits count up (odometer-style). Signal chips stagger-appear (100ms per chip, scale 0.8→1.0 + fade-in). Explainability rows slide in from right (80ms stagger). Status pill color-morphs to verdict color. | 900ms total |
| **RESULT** | Full display. All elements interactive. Complaint CTAs visible if score < 30. Content re-editable for new scan. | Persistent until new scan |
| **ERROR** | Scan sweep stops. Red pulse border on workspace (2 cycles). Toast notification appears top-right: "Analysis failed — please retry". Paste zone re-enabled. | 2s pulse, toast 5s auto-dismiss |

### 8.2 Core Animations

*   **Scan Sweep:** A clean horizontal neon cyan indicator line sweeps down the message workspace preview to represent active analysis (1.6s linear loop).
*   **Verdict Reveal:** The Trust Index Ring progresses from `0` to the target score with a count-up transition on the digits (900ms `cubic-bezier(.2,.7,.2,1)`).
*   **Card Hover:** Smooth vertical offset lift (`-2px`) combined with transition to `--elev-2` (150ms).

### 8.3 Micro-Interactions Inventory

| Interaction | Animation | Timing |
| :--- | :--- | :--- |
| Signal Chip appears | Fade-in + scale `0.8 → 1.0` | Staggered 100ms per chip |
| Explainability row reveals | Slide-in from right | Staggered 80ms per row |
| Status pill transitions | Background color cross-fade | 300ms ease |
| Trust Index counter | Odometer-style digit roll (per digit) | 900ms `cubic-bezier(.2,.7,.2,1)` |
| Copy to clipboard | Icon swap (📋 → ✓), brief green flash on button | 200ms, checkmark holds 1.5s |
| Error state | Red border pulse on affected component | 2 cycles × 600ms |
| Page transitions | Cross-fade between routes | 200ms ease-out |
| Button press | Scale `0.97` + color shift to `--primary-press` | 100ms |
| Tab switch (nav) | Active indicator slides horizontally | 250ms spring |
| Toast enter | Slide-in from right + fade-in | 300ms ease-out |
| Toast exit | Slide-out right + fade-out | 200ms ease-in |
| Skeleton shimmer | Left-to-right gradient sweep on loading cards | 1.5s infinite linear |

---

## 9. Signature Element: The Verification Workspace

The center Stage features the **translucent preview of the scanned content** (message, email, or post).
Holographic indicator lines (`1px` width) anchor floating threat signal chips directly to the specific words, metadata, or coordinates that triggered them:

```
        ╭ [AI TEXT 87%] ⚡              Translucent preview panel
   ┌────┴───────────────────────────┐   
   │  "URGENT: Verify your demat   │◀── [TYPOSQUAT: sebi-gov-in] ⚠
   │   KYC status within 24 hours"  │   
   └────────────┬───────────────────┘   
                ╰ [URGENCY 9/10] ⚑
```

*   **Responsive Adaptation:**
    *   *Desktop (`≥ 768px`):* Signal chips use `position: absolute` with 1px SVG connector lines pointing directly to threat coordinates.
    *   *Mobile (`< 768px`):* Signal chips collapse smoothly into a stacked vertical list of inline alert badges directly beneath the scanned message preview to prevent overlapping.

Beside the preview, the **Trust Index Ring** serves as the definitive authority readout.

### 9.1 PRAMAAN Seal QR Code Design

The QR code is the physical manifestation of the PRAMAAN Seal — it must look distinct from generic QR codes.

| Aspect | Specification |
| :--- | :--- |
| **Size** | `200px × 200px` (desktop), `160px × 160px` (mobile) |
| **Finder Pattern** | Rounded corners (`r-sm`) instead of sharp squares |
| **Color** | Dark mode: `--primary` modules on `--surface` background. Light mode: `--primary` modules on `white` |
| **Branded Center** | 20% center reserved for PRAMAAN shield icon (transparent overlay) |
| **Surrounding Card** | Glass card with `1px` `--glass-border`, `r-lg`, containing: QR + Seal ID label (`mono-data`) + Entity name + Signed date |
| **Error Correction** | Level H (30%) to accommodate center branding |

---

## 10. Component Specs

### 10.1 Component Sizing

| Component | Height | Padding | Min-Width | Touch Target |
| :--- | :--- | :--- | :--- | :--- |
| Top Nav Bar | `64px` (desktop) / `56px` (mobile) | `0 16px` | `100%` | — |
| Commit Button | `44px` | `0 20px` | `160px` | `44px × 44px` ✓ |
| Secondary Button | `44px` | `0 20px` | `160px` | `44px × 44px` ✓ |
| State Pill | `28px` | `4px 12px` | auto | `28px × auto` |
| Input (Paste Zone) | `200px` min | `16px` | `100%` | — |
| Signal Chip | auto | `8px 12px` | auto | `44px` min height |
| Trust Index Ring | `200px × 200px` (desktop) / `160px × 160px` (mobile) | — | — | — |
| Explainability Row | `48px` min | `12px 16px` | `100%` | `48px` ✓ |
| Nav Tab Item | `44px` | `0 16px` | `64px` | `44px × 64px` ✓ |

### 10.2 Top Nav Bar
Height `64px` (desktop), `56px` (mobile). Left: Logo + "PRAMAAN·SHIELD". Center: Navigation tabs (Scan, Verify, Report, Dashboard). Right: Theme switcher (☾/☀), Bilingual toggle, and User profile.

**Mobile:** Hamburger menu replaces center tabs. Theme + Language toggles move into hamburger drawer.

### 10.3 Buttons

#### Commit Button (Primary Action)
High-contrast Indigo/Cobalt solid button (`r-sm`, white text). Primary action: *"Report to SEBI SCORES 2.0"*.

| State | Background | Text | Border | Shadow | Transform |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Default | `--primary` | `--on-primary` | none | `--elev-1` | none |
| Hover | `--primary-press` | `--on-primary` | none | `--elev-2` | `translateY(-1px)` |
| Active/Pressed | `--primary-press` | `--on-primary` | none | `--elev-1` | `scale(0.97)` |
| Focus-Visible | `--primary` | `--on-primary` | none | `--focus-ring` | none |
| Loading | `--primary` at `70%` | hidden | none | `--elev-1` | none (spinner shown) |
| Disabled | `--surface-2` | `--text-faint` | `1px --border` | none | none (`cursor: not-allowed`) |

#### Secondary Button (Outlined Glass)
Outlined translucent glass button (`r-sm`). Action: *"Cyber Crime Helpline 1930 / Chakshu"*.

| State | Background | Text | Border | Shadow |
| :--- | :--- | :--- | :--- | :--- |
| Default | `transparent` | `--primary` | `1px --glass-border` | none |
| Hover | `--primary-soft` | `--primary` | `1px --primary` at `30%` | `--elev-1` |
| Active/Pressed | `--primary-soft` | `--primary-press` | `1px --primary` | none |
| Focus-Visible | `transparent` | `--primary` | `1px --glass-border` | `--focus-ring` |
| Disabled | `transparent` | `--text-faint` | `1px --border` | none |

### 10.4 Verdict Status Pill

Tinted background (`10%` or `--*-soft` opacity) with high contrast text in the corresponding state color. Combined with icon and text to satisfy accessibility (never color alone).

| Verdict | Background | Text | Icon | Hindi Label |
| :--- | :--- | :--- | :--- | :--- |
| `VERIFIED` | `--ok-soft` | `--ok` | ✓ (shield) | सत्यापित |
| `EXERCISE CAUTION` | `--warn-soft` | `--warn` | ⚠ (triangle) | चेतावनी |
| `SUSPICIOUS` | `--bad-soft` | `--bad` | ✕ (alert) | संदिग्ध |

**Pill States:**
| State | Visual Change |
| :--- | :--- |
| Default | Static pill with icon + text |
| Loading (scan in progress) | Skeleton shimmer in `--surface-2`, no text, pulsing `○` icon |
| Transition (verdict arriving) | Background cross-fade to verdict color (300ms) |

### 10.5 Seal Verdict Badges

These are used on the `/verify` page for the 6 possible PRAMAAN Seal verification outcomes:

| Verdict | Pill BG | Pill Text | Icon | Ring Color | Visual Treatment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `VERIFIED` | `--ok-soft` | `--ok` | ✓ Shield | Emerald | Solid glow, subtle pulse |
| `TAMPERED` | `--bad-soft` | `--bad` | ⚠ Broken shield | Crimson | Static, red `2px` border accent |
| `FORGED` | `--bad-soft` | `--bad` | ✕ Skull/cross | Crimson | Pulsing red glow (`1s infinite`) |
| `REVOKED` | `--warn-soft` | `--warn` | ⊘ Circle-slash | Amber | Static, amber `2px` border accent |
| `EXPIRED` | `--surface-2` | `--text-muted` | ⌛ Hourglass | Grey (`--border-strong`) | Dimmed, desaturated |
| `UNVERIFIED` | `--surface-2` | `--text-faint` | ? Question mark | Grey dashed ring | Dashed ring outline, faded |

### 10.6 Inputs

#### Paste Zone
Dashed border zone for pasting text or uploading files.

| State | Border | Background | Helper Text |
| :--- | :--- | :--- | :--- |
| Empty (default) | `2px dashed var(--border)` | `var(--surface-2)` | "Paste message, email, or upload file..." |
| Focused | `2px dashed var(--primary)` | `var(--surface-2)` | Same, dimmed |
| Drag-over | `2px solid var(--primary)` | `var(--primary-soft)` | "Drop file here" |
| Filled | `1px solid var(--border)` | `var(--surface)` | Content visible, editable |
| Validating | `1px solid var(--secondary)` | `var(--surface)` | Cyan pulse border |
| Error | `2px solid var(--bad)` | `var(--bad-soft)` | Error message in `--bad` |

### 10.7 Navigation Tabs

| State | Text Color | Bottom Indicator | Background |
| :--- | :--- | :--- | :--- |
| Inactive | `--text-muted` | None | `transparent` |
| Hover | `--text` | None | `--primary-soft` at `50%` |
| Active (current page) | `--primary` (dark) / `--primary` (light) | `2px` solid `--primary` bar, full width | `transparent` |
| Focus-Visible | `--text` | None | `--focus-ring` shadow |

Active indicator uses a sliding horizontal animation (`250ms spring`) when switching tabs.

### 10.8 Bilingual Toggle (हिं/EN)

**Type:** Segmented control (2-segment pill), `r-full`.

| Segment | Active State | Inactive State |
| :--- | :--- | :--- |
| **हिं** or **EN** | `--primary` bg, `--on-primary` text | `transparent` bg, `--text-muted` text |

**Sizing:** `72px` width × `32px` height. Active segment background slides left/right with `200ms ease`.
**Placement:** Desktop — Top Nav right cluster. Mobile — Hamburger drawer, above theme toggle.

### 10.9 Toast / Notification Component

Appears top-right (desktop) or top-center (mobile), over all content.

| Variant | Left Border | Icon | Background | Auto-Dismiss |
| :--- | :--- | :--- | :--- | :--- |
| Success | `3px --ok` | ✓ | `--surface` | 3s |
| Error | `3px --bad` | ✕ | `--surface` | 5s (or manual) |
| Warning | `3px --warn` | ⚠ | `--surface` | 5s |
| Info | `3px --primary` | ℹ | `--surface` | 4s |

**Motion:** Slide-in from right (300ms ease-out) → auto-dismiss slide-out (200ms ease-in).
**Structure:** `border-radius: r-md`, `--elev-3` shadow, max-width `380px`, close `×` button top-right.

### 10.10 Loading & Skeleton States

Used during scan processing (2–15 seconds) and initial page loads.

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--skeleton-base) 25%,
    var(--skeleton-shine) 50%,
    var(--skeleton-base) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite linear;
  border-radius: var(--r-md);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

**Skeleton versions needed for:**
| Component | Skeleton Shape |
| :--- | :--- |
| Trust Index Ring | Circle outline with shimmering arc |
| Explainability Row | Rectangular bar `100% × 48px` |
| Signal Chip | Rounded pill `120px × 36px` |
| Metric Card (sidebar) | Square `100% × 80px` |
| Verdict Pill | Pill `100px × 28px` |
| Sparkline | Flat line `120px × 32px` |

---

## 11. Screen Blueprints

### 11.1 Scan Workspace Console — Desktop (`/scan`)

```
┌─────────────────────────────────────────────────────────────────────────┐
   PRAMAAN·SHIELD    ( Scan   Verify   Report   Dashboard )    ☾   हिं/EN   ●
├─────────────────────────────────────────────────────────────────────────┤
│ CASE DETAILS     │               VERIFICATION CANVAS    │ VERDICT TELEMETRY     │
│ ┌──────────────┐ │                                      │   TRUST INDEX         │
│ │ Email Scan   │ │          ╭ AI-TEXT 87% ⚡             │     ╭─────╮           │
│ │ ID: #29402   │ │     ┌────┴──────────────────┐        │    /  08  \ SUSPICIOUS│
│ └──────────────┘ │     │  Translucent Message  │◀── registry   \ /100 / संदिग्ध │
│ [ Scan Content ] │     │  KYC verification...  │  fail   │     ╰─────╯           │
│                  │     └─────────┬─────────────┘        │                       │
│ AI PROBABILITY   │          ╰ URGENCY 9/10 ⚑            │ EXPLAINABILITY LEDGER │
│ 87% [Threat]     │                                      │ ✕ AI Text      [FAIL] │
│ ▁▂▅▇ sparkline   │ ┌──────────────────────────────────┐ │ ✕ Registry     [FAIL] │
│                  │ │ ⚠ Registry Mismatch              │ │ ⚠ Urgency      [WARN] │
│ URGENCY SCALE    │ │ Registered: sebi.gov.in          │ │ ✓ TLS Link     [PASS] │
│ 9/10 [Critical]  │ │ Scanned: sebi-gov.in             │ │ ────────────────────  │
│ ●●●●●●●●●○       │ └──────────────────────────────────┘ │ [ Report SEBI SCORES ]│
└──────────────────┴──────────────────────────────────────┴───────────────────────┘
```

---

### 11.2 Scan Workspace Console — Mobile (`/scan`)

```
┌──────────────────────────────────┐
│ ☰  PRAMAAN·SHIELD       ☾  हिं  │  ← 56px top bar
├──────────────────────────────────┤
│                                  │
│  ┌────────────────────────────┐  │
│  │  📋 Paste or upload content │  │  ← Paste zone (full width)
│  │  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐  │  │
│  │  │                      │  │  │
│  │  │  "URGENT: Verify     │  │  │
│  │  │   your demat KYC..." │  │  │
│  │  │                      │  │  │
│  │  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘  │  │
│  └────────────────────────────┘  │
│                                  │
│  ┌──── Signal Badges ─────────┐  │  ← Stacked inline (no connectors)
│  │ ⚡ AI-TEXT 87%              │  │
│  │ ⚠ TYPOSQUAT: sebi-gov.in   │  │
│  │ ⚑ URGENCY 9/10             │  │
│  │ ✕ REGISTRY: Not found      │  │
│  └────────────────────────────┘  │
│                                  │
│        ╭───────────╮             │  ← Trust Ring (centered, 160px)
│       / SUSPICIOUS \             │
│      /     08      \             │
│     |     /100      |            │
│      \   संदिग्ध   /             │
│       \            /             │
│        ╰───────────╯             │
│                                  │
│  ┌──── Explainability ────────┐  │  ← Accordion (expandable)
│  │ ▸ ✕ AI Text         [FAIL]│  │
│  │ ▸ ✕ Registry        [FAIL]│  │
│  │ ▸ ⚠ Urgency         [WARN]│  │
│  │ ▸ ✓ TLS Link        [PASS]│  │
│  └────────────────────────────┘  │
│                                  │
├──────────────────────────────────┤  ← Sticky bottom bar (64px)
│ [ 📢 Report SCORES ]  [ 📞 1930 ]│
└──────────────────────────────────┘
```

**Key mobile adaptations:**
*   Signal chips → stacked vertical badge list (no absolute positioning, no SVG connectors).
*   Trust Ring → centered below content, reduced to `160px`.
*   Explainability ledger → accordion with tap-to-expand rows.
*   Action buttons → sticky bottom bar (always visible, thumb-zone placement).
*   Left/Right sidebars → collapsed into main scroll flow.

---

### 11.3 Verify Seal Console — Desktop (`/verify`)

```
┌─────────────────────────────────────────────────────────────────────────┐
   PRAMAAN·SHIELD    ( Scan  ▸Verify   Report   Dashboard )    ☾   हिं/EN   ●
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│           ┌──────────────────────────────────────────────┐              │
│           │          VERIFY PRAMAAN SEAL                  │              │
│           │                                              │              │
│           │   ┌────────────────┐    OR    ┌────────────┐ │              │
│           │   │  📷 Scan QR    │         │ Seal ID:   │ │              │
│           │   │  ┌──────────┐  │         │ ┌────────┐ │ │              │
│           │   │  │ camera   │  │         │ │PRMN-...│ │ │              │
│           │   │  │ viewfinder│  │         │ └────────┘ │ │              │
│           │   │  └──────────┘  │         │ [Verify ➜] │ │              │
│           │   └────────────────┘         └────────────┘ │              │
│           └──────────────────────────────────────────────┘              │
│                                                                         │
│                        ↓ RESULT CARD ↓                                  │
│                                                                         │
│           ┌──────────────────────────────────────────────┐              │
│           │  ╭─────╮                                     │              │
│           │ / ✓ OK  \   VERIFIED — सत्यापित               │              │
│           │ \ /100 /                                     │              │
│           │  ╰─────╯                                     │              │
│           │                                              │              │
│           │  Signer:    SEBI (Securities and Exchange     │              │
│           │             Board of India)                   │              │
│           │  Reg. No:   REGULATOR                        │              │
│           │  Signed:    8 July 2026, 10:30 UTC           │              │
│           │  Valid:     8 July 2026 → 8 Oct 2026         │              │
│           │  Content:   ✓ Intact (hash matches)          │              │
│           │  Status:    ✓ Active (not revoked)           │              │
│           │                                              │              │
│           │  [📄 View Original]   [📋 Copy Details]       │              │
│           └──────────────────────────────────────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Verify — 6 Verdict Visual States

The result card adapts its entire visual treatment based on the seal verification outcome:

```
VERIFIED:                     TAMPERED:                     FORGED:
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│  ╭─────╮        │          │  ╭─────╮        │          │  ╭─────╮ ⚡PULSE│
│ / ✓ 98  \ ──ok  │          │ / ⚠ ── \  ──bad │          │ / ✕ ── \ ──bad  │
│ \ /100 /        │          │ \ /100 /        │          │ \ /100 /        │
│  ╰─────╯        │          │  ╰─────╯        │          │  ╰─────╯        │
│ VERIFIED        │          │ TAMPERED        │          │ FORGED          │
│ सत्यापित         │          │ छेड़छाड़          │          │ जाली             │
│ Signed by SEBI  │          │ Content differs │          │ Not from a      │
│ Content intact  │          │ from what was   │          │ registered      │
│                 │          │ signed          │          │ entity key      │
└──green glow─────┘          └──red accent─────┘          └──red pulsing───┘

REVOKED:                      EXPIRED:                      UNVERIFIED:
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│  ╭─────╮        │          │  ╭ ─ ─ ─╮       │          │  ╭ ╌ ╌ ╌╮       │
│ / ⊘ ── \ ──warn │          │ / ⌛ ── \ ──grey │          │ / ? ── \ ──faint│
│ \ /100 /        │          │ \ /100 /        │          │ \ /100 /        │
│  ╰─────╯        │          │  ╰ ─ ─ ─╯       │          │  ╰ ╌ ╌ ╌╯       │
│ REVOKED         │          │ EXPIRED         │          │ UNVERIFIED      │
│ रद्द             │          │ अवधि समाप्त      │          │ असत्यापित        │
│ Seal was revoked│          │ Seal outside    │          │ No PRAMAAN Seal │
│ by issuer       │          │ validity window │          │ found           │
└──amber accent───┘          └──grey dimmed────┘          └──dashed grey───┘
```

---

### 11.4 Verify Seal Console — Mobile (`/verify`)

```
┌──────────────────────────────────┐
│ ☰  PRAMAAN·SHIELD       ☾  हिं  │
├──────────────────────────────────┤
│                                  │
│  VERIFY PRAMAAN SEAL             │
│                                  │
│  ┌────────────────────────────┐  │
│  │  📷 Tap to scan QR code    │  │  ← Full-width camera
│  │  ┌──────────────────────┐  │  │
│  │  │                      │  │  │
│  │  │     [viewfinder]     │  │  │
│  │  │                      │  │  │
│  │  └──────────────────────┘  │  │
│  └────────────────────────────┘  │
│                                  │
│  ── or enter Seal ID ──          │
│  ┌────────────────────────────┐  │
│  │ PRMN-2026-SEBI-A3F2C      │  │
│  └────────────────────────────┘  │
│  [ Verify ➜ ]                    │
│                                  │
│  ┌──── Result Card ───────────┐  │
│  │       ╭───────╮            │  │
│  │      / ✓ 98   \            │  │
│  │     |  /100    |           │  │
│  │      \सत्यापित /            │  │
│  │       ╰───────╯            │  │
│  │                            │  │
│  │  Signer: SEBI             │  │
│  │  Signed: 8 Jul 2026       │  │
│  │  Content: ✓ Intact        │  │
│  │  Status: ✓ Active         │  │
│  │                            │  │
│  │  [📄 View]    [📋 Copy]    │  │
│  └────────────────────────────┘  │
│                                  │
└──────────────────────────────────┘
```

---

### 11.5 Dashboard — Desktop (`/dashboard`)

```
┌─────────────────────────────────────────────────────────────────────────┐
   PRAMAAN·SHIELD    ( Scan   Verify   Report  ▸Dashboard )    ☾   हिं/EN   ●
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │ TOTAL SCANS │ │ FAKES FOUND │ │ SEALS       │ │ REPORTS     │      │
│  │   15,420    │ │    4,218    │ │ VERIFIED    │ │ GENERATED   │      │
│  │   ▁▂▃▅▇    │ │   ▁▃▅▇▅    │ │     892     │ │    1,256    │      │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘      │
│                                                                         │
│  ┌──────────────────────────────┐ ┌──────────────────────────────────┐  │
│  │  THREAT DISTRIBUTION         │ │  TOP FLAGGED CONTENT             │  │
│  │  ┌────────────────────────┐  │ │                                  │  │
│  │  │   Donut / Bar chart    │  │ │  1. BSE CEO Deepfake      847x  │  │
│  │  │   by content_type      │  │ │  2. Fake KYC Email        412x  │  │
│  │  │   Text | Video | Audio │  │ │  3. Zerodha Phishing      289x  │  │
│  │  └────────────────────────┘  │ │  4. Groww Clone SMS       156x  │  │
│  └──────────────────────────────┘ └──────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Stats cards:** Each stat card has:
*   `label-sm` uppercase label at top.
*   `metric-lg` large number centered.
*   Sparkline at bottom.
*   Background: `--surface` with `1px --glass-border`.
*   Hover: lift `-2px` + `--elev-2`.

---

### 11.6 Dashboard — Mobile (`/dashboard`)

```
┌──────────────────────────────────┐
│ ☰  PRAMAAN·SHIELD       ☾  हिं  │
├──────────────────────────────────┤
│                                  │
│  ┌──────────┐  ┌──────────┐     │  ← 2-column grid
│  │  SCANS   │  │  FAKES   │     │
│  │  15,420  │  │   4,218  │     │
│  │  ▁▂▃▅▇   │  │  ▁▃▅▇▅   │     │
│  └──────────┘  └──────────┘     │
│  ┌──────────┐  ┌──────────┐     │
│  │  SEALS   │  │ REPORTS  │     │
│  │    892   │  │   1,256  │     │
│  └──────────┘  └──────────┘     │
│                                  │
│  ┌────────────────────────────┐  │
│  │  THREAT DISTRIBUTION       │  │  ← Full-width chart
│  │  [horizontal bar chart]    │  │
│  └────────────────────────────┘  │
│                                  │
│  ┌────────────────────────────┐  │
│  │  TOP FLAGGED CONTENT       │  │
│  │  1. BSE CEO Deepfake 847x │  │
│  │  2. Fake KYC Email   412x │  │
│  │  3. Zerodha Phishing 289x │  │
│  └────────────────────────────┘  │
│                                  │
└──────────────────────────────────┘
```

---

## 12. Theming Implementation

*   Tokens mapped as CSS variables inside `[data-theme="light"]` and `[data-theme="dark"]`.
*   A toggler updates `document.documentElement.dataset.theme` and writes to `localStorage`.
*   System preference detection via `prefers-color-scheme: dark` media query as initial default.

---

## 13. Accessibility

*   All contrast ratios meet WCAG AA standards (minimum `4.5:1` for body text, `3:1` for large text).
*   Verdict elements must combine **text**, **icon** (✓/✕/⚠), **and color** to convey security state — never color alone.
*   Interactive triggers have a minimum hit area of `44px × 44px` (WCAG 2.5.8 Target Size).
*   All interactive elements show `:focus-visible` ring using `box-shadow: var(--focus-ring)`.
*   `outline: 2px solid transparent` preserved for Windows High Contrast Mode.
*   Screen reader: Trust scores announced as "Trust Score: 8 out of 100, Suspicious" (not just the number).
*   Reduced motion: `@media (prefers-reduced-motion: reduce)` — disable scan sweep, skeleton shimmer, and transition animations. Instant state changes instead.

---

## 14. Voice & Microcopy

*   Clear, direct sentence casing. Action button states name the outcome explicitly (e.g. *"Report to SEBI SCORES 2.0"*, *"Report Fraud to Helpline 1930"*, *"Download PDF Verification Report"*).
*   Standardized status labels: **Scan**, **Trust Index**, **Verdict**, **VERIFIED**, **EXERCISE CAUTION**, **SUSPICIOUS**.
*   Bilingual equivalents: **सत्यापित (VERIFIED)**, **संदिग्ध (SUSPICIOUS)**, **चेतावनी (EXERCISE CAUTION)**.
*   Seal-specific bilingual labels: **छेड़छाड़ (TAMPERED)**, **जाली (FORGED)**, **रद्द (REVOKED)**, **अवधि समाप्त (EXPIRED)**, **असत्यापित (UNVERIFIED)**.

---

## 15. Do / Don't

| ✅ Do | ❌ Don't |
| :--- | :--- |
| Use glassy card panels with glowing 1px borders | Use heavy shadows or solid grey bordered boxes |
| Use Obsidian Navy base and Indigo/Cyan brand accents | Use medical patient diagrams or musculoskeletal refs |
| Place floating threat annotation cards over text | Use padlock or binary code background clichés |
| Display Trust Index Ring as the core visual anchor | Compete it with multiple dials of equal weight |
| Pair every verdict color with clear text & icon | Rely on red/green colors alone for status |
| Design mobile-first, then scale up to desktop | Design desktop-only and shrink to mobile |
| Show skeleton loading states during 2-15s scans | Show blank screens or generic spinners |
| Use the standardized verdict enum labels | Invent new labels per page (Threat Detected, DO NOT TRUST, etc.) |
| Define all component states (hover, focus, loading, disabled) | Define only the default/resting state |
| Make touch targets minimum 44px × 44px | Use tiny tap targets that frustrate mobile users |
