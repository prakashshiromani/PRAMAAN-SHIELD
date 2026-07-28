# 🛡️ PRAMAAN-SHIELD (प्रमाण शील्ड)

**Three-Pillar Trust & Authentication Engine for Securities Markets**  
*Detection · Authentication · Redressal*  

[![SEBI TechSprint 2026](https://img.shields.io/badge/SEBI--TechSprint--2026-Problem--Statement--1-0052CC?style=for-the-badge)](https://sebi.gov.in)
[![Python](https://img.shields.io/badge/FastAPI-3.11+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-000000?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![ECDSA SECP256R1](https://img.shields.io/badge/Cryptography-ECDSA--SECP256R1-4B0082?style=for-the-badge)](file:///c:/Users/Prakash%20Max/OneDrive/Desktop/sbi%20project/doce/SECURITY.md)
[![Test Suite](https://img.shields.io/badge/PyTest-44%2F44%20PASSED-10B981?style=for-the-badge)](file:///c:/Users/Prakash%20Max/OneDrive/Desktop/sbi%20project/backend/tests)

---

## 📌 Executive Summary

Financial fraud in India's securities market has evolved from crude email scams to AI-driven voice clones, deepfake CEO videos, and typosquatted broker domain networks. According to Deloitte and McAfee, deepfake-driven financial fraud in India has surged by **550% (2019–2024)**, with projected losses exceeding **₹70,000 Crore**. 

Events such as the **BSE CEO Deepfake Video (Jan 2026)** demonstrate that retail investors lack real-time tools to verify whether a viral video, advisory text, or voice message is authentic.

**PRAMAAN-SHIELD** solves this crisis through a unified, clinical-grade three-pillar architecture:
1. **Pillar A — Detect (Is this fake?)**: Multi-modal parallel analysis pipeline detecting deepfake videos, rPPG cardiac pulses, blink rates, manipulation heatmaps, voice clones, typosquatted broker domains, email authentication headers, and pump-and-dump coordination networks.
2. **Pillar B — Authenticate (Is this real?)**: Cryptographic **PRAMAAN Seals** using ECDSA SECP256R1 digital signatures embedded in QR codes, aligned with C2PA provenance standards.
3. **Pillar C — Redressal (How to act?)**: One-tap automated complaint generation for **SEBI SCORES** and the **National Cybercrime Helpline (1930)** in bilingual Hindi/English formats.

---

## 🏛️ Architecture & System Blueprint

```
                                  PRAMAAN-SHIELD ARCHITECTURE
                                  
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │                                     CLIENT LAYER                                       │
  │     Next.js 14 App  ·  Telegram Bot (@PramaanikBot)  ·  SEBI Intermediary Signing Portal │
  └───────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
  ┌───────────────────────────────────────────▼────────────────────────────────────────────┐
  │                             PILLAR A — DETECTION PIPELINE                              │
  │ ┌───────────────────┬───────────────────┬───────────────────┬────────────────────────┐ │
  │ │ A1: Hash Registry │ A2: Phishing Text │ A3: Voice Clone   │ A4: Video Forensics    │ │
  │ │ Sub-50ms pHash    │ Levenshtein <= 2  │ AASIST + RawNet2  │ Heatmap + rPPG Pulse   │ │
  │ │ Redis Hamming     │ 200+ SEBI Domains │ Wiener Entropy    │ Blink Rate Tracking    │ │
  │ └───────────────────┴───────────────────┴───────────────────┴────────────────────────┘ │
  │ ┌───────────────────┬───────────────────┬───────────────────┬────────────────────────┐ │
  │ │ A5: SEBI Registry │ A6: Social Pump & │ A7: Email Headers │ A8: Subprocess Sandbox │ │
  │ │ Matching Entity   │ Telegram Scraper  │ SPF/DKIM/DMARC    │ ProcessPool Timeout    │ │
  │ └───────────────────┴───────────────────┴───────────────────┴────────────────────────┘ │
  └───────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
  ┌───────────────────────────────────────────▼────────────────────────────────────────────┐
  │                             PILLAR B — AUTHENTICATION ENGINE                           │
  │    ECDSA SECP256R1 Digital Signatures  ·  Canonical JSON Sorting  ·  Pinned Registry Keys  │
  └───────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
  ┌───────────────────────────────────────────▼────────────────────────────────────────────┐
  │                              PILLAR C — REDRESSAL & REPORTING                          │
  │    Automated SCORES Template  ·  National Cybercrime Helpline (1930)  ·  Bilingual HI/EN │
  └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Multi-Modal Forensic Capabilities

### 🎥 1. Video Deepfake & Liveness Detection Pipeline
* **OpenCV Frame Sampling**: Samples every 10th frame (up to 30 frames max) with grab-optimization.
* **Face Detection**: MTCNN primary locator with OpenCV Haar Cascade CPU fallback.
* **Manipulation Heatmap**: Computes Laplacian gradient magnitude on 224x224 face crops, normalizes, inverts, and applies JET colormap (`cv2.COLORMAP_JET`). Returns Base64 PNG overlays highlighting over-smoothed synthetic skin.
* **rPPG Biological Pulse Analysis**: Extracts forehead ROI green channel temporal signal and runs FFT in the 0.8–2.0 Hz frequency band (48–120 BPM). Detects real cardiac heartbeat pulses.
* **Blink Rate Tracking**: Tracks eye open/closed states across frames using OpenCV eye cascades to calculate blinks per second. Deepfakes typically show 0 blinks.
* **Temporal Consistency**: Calculates normalized grayscale histogram correlation across consecutive frames to detect frame boundary flickering.

---

### 🎙️ 2. Audio Anti-Spoofing & Voice Clone Detection
* **AASIST Graph Attention Model**: Analyzes spectral flatness (Wiener entropy), energy variance, and zero-crossing rates. Synthetic TTS voices show unnaturally flat spectrums and monotone delivery.
* **RawNet2 Raw Waveform Model**: Analyzes silence ratio, dynamic crest factor (peak/RMS), and envelope autocorrelation periodicity.
* **Dual Execution Modes**:
  * **PRODUCTION Mode**: Active when `.pth` weight files exist in `ml/aasist/weights/` and `ml/rawnet2/weights/`.
  * **HACKATHON Mode**: Active as a zero-dependency acoustic signal forensics fallback.

---

### 📄 3. Text Phishing & Typosquatting Engine
* **Levenshtein Edit Distance**: Extracts URLs and checks domain edit distance ($d \le 2$) against 200+ legitimate SEBI-registered brokers and stock exchanges (`zerodha.com`, `groww.in`, `sebi.gov.in`, `bseindia.com`).
* **Entity-Domain Binding**: Validates whether a named SEBI entity actually owns the links present in the message. Detects **Impersonation Attacks** when scammers use official names with fake links.
* **Pattern Classifier**: Evaluates English and Hindi financial threat keywords (`demat account block within 24 hours`, `खाता फ्रीज`) and pump-and-dump fraud keywords (`guaranteed 2000% return`, `VIP telegram jackpot`).
* **Gemini 1.5 Flash LLM**: Performs Named Entity Recognition (NER) and prompt injection defense via `<<<UNTRUSTED>>>` system guard markers.

---

### 📧 4. Email Authentication Header Parser
* **RFC 7208 / RFC 6376 / RFC 7489**: Parses raw `.eml` files to extract SPF, DKIM signature, and DMARC alignment statuses.
* **Authentication Ledger**: Displays clear pass/fail status (`SPF: ✅ | DKIM: ✅ | DMARC: ❌`) for email security verification.

---

## 🔒 Cryptographic PRAMAAN Seal (Authentication)

* **Asymmetric Key Standard**: Per-entity SECP256R1 (NIST P-256) ECDSA keypairs.
* **Canonical JSON Serialization**: Payloads are sorted deterministically before SHA-256 hashing and signing.
* **Trust Anchor Pinning**: Public keys are fetched strictly from the trusted `sebi_registry` MongoDB database, **NEVER** from the QR code payload.
* **5-Step Verification**:
  1. Resolve public key from trusted `sebi_registry`.
  2. Verify ECDSA signature against pinned key.
  3. Re-hash presented document bytes to confirm content integrity.
  4. Check revocation status in `seal_records`.
  5. Validate validity window (`not_before` / `not_after`).

---

## 📊 Hardened Trust Engine Scoring Model

Every scan starts at a neutral **50 / 100 Baseline Score**.

```
    0 ────────────── 30 ────────────────────── 70 ────────────── 100
      🔴 SUSPICIOUS      🟡 EXERCISE CAUTION      🟢 VERIFIED
```

### Circuit Breakers (Hard Gate Rules):
1. **Known Fake Hash Match** ➔ Hard Cap $\le 15$ (**SUSPICIOUS 🔴**)
2. **Typosquatted / Impersonated Domain** ➔ Hard Cap $\le 15$ (**SUSPICIOUS 🔴**)
3. **Deepfake Video Detected** ($P > 0.5$) ➔ Hard Cap $\le 15$ (**SUSPICIOUS 🔴**)
4. **Voice Clone Detected** ($P > 0.5$) ➔ Hard Cap $\le 15$ (**SUSPICIOUS 🔴**)
5. **Valid Cryptographic PRAMAAN Seal** ➔ Score $\ge 90$ (**VERIFIED 🟢**)

---

## 🛠️ Quick Start & Installation

### Prerequisites
* **Python**: `3.11` or higher
* **Node.js**: `20.x` or higher
* **MongoDB**: `7.0` (Optional — Graceful In-Memory Fallback Active)
* **Redis**: `7.2` (Optional — Graceful Fallback Active)

---

### Step 1: Backend Setup

```powershell
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate    # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run Database Seeder (SEBI Registry & Known Fake Hashes)
python -m app.db.seed

# Start FastAPI Backend
uvicorn app.main:app --reload --port 8000
```

* **Swagger API Docs**: [`http://localhost:8000/docs`](http://localhost:8000/docs)
* **Health Check**: [`http://localhost:8000/health`](http://localhost:8000/health)

---

### Step 2: Frontend Setup

```powershell
cd frontend

# Install Node dependencies
npm install

# Start Next.js App
npm run dev
```

* **Web Console**: [`http://localhost:3000`](http://localhost:3000)

---

### Step 3: Run Automated Test Suite

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

---

## 📜 Team Credits

**PRAMAAN-SHIELD** is built for the **SEBI Securities Market TechSprint 2026**.

**Team Black Ghost**:
* **Prakash Kumar Shiromani** — *Team Lead & Full-Stack Architect*
* **Aditya Kumar Yadav** — *Security & Cryptography Specialist*
* **Nikhil Verma** — *ML & Video Deepfake Engineer*
* **Ambuj Kumar** — *NLP & Audio ML Engineer*
* **Diya Shukla** — *Frontend Developer & UI/UX Designer*
