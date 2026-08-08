# 🛡️ PRAMAAN-SHIELD — DEPLOYMENT GUIDE (Updated)

---

## 📊 DIAGRAM 1 — TUMHARA COMPLETE SYSTEM MAP

```
╔══════════════════════════════════════════════════════════════════════╗
║                    PRAMAAN-SHIELD LIVE SYSTEM                        ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   👤 USER (Browser)                                                  ║
║        │                                                             ║
║        ▼                                                             ║
║  ┌─────────────────────────────────┐                                 ║
║  │   🌐 VERCEL (FREE)              │  ← FRONTEND yahan hai          ║
║  │   pramaan-shield.vercel.app     │                                 ║
║  │   Next.js 14 App                │                                 ║
║  └──────────────┬──────────────────┘                                 ║
║                 │  API calls                                         ║
║                 ▼                                                    ║
║  ┌─────────────────────────────────┐                                 ║
║  │  🚀 RENDER CLOUD (FREE)         │  ← BACKEND yahan deploy hoga   ║
║  │  pramaan-shield-backend         │                                 ║
║  │       .onrender.com             │                                 ║
║  │  FastAPI + PyTorch + ViT Model  │                                 ║
║  └────────┬──────────────┬─────────┘                                 ║
║           │              │                                           ║
║           ▼              ▼                                           ║
║  ┌─────────────┐  ┌─────────────────┐                               ║
║  │ 🍃 MongoDB  │  │ ⚡ Redis         │                               ║
║  │   ATLAS     │  │  UPSTASH        │                               ║
║  │  (FREE)     │  │  (FREE)         │                               ║
║  │  ✅ DONE!   │  │  ✅ DONE!        │                               ║
║  └─────────────┘  └─────────────────┘                               ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## ✅ DIAGRAM 2 — KYA HO GAYA, KYA BAAKI HAI

```
╔══════════════════╦════════════════════════════╦══════════╗
║ Service          ║ Kahan                      ║ Status   ║
╠══════════════════╬════════════════════════════╬══════════╣
║ 🍃 MongoDB       ║ MongoDB Atlas (Cloud)      ║ ✅ DONE  ║
║ ⚡ Redis         ║ Upstash (Cloud)            ║ ✅ DONE  ║
║ 📦 GitHub Repo   ║ prakashshiromani/          ║ ✅ DONE  ║
║                  ║ PRAMAAN-SHIELD             ║          ║
╠══════════════════╬════════════════════════════╬══════════╣
║ ⚙️  FastAPI       ║ Render Cloud               ║ ❌ TODO  ║
║    Backend      ║ (FREE — Blueprint ready)   ║          ║
╠══════════════════╬════════════════════════════╬══════════╣
║ 🌐 Next.js       ║ Vercel                     ║ ❌ TODO  ║
║    Frontend     ║ (FREE — auto deploy)       ║          ║
╚══════════════════╩════════════════════════════╩══════════╝

TOTAL REMAINING WORK: 2 Steps
ESTIMATED TIME:       15-20 minutes
```

---

## 📊 DIAGRAM 3 — KYU RENDER? (HF Spaces kyun nahi?)

```
                    BACKEND DEPLOY OPTIONS
                    ─────────────────────

     HF SPACES FREE          vs        RENDER FREE
    ┌─────────────────┐               ┌───────────────────┐
    │ Docker          │               │ Python Web Service│
    │                 │               │                   │
    │ NOW PAID ❌     │               │ render.yaml       │
    │ (PRO required)  │               │ already ready ✅  │
    │                 │               │                   │
    │ ❌ NOT FREE     │               │ ✅ 100% FREE      │
    └─────────────────┘               └───────────────────┘
         ❌ NAHI                           ✅ YEH LO
```

> **Note:** HuggingFace ne Docker Spaces ke liye ab **Paid PRO Plan** zaroori kar diya hai.
> Render par humara `render.yaml` pehle se configured hai — seedha Blueprint import karo!

---

## 📊 DIAGRAM 4 — STEP BY STEP FLOW (Exact order)

```
START
  │
  ▼
┌─────────────────────────────────────────┐
│ STEP 1: Render Blueprint Deploy         │ ← 10 min
│ (render.yaml already project mein hai) │
│ GitHub connect karo → Blueprint import  │
│ Secrets add karo → Deploy!             │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│ STEP 2: Vercel Frontend Deploy          │ ← 5 min
│ (GitHub se auto-import)                │
│ NEXT_PUBLIC_API_URL =                  │
│  https://pramaan-shield-backend        │
│            .onrender.com               │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│ STEP 3: Test karo                      │ ← 2 min
│ https://pramaan-shield.vercel.app      │
│ Scan karo → Result aana chahiye        │
└───────────────────┬─────────────────────┘
                    │
                    ▼
                  DONE! 🎉
         Submit on HackCulture
```

---

## ⚡ STEP 1 — RENDER BACKEND (10 min)

### 1.1 — Render par jaao

👉 **Click karo**: https://dashboard.render.com
→ "**Sign in with GitHub**" se login karo

### 1.2 — New Blueprint banao

👉 **Click karo**: New + → **Blueprint**

```
1. "Connect a repository" → prakashshiromani/PRAMAAN-SHIELD

