# 🎯 Pramaan-Shield (Powered by BlackGhost) — FINAL COMPLETE VERSION

**This is the definitive version. Everything merged, everything honest.**  
---

## 📌 One-Liner Pitch

**"Pramaan-Shield: Proof check karne ka sabse fast aur robust system, built by BlackGhost."**  
---

## 🧠 Core Philosophy

**"Don't just catch fakes — prove what's real."**  
Two-sided trust layer for securities markets:

* **Detect** — catches AI-generated attacks (phishing, voice clones, deepfakes)  
* **Authenticate** — lets SEBI/exchanges/companies cryptographically prove their communications are real  
* **Report** — one-tap complaint filing to close the investor protection loop

The authentication half is what makes this a **systemic fix** rather than a point solution — it's exactly the "verification framework" gap SEBI has publicly flagged as needing.  
---

## 🔥 PROBLEM (Real Data)

### Crisis

| Fact | Source |
| :---- | :---- |
| BSE CEO deepfake (Jan 2026\) — fake stock tips, March mein resurface | BSE Advisory |
| Fraud networks distribute via 38 WhatsApp funnels in one day, cost $5 | Industry Reports |
| Deepfake financial fraud **550% increase** (2019-2024), projected loss **₹70,000 crore** | Deloitte/McAfee |
| Ambani, Tata, Narayana Murthy, Virat Kohli deepfakes for fake trading apps | News Reports |
| SEBI Nov 2025 warning: scammers impersonate registered intermediaries | SEBI Circular |
| 1 May 2026 mandate: intermediaries must display registration on social media | SEBI Mandate |

### Three Gaps (None Solved Today)

| Gap | Reality |
| :---- | :---- |
| **Detection** | No real-time "scan before you trust" tool for citizens |
| **Authentication** | No mechanism to verify if a communication from SEBI/exchanges is genuine |
| **Redressal** | Filing a SCORES complaint takes 30+ minutes — retail investors don't bother |

SEBI's response is **reactive** — video goes viral → months later advisory → video resurfaces. **No proactive citizen-facing solution exists.**  
---

## 👥 Target Users & Channels

*Problem statement explicitly asks: "specify their target user, the channel(s) addressed"*

| User | Channel | What They Get |
| :---- | :---- | :---- |
| **Retail / First-Gen Investors** | WhatsApp, Telegram, SMS, Email, YouTube, Instagram | Web app \+ Telegram bot to forward anything suspicious → instant verdict (Hindi/English) |
| **Brokers & Intermediaries** | Client communication pipelines, internal SOC | API to bulk-screen inbound/outbound messages before they reach clients |
| **SEBI / Exchanges / Listed Companies** | Outbound circulars, press releases, exec videos | Signing tool to issue PRAMAAN Seal on every official release |

---

## 🏗️ Architecture: PRAMAAN Trust Engine

┌───────────────────────────────────────────────────────────────────────┐  
│                        PRAMAAN TRUST ENGINE                          │  
│              Unified Trust Score \+ Explainability Layer               │  
├──────────────────────┬──────────────────────┬─────────────────────────┤  
│   PILLAR A           │   PILLAR B           │   PILLAR C             │  
│   DETECTION          │   AUTHENTICATION     │   REDRESSAL            │  
│   (Inbound)          │   (Outbound)         │   (Action)             │  
│                      │                      │                        │  
│   "Is this fake?"    │   "Is this real?"    │   "Report instantly"   │  
├──────────────────────┼──────────────────────┼─────────────────────────┤  
│                      │                      │                        │  
│ ┌──────────────────┐ │ ┌──────────────────┐ │ ┌───────────────────┐  │  
│ │ 1\. Hash Registry │ │ │ Digital Sign     │ │ │ SEBI SCORES       │  │  
│ │ (instant known   │ │ │ (RSA/ECDSA)      │ │ │ auto-complaint    │  │  
│ │  fake lookup)    │ │ │ \+ QR Code        │ │ │ template          │  │  
│ └──────────────────┘ │ └──────────────────┘ │ └───────────────────┘  │  
│                      │                      │                        │  
│ ┌──────────────────┐ │ ┌──────────────────┐ │ ┌───────────────────┐  │  
│ │ 2\. Text/Email/   │ │ │ C2PA Content     │ │ │ Cybercrime 1930   │  │  
│ │ SMS Phishing     │ │ │ Credentials      │ │ │ auto-complaint    │  │  
│ │ Detector  ⭐NEW  │ │ │ (metadata)       │ │ │ template          │  │  
│ └──────────────────┘ │ └──────────────────┘ │ └───────────────────┘  │  
│                      │                      │                        │  
│ ┌──────────────────┐ │ ┌──────────────────┐ │ ┌───────────────────┐  │  
│ │ 3\. Voice Clone   │ │ │ SEBI Registry    │ │ │ Evidence Package  │  │  
│ │ Detector         │ │ │ Lookup           │ │ │ (hash, transcript │  │  
│ │ (AASIST/RawNet2) │ │ │                  │ │ │  timestamp, AI    │  │  
│ └──────────────────┘ │ └──────────────────┘ │ │  analysis report) │  │  
│                      │                      │ └───────────────────┘  │  
│ ┌──────────────────┐ │ ┌──────────────────┐ │                        │  
│ │ 4\. Video Deep-   │ │ │ Append-Only      │ │                        │  
│ │ fake Detector    │ │ │ Ledger           │ │                        │  
│ │ (CNN+rPPG+lip)   │ │ │ (audit trail)    │ │                        │  
│ └──────────────────┘ │ └──────────────────┘ │                        │  
│                      │                      │                        │  
│ ┌──────────────────┐ │ ┌──────────────────┐ │                        │  
│ │ 5\. Social Media  │ │ │ Public Verify    │ │                        │  
│ │ Manipulation     │ │ │ Portal \+ QR      │ │                        │  
│ │ Detector         │ │ │ Scanner          │ │                        │  
│ └──────────────────┘ │ └──────────────────┘ │                        │  
│                      │                      │                        │  
├──────────────────────┴──────────────────────┴─────────────────────────┤  
│                         OUTPUT LAYER                                  │  
│  Unified Trust Score (0-100) \+ Explainability Breakdown               │  
│  "Trust Score: 8/100 — voice liveness FAILED, sender NOT in SEBI     │  
│   registry, domain typosquat detected (zerrodha.com)"                │  
│                                                                       │  
│  🌐 Hindi \+ English output  •  📱 Mobile-first web app               │  
└───────────────────────────────────────────────────────────────────────┘  
---

