# 📄 Product Requirements Document (PRD)

## PRAMAAN-SHIELD (प्रमाण शील्ड)

**A Unified Detection, Authentication & Redressal Engine for Securities Market Communications**

---

| Field | Detail |
| :--- | :--- |
| **Product Name** | PRAMAAN-SHIELD |
| **Version** | 1.0 |
| **Date** | July 2026 |
| **Competition** | SEBI Securities Market TechSprint 2026 — Problem Statement 1 |
| **Theme** | AI-Driven Detection of Synthetic Media and Phishing Attacks in Securities Markets |
| **Team** | Black Ghost |
| **Team Lead** | Prakash Kumar Shiromani |
| **Team Members** | Aditya Kumar Yadav, Nikhil Verma, Ambuj Kumar, Diya Shukla |
| **Status** | In Development |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Philosophy](#3-product-vision--philosophy)
4. [Target Users & Channels](#4-target-users--channels)
5. [Product Architecture](#5-product-architecture)
6. [Feature Requirements — Pillar A: Detection](#6-feature-requirements--pillar-a-detection)
7. [Feature Requirements — Pillar B: Authentication](#7-feature-requirements--pillar-b-authentication)
8. [Feature Requirements — Pillar C: Redressal](#8-feature-requirements--pillar-c-redressal)
9. [Unified Trust Score](#9-unified-trust-score-0100)
10. [Technology Stack](#10-technology-stack)
11. [Web Application Pages](#11-web-application-pages)
12. [Business Model](#12-business-model)
13. [Non-Functional Requirements](#13-non-functional-requirements)
14. [DPDP Act 2023 Compliance](#14-dpdp-act-2023-compliance)
15. [Scope Classification — Real vs Mocked](#15-scope-classification--real-vs-mocked)
16. [Evaluation Criteria Mapping](#16-evaluation-criteria-mapping)
17. [Demo Script](#17-demo-script-2-minutes)
18. [Performance Benchmarks](#18-performance-benchmarks)
19. [Roadmap](#19-roadmap)
20. [Differentiators](#20-differentiators)
21. [Risks & Mitigations](#21-risks--mitigations)
22. [Submission Summary](#22-submission-summary-copy-paste-ready)

---

## 1. Executive Summary

PRAMAAN-SHIELD is a **three-pillar trust engine** designed to protect retail investors in India's securities markets from deepfake videos, phishing attacks, voice clone scams, and fraudulent communications.

> **One-Liner Pitch:** *"Pramaan-Shield: Proof check karne ka sabse fast aur robust system."*

The system uniquely addresses **both sides** of the trust problem:

- **Detection** — catches AI-generated attacks (phishing, voice clones, deepfakes)
- **Authentication** — lets SEBI/exchanges/companies cryptographically prove their communications are real
- **Redressal** — one-tap complaint filing to close the investor protection loop

The authentication half is what makes this a **systemic fix** rather than a point solution — it's exactly the "verification framework" gap SEBI has publicly flagged as needing.

Everything converges into a **single Trust Score (0–100)** with a plain-language explainability breakdown, delivered bilingually in **Hindi and English**.

---

## 2. Problem Statement

### 2.1 Market Crisis

| Fact | Source |
| :--- | :--- |
| BSE CEO deepfake (Jan 2026) — fake stock tips, resurfaced in March via WhatsApp | BSE Advisory |
| Fraud networks distribute via 38 WhatsApp funnels in one day, cost $5 | Industry Reports |
| Deepfake financial fraud **550% increase** (2019–2024), projected loss **₹70,000 crore** | Deloitte / McAfee |
| Ambani, Tata, Narayana Murthy, Virat Kohli deepfakes for fake trading apps | News Reports |
| SEBI Nov 2025 warning: scammers impersonate registered intermediaries | SEBI Circular |
| 1 May 2026 mandate: intermediaries must display registration on social media | SEBI Mandate |

### 2.2 Three Unsolved Gaps

| Gap | Current Reality |
| :--- | :--- |
| **Detection** | No real-time "scan before you trust" tool for citizens |
| **Authentication** | No mechanism to verify if a communication from SEBI/exchanges is genuine |
| **Redressal** | Filing a SCORES complaint takes 30+ minutes — retail investors don't bother |

> **Key Insight:** SEBI's current response is **reactive** — video goes viral → months later advisory → video resurfaces. **No proactive citizen-facing solution exists.** PRAMAAN-SHIELD is designed to be that proactive solution.

---

## 3. Product Vision & Philosophy

> **Core Philosophy:** *"Don't just catch fakes — prove what's real."*

PRAMAAN-SHIELD provides a two-sided trust layer for securities markets:

1. **Detect** the fake → through AI/ML models and deterministic hash matching
2. **Prove** the real → through cryptographic signatures (PRAMAAN Seal)
3. **Act** on fraud → through automated complaint generation

This bidirectional approach (detect + authenticate) creates a **structural moat** — unlike pure detection, which is an arms race, authentication is deterministic: a seal verifies only against the entity's **registry-pinned public key**, so it cannot be forged by anyone who does not hold that entity's private key (see [SECURITY.md](SECURITY.md)).

---

## 4. Target Users & Channels

| User Segment | Channel(s) Addressed | What They Get |
| :--- | :--- | :--- |
| **Retail / First-Gen Investors** | WhatsApp, Telegram, SMS, Email, YouTube, Instagram | Free web app + Telegram bot → forward anything suspicious → instant verdict (Hindi/English) |
| **Brokers & Intermediaries** | Client communication pipelines, internal SOC | API to bulk-screen inbound/outbound messages before they reach clients |
| **SEBI / Exchanges / Listed Companies** | Outbound circulars, press releases, exec videos | Signing tool to issue PRAMAAN Seal on every official release |

### 4.1 User Personas

**Persona 1: Ramesh (Retail Investor)**
- First-generation investor, age 35–55
- Gets stock tips on WhatsApp groups
- Cannot differentiate a deepfake CEO video from real
- Doesn't know SEBI SCORES exists
- **Need:** One-tap "is this legit?" answer in Hindi

**Persona 2: Priya (Compliance Officer at Brokerage)**
- Works at a registered intermediary
- Receives client complaints about phishing emails impersonating her firm
- **Need:** Bulk screening API + ability to sign official communications

**Persona 3: SEBI Regulatory Authority**
- Issues circulars and press releases
- Wants to combat impersonation
- Aligns with May 2026 mandate
- **Need:** Signing portal for PRAMAAN Seals on official communications

---

## 5. Product Architecture

### 5.1 High-Level Architecture — Three Pillars

```
┌───────────────────────────────────────────────────────────────────────┐
│                        PRAMAAN TRUST ENGINE                          │
│              Unified Trust Score + Explainability Layer               │
├──────────────────────┬──────────────────────┬─────────────────────────┤
│   PILLAR A           │   PILLAR B           │   PILLAR C             │
│   DETECTION          │   AUTHENTICATION     │   REDRESSAL            │
│   (Inbound)          │   (Outbound)         │   (Action)             │
│                      │                      │                        │
│   "Is this fake?"    │   "Is this real?"    │   "Report instantly"   │
├──────────────────────┼──────────────────────┼─────────────────────────┤
│ 1. Hash Registry     │ Digital Signature    │ SEBI SCORES            │
│    (instant lookup)  │ (ECDSA + QR Code)    │ auto-complaint         │
│                      │                      │                        │
│ 2. Text/Email/SMS    │ C2PA Content         │ Cybercrime 1930        │
│    Phishing Detector │ Credentials          │ auto-complaint         │
│                      │                      │                        │
│ 3. Voice Clone       │ SEBI Registry        │ Evidence Package       │
│    Detector          │ Lookup               │ (hash, transcript,     │
│    (AASIST/RawNet2)  │                      │  timestamp, AI report) │
│                      │                      │                        │
│ 4. Video Deepfake    │ Append-Only Ledger   │                        │
│    Detector          │ (audit trail)        │                        │
│    (CNN+rPPG+lip)    │                      │                        │
│                      │                      │                        │
│ 5. Social Media      │ Public Verify        │                        │
│    Manipulation      │ Portal + QR Scanner  │                        │
│    Detector          │                      │                        │
├──────────────────────┴──────────────────────┴─────────────────────────┤
│                         OUTPUT LAYER                                  │
│  Unified Trust Score (0-100) + Explainability Breakdown               │
│  🌐 Hindi + English output  •  📱 Mobile-first web app               │
└───────────────────────────────────────────────────────────────────────┘
```

### 5.2 Detection Pipeline Flow

```
User submits content (message/email/voice/video)
  via Web App or Telegram Bot
        ↓
┌─────────────────────────────────────┐
│ STEP 1: Perceptual Hash Check       │
│ (pHash/videohash → Redis lookup)    │
│ Match? → KNOWN FAKE (<50ms)         │
│ No match? → Continue to ML modules  │
└─────────────────────────────────────┘
        ↓ (if new content)
┌─────────────────────────────────────┐
│ STEP 2: Parallel Analysis           │
│ ┌───────────┐ ┌──────────────────┐  │
│ │ Text:     │ │ Voice:           │  │
│ │ 4-layer   │ │ AASIST + RawNet2 │  │
│ │ pipeline  │ │ anti-spoofing    │  │
│ └───────────┘ └──────────────────┘  │
│ ┌───────────┐ ┌──────────────────┐  │
│ │ Video:    │ │ SEBI Registry:   │  │
│ │ CNN+rPPG  │ │ Entity lookup    │  │
│ │ +lip-sync │ │ cross-check      │  │
│ └───────────┘ └──────────────────┘  │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ STEP 3: Trust Score Aggregation     │
│ Weighted combination → 0-100 score  │
│ + Full explainability breakdown     │
└─────────────────────────────────────┘
        ↓ (if score < 30)
┌─────────────────────────────────────┐
│ STEP 4: One-Tap Complaint           │
│ Auto-generated SCORES / 1930        │
│ template with evidence attached     │
└─────────────────────────────────────┘
```

### 5.3 Authentication Flow

```
SIGNING (Entity Side):
  Verified entity → PRAMAAN Portal
        ↓
  Upload official communication
        ↓
  System generates:
    → SHA-256 content hash
    → ECDSA digital signature (entity's private key)
    → Timestamp + SEBI registration number
    → QR code embedding all above
        ↓
  PRAMAAN Seal embedded in communication

VERIFICATION (Investor Side):
  Investor encounters PRAMAAN Seal
        ↓
  Opens web app → scans QR / enters Seal ID
        ↓
  System checks (in order):
    1️⃣ Resolve trust anchor from SEBI REGISTRY (entity's pinned
        public key) — NEVER from the QR/seal payload
    2️⃣ Signature valid under that REGISTERED key?
    3️⃣ Re-compute SHA-256 of the PRESENTED content →
        does it match the signed content_hash?
    4️⃣ Seal status == active (not revoked)?
    5️⃣ Timestamp within [not_before, not_after] window?
        ↓
  Result:
    ✅ VERIFIED  — "Signed by SEBI, 8 July 2026, content intact"
    🚫 FORGED    — "Signature not from a registered entity key"
    🚫 TAMPERED  — "Presented content differs from what was signed"
    🚫 REVOKED   — "Seal was revoked by issuer"
    ⌛ EXPIRED   — "Seal outside its validity window"
    ❌ UNVERIFIED — "No PRAMAAN Seal found"
```

> **🔐 Security note:** The trust anchor (public key) is resolved from the
> SEBI-side registry, **never** from the key travelling inside the QR — this
> is what makes forgery impossible. Full PKI design, threat model, and verify
> pseudocode are in **[SECURITY.md](SECURITY.md)**.

---

## 6. Feature Requirements — Pillar A: Detection

### Module A1: Perceptual Hash Registry — FIRST CHECK, FASTEST

| Attribute | Specification |
| :--- | :--- |
| **Purpose** | Instant lookup against database of known fakes — no ML needed |
| **Input** | Video, image, or text content |
| **Hash Algorithm** | pHash (images), videohash (video), text hash (messages) |
| **Storage** | Redis in-memory hash index |
| **Match Criteria** | Hamming distance ≤ 10 |
| **Priority** | **P0** — First check in pipeline, cheapest and fastest |

**Functional Requirements:**

| ID | Requirement |
| :--- | :--- |
| FR-A1.1 | Generate 64-bit perceptual hash for every uploaded video/image |
| FR-A1.2 | Redis lookup with Hamming distance threshold ≤ 10 |
| FR-A1.3 | On match → return `KNOWN FAKE` with flagging date, source, detection count |
| FR-A1.4 | On no match → pass content to next detection modules |
| FR-A1.5 | Auto-generate **10–15 variant hashes (Hash Families)** on flagging: Cropped (10%, 20%, 30%), Mirrored (horizontal flip), Re-encoded (different quality levels), Speed changed (0.8x, 1.2x), With/without watermark overlay |
| FR-A1.6 | Pre-populate registry with 50+ known fake financial videos/images at launch |
| FR-A1.7 | Verified entities (SEBI, exchanges) can fast-track flag → instant registry entry (only trusted sources write directly) |
| FR-A1.8 | Community signals: user flags on the same content feed a **human/verified-entity review queue** — they do **NOT** auto-escalate into the registry (prevents poisoning of legitimate content) |
| FR-A1.9 | A `KNOWN FAKE` verdict (which applies a large trust penalty) requires **two-factor confirmation** — perceptual-hash match **AND** a secondary check (second hash algorithm or lightweight classifier) — to prevent collision-driven false positives |

**Performance Targets:**

| Metric | Target |
| :--- | :--- |
| Lookup speed | < 50ms |
| Throughput | 10K hashes/sec |
| False positive rate | Near zero (deterministic) |
| Pre-populated at launch | 50+ known fakes |

> **BSE CEO Case Solved Structurally:** Flagged once in January → hash family stored → March resurface attempt → instantly blocked. Problem solved STRUCTURALLY, not reactively.

---

### Module A2: Text/Email/SMS Phishing Detector ⭐ CRITICAL MODULE

| Attribute | Specification |
| :--- | :--- |
| **Purpose** | Analyze text content for phishing, AI-generated scam text, domain spoofing |
| **Input** | Email, SMS, WhatsApp messages, social media posts |
| **Priority** | **P0** |

**4-Layer Detection Pipeline:**

```
Input: Text/Email/SMS content
     ↓
┌─────────────────────────────────────────────────────┐
│  LAYER 1: AI-Generated Text Detection               │
│  Perplexity + Burstiness analysis                    │
│  → Is this written by an LLM or a human?            │
├─────────────────────────────────────────────────────┤
│  LAYER 2: Phishing Pattern Classifier               │
│  Fine-tuned on phishing corpora                      │
│  → Does this match known scam patterns?             │
├─────────────────────────────────────────────────────┤
│  LAYER 3: Domain & Sender Verification              │
│  SPF/DKIM/DMARC + Typosquatting check               │
│  → Is the sender who they claim to be?              │
├─────────────────────────────────────────────────────┤
│  LAYER 4: Securities-Specific Red Flags             │
│  SEBI registry cross-check + urgency scoring        │
│  → Does this content match securities fraud patterns?│
└─────────────────────────────────────────────────────┘
     ↓
Combined phishing score + explainability
```

#### Layer 1: AI-Generated Text Detection
| ID | Requirement |
| :--- | :--- |
| FR-A2.1 | Perplexity analysis — LLM text has consistently LOW perplexity |
| FR-A2.2 | Burstiness analysis — LLM text is unnaturally UNIFORM vs human variation |
| FR-A2.3 | Output: `{ai_generated_probability: 0.87, features: {perplexity: "low", burstiness: "low"}}` |

*Honest accuracy: ~85-90% on English, lower on short texts — this is a SIGNAL, not definitive*

#### Layer 2: Phishing Pattern Classifier
| ID | Requirement |
| :--- | :--- |
| FR-A2.4 | Training data: PhishTank, APWG, Nigerian fraud corpus + Indian financial phishing samples |
| FR-A2.5 | Model: Gemini 1.5 Flash with few-shot prompting OR fine-tuned classifier |
| FR-A2.6 | Social engineering urgency scoring (0–10 scale) |

**Patterns to Detect:**
- Urgency: "account block", "account freeze", "kyc expire"
- Authority impersonation: "SEBI notice", "penalty"
- Scarcity: "limited time", "last chance", "only 5 spots left"
- Unrealistic promises: "guaranteed return", "500% in 30 days"
- Secrecy: "insider tip", "confidential", "don't tell anyone"

```python
# Urgency patterns specific to Indian securities market:
URGENCY_PATTERNS = [
   "account block", "account freeze", "kyc expire",
   "sebi notice", "penalty", "last chance",
   "act now", "limited time", "guaranteed return",
   "insider tip", "confidential", "don't tell anyone"
]
# Score: 0 (no urgency) → 10 (extreme urgency)
```

#### Layer 3: Domain & Sender Verification
| ID | Requirement |
| :--- | :--- |
| FR-A2.7 | Domain typosquatting detection via Levenshtein distance against 200+ legitimate Indian domains |
| FR-A2.8 | SPF/DKIM/DMARC email header validation (for raw .eml inputs only) |

**Typosquatting Examples:**
```
Legitimate domains:          Scam domains (Levenshtein ≤ 3):
zerodha.com          →       zerrodha.com, zer0dha.com, zerodha-login.com
sebi.gov.in          →       serbi-gov.in, sebi-gov.in, sebi.gov.org
groww.in             →       gr0ww.in, groww-app.in
angelone.in          →       angel-one.in, angelone-trade.in
```

> **⚠️ Limitation:** SPF/DKIM/DMARC validation only works on raw email headers (.eml files). If user pastes email TEXT, header validation is not possible — only Layers 1, 2, and 4 fire. Be transparent about this.

#### Layer 4: Securities-Specific Red Flags
| ID | Requirement |
| :--- | :--- |
| FR-A2.9 | Extract entity names/registration numbers via Gemini NER |
| FR-A2.10 | Match against SEBI intermediary database (pre-parsed JSON) |
| FR-A2.11 | Claim verification against authenticated registry (Pillar B) |

**SEBI Registry Results Examples:**
- ✅ "Zerodha — SEBI Registered (INZ000031633)"
- ❌ "XYZ Trading — NOT FOUND in SEBI registry"
- ⚠️ "Zerodha" mentioned but communication channel is unofficial → "Entity exists but communication is UNVERIFIED"

#### Combined Phishing Output Example:
```
┌───────────────────────────────────────────────┐
│  📧 TEXT/PHISHING ANALYSIS                    │
│                                               │
│  Phishing Score: 8.7/10 🔴 HIGH RISK         │
│                                               │
│  Breakdown:                                   │
│  🚫 AI-Generated: 87% probability (LLM text) │
│  🚫 Urgency: 9/10 ("account will be blocked") │
│  🚫 Domain: zerrodha.com (typosquat of        │
│     zerodha.com, distance: 1)                 │
│  🚫 Registry: "XYZ Capital" NOT registered    │
│  ⚠️ SPF: FAIL | DKIM: FAIL                   │
│  🚫 Claim: No matching SEBI circular found    │
│                                               │
│  Verdict: LIKELY PHISHING SCAM                │
└───────────────────────────────────────────────┘
```

**Performance Targets:**

| Metric | Target | Honest Note |
| :--- | :--- | :--- |
| Phishing detection F1 | 90%+ on benchmark | Real-world will be 80-85% — combined with other layers compensates |
| AI-text detection | 85-90% on English | Lower on short texts and Hindi content |
| Typosquat detection | ~99% | Deterministic (Levenshtein), very reliable |
| SPF/DKIM/DMARC | 100% | Only works on raw email headers, not pasted text |

---

### Module A3: Voice Clone Detector

| Attribute | Specification |
| :--- | :--- |
| **Purpose** | Detect AI-generated/cloned voice in audio calls or recorded messages |
| **Models** | AASIST + RawNet2 (pre-trained on ASVspoof-style data) |
| **Input** | Audio files (voice notes, call recordings) |
| **Priority** | **P0** |

**Functional Requirements:**

| ID | Requirement |
| :--- | :--- |
| FR-A3.1 | AASIST model — state-of-the-art anti-spoofing (2022), graph attention network |
| FR-A3.2 | RawNet2 — raw waveform synthesis artifact detection |
| FR-A3.3 | Combined voice authenticity score |
| FR-A3.4 | Output: `"Voice Liveness: 23% — LIKELY SYNTHETIC"` |

**Detection Targets:**
- Voice clones of CEOs/regulators giving fake stock tips
- AI-generated phone calls impersonating brokers
- Synthetic voice messages on WhatsApp/Telegram

**Pipeline:**
```
Audio input → Feature extraction (raw waveform)
   ↓
AASIST model → Anti-spoofing score
   ↓
RawNet2 model → Synthesis artifact detection
   ↓
Combined voice authenticity score
   ↓
"Voice Liveness: 23% — LIKELY SYNTHETIC"
```

| Metric | Value | Honest Note |
| :--- | :--- | :--- |
| EER on ASVspoof | ~1-2% | Benchmark performance, real WhatsApp audio will be worse |
| Real-world estimate | ~85-90% | Compression artifacts may confuse the model |
| Approach | Pre-trained, no custom training | Download → integrate → test on Indian samples |

---

### Module A4: Video Deepfake Detector

| Attribute | Specification |
| :--- | :--- |
| **Purpose** | Detect synthetic/manipulated video — face swaps, lip-sync deepfakes, fully generated videos |
| **Models** | EfficientNet / XceptionNet (FaceForensics++ pre-trained) |
| **Input** | Video files |
| **Priority** | **P0** |

**Three-Layer Video Analysis:**

1. **Frame-Level CNN** — Pre-trained model analyzes individual frames for manipulation artifacts
2. **Temporal Consistency** — Checks smooth frame-to-frame transitions; deepfakes have subtle flickering edges, inconsistent lighting
3. **Biological Signal Checks:**
   - **rPPG (Remote Photoplethysmography)** — Real human skin shows subtle color changes due to blood flow/pulse. Deepfakes CAN'T reproduce this — **hardest thing for generative video to fake**
   - **Blink Rate Analysis** — Humans blink 15-20 times/minute. Deepfakes blink at wrong intervals
   - **Lip-Sync Mismatch** — Audio-visual correlation check

**Functional Requirements:**

| ID | Requirement |
| :--- | :--- |
| FR-A4.1 | Frame-level manipulation detection with CNN |
| FR-A4.2 | Temporal consistency analysis between frames |
| FR-A4.3 | rPPG biological signal detection (partial for hackathon, full in production) |
| FR-A4.4 | Blink rate analysis |
| FR-A4.5 | Lip-sync audio-visual correlation check |
| FR-A4.6 | Generate frame heatmaps showing manipulated regions |

**Output Example:**
```
Video Analysis:
🔴 Frame manipulation detected (confidence: 91%)
🔴 Temporal inconsistency at frames 120-145
🔴 rPPG signal: ABSENT (no biological pulse detected)
⚠️ Lip-sync: Minor mismatch detected
Frame heatmap: [visual overlay showing manipulated regions]
```

| Metric | Value | Honest Note |
| :--- | :--- | :--- |
| FaceForensics++ benchmark | ~95% | High quality, controlled videos |
| Real-world Indian WhatsApp | ~75-85% | Compressed, low-res — accuracy drops |
| rPPG | Conceptually strong | Partial implementation for hackathon, mention in pitch |

---

### Module A5: Social Media Manipulation Detector

| Attribute | Specification |
| :--- | :--- |
| **Purpose** | Detect coordinated inauthentic behavior and fake financial social media posts |
| **Priority** | **P2** — LOWEST build priority |

**Functional Requirements:**

| ID | Requirement |
| :--- | :--- |
| FR-A5.1 | Bot/coordination detection via posting-pattern graph analysis |
| FR-A5.2 | Fact-check against authenticated registry (Pillar B) |

> **⚠️ Honest Assessment:** Real-time social media crawling needs significant infrastructure (API access, rate limits, crawler setup). For hackathon: demo with pre-collected examples, position as "Phase 2" for production. Don't overclaim.

---

## 7. Feature Requirements — Pillar B: Authentication

| Attribute | Specification |
| :--- | :--- |
| **Purpose** | Enable SEBI/exchanges/intermediaries to cryptographically sign official communications |
| **Standard** | Aligned with C2PA Content Credentials (Adobe, Microsoft, BBC framework) |
| **Crypto** | ECDSA digital signatures |
| **Priority** | **P0** |

### 7.1 Entity Side — Issuing a PRAMAAN Seal

| ID | Requirement |
| :--- | :--- |
| FR-B1 | Entity authenticates to PRAMAAN signing portal via **strong auth** (mutual-TLS client cert in production / OAuth client-cert in demo). Entity identity is derived from the **authenticated session — never from a request body field** |
| FR-B2 | Upload official communication (circular, press release, video, statement) |
| FR-B3 | Generate SHA-256 content hash |
| FR-B4 | Sign with the **entity's OWN ECDSA private key** (per-entity keypair — no shared server key) |
| FR-B5 | Attach timestamp, SEBI registration number, and **validity window** (`not_before` / `not_after`) |
| FR-B6 | Embed pointers + signature into QR code (PRAMAAN Seal). The **public key is NOT embedded** — the verifier fetches it from the registry |
| FR-B7 | Record in **append-only, audited** ledger (who signed, when) — MongoDB for hackathon → permissioned ledger for production |
| FR-B7a | Support **revocation**: entity can mark a seal `revoked`; verification must honour it |

### 7.2 Investor Side — Verifying a PRAMAAN Seal

| ID | Requirement |
| :--- | :--- |
| FR-B8 | Open web app → "Verify Seal" page |
| FR-B9 | Scan QR code OR manually enter Seal ID |
| FR-B10 | **Check 1:** Resolve entity's public key from the **SEBI registry** (trust anchor), then verify signature under that pinned key — reject if entity/key not registered |
| FR-B11 | **Check 2:** Re-compute SHA-256 of the **presented content** and compare to the signed `content_hash` (real tamper check) |
| FR-B12 | **Check 3:** Seal `status == active` (not revoked) |
| FR-B13 | **Check 4:** Timestamp within `[not_before, not_after]` window |
| FR-B14 | Return clear verdict: `VERIFIED` / `TAMPERED` / `FORGED` / `REVOKED` / `EXPIRED` / `UNVERIFIED` with full details |

### 7.3 Why Authentication Wins

| Advantage | Detail |
| :--- | :--- |
| **Deterministic** | Cryptographic verification is deterministic — no ML confidence scores in the authentication path. (Detection remains probabilistic; the two are kept separate and never conflated.) |
| **Arms-race proof** | Deepfakes improve, but a signature that verifies only against a **registry-pinned entity key** cannot be forged by an attacker who does not hold that key |
| **SEBI mandate aligned** | Direct implementation of May 2026 requirement |
| **Unique** | NO OTHER TEAM will build this — everyone focuses on detection only |
| **Gap-filling** | Directly addresses SEBI's flagged gap: "no mechanism for an ordinary investor to verify official communications" |

> **🔐 Trust model:** Forgery resistance comes from **two** properties working
> together — (1) the public key is fetched from the SEBI registry, never from
> the seal itself, and (2) the presented content is re-hashed at verify time.
> See **[SECURITY.md](SECURITY.md)** for the full PKI design and threat model.

---

## 8. Feature Requirements — Pillar C: Redressal

| Attribute | Specification |
| :--- | :--- |
| **Purpose** | One-tap complaint filing with auto-generated templates and evidence |
| **Priority** | **P0** |

### Functional Requirements

| ID | Requirement |
| :--- | :--- |
| FR-C1 | Trigger when Trust Score < 30 |
| FR-C2 | Gemini 1.5 Flash auto-generates complaint description (Hindi + English) |
| FR-C3 | Evidence package auto-attached: content hash, AI analysis transcript, timestamp, screenshot/media reference, hash registry match details, entity registration status |
| FR-C4 | Pre-filled **SEBI SCORES** template: formal complaint, auto-selected category, entity details, evidence summary, investor details placeholder |
| FR-C5 | Pre-filled **cybercrime.gov.in (1930)** template: FIR-style, fraud category, evidence list, financial loss details, contact info placeholder |
| FR-C6 | User action options: 📋 Copy to clipboard, 📄 Download as PDF, 📧 Email to SEBI |

### Impact

| Before PRAMAAN | After PRAMAAN |
| :--- | :--- |
| 30+ minutes to file a complaint | 10 seconds |
| Most retail investors don't know SCORES exists | One-tap filing from scan results |
| No evidence attached | Evidence auto-attached (hash, analysis, timestamps) |
| English only | Bilingual (Hindi + English) |

> **⚠️ Honest Limitation:** SEBI SCORES has no public API. We generate the template — user copies/pastes/downloads. We do NOT claim auto-submission. This is transparent and realistic.

---

## 9. Unified Trust Score (0–100)

**One score. One answer. Full explainability.**

### 9.1 Score Calculation Logic

The score is **not** a naive "start at 100 and subtract" model (which lets a
sophisticated scam avoid every red flag and still score green). Instead:

- **Baseline = CAUTION.** Content starts neutral, not trusted.
- **Trust is EARNED** by *affirmative proof* the attacker cannot fake.
- **Hard gates** — any single strong fail caps the score in RED.

```python
# Conceptual model (exact weights kept internal — see SECURITY.md §7):

score = NEUTRAL_BASELINE            # e.g. 50 → "EXERCISE CAUTION", not 100

# --- HARD GATES: any one → RED, regardless of other signals ---
if hash_known_fake_confirmed:   return RED     # two-factor confirmed known fake
if seal_verdict in (FORGED, TAMPERED): return RED
if domain_is_typosquat:         return RED
if gemini_injection_attempt:    return RED     # message tried to manipulate analyzer

# --- AFFIRMATIVE PROOF: earns GREEN (attacker cannot fake these) ---
if valid_pramaan_seal:          score += STRONG_POSITIVE   # registry-pinned + intact
if exact_registry_match:        score += POSITIVE          # by registration_number
if verified_official_domain:    score += POSITIVE

# --- SOFT SIGNALS: nudge within a band, never cross a gate ---
score += weighted(ai_text_prob, urgency, voice_ml, video_ml)   # non-linear

trust_score = clamp(score, 0, 100)
```

> **Why this matters:** A scam that carefully avoids every negative signal still
> lands in **CAUTION (yellow)** — never green — because green requires
> affirmative proof (a valid seal or exact registry match) it cannot forge.
> Absence of red flags is never treated as safety.

### 9.2 Display

```
SUSPICIOUS:                              VERIFIED:
┌──────────────────────────┐            ┌──────────────────────────┐
│ TRUST SCORE: 8/100 🔴    │            │ TRUST SCORE: 98/100 ✅   │
│ "DO NOT TRUST"           │            │ "VERIFIED — SEBI"        │
│                          │            │                          │
│ 🚫 Hash: Known fake     │            │ ✅ Seal: SEBI signed     │
│ 🚫 Voice: Synthetic     │            │ ✅ Timestamp: Valid      │
│ 🚫 Registry: NOT found  │            │ ✅ Content: Intact      │
│ 🚫 Domain: Typosquat    │            │ ✅ Registry: Verified   │
│ ⚠️ rPPG: No pulse       │            │ ✅ C2PA: Valid          │
│                          │            │                          │
│ [📢 Report SCORES]      │            │ No action needed ✅      │
│ [📢 Report 1930]        │            │                          │
└──────────────────────────┘            └──────────────────────────┘
```

### 9.3 Score Color Coding

| Score Range | Color | Label |
| :--- | :--- | :--- |
| 70–100 | 🟢 Green | Likely Safe / Verified |
| 30–69 | 🟡 Yellow | Exercise Caution |
| 0–29 | 🔴 Red | Likely Fake / Suspicious |

### 9.4 Trust Score Requirements

| ID | Requirement |
| :--- | :--- |
| FR-TS1 | Aggregate signals from ALL detection/authentication modules |
| FR-TS2 | Display full explainability breakdown (which checks fired, what they found, contribution) |
| FR-TS3 | Plain-language output for non-technical users |
| FR-TS4 | Bilingual output (Hindi + English toggle) |

> **Why unified score matters:** Investor doesn't care which model flagged it. They want ONE answer: *"this is 92% likely fake"* or *"this is verified, signed by SEBI on July 8, 2026."*

---

## 10. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Next.js (React) | SSR, routing, mobile-first responsive, dark mode, bilingual UI |
| **Backend** | FastAPI (Python) | ML inference orchestration, API layer, async processing |
| **Database** | MongoDB | SEBI intermediary registry, seal records, scan history, user reports |
| **Cache** | Redis | In-memory hash index (10K lookups/sec), rate limiting |
| **AI/LLM** | Gemini 1.5 Flash | NER, complaint drafting, Hindi↔English translation, text analysis |
| **Voice ML** | AASIST + RawNet2 (pre-trained) | Voice clone and anti-spoofing detection on raw waveforms |
| **Video ML** | EfficientNet / XceptionNet (FaceForensics++ pre-trained) | Deepfake frame-level analysis with temporal consistency |
| **Cryptography** | ECDSA (Python `cryptography` library) | PRAMAAN Seal signing and verification |
| **Hashing** | pHash / videohash / imagehash | Perceptual hash generation for known-fake registry |
| **Messaging** | python-telegram-bot | Telegram bot interface for investors |

### System Architecture

```
┌───────────────────────────────────────────────────────┐
│                    FRONTEND                           │
│                Next.js (React)                        │
│      Dark mode • Mobile-first • Bilingual UI          │
│  Pages: / | /scan | /verify | /report                 │
│         /dashboard | /seal-portal                     │
├───────────────────────────────────────────────────────┤
│                    BACKEND                            │
│  ┌─────────────────────────────────────────────────┐  │
│  │            FastAPI (Python)                      │  │
│  │  • Video/image hashing (videohash/pHash)        │  │
│  │  • Voice analysis (AASIST/RawNet2 inference)    │  │
│  │  • Video deepfake analysis (CNN inference)      │  │
│  │  • Phishing text analysis pipeline              │  │
│  │  • PKI: Seal generation & verification (ECDSA)  │  │
│  │  • Gemini API calls (NER, translation, drafts)  │  │
│  │  • Trust score aggregation                      │  │
│  └─────────────────────────────────────────────────┘  │
│  ┌───────────────────┐  ┌───────────────────────┐     │
│  │   MongoDB          │  │     Redis             │     │
│  │  • SEBI registry   │  │  • Hash index         │     │
│  │  • Seal records    │  │  • Fast lookup cache  │     │
│  │  • Scan history    │  │  • Rate limiting      │     │
│  │  • User reports    │  │                       │     │
│  └───────────────────┘  └───────────────────────┘     │
│  ┌─────────────────────────────────────────────────┐  │
│  │            Gemini 1.5 Flash                      │  │
│  │  • NER (name/registration number extraction)    │  │
│  │  • Complaint template drafting                  │  │
│  │  • Hindi ↔ English translation                  │  │
│  │  • AI-generated text detection signal           │  │
│  └─────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────┐  │
│  │          Telegram Bot (PramaanikBot)             │  │
│  │  • Forward message → instant verdict            │  │
│  │  • Same backend API, different interface         │  │
│  └─────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

---

## 11. Web Application Pages

| Page | Route | Purpose |
| :--- | :--- | :--- |
| **Landing** | `/` | Hero — "Har message ka PRAMAAN lo", stats, how it works |
| **Scan** | `/scan` | Upload/paste content → run all detection modules → show Trust Score + explainability |
| **Verify** | `/verify` | Upload QR / enter Seal ID → verify PRAMAAN Seal authentication |
| **Report** | `/report` | Pre-filled complaint templates → copy/download/email |
| **Dashboard** | `/dashboard` | Stats: total scans, fakes detected, reports filed, top flagged content |
| **Seal Portal** | `/seal-portal` | (Demo) Entity portal to generate PRAMAAN Seals |

### UI/UX Requirements
- Mobile-first responsive design
- Dark mode as default
- Bilingual toggle: Hindi ↔ English
- Accessible for first-generation investors (minimal text input)
- Trust Score displayed prominently with color coding (Green/Yellow/Red)
- One-tap actions for complaint generation

---

## 12. Business Model

Market Size (TAM): 22 Crore+ demat accounts in India (CDSL + NSDL basis) — the addressable retail investor base directly exposed to this fraud vector.

| Segment | Model | Details |
| :--- | :--- | :--- |
| **B2C — Retail Investors** | **Free** | Web app + Telegram bot. Trust-building layer that drives organic adoption. Every scan improves detection accuracy. |
| **B2B — Brokers & Intermediaries** | **API Subscription (SaaS)** | Per-call or monthly subscription pricing. Plug into communication pipelines to screen inbound/outbound messages. |
| **B2G — SEBI & Exchanges** | **License** | PRAMAAN Seal authentication infrastructure as technical backbone for May 2026 mandate. Signing portal, QR verification, registry integration. |

### Long-Term Defensibility
- Authentication requires participation from verified entities (not just end users)
- Once SEBI/exchanges adopt Seal framework → **structural moat**
- Positioning for **SEBI Innovation Sandbox pilot** to validate in regulated environment before broader rollout

---

## 13. Non-Functional Requirements

| Requirement | Specification |
| :--- | :--- |
| **Latency — Hash Lookup** | < 50ms |
| **Latency — Full Analysis** | < 10 seconds for complete pipeline |
| **Throughput** | 10K hash lookups/sec |
| **Availability** | 99.9% uptime target |
| **Scalability** | Redis + MongoDB scale horizontally. Seal verification is O(1). |
| **Security** | ECDSA cryptographic signatures, HTTPS, no plaintext key storage |
| **Localization** | Hindi + English (Phase 2: Tamil, Bengali, Marathi) |
| **Accessibility** | Mobile-first, minimal text input, visual Trust Score indicator |
| **Data Retention** | Uploaded media auto-deleted after scan (60 sec buffer) |

---

## 14. DPDP Act 2023 Compliance

| Aspect | Implementation |
| :--- | :--- |
| **Data Minimization** | Only perceptual/content **hashes** + verdict metadata stored — **never** raw scanned text/media (which may contain phone, name, PAN) |
| **Consent** | Clear consent screen before any upload/scan |
| **Zero Media Retention** | Uploaded media auto-deleted after scan (60 sec buffer) |
| **Pseudonymization (not "anonymization")** | IP stored as **keyed HMAC-SHA256** with a secret salt — plain `SHA256(IP)` is reversible (2³² space) and is **not** used |
| **PII Redaction** | Any stored analysis transcript is PII-redacted; strict TTL applied |
| **No mandatory accounts** | No user login required for scanning |
| **Transparency** | Clear disclosure: what is processed, what is retained, how, why |
| **Hackathon** | Server-side ML (reliability for demo) |
| **Production** | On-device processing (WebAssembly/TFLite) — media never leaves phone |

> **Honesty note:** We deliberately claim **"data minimization + pseudonymization,"**
> not "zero PII / fully anonymized," because plain hashing of IPs is reversible.
> This precision is itself what regulatory judges look for. Full detail in
> **[SECURITY.md](SECURITY.md) §11**.

> 99% of teams ignore DPDP compliance. Including this shows regulatory maturity judges value.

---

## 15. Scope Classification — Real vs Mocked

### ✅ REAL (Actually Built & Working)

| Feature | Status | Evidence |
| :--- | :--- | :--- |
| Perceptual hash registry + lookup | Fully working | Redis, <50ms, pre-populated 50+ hashes |
| Text/email phishing analysis | Fully working | Gemini + domain check + urgency scoring |
| PRAMAAN Seal (sign + verify) | Fully working | ECDSA crypto, QR generation, verification portal |
| SEBI registry lookup | Working on scraped data | PDF → JSON, 100+ intermediaries |
| One-tap complaint templates | Fully working | SCORES + 1930 templates, bilingual |
| Unified Trust Score | Fully working | Weighted aggregation, explainability |
| Hindi + English output | Fully working | Gemini translation + pre-built templates |
| Telegram bot | Fully working | Forward message → instant verdict |
| Voice clone detection | Working (pre-trained) | AASIST on server, tested on Indian samples |
| Video deepfake detection | Working (pre-trained) | CNN frame analysis + heatmap visualization |

### ⚠️ PARTIALLY BUILT (Demo with Limitations)

| Feature | Reality | Positioning |
| :--- | :--- | :--- |
| rPPG biological signals | Partial — basic demo | "Production feature, validated conceptually" |
| SPF/DKIM/DMARC | Works on raw .eml files, not pasted text | "Full email pipeline in production, text-only for demo" |
| Hash families (auto-variants) | Basic implementation | "Expanding variant generation in production" |
| Social media manipulation | Pre-collected samples | "Phase 2: real-time integration with social APIs" |

### 🔲 MOCKED (Transparent About It)

| Feature | Reality | Positioning |
| :--- | :--- | :--- |
| SEBI SCORES auto-submission | No API exists — template generator | "Auto-submit pending SEBI API availability" |
| Real SEBI intermediary API | Scraped JSON, not live API | "Production: SEBI API integration" |
| C2PA full integration | Standard alignment mentioned | "Production roadmap: full C2PA compliance" |
| Append-only ledger | MongoDB for now | "Production: tamper-evident audit trail" |
| WhatsApp Business API | Not approved yet | "Telegram primary, WhatsApp in Phase 2" |
| Real company seals | Mock signatures | "Demo with mock entities — production: SEBI-mandated onboarding" |

---

## 16. Evaluation Criteria Mapping

| Criteria | How We Hit It | Strength |
| :--- | :--- | :--- |
| **Market Impact** | Direct investor protection — 3 gaps solved (auth + detect + redressal). SEBI's own identified problems. | ⭐⭐⭐⭐⭐ |
| **Technology Stack** | AI/ML (AASIST, CNN, rPPG) + Crypto (ECDSA, C2PA) + NLP (Gemini) + Registry + Hashing | ⭐⭐⭐⭐⭐ |
| **Feasibility** | Core modules working pre-hackathon. Pre-trained models, no custom training needed. | ⭐⭐⭐⭐ |
| **Scalability** | Redis hash lookup + MongoDB scale horizontally. Seal verification is O(1). | ⭐⭐⭐⭐⭐ |
| **SEBI Mandate Alignment** | Nov 2025 warning + May 2026 mandate — Seal IS the digital mandate implementation | ⭐⭐⭐⭐⭐ |
| **Innovation** | PRAMAAN Seal + Hash Families + One-tap Redressal + Unified Trust Score — unique combination no other team will have | ⭐⭐⭐⭐⭐ |

---

## 17. Demo Script (2 Minutes)

### Opening (10 sec)
> *"January 2026 — BSE CEO ka deepfake video. Fake stock tips. SEBI ne advisory nikali. March mein wahi video phir viral. Retail investors ke paas koi tool nahi hai verify karne ke liye. PRAMAAN hai woh tool."*

### Case 1 — PHISHING EMAIL CAUGHT (40 sec)
> *"Yeh email aaya — SEBI ke naam se, 'Your demat account will be blocked.' Paste karte hain PRAMAAN mein..."*

**→ Trust Score: 11/100 🔴**
- 🚫 AI-Generated: 87% (LLM-written text)
- 🚫 Domain: serbi-gov.in (typosquat of sebi.gov.in)
- 🚫 Urgency: 9/10 ("account will be blocked in 24 hours")
- 🚫 Registry: "SEBI Advisory Dept" — entity format doesn't match
- 🚫 SPF/DKIM: FAIL

> *"Chaar layers ne pakda — AI-generated text, fake domain, urgency manipulation, sender not verified."*
> → One-tap → SCORES complaint generated with evidence

### Case 2 — DEEPFAKE VIDEO CAUGHT (30 sec)
> *"BSE CEO deepfake video upload karte hain..."*

**→ Trust Score: 5/100 🔴**
- 🚫 Hash: KNOWN FAKE — flagged Jan 15, 2026 (instant, <50ms)
- 🔴 Frame heatmap showing manipulation regions

> *"Hash registry ne pakda — pehle flag hua tha, dobara resurface nahi ho sakta."*

### Case 3 — REAL SEBI CIRCULAR VERIFIED (20 sec)
> *"Ab SEBI ka asli circular — PRAMAAN Seal hai. Scan karte hain..."*

**→ Trust Score: 98/100 ✅**
- ✅ Signed by: SEBI, India
- ✅ Timestamp: 8 July 2026
- ✅ Content hash: Matches (not tampered)

> *"Pramaan hai — verified, signed, authentic."*

### Closing (20 sec)
> *"Detect karo. Verify karo. Report karo. Teen pillar — detection, authentication, redressal. Investor ka poora journey covered. Yeh hai PRAMAAN — har message ka proof."*
> Show Hindi toggle — same results in Hindi. *"Bilingual. Accessible. For every Indian investor."*

---

## 18. Performance Benchmarks

| Module | Benchmark Dataset | Metric to Report |
| :--- | :--- | :--- |
| Phishing classifier | PhishTank / APWG | Precision, Recall, F1 — with confusion matrix |
| Voice detection | ASVspoof samples | EER (Equal Error Rate) on test set |
| Video detection | FaceForensics++ | Accuracy on raw/compressed variants |
| Hash registry | Pre-populated 50+ fakes | Lookup time (<50ms), match accuracy |
| Domain typosquat | 200 real vs 200 fake domains | Detection rate (~99%) |

### Live Demo Cases (3 Minimum)
1. **Clean fake caught** — phishing email with full explainability
2. **Legitimate communication verified** — SEBI circular with PRAMAAN Seal
3. **Borderline case** — "AI-text score moderate, domain legitimate, entity registered — Trust Score: 65, EXERCISE CAUTION"

> **The borderline case is critical** — it shows intellectual honesty and system maturity. Any team can show a clear fake/real. Showing a nuanced case = judges know you understand real-world complexity.

---

## 19. Roadmap

### Phase 1: Pre-Work (NOW → Hackathon) — 8 Weeks

| Week | Focus | Deliverables |
| :--- | :--- | :--- |
| **1–2** | Foundation | Next.js + FastAPI boilerplate, MongoDB/Redis setup, SEBI registry scrape → JSON, ECDSA key gen + QR library, Telegram bot skeleton |
| **3–4** | Core Modules | Phishing detector (Gemini + domain check + urgency), Hash registry (Redis, 50+ known fakes), PRAMAAN Seal sign + verify, SEBI registry lookup |
| **5–6** | Advanced Modules | AASIST/RawNet2 voice integration + Indian sample testing, Video deepfake model + frame heatmap, Complaint template generator, Bilingual output |
| **7–8** | Polish + Demo | Trust Score aggregation + explainability UI, Integration testing (all modules end-to-end), Demo script practice (2-min, 3 cases), Mock data prep, backup plan, Pitch deck |

### Phase 2: Hackathon (48 Hours)

| Hours | Focus |
| :--- | :--- |
| **0–12** | Integration, bug fixes, end-to-end flow working |
| **12–24** | Demo polish, edge cases, UI animations |
| **24–36** | Presentation prep, Q&A practice |
| **36–48** | Final demo rehearsal, submission |

### Phase 3: Post-Hackathon

| Phase | Timeline | Features |
| :--- | :--- | :--- |
| **Pilot** | 3 months | WhatsApp Business API, regional languages (Tamil, Bengali, Marathi), browser extension, rPPG full pipeline |
| **Production** | 6 months | SEBI Innovation Sandbox pilot, 5000+ intermediaries with PRAMAAN Seal, append-only audit ledger, C2PA full compliance |

---

## 20. Differentiators

| # | Differentiator | What We Say |
| :--- | :--- | :--- |
| 1 | **Bidirectional** | "Nearly every team will only do detection. We also solve authentication — directly addressing the 'no way to verify official communications' half of the problem statement." |
| 2 | **Unified Explainable Trust Score** | "One score across text/voice/video/social — not four separate disconnected tools. With full explainability." |
| 3 | **Regulator-Aligned** | "Ties directly to SEBI's May 2026 circular and Nov 2025 warning. We can literally cite the mandates our tool implements." |
| 4 | **Hash Registry** | "Resurfacing problem solved structurally. BSE CEO video can never resurface. No other team addresses this." |
| 5 | **Complete Investor Journey** | "Detect → Verify → Report. One-tap SCORES complaint with evidence. No other team closes this loop." |
| 6 | **Reaches Users Where They Get Scammed** | "Telegram bot + mobile-first web app, not just a dashboard nobody outside a SOC will use." |
| 7 | **Honest Scope** | "We report real benchmarks, acknowledge limitations, pair AI with deterministic methods. We propose SEBI Sandbox validation, not production claims." |

---

## 21. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
| :--- | :--- | :--- | :--- |
| WhatsApp compression degrades ML accuracy | Voice/Video detection drops to 75-85% | High | Pair ML with deterministic checks (hash, domain, registry). Transparency about limitations. |
| SEBI SCORES has no public API | Cannot auto-submit complaints | Certain | Generate templates for manual copy/paste/download. Position as "pending API availability." |
| Deepfakes keep improving | Detection accuracy erodes over time | Medium | Authentication (Pillar B) is arms-race proof. Continuous model updates for detection. |
| Cold start — empty hash registry | First-time fakes won't be caught by hash | Medium | Pre-populate 50+ known fakes. Community flagging. ML modules as fallback. |
| Hindi AI-text detection accuracy | Lower than English (~70-80%) | High | Combine with other deterministic signals. Position as improving with data. |
| Live demo failure | Loss of credibility at hackathon | Low | Backup pre-recorded demo. Mock data fallback. Practice extensively. |

---

## 22. Submission Summary (Copy-Paste Ready)

**Project:** PRAMAAN (प्रमाण)
**Theme:** AI-Driven Detection of Synthetic Media & Phishing Attacks in Securities Markets

**Problem:** Deepfake financial fraud has grown 550% since 2019 (projected loss ₹70,000 crore). The BSE CEO deepfake video resurfaced months after being flagged. No real-time citizen verification tool, no mechanism to authenticate legitimate financial communications, no easy way for retail investors to report fraud. SEBI's response remains reactive.

**Solution:** PRAMAAN — a three-pillar trust engine:

**Pillar A — Detection (Inbound):**
- Perceptual hash registry with hash families for instant known-fake detection (<50ms)
- Text/email/SMS phishing analysis: AI-generated text detection (perplexity/burstiness), phishing pattern classification, domain typosquatting (Levenshtein), SPF/DKIM/DMARC validation, urgency pattern scoring
- Voice clone detection via AASIST/RawNet2 anti-spoofing models
- Video deepfake detection via frame-level CNN + temporal consistency + biological signal checks (rPPG, blink rate, lip-sync)
- Social media manipulation detection via coordination analysis + authenticated registry fact-checking

**Pillar B — Authentication (Outbound):**
- PRAMAAN Seal: cryptographic digital signature (ECDSA) + QR code for every official financial communication
- Aligned with C2PA Content Credentials standard
- SEBI intermediary registry lookup
- Public verification portal

**Pillar C — Redressal (Action):**
- One-tap auto-generated complaint templates for SEBI SCORES and cybercrime.gov.in (1930)
- Evidence package auto-attached (hash, AI analysis, timestamp, transcript)
- Bilingual output (Hindi + English)

**Output:** Unified Trust Score (0-100) with full explainability breakdown showing which checks fired and why.

**Tech:** Next.js + FastAPI + MongoDB + Redis + Gemini 1.5 Flash + AASIST/RawNet2 + ECDSA + Telegram Bot

**Target Users:** Retail investors (web app + Telegram bot), Brokers (API), SEBI/Exchanges (signing portal)

**Differentiators:**
- Only solution addressing BOTH detection AND authentication (PRAMAAN Seal)
- Hash families prevent resurfacing (BSE CEO case solved structurally)
- Text/email phishing with 4-layer pipeline (AI-text + phishing patterns + domain/sender + securities-specific)
- Complete investor journey: Detect → Verify → Report
- Unified explainable trust score across all modalities
- Bilingual (Hindi + English), DPDP Act 2023 compliant
- Aligned with SEBI Nov 2025 warning + May 2026 mandate

**Impact:** Direct investor protection for India's most vulnerable demographic — first-generation retail investors on social media. Proposed validation through SEBI Innovation Sandbox.

---

> **Document Version:** 1.0
> **Last Updated:** July 2026
> **Team:** Black Ghost
> **Confidentiality:** For SEBI TechSprint 2026 Submission
