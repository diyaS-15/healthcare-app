# 🏥 Blood Report AI - Intelligent Health Analysis Platform

**The future of personal health insights powered by AI**

An end-to-end encrypted, AI-powered platform that transforms blood reports into actionable health insights. Built with modern tech, ready for production deployment.

---

## ✨ What It Does

### For Users
1. **Upload** blood reports (PDF, PNG, TIFF)
2. **Smart Extraction** - AI extracts all markers automatically
3. **AI Explanation** - GPT-4o explains what markers mean
4. **Trend Analysis** - Tracks changes over time
5. **Chat** - Ask questions, get answers (voice or text)
6. **Health Insights** - Comprehensive analytics dashboard

### For Developers
- **Complete System** - Not just a demo, fully functional
- **Production Ready** - Proper auth, encryption, error handling
- **Well Documented** - Comments, architecture guide, deployment steps
- **Extensible** - Add features easily (PDF export, notifications, etc.)
- **Secure** - End-to-end encryption, RLS, JWT auth

---

## 🎯 Key Features

✅ **End-to-End Encryption**
- Client-side AES-256-GCM
- Server-side AES-256-GCM  
- Medical data stays private

✅ **Intelligent Analysis**
- GPT-4o powered marker extraction
- Statistical trend detection
- Cross-marker pattern analysis
- Stability scoring

✅ **Voice Interaction**
- Whisper speech-to-text
- ElevenLabs/OpenAI TTS
- Voice-based Q&A

✅ **Beautiful UI**
- React + Tailwind CSS
- Responsive design
- Dark-mode ready (add it yourself!)
- Smooth animations

✅ **Production Architecture**
- FastAPI async backend
- Supabase PostgreSQL
- Row-Level Security
- Proper error handling

✅ **Easy Deployment**
- Railway (backend)
- Vercel (frontend)
- One-click CI/CD

---

## 🚀 Quick Start

### 3-Step Setup

**1. Install**
```bash
# Backend
cd blood-report-ai/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Frontend  
cd blood-report-ai/frontend
npm install
```

**2. Configure**
```bash
# Get API keys from:
# - Supabase (free): https://supabase.com
# - OpenAI: https://platform.openai.com/api-keys

# Create .env files:
cd blood-report-ai/backend && cp .env.example .env
cd blood-report-ai/frontend && cp .env.example .env.local

# Fill in your keys
```

**3. Run**
```bash
# Terminal 1
cd blood-report-ai/backend
python -m uvicorn main:app --reload

# Terminal 2
cd blood-report-ai/frontend
npm run dev

# Open http://localhost:5173
```

**Full Setup Guide:** See [QUICKSTART.md](QUICKSTART.md) (5 minutes) or [SETUP_GUIDE.md](SETUP_GUIDE.md) (comprehensive)

---

## 📁 Project Structure

### Backend (FastAPI Python)
```
backend/
├── main.py                 # App entry point
├── config.py              # Settings
├── dependencies.py        # Auth middleware
├── models/
│   ├── schemas.py        # Request/response models
│   └── db_models.py      # Database schema docs
├── routers/              # 25+ API endpoints
│   ├── auth.py           # Login/signup
│   ├── reports.py        # Upload & analysis
│   ├── trends.py         # Trend API
│   ├── chat.py           # Chat API
│   └── voice.py          # Voice API
├── services/            # Business logic
│   ├── encryption.py    # AES-256-GCM
│   ├── extractor.py     # PDF/Image→JSON
│   ├── normalizer.py    # Marker normalization
│   ├── trend_engine.py  # Statistical analysis
│   ├── llm_brain.py     # GPT-4o prompts
│   └── voice_service.py # Whisper+TTS
└── utils/
    └── supabase_client.py # Database ops
```