## 🔍 PILLAR A: DETECTION (5 Modules)

### Module A1: Perceptual Hash Registry — FIRST CHECK, FASTEST

**What:** Every uploaded video/image gets a perceptual hash. Compare against a database of known fakes. Match \= instant flag, no ML needed.  
**How It Works:**  
Upload video/image  
     ↓  
Generate 64-bit perceptual hash (pHash / videohash)  
     ↓  
Redis lookup: Hamming distance ≤ 10?  
     ↓  
YES → 🚫 KNOWN FAKE (\< 50ms, instant)  
      Show: "Flagged on \[date\], by \[SEBI/BSE/Community\], detected \[count\] times"  
NO  → Pass to next detection modules  
**Hash Families (Pre-Work Enhancement):** When a video is flagged, auto-generate **10-15 variant hashes:**

* Cropped (10%, 20%, 30%)  
* Mirrored (horizontal flip)  
* Re-encoded (different quality levels)  
* Speed changed (0.8x, 1.2x)  
* With/without watermark overlay

**Result:** Scammer edits video slightly and reshares → system still catches it.  
**Pre-Population (Solves Cold Start):**

* Pre-load 50+ known fake financial videos/images (BSE CEO deepfake, known scam templates)  
* Verified entities (SEBI, exchanges) can fast-track flag → instant registry entry  
* Community signals: 50+ user flags on same content \= auto-escalation

**Why this is first:** Cheapest, fastest, most reliable check. If hash matches, skip expensive ML analysis entirely.

| Metric | Value |
| :---- | :---- |
| Lookup speed | \< 50ms |
| Capacity | 10K hashes/sec |
| False positive rate | Near zero (deterministic) |
| Pre-populated | 50+ known fakes at launch |

NOTE

**BSE CEO case direct answer:** Flagged once in January → hash family stored → March resurface attempt → instantly blocked. Problem solved STRUCTURALLY, not reactively.

---

### Module A2: Text/Email/SMS Phishing Detector ⭐ FULLY DETAILED

**What:** Analyzes text-based content (emails, SMS, WhatsApp messages, social media posts) for phishing attempts, AI-generated scam text, and domain spoofing.  
**The 4-Layer Detection Pipeline:**  
Input: Text/Email/SMS content  
     ↓  
┌─────────────────────────────────────────────────────┐  
│  LAYER 1: AI-Generated Text Detection               │  
│  Perplexity \+ Burstiness analysis                    │  
│  → Is this written by an LLM or a human?            │  
├─────────────────────────────────────────────────────┤  
│  LAYER 2: Phishing Pattern Classifier               │  
│  Fine-tuned on phishing corpora                      │  
│  → Does this match known scam patterns?             │  
├─────────────────────────────────────────────────────┤  
│  LAYER 3: Domain & Sender Verification              │  
│  SPF/DKIM/DMARC \+ Typosquatting check               │  
│  → Is the sender who they claim to be?              │  
├─────────────────────────────────────────────────────┤  
│  LAYER 4: Securities-Specific Red Flags             │  
│  SEBI registry cross-check \+ urgency scoring        │  
│  → Does this content match securities fraud patterns?│  
└─────────────────────────────────────────────────────┘  
     ↓  
Combined phishing score \+ explainability

#### Layer 1: AI-Generated Text Detection

**Why this matters:** LLM-written scam text has a different statistical fingerprint than human-written scam text. Modern phishing emails written by ChatGPT/Gemini are grammatically perfect — but they have telltale statistical patterns.  
**Technical approach:**