2. Render automatically "render.yaml" detect kar lega!
   Service name: pramaan-shield-backend ✅ auto-set

3. [Apply] button dabao
```

### 1.3 — Environment Variables add karo

> Render Dashboard → pramaan-shield-backend → **Environment** tab

```
Key                    Value
──────────────────     ──────────────────────────────────────────────
GEMINI_API_KEY      =  <YOUR_GEMINI_API_KEY>

MONGO_URI           =  <YOUR_MONGODB_URI>

REDIS_URL           =  <YOUR_REDIS_URL>

TELEGRAM_BOT_TOKEN  =  8947205657:AAFgMGr5r8iujfLFrwz8PP6pNtb4E4Vt2I0
IP_HMAC_SALT        =  pramaan2026sebi_salt_blackghost
ENTITY_KEY_PEPPER   =  blackghost_entity_pepper_2026sebi
REPORT_ACCESS_SECRET=  pramaan_report_secret_2026
ALLOWED_ORIGINS     =  https://pramaan-shield.vercel.app
```

> [Save Changes] → Render automatically redeploy karega

> ✅ **Backend URL ready**: `https://pramaan-shield-backend.onrender.com`

---

## ⚡ STEP 2 — VERCEL FRONTEND (5 min)

### 2.1 — Vercel pe login

👉 **Click karo**: https://vercel.com
→ "Continue with GitHub" se login

### 2.2 — New Project

👉 **Click karo**: https://vercel.com/new

```
Import Git Repository → prakashshiromani/PRAMAAN-SHIELD select karo

Configure Project:
  Root Directory:      frontend    ← IMPORTANT! "frontend" type karo
  Framework Preset:    Next.js     ← auto detect hoga

Environment Variables:
  NEXT_PUBLIC_API_URL = https://pramaan-shield-backend.onrender.com

[Deploy]
```

> ✅ **Frontend URL ready**: `https://pramaan-shield.vercel.app`

---

## ⚡ STEP 3 — TEST (2 min)

Browser mein open karo:

```
1. Backend health check:
   https://pramaan-shield-backend.onrender.com/health

   Expected response:
   {"status": "ok", "version": "1.0.0", "service": "PRAMAAN-SHIELD"}

2. Backend API docs:
   https://pramaan-shield-backend.onrender.com/docs

3. Frontend:
   https://pramaan-shield.vercel.app

   Scan page pe jao → koi text paste karo → Result aana chahiye
```

> ⚠️ **Note:** Render Free tier par 15 min inactivity ke baad service "sleep" ho jaati hai.
> Demo ke waqt pehle `/health` open karke 30-60 sec warm up karo!

---

## 📋 HACKCULTURE FORM MEIN YEH DAALO

```
┌─────────────────────────────────────────────────────────────────┐
│ Project Title:    PRAMAAN-SHIELD — Three-Pillar Trust Engine    │
│                                                                 │
│ Prototype Name:   PRAMAAN-SHIELD (प्रमाण शील्ड)                │
│                                                                 │
│ Brief Solution:   AI-driven deepfake detection + voice clone    │
│                   detection + phishing analysis + ECDSA         │
│                   cryptographic PRAMAAN Seal + one-tap SEBI     │
│                   SCORES complaint — unified Trust Score 0-100  │
│                   with bilingual Hindi/English explainability   │
│                                                                 │
│ Demo Video Link:  [YouTube Unlisted link — Loom se record karo] │
│                                                                 │
│ Prototype Link:   https://pramaan-shield.vercel.app        🌟   │
│                                                                 │
│ GitHub Link:      https://github.com/prakashshiromani/          │
│                                    PRAMAAN-SHIELD               │
│                                                                 │
│ Pitch Deck:       [Google Slides / Canva link]                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🆘 AGAR PROBLEM AAYE

| Problem | Fix |
|---------|-----|
| Render build fail | Dashboard → Service → **Logs** tab check karo |
| "CORS error" frontend pe | Render → Environment → `ALLOWED_ORIGINS` check karo |
| Vercel "404 not found" | Root Directory = `frontend` set hai? Check karo |
| Render service "sleeping" | URL open karo, 30-60 sec wait karo — warm up ho jaata hai |
| MongoDB connection refused | Atlas → Network Access → `0.0.0.0/0` whitelist karo |
| Render "Build failed" | `requirements-render.txt` check karo — sahi version hai |

---

## 🎯 SUMMARY — SIRF 2 KAAM BAAKI HAIN

```
✅ MongoDB Atlas    — DONE
✅ Redis Upstash    — DONE
✅ GitHub Repo      — DONE (prakashshiromani/PRAMAAN-SHIELD)
─────────────────────────────────────────
❌ STEP 1: Render Backend Deploy    [10 min]
❌ STEP 2: Vercel Frontend Deploy   [5 min]
─────────────────────────────────────────
TOTAL: ~15 minutes baki hain!
```