### Frontend (React Vite)
```
frontend/
├── src/
│   ├── pages/           # Full-page components
│   │   ├── Login.jsx    # Authentication
│   │   ├── Dashboard.jsx # Home page
│   │   ├── Upload.jsx   # File upload
│   │   ├── Analysis.jsx # Report analysis
│   │   └── Analytics.jsx # Health dashboard
│   ├── lib/            # Business logic
│   │   ├── api.js      # HTTP client
│   │   ├── supabase.js # Auth client
│   │   └── encryption.js # Crypto utils
│   ├── store/          # State management
│   │   └── authStore.js # Zustand store
│   └── App.jsx         # Router setup
└── tailwind.config.js
```

### Database (Supabase PostgreSQL)
```
Database schema includes:
- users (Supabase Auth linked)
- blood_reports
- blood_markers
- trend_analysis
- ai_conversations
- knowledge_base
- audit_log

All with Row-Level Security enabled
See: supabase/migrations/001_init.sql (250+ lines)
```

---

## 🔐 Security

### Encryption
- **Client-side:** Web Crypto API AES-256-GCM
- **Server-side:** Python cryptography AES-256-GCM
- **Transport:** HTTPS TLS 1.3
- **Database:** Row-Level Security

### Authentication
- **Provider:** Supabase Auth (OAuth ready)
- **Sessions:** JWT tokens (HS256)
- **Middleware:** JWT validation on every endpoint

### Data Isolation
- **RLS Policies:** Users can only see their own data
- **Audit Logging:** Track every action
- **No PII Export:** Data never leaves system unencrypted

---

## 🤖 AI Features

### 1. Marker Extraction
```
Input: Blood report (PDF/PNG)
↓
Tesseract OCR + PyMuPDF
↓
GPT-4o Vision API
↓
Output: JSON {marker_name, value, unit, ref_range}
```

### 2. Trend Analysis
```
Input: Historical marker values
↓
NumPy linear regression
↓
SciPy statistics
↓
Output: {direction, change%, volatility, consistency}
```

### 3. Natural Language
```
Input: Markers + trends
↓
GPT-4o with safety guardrails
↓
25-rule prompt engineering
↓
Output: Educational explanation (not diagnosis!)
```

### 4. Voice Chat
```
Input: User speaking
↓
Whisper speech-to-text
↓
GPT-4o conversation
↓
ElevenLabs text-to-speech
↓
Output: Voice response
```

---

## 📊 Architecture Diagram

```
┌─ FRONTEND (React) ─┐
│ Login | Dashboard  │
│ Upload | Analysis  │
│ Analytics | Voice  │
└────────┬───────────┘
         │ HTTPS + Encryption
         ↓
┌─ BACKEND (FastAPI) ─────┐
│ Auth | Reports | Trends │
│ Chat | Voice | Config   │
├────────────────────────┤
│ Services:              │
│ • Encryption (AES-256) │
│ • Extraction (GPT-4o)  │
│ • Normalization        │
│ • Trends (NumPy)       │
│ • LLM Brain (GPT-4o)   │
│ • Voice (Whisper+TTS)  │
└────────┬───────────────┘
         │ Async
         ↓
┌─ DATABASE (Supabase PostgreSQL) ─┐
│ Users | Reports | Markers | Trends│
│ Conversations | Knowledge | Logs  │
│ (Row-Level Security enabled)      │
└────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for deep dive.

---

## 🚀 Deployment

### Development (Local)
```bash
# Backend: localhost:8000
python -m uvicorn main:app --reload