* **Perplexity analysis:** LLM-generated text has consistently LOW perplexity (model is "unsurprised" by its own output). Human text has variable perplexity.  
* **Burstiness analysis:** Human writing alternates between short/long sentences, simple/complex vocabulary. LLM text is unnaturally UNIFORM.  
* **Implementation:** Use a detector model (OpenAI's text classifier approach, or Gemini-based analysis) that outputs: {"ai\_generated\_probability": 0.87, "features": {"perplexity": "low", "burstiness": "low"}}

**Honest accuracy note:** AI-text detection is imperfect (\~85-90% on English, lower on short texts). This is a SIGNAL, not a definitive detector — combined with other layers it becomes powerful.

#### Layer 2: Phishing Pattern Classifier

**Training data:** Public phishing datasets (PhishTank, APWG, Nigerian fraud corpus) \+ custom Indian financial phishing samples **Model:** Fine-tuned classifier OR Gemini 1.5 Flash with few-shot prompting  
**What it catches:**

* "Your demat account will be blocked in 24 hours" (urgency)  
* "SEBI has declared dividend on your behalf" (authority impersonation)  
* "Click here to verify your PAN" (credential harvesting)  
* "Guaranteed 500% return in 30 days" (unrealistic promises)  
* "Only 5 spots left, invest now" (artificial scarcity)

**Social engineering urgency scoring:**  
python  
\# Urgency patterns specific to Indian securities market:  
URGENCY\_PATTERNS \= \[  
   "account block", "account freeze", "kyc expire",  
   "sebi notice", "penalty", "last chance",  
   "act now", "limited time", "guaranteed return",  
   "insider tip", "confidential", "don't tell anyone"  
\]  
\# Score: 0 (no urgency) → 10 (extreme urgency)

#### Layer 3: Domain & Sender Verification

**Domain Typosquatting Detection:**  
Legitimate domains:          Scam domains (Levenshtein ≤ 3):  
zerodha.com          →       zerrodha.com, zer0dha.com, zerodha-login.com  
sebi.gov.in          →       serbi-gov.in, sebi-gov.in, sebi.gov.org  
groww.in             →       gr0ww.in, groww-app.in  
angelone.in          →       angel-one.in, angelone-trade.in  
**Implementation:** Maintain a list of 200+ legitimate Indian broker/exchange/regulator domains. For any URL in the content, calculate Levenshtein distance. Distance ≤ 3 \= typosquat alert.  
**Email Header Validation (for email inputs):**

* **SPF (Sender Policy Framework):** Does the sending IP match the domain's authorized senders?  
* **DKIM (DomainKeys Identified Mail):** Is the email cryptographically signed by the claimed domain?  
* **DMARC (Domain-based Message Authentication):** Does the domain's DMARC policy say to reject failures?

Result examples:  
✅ SPF: PASS | DKIM: PASS | DMARC: PASS → Sender verified  
🚫 SPF: FAIL | DKIM: FAIL | DMARC: NONE → Sender NOT verified — likely spoofed  
IMPORTANT

**Honest limitation:** SPF/DKIM/DMARC validation only works on raw email headers. If user pastes email TEXT (not .eml file), header validation is not possible. In that case, only Layers 1, 2, and 4 fire. Be transparent about this in demo.

#### Layer 4: Securities-Specific Red Flags

**SEBI Registry Cross-Check:**

* Extract entity names/registration numbers from text (Gemini NER)  
* Match against SEBI intermediary database (pre-parsed JSON)  
* Results:  
  * ✅ "Zerodha — SEBI Registered (INZ000031633)"  
  * ❌ "XYZ Trading — NOT FOUND in SEBI registry"  
  * ⚠️ "Zerodha" mentioned but communication channel is unofficial → "Entity exists but communication is UNVERIFIED"

**Claim Verification:**

* Cross-check factual claims against authenticated registry (Pillar B)  
* "SEBI has issued new circular about F\&O rules" → Check: Does any signed SEBI circular match this claim?  
* If no match → "⚠️ No official SEBI communication found matching this claim"

#### Combined Phishing Output

┌───────────────────────────────────────────────┐  
│  📧 TEXT/PHISHING ANALYSIS                    │  
│                                               │  
│  Phishing Score: 8.7/10 🔴 HIGH RISK         │  
│                                               │  
│  Breakdown:                                   │  
│  🚫 AI-Generated: 87% probability (LLM text) │  
│  🚫 Urgency: 9/10 ("account will be blocked") │  
│  🚫 Domain: zerrodha.com (typosquat of        │  
│     zerodha.com, distance: 1\)                 │  
│  🚫 Registry: "XYZ Capital" NOT registered    │  
│  ⚠️ SPF: FAIL | DKIM: FAIL                   │  
│  🚫 Claim: No matching SEBI circular found    │  
│                                               │  
│  Verdict: LIKELY PHISHING SCAM                │  
└───────────────────────────────────────────────┘

| Metric | Target | Honest Note |
| :---- | :---- | :---- |
| Phishing detection F1 | 90%+ on benchmark | Real-world will be 80-85% — combined with other layers compensates |
| AI-text detection | 85-90% on English | Lower on short texts and Hindi content |
| Typosquat detection | \~99% | Deterministic (Levenshtein), very reliable |
| SPF/DKIM/DMARC | 100% | Only works on raw email headers, not pasted text |

---

### Module A3: Voice Clone Detector

**What:** Detects AI-generated/cloned voice in audio calls or recorded messages.  
**Models:** AASIST \+ RawNet2 (pre-trained on ASVspoof-style data)

* AASIST \= state-of-the-art anti-spoofing (2022), graph attention network  
* RawNet2 \= works on raw waveforms, catches spectral/prosody artifacts that voice cloners leak

**What it catches:**

* Voice clones of CEOs/regulators giving fake stock tips  
* AI-generated phone calls impersonating brokers  
* Synthetic voice messages on WhatsApp/Telegram

**Pipeline:**  
Audio input → Feature extraction (raw waveform)  
   ↓  
AASIST model → Anti-spoofing score  
   ↓  
RawNet2 model → Synthesis artifact detection  
   ↓  
Combined voice authenticity score  
   ↓  
"Voice Liveness: 23% — LIKELY SYNTHETIC"

| Metric | Value | Honest Note |
| :---- | :---- | :---- |
| EER on ASVspoof | \~1-2% | Benchmark performance, real WhatsApp audio will be worse |
| Real-world estimate | \~85-90% | Compression artifacts may confuse the model |
| Approach | Pre-trained, no custom training | Download → integrate → test on Indian samples |

**Pre-work task:** Download AASIST/RawNet2, test on 50+ Indian audio samples (Hindi, English, regional), note real accuracy. Use THOSE numbers in pitch — not benchmark numbers.  
---

### Module A4: Video Deepfake Detector

**What:** Detects synthetic/manipulated video — face swaps, lip-sync deepfakes, fully generated videos.  
**Three-Layer Video Analysis:**

1. **Frame-Level CNN:** Pre-trained model (EfficientNet/XceptionNet on FaceForensics++) analyzes individual frames for manipulation artifacts  
2. **Temporal Consistency:** Real video has smooth frame-to-frame transitions. Deepfakes often have subtle temporal glitches (flickering edges, inconsistent lighting between frames)  
3. **Biological Signal Checks:**  
   * **rPPG (Remote Photoplethysmography):** Real human skin shows subtle color changes due to blood flow/pulse. Deepfakes CAN'T reproduce this — even diffusion models fail here. This is the **hardest thing for generative video to fake.**  
   * **Blink Rate Analysis:** Humans blink 15-20 times/minute. Early deepfakes didn't blink at all. Modern ones blink but at wrong intervals.  
   * **Lip-Sync Mismatch:** Audio-visual correlation check — is the mouth movement matching the audio?

**Output:**  
Video Analysis:  
🔴 Frame manipulation detected (confidence: 91%)  
🔴 Temporal inconsistency at frames 120-145  
🔴 rPPG signal: ABSENT (no biological pulse detected)  
⚠️ Lip-sync: Minor mismatch detected  
Frame heatmap: \[visual overlay showing manipulated regions\]

| Metric | Value | Honest Note |
| :---- | :---- | :---- |
| FaceForensics++ benchmark | \~95% | High quality, controlled videos |
| Real-world Indian WhatsApp | \~75-85% | Compressed, low-res — accuracy drops |
| rPPG | Conceptually strong | Full pipeline complex — partial implementation for hackathon, mention in pitch |

**Pre-work task:** Download pre-trained detector, test on compressed WhatsApp-quality videos. Generate frame heatmaps for demo. rPPG \= mention in pitch as production feature, partial demo for hackathon.  
---

### Module A5: Social Media Manipulation Detector

**What:** Detects coordinated inauthentic behavior and fake financial social media posts.  
**Two approaches:**

1. **Bot/Coordination Detection:** Posting-pattern graph analysis — if 50 accounts post identical stock tips within 5 minutes, that's coordination  
2. **Fact-Check Against Authenticated Registry:** If a "leaked SEBI circular" screenshot doesn't match any signed original in Pillar B → instant red flag

| Metric | Honest Note |
| :---- | :---- |
| Feasibility | Real-time crawling needs infrastructure — for hackathon, demo with pre-collected samples |
| Build priority | **LOWEST** — mention in slides, demo with mock data |

WARNING

**Honest assessment:** Real-time social media crawling needs significant infrastructure (API access, rate limits, crawler setup). For hackathon: demo with pre-collected examples, position as "Phase 2" for production. Don't overclaim.

---

## 🛡️ PILLAR B: AUTHENTICATION

### What It Does

Legitimate financial entities sign their communications with cryptographic signatures. Investors verify by scanning a QR code or entering a Seal ID.

### Entity Side (Issuing a PRAMAAN Seal)

SEBI / Exchange / Company  
       ↓  
Creates official communication (circular, press release, video)  
       ↓  
PRAMAAN portal signs it:  
 → Content hash (SHA-256)  
 → Digital signature (ECDSA with entity's private key)  
 → Timestamp  
 → Entity name \+ SEBI registration number  
 → QR code embedding all of the above  
       ↓  
Seal embedded in communication

### Investor Side (Verifying)

Investor sees communication with PRAMAAN Seal  
       ↓  
Opens PRAMAAN web app → "Verify Seal"  
       ↓  
Scans QR code OR enters Seal ID  
       ↓  
System checks:  
 ✅ Signature valid? (cryptographic verification)  
 ✅ Content hash matches? (no tampering)  
 ✅ Entity registered? (SEBI database check)  
 ✅ Timestamp valid? (not expired/replayed)  
       ↓  
Result:  
 ✅ VERIFIED — "Signed by SEBI, 8 July 2026, content intact"  
 ❌ UNVERIFIED — "No PRAMAAN Seal found"  
 🚫 TAMPERED — "Content modified after signing"

### Standards Alignment

* **C2PA (Coalition for Content Provenance and Authenticity):** Our Seal is aligned with C2PA's "Content Credentials" standard — same concept, tailored for Indian securities market  
* **Production Roadmap:** Hash \+ signature anchored to append-only ledger (tamper-evident registry) for audit trail. Hackathon: MongoDB storage. Production: permissioned ledger.

### Why This Wins

* **100% deterministic** — no AI, no confidence scores, no false positives  
* **Arms-race proof** — deepfakes improve, cryptographic signatures can't be faked  
* **Problem statement says it:** "verification of authentic financial communications" — this IS that  
* **SEBI May 2026 mandate aligned** — digital version of "display registration details"  
* **NO OTHER TEAM will build this** — everyone focuses on detection only

---

## 📢 PILLAR C: REDRESSAL (One-Tap Reporting)

### What It Does

When Trust Score is LOW → auto-generate complaint with evidence → user reviews → one tap submit.

### How It Works

Scan result: FAKE/SUSPICIOUS (Trust Score \< 30\)  
       ↓  
User taps "Report to SEBI SCORES" or "Report to Cybercrime 1930"  
       ↓  
Gemini 1.5 Flash auto-generates:  
 → Complaint description (Hindi \+ English)  
 → Evidence package:  
    • Content hash (tamper-proof identifier)  
    • AI analysis transcript (which checks fired, scores)  
    • Timestamp of scan  
    • Screenshot/media file reference  
    • Hash registry match details (if any)  
    • Entity registration status  
       ↓  
Pre-filled template displayed → User reviews  
       ↓  
Options:  
 📋 Copy to clipboard → paste into SCORES portal  
 📄 Download as PDF complaint letter  
 📧 Email to SEBI's complaint email

### Two Templates

| Target | Template Content |
| :---- | :---- |
| **SEBI SCORES** | Formal complaint, category auto-selected (e.g., "Unauthorized investment advice"), entity details, evidence summary, investor details placeholder |
| **cybercrime.gov.in (1930)** | FIR-style template, fraud category, evidence list, financial loss details (if any), contact information placeholder |

### Impact

* **Before:** 30+ minutes to file, most retail investors don't know SCORES exists  
* **After:** 10 seconds, evidence auto-attached, bilingual template ready  
* **This is the most ORIGINAL feature** — no other team will close the investor journey loop

IMPORTANT

**Honest limitation:** SEBI SCORES has no public API. We generate the template — user copies/pastes/downloads. We do NOT claim auto-submission. This is transparent and realistic.

---

## 📊 Unified Trust Score (The Killer UX Feature)

**One score. One answer. Full explainability.**  
The engine combines signals from ALL modules with an explainability layer showing which checks fired.

### Score Calculation

```python
# Hardened Trust Engine (Positive-Proof Baseline + Hard Gates):
score = 50  # Start at NEUTRAL (EXERCISE CAUTION)

# 1. Hard Gates (Instant RED cap <= 15)
if hash_match or seal_forged or domain_typosquat:
    score = min(score, 15)  # Forced RED (SUSPICIOUS)

# 2. Soft Signals (Nudge within band)
if phishing_score > 7:   score -= 20
if voice_synthetic > 80: score -= 20
if video_deepfake > 80:  score -= 25

# 3. Affirmative Proof (Boost to GREEN >= 70)
if pramaan_seal_verified: score += 45
if sebi_registry_matched: score += 15

# Clamp to 0-100 & assign verdict (VERIFIED / EXERCISE CAUTION / SUSPICIOUS)
score = max(0, min(100, score))
```

### Display

SUSPICIOUS:                              VERIFIED:  
┌──────────────────────────┐            ┌──────────────────────────┐  
│ TRUST SCORE: 8/100 🔴    │            │ TRUST SCORE: 98/100 ✅   │  
│ "SUSPICIOUS"             │            │ "VERIFIED — SEBI"        │  
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
**Why unified score matters:** Investor doesn't care which model flagged it. They want ONE answer: *"this is 92% likely fake"* or *"this is verified, signed by SEBI on July 8, 2026."*  
---

## 🛠️ TECH STACK

### Architecture

┌───────────────────────────────────────────────────────┐  
│                    FRONTEND                           │  
│                Next.js (React)                        │  
│      Dark mode • Mobile-first • Bilingual UI          │  
│                                                       │  
│  Pages: / (landing) | /scan | /verify | /report       │  
│         /dashboard | /seal-portal (entity demo)       │  
├───────────────────────────────────────────────────────┤  
│                    BACKEND                            │  
│                                                       │  
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
│                                                       │  
│  ┌───────────────────┐  ┌───────────────────────┐     │  
│  │   MongoDB          │  │     Redis             │     │  
│  │  • SEBI registry   │  │  • Hash index         │     │  
│  │  • Seal records    │  │  • Fast lookup cache  │     │  
│  │  • Scan history    │  │  • Rate limiting      │     │  
│  │  • User reports    │  │                       │     │  
│  └───────────────────┘  └───────────────────────┘     │  
│                                                       │  
│  ┌─────────────────────────────────────────────────┐  │  
│  │            Gemini 1.5 Flash                      │  │  
│  │  • NER (name/registration number extraction)    │  │  
│  │  • Complaint template drafting                  │  │  
│  │  • Hindi ↔ English translation                  │  │  
│  │  • AI-generated text detection signal           │  │  
│  │  • Content analysis (urgency/pattern scoring)   │  │  
│  └─────────────────────────────────────────────────┘  │  
│                                                       │  
│  ┌─────────────────────────────────────────────────┐  │  
│  │          Telegram Bot (PramaanikBot)             │  │  
│  │  • Forward message → instant verdict            │  │  
│  │  • Same backend API, different interface         │  │  
│  └─────────────────────────────────────────────────┘  │  
└───────────────────────────────────────────────────────┘

### Stack Summary

| Layer | Technology | Why |
| :---- | :---- | :---- |
| Frontend | Next.js (React) | SSR, routing, mobile-first responsive |
| Backend | FastAPI (Python) | ML ecosystem, async, fast API, type-safe |
| Database | MongoDB | Flexible schema for registry \+ seal \+ scan records |
| Cache | Redis | In-memory hash index — 10K lookups/sec |
| AI/LLM | Gemini 1.5 Flash | NER, translation, complaint drafting, text analysis |
| Voice ML | AASIST \+ RawNet2 (pretrained) | State-of-the-art anti-spoofing |
| Video ML | EfficientNet/XceptionNet (pretrained) | FaceForensics++ benchmark |
| Crypto | Python cryptography lib | ECDSA for PRAMAAN Seal |
| Hashing | videohash \+ imagehash | Perceptual hash generation |
| Bot | python-telegram-bot | Telegram integration |

### Web App Pages

| Page | Purpose |
| :---- | :---- |
| **/** | Hero landing — "Har message ka PRAMAAN lo", stats, how it works |
| **/scan** | Upload/paste content → run all detection modules → show Trust Score \+ explainability |
| **/verify** | Upload QR / enter Seal ID → verify PRAMAAN Seal authentication |
| **/report** | Pre-filled complaint templates → copy/download/email |
| **/dashboard** | Stats: total scans, fakes detected, reports filed, top flagged content |
| **/seal-portal** | (Demo) Entity portal to generate PRAMAAN Seals |

---

## 🧪 HONESTY SECTION: What's REAL vs What's MOCKED

**This is what separates winners from losers. Judges respect transparency.**

### ✅ REAL (Actually Built & Working)

| Feature | Status | Evidence |
| :---- | :---- | :---- |
| Perceptual hash registry \+ lookup | Fully working | Redis, \<50ms, pre-populated 50+ hashes |
| Text/email phishing analysis | Fully working | Gemini \+ domain check \+ urgency scoring |
| PRAMAAN Seal (sign \+ verify) | Fully working | ECDSA crypto, QR generation, verification portal |
| SEBI registry lookup | Working on scraped data | PDF → JSON, 100+ intermediaries |
| One-tap complaint templates | Fully working | SCORES \+ 1930 templates, bilingual |
| Unified Trust Score | Fully working | Weighted aggregation, explainability |
| Hindi \+ English output | Fully working | Gemini translation \+ pre-built templates |
| Telegram bot | Fully working | Forward message → instant verdict |
| Voice clone detection | Working (pre-trained) | AASIST on server, tested on Indian samples |
| Video deepfake detection | Working (pre-trained) | CNN frame analysis \+ heatmap visualization |

### ⚠️ PARTIALLY BUILT (Demo with Limitations)

| Feature | Reality | What We Say |
| :---- | :---- | :---- |
| rPPG biological signals | Partial — mention in pitch, basic demo | "Production feature, validated conceptually" |
| SPF/DKIM/DMARC | Works on raw .eml files, not pasted text | "Full email pipeline in production, text-only for demo" |
| Hash families (auto-variants) | Basic implementation, not all variants | "Expanding variant generation in production" |
| Social media manipulation | Pre-collected samples, not real-time crawl | "Phase 2: real-time integration with social APIs" |

### 🔲 MOCKED (Transparent About It)

| Feature | Reality | What We Say |
| :---- | :---- | :---- |
| SEBI SCORES auto-submission | No API exists — we generate templates | "Template generator — auto-submit pending SEBI API availability" |
| Real SEBI intermediary API | Scraped JSON, not live API | "Using publicly available data, production: SEBI API integration" |
| C2PA full integration | Mentioned as standard alignment | "Production roadmap: full C2PA compliance" |
| Append-only ledger | MongoDB for now | "Production: tamper-evident audit trail" |
| WhatsApp Business API | Not approved yet | "Applied — Telegram bot as primary, WhatsApp in Phase 2" |
| Real company seals | Mock signatures | "Demo with mock entities — production: SEBI-mandated onboarding" |

---

## 📊 EVALUATION CRITERIA MAPPING

| Criteria | How We Hit It | Strength |
| :---- | :---- | :---- |
| **Market Impact** | Direct investor protection — 3 gaps solved (auth \+ detect \+ redressal). SEBI's own identified problems. | ⭐⭐⭐⭐⭐ |
| **Technology Stack** | AI/ML (AASIST, CNN, rPPG) \+ Cryptography (ECDSA, C2PA) \+ NLP (Gemini) \+ Registry infra \+ Perceptual hashing | ⭐⭐⭐⭐⭐ |
| **Feasibility** | Core modules working pre-hackathon. Pre-trained models, no custom training needed. | ⭐⭐⭐⭐ |
| **Scalability** | Redis hash lookup \+ MongoDB registry scale horizontally. Seal verification is O(1). | ⭐⭐⭐⭐⭐ |
| **SEBI Mandate Alignment** | Nov 2025 warning \+ May 2026 mandate — Seal IS the digital mandate implementation | ⭐⭐⭐⭐⭐ |
| **Innovation** | PRAMAAN Seal (authentication) \+ Hash Families \+ One-tap Redressal \+ Unified Trust Score — unique combination no other team will have | ⭐⭐⭐⭐⭐ |

---

## 🎬 DEMO SCRIPT (2 Minutes)

### Opening (10 sec)

*"January 2026 — BSE CEO ka deepfake video. Fake stock tips. SEBI ne advisory nikali. March mein wahi video phir viral. Retail investors ke paas koi tool nahi hai verify karne ke liye. PRAMAAN hai woh tool."*

### Case 1 — PHISHING EMAIL CAUGHT (40 sec) ⭐ NEW

*"Yeh email aaya — SEBI ke naam se, 'Your demat account will be blocked.' Paste karte hain PRAMAAN mein..."*  
→ Trust Score: 11/100 🔴

* 🚫 AI-Generated: 87% (LLM-written text)  
* 🚫 Domain: serbi-gov.in (typosquat of sebi.gov.in)  
* 🚫 Urgency: 9/10 ("account will be blocked in 24 hours")  
* 🚫 Registry: "SEBI Advisory Dept" — entity format doesn't match SEBI's actual structure  
* 🚫 SPF/DKIM: FAIL

*"Chaar layers ne pakda — AI-generated text, fake domain, urgency manipulation, sender not verified."*  
→ One-tap → SCORES complaint generated with evidence

### Case 2 — DEEPFAKE VIDEO CAUGHT (30 sec)

*"BSE CEO deepfake video upload karte hain..."*  
→ Trust Score: 5/100 🔴

* 🚫 Hash: KNOWN FAKE — flagged Jan 15, 2026 (instant, \<50ms)  
* 🔴 Frame heatmap showing manipulation regions

*"Hash registry ne pakda — pehle flag hua tha, dobara resurface nahi ho sakta."*

### Case 3 — REAL SEBI CIRCULAR VERIFIED (20 sec)

*"Ab SEBI ka asli circular — PRAMAAN Seal hai. Scan karte hain..."*  
→ Trust Score: 98/100 ✅

* ✅ Signed by: SEBI, India  
* ✅ Timestamp: 8 July 2026  
* ✅ Content hash: Matches (not tampered)

*"Pramaan hai — verified, signed, authentic."*

### Closing (20 sec)

*"Detect karo. Verify karo. Report karo. Teen pillar — detection, authentication, redressal. Investor ka poora journey covered. Yeh hai PRAMAAN — har message ka proof."*  
*Show Hindi toggle — same results in Hindi. "Bilingual. Accessible. For every Indian investor."*  
---

## 🔐 DPDP Act 2023 Compliance

| Aspect | Implementation |
| :---- | :---- |
| **Data Minimization** | Only hashes stored, not original media |
| **Consent** | Clear consent screen before any upload/scan |
| **Zero Retention** | Uploaded media auto-deleted after scan (60 sec buffer) |
| **No PII** | No mandatory user accounts for scanning |
| **Transparency** | Clear disclosure: what is processed, how, why |
| **Hackathon** | Server-side ML (reliability for demo) |
| **Production** | On-device processing (WebAssembly/TFLite) — media never leaves phone |

99% of teams ignore DPDP compliance. Including this shows regulatory maturity judges value.  
---

## 🗓️ ROADMAP

### Pre-Work (NOW → Hackathon) — 8 Weeks

| Week | Focus | Deliverables |
| :---- | :---- | :---- |
| **1-2** | Foundation | Next.js \+ FastAPI boilerplate, MongoDB/Redis setup, SEBI registry scrape → JSON, ECDSA key generation \+ QR code library, Telegram bot skeleton |
| **3-4** | Core Modules | Phishing detector (Gemini \+ domain check \+ urgency patterns), Perceptual hash registry (Redis, pre-populate 50+ known fakes), PRAMAAN Seal sign \+ verify portal, SEBI registry lookup working |
| **5-6** | Advanced Modules | AASIST/RawNet2 voice model integration \+ test on Indian samples, Video deepfake model integration \+ frame heatmap, One-tap complaint template generator (SCORES \+ 1930), Bilingual output (Hindi \+ English) |
| **7-8** | Polish \+ Demo | Unified Trust Score aggregation \+ explainability UI, Integration testing (all modules end-to-end), Demo script practice (2-minute story, 3 cases), Mock data prep, backup plan (agar live demo fail ho), Pitch deck |

### Hackathon (48 Hours)

| Hours | Focus |
| :---- | :---- |
| **0-12** | Integration, bug fixes, end-to-end flow working |
| **12-24** | Demo polish, edge cases, UI animations |
| **24-36** | Presentation prep, Q\&A practice |
| **36-48** | Final demo rehearsal, submission |

### Post-Hackathon

| Phase | Timeline | Features |
| :---- | :---- | :---- |
| **Pilot** | 3 months | WhatsApp Business API, regional languages (Tamil, Bengali, Marathi), browser extension, rPPG full pipeline |
| **Production** | 6 months | SEBI Innovation Sandbox pilot, 5000+ intermediaries with PRAMAAN Seal, append-only audit ledger, C2PA full compliance |

---

## 🎯 EVIDENCE OF PERFORMANCE (What Judges Will Ask For)

### Benchmarks to Report

| Module | Benchmark Dataset | Metric to Show |
| :---- | :---- | :---- |
| Phishing classifier | PhishTank / APWG dataset | Precision, Recall, F1 — with confusion matrix |
| Voice detection | ASVspoof samples | EER (Equal Error Rate) on test set |
| Video detection | FaceForensics++ samples | Accuracy on raw/compressed variants |
| Hash registry | Pre-populated 50+ fakes | Lookup time (\< 50ms), match accuracy |
| Domain typosquat | 200 real vs 200 fake domains | Detection rate (should be \~99%) |

### Live Demo Cases (3 Minimum)

1. **Clean fake caught** — phishing email with full explainability breakdown  
2. **Legitimate communication verified** — SEBI circular with PRAMAAN Seal  
3. **Borderline case** — show explainability: "AI-text score moderate, but domain is legitimate and entity is registered — Trust Score: 65, EXERCISE CAUTION"

**The borderline case is critical** — it shows intellectual honesty and system maturity. Any team can show a clear fake/real. Showing a nuanced case \= judges know you understand real-world complexity.  
---

## 🏆 WHY WE WIN — Differentiators

| \# | Differentiator | What We Say |
| :---- | :---- | :---- |
| 1 | **Bidirectional** | "Nearly every team will only do detection. We also solve authentication — directly addressing the 'no way to verify official communications' half of the problem statement." |
| 2 | **Unified Explainable Trust Score** | "One score across text/voice/video/social — not four separate disconnected tools. With full explainability showing which checks fired." |
| 3 | **Regulator-Aligned** | "Ties directly to SEBI's May 2026 circular and Nov 2025 warning. We can literally cite the mandates our tool implements." |
| 4 | **Hash Registry** | "Resurfacing problem solved structurally. BSE CEO video can never resurface. No other team addresses this." |
| 5 | **Complete Investor Journey** | "Detect → Verify → Report. One-tap SCORES complaint with evidence. No other team closes this loop." |
| 6 | **Reaches Users Where They Get Scammed** | "Telegram bot \+ mobile-first web app, not just a dashboard nobody outside a SOC will use." |
| 7 | **Honest Scope** | "We report real benchmarks, acknowledge limitations, pair AI with deterministic methods. We propose SEBI Sandbox validation, not production claims." |

---

## 📝 SUBMISSION SUMMARY (Copy-Paste Ready)

**Project:** PRAMAAN (प्रमाण) **Theme:** AI-Driven Detection of Synthetic Media & Phishing Attacks in Securities Markets  
**Problem:** Deepfake financial fraud has grown 550% since 2019 (projected loss ₹70,000 crore). The BSE CEO deepfake video resurfaced months after being flagged. There is no real-time citizen verification tool, no mechanism to authenticate legitimate financial communications, and no easy way for retail investors to report fraud. SEBI's response remains reactive.  
**Solution:** PRAMAAN — a three-pillar trust engine:  
**Pillar A — Detection (Inbound):**

* Perceptual hash registry with hash families for instant known-fake detection (\< 50ms)  
* Text/email/SMS phishing analysis: AI-generated text detection (perplexity/burstiness), phishing pattern classification, domain typosquatting (Levenshtein), SPF/DKIM/DMARC validation, urgency pattern scoring  
* Voice clone detection via AASIST/RawNet2 anti-spoofing models  
* Video deepfake detection via frame-level CNN \+ temporal consistency \+ biological signal checks (rPPG, blink rate, lip-sync)  
* Social media manipulation detection via coordination analysis \+ authenticated registry fact-checking

**Pillar B — Authentication (Outbound):**

* PRAMAAN Seal: cryptographic digital signature (ECDSA) \+ QR code for every official financial communication  
* Aligned with C2PA Content Credentials standard  
* SEBI intermediary registry lookup  
* Public verification portal

**Pillar C — Redressal (Action):**

* One-tap auto-generated complaint templates for SEBI SCORES and cybercrime.gov.in (1930)  
* Evidence package auto-attached (hash, AI analysis, timestamp, transcript)  
* Bilingual output (Hindi \+ English)

**Output:** Unified Trust Score (0-100) with full explainability breakdown showing which checks fired and why.  
**Tech:** Next.js \+ FastAPI \+ MongoDB \+ Redis \+ Gemini 1.5 Flash \+ AASIST/RawNet2 \+ ECDSA \+ Telegram Bot  
**Target Users:** Retail investors (web app \+ Telegram bot), Brokers (API), SEBI/Exchanges (signing portal)  
**Differentiators:**

* Only solution addressing BOTH detection AND authentication (PRAMAAN Seal)  
* Hash families prevent resurfacing (BSE CEO case solved structurally)  
* Text/email phishing with 4-layer pipeline (AI-text \+ phishing patterns \+ domain/sender \+ securities-specific)  
* Complete investor journey: Detect → Verify → Report  
* Unified explainable trust score across all modalities  
* Bilingual (Hindi \+ English), DPDP Act 2023 compliant  
* Aligned with SEBI Nov 2025 warning \+ May 2026 mandate

**Impact:** Direct investor protection for India's most vulnerable demographic — first-generation retail investors on social media. Proposed validation through SEBI Innovation Sandbox.