# Frontend: localhost:5173
npm run dev
```

### Production
```
Railway Backend → https://yourname-prod.railway.app
Vercel Frontend → https://yourname.vercel.app
Supabase Database → Cloud hosted
```

**One-Command Deployment:**
1. Push to GitHub
2. Connect to Railway (backend)
3. Connect to Vercel (frontend)
4. Set environment variables
5. Deploy automatically on every push

See [SETUP_GUIDE.md](SETUP_GUIDE.md) Phase 5 for step-by-step.

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [QUICKSTART.md](QUICKSTART.md) | Get running in 5 minutes |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Complete setup (all phases) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical deep dive |
| Code comments | Inline explanations |

---

## 💡 What Makes This Different

### vs. Existing Blood Analysis Apps
- ✅ **Open Source** - You own the code
- ✅ **End-to-End Encrypted** - Even we don't see your data
- ✅ **No Paywall** - Deploy for free
- ✅ **Extensible** - Add features as needed
- ✅ **Production-Ready** - Not a tutorial, actual system

### vs. Just an API
- ✅ **Complete UI** - Beautiful React interface
- ✅ **Auth System** - User management included
- ✅ **Database** - Full schema, RLS, migrations
- ✅ **AI Safety** - Guardrails preventing misuse
- ✅ **Documentation** - Not just code, actual guidance

---

## 🛠️ Tech Stack

**Backend:**
- FastAPI 0.111 - Modern async framework
- Pydantic v2 - Data validation
- Supabase - Auth + PostgreSQL
- OpenAI - GPT-4o, Whisper APIs
- ElevenLabs - Voice synthesis
- NumPy/SciPy - Statistics
- cryptography - AES encryption

**Frontend:**
- React 18 - UI framework
- Vite - Build tool
- React Router v6 - Routing
- Zustand - State management
- Tailwind CSS - Styling
- Web Crypto API - Client-side encryption

**Infrastructure:**
- Supabase - Database + Auth
- Railway - Backend hosting
- Vercel - Frontend hosting
- GitHub - Version control

---

## 📋 Checklist to Go Live

- [ ] Create Supabase account
- [ ] Create OpenAI account + get API key
- [ ] Copy `.env.example` → `.env`
- [ ] Fill in all environment variables
- [ ] Run SQL migration in Supabase
- [ ] Test locally (see QUICKSTART.md)
- [ ] Create Railway account
- [ ] Create Vercel account
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Vercel
- [ ] Test in production
- [ ] Celebrate! 🎉

---

## 🐛 Troubleshooting

### "Supabase connection refused"
→ Check SUPABASE_URL is correct in .env

### "Cannot find module"
→ Run `pip install -r requirements.txt` or `npm install`

### "API returns 401"
→ JWT token expired, make sure SUPABASE_JWT_SECRET matches

### "File upload fails"
→ Check CORS in backend .env includes your frontend URL

See [SETUP_GUIDE.md](SETUP_GUIDE.md) Troubleshooting section for more.

---

## 🎓 Learn From This

This project demonstrates:

- **Backend:** FastAPI best practices, async Python, JWT auth, database design
- **Frontend:** React hooks, routing, state management, Tailwind CSS
- **Full Stack:** API design, error handling, security, deployment
- **AI Integration:** Prompt engineering, LLM safety, multi-AI orchestration
- **DevOps:** Environment management, CI/CD, cloud deployment

Perfect reference for:
- Building your own SaaS
- Learning modern Python web dev
- Understanding AI integration patterns
- Secure data handling practices

---

## 📝 License

Open source. Use as you wish.

---

## 🙋 Next Steps

**Ready to go?**
1. Read [QUICKSTART.md](QUICKSTART.md) (5 min read)
2. Set up locally
3. Test in browser
4. Deploy to cloud

**Want to extend it?**
1. Check [ARCHITECTURE.md](ARCHITECTURE.md)
2. Add new endpoint in `routers/`
3. Add service logic in `services/`
4. Add React component in `frontend/src/pages/`
5. Push to GitHub, watch it deploy

**Questions?**
- Check inline code comments
- Read documentation files
- Check error messages (they're detailed)
- Review test flow in SETUP_GUIDE

---

## 🎯 The Vision

This isn't just software—it's a **health liberation tool**.

In a world where:
- Health data is monetized
- Black-box algorithms make decisions
- Users have no control

We're building:
- Open, transparent systems
- User-controlled data
- Understandable AI
- Tools that empower, not exploit

**Every person deserves to understand their health.**

---

**Built with ❤️ for clarity, security, and empowerment.**

Let's make health data personal again. 🚀

