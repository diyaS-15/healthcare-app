# 🏗️ Blood Report AI - Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (React)                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │   Login      │ │  Dashboard   │ │   Analysis   │         │
│  └──────────────┘ └──────────────┘ └──────────────┘         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │   Upload     │ │  Analytics   │ │  Voice Chat  │         │
│  └──────────────┘ └──────────────┘ └──────────────┘         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS + Client-side Encryption
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND API (FastAPI)                       │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │ Auth API   │ │ Reports    │ │ Trends API │              │
│  └────────────┘ └────────────┘ └────────────┘              │
│  ┌────────────┐ ┌────────────────────────────┐              │
│  │ Chat API   │ │ Voice API (Whisper + TTS)  │              │
│  └────────────┘ └────────────────────────────┘              │
└──────────────────────────┬──────────────────────────────────┘
           │                                    │
           │ JWT Auth                          │ Uses these services
           ↓                                    ↓
     ┌──────────────────────────────────────────────┐
     │         BUSINESS LOGIC LAYER                  │
     │  ┌────────────────────────────────────────┐  │
     │  │ 1. Encryption Service (AES-256-GCM)  │  │
     │  │    - Encrypts/decrypts sensitive data │  │
     │  └────────────────────────────────────────┘  │
     │  ┌────────────────────────────────────────┐  │
     │  │ 2. PDF/Image Extractor (GPT-4o)      │  │
     │  │    - Extracts markers from documents   │  │
     │  └────────────────────────────────────────┘  │
     │  ┌────────────────────────────────────────┐  │
     │  │ 3. Normalizer                          │  │
     │  │    - Maps 100+ marker name variants    │  │
     │  └────────────────────────────────────────┘  │
     │  ┌────────────────────────────────────────┐  │
     │  │ 4. Trend Engine (NumPy/SciPy)         │  │
     │  │    - Statistical analysis              │  │
     │  │    - Pattern detection                 │  │
     │  │    - Stability scoring                 │  │
     │  └────────────────────────────────────────┘  │
     │  ┌────────────────────────────────────────┐  │
     │  │ 5. LLM Brain (GPT-4o)                 │  │
     │  │    - Intelligent explanations          │  │
     │  │    - Safety guardrails                 │  │
     │  │    - Follow-up responses               │  │
     │  └────────────────────────────────────────┘  │
     │  ┌────────────────────────────────────────┐  │
     │  │ 6. Voice Service (Whisper+ElevenLabs) │  │
     │  │    - Speech-to-text                    │  │
     │  │    - Text-to-speech (2 providers)     │  │
     │  └────────────────────────────────────────┘  │
     └──────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ↓               ↓               ↓
      ┌─────────┐   ┌──────────┐   ┌──────────────┐
      │Supabase │   │ OpenAI   │   │ ElevenLabs   │
      │Database │   │ APIs     │   │ TTS API      │
      │(Auth +  │   │(GPT-4o   │   │              │
      │ PostgreSQL) │Whisper)  │   │              │
      └─────────┘   └──────────┘   └──────────────┘
```

---

## Tech Stack

### Frontend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI Framework** | React 18 | Component-based UI |
| **Build Tool** | Vite | Fast dev server, optimized builds |
| **Routing** | React Router v6 | Client-side navigation |
| **State Management** | Zustand | Lightweight auth state |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **Encryption** | Web Crypto API | Client-side AES-256-GCM |
| **HTTP Client** | Axios (via api.js) | API communication |
| **Backend SDK** | @supabase/supabase-js | Auth + DB queries |

**Key Files:**
- `App.jsx` - Protected routes, auth initialization
- `pages/*.jsx` - UI pages (Login, Dashboard, Upload, Analysis, Analytics)
- `lib/api.js` - HTTP client wrapping all backend endpoints
- `lib/encryption.js` - AES-256-GCM crypto primitives
- `store/authStore.js` - Zustand auth state

---

### Backend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Web Framework** | FastAPI 0.111 | Modern async Python API |
| **ASGI Server** | Uvicorn | Production ASGI server |
| **Validation** | Pydantic v2 | Request/response validation, 50+ schemas |
| **Auth** | Supabase Auth + JWT | OAuth + session tokens |
| **Database** | Supabase PostgreSQL + SQLAlchemy | Async DB operations |
| **AI/ML** | OpenAI GPT-4o, Whisper | NLP for extraction & explanation |
| **Audio** | ElevenLabs API | High-quality TTS |
| **Statistics** | NumPy, SciPy | Trend detection algorithms |
| **Crypto** | cryptography + secrets | AES-256-GCM encryption |
| **Deployment** | Railway, Docker | Containerized deployment |

**Key Files:**
- `main.py` - FastAPI app initialization, middleware, exception handlers
- `config.py` - Environment variable management
- `dependencies.py` - JWT auth middleware
- `models/schemas.py` - 50+ Pydantic request/response models
- `routers/*.py` - 5 API routers (auth, reports, trends, chat, voice)
- `services/*.py` - Business logic (encryption, extraction, analysis, LLM, voice)
- `utils/supabase_client.py` - Database abstraction layer

---

### Database

| Database | Technology | Purpose |
|----------|-----------|---------|
| **Primary DB** | Supabase PostgreSQL | Main data storage |
| **Vector DB** | pgvector (PostgreSQL extension) | Semantic search for knowledge base |
| **Auth Backend** | Supabase Auth | User authentication |
| **Security** | Row-Level Security (RLS) | Data isolation per user |

**8 Tables:**

1. **users** (linked to auth.users)
   - profile_id (PK)
   - user_id (FK to auth.users)
   - full_name, email
   - created_at, updated_at
   - RLS: Users see only their own profile

2. **blood_reports**
   - report_id (PK)
   - user_id (FK)
   - report_date, lab_name
   - encrypted_raw_text (encrypted PDF content)
   - processed_at
   - RLS: Users see only their own reports

3. **blood_markers**
   - marker_id (PK)
   - report_id (FK)
   - marker_name, value, unit
   - reference_range_min, reference_range_max
   - is_abnormal
   - RLS: Users see only their own markers

4. **trend_analysis**
   - trend_id (PK)
   - user_id (FK)
   - marker_name
   - trend_direction (increasing/decreasing/stable)
   - change_percent, consistency
   - stability_score (0-100)
   - RLS: Users see only their own trends

5. **ai_conversations**
   - conversation_id (PK)
   - user_id (FK)
   - report_id (FK, nullable)
   - message_content (encrypted)
   - sender (user/assistant)
   - timestamp
   - RLS: Users see only their own conversations

6. **knowledge_base**
   - knowledge_id (PK)
   - marker_name
   - educational_content
   - vector_embedding (pgvector)
   - NO RLS (public educational content)

7. **audit_log**
   - log_id (PK)
   - user_id (FK)
   - action, resource_type, resource_id
   - timestamp
   - RLS: Users see only their own logs

---

## API Architecture

### Authentication Flow

```
Client Login Request
    ↓
Supabase Auth ← Email + Password
    ↓
JWT Token (signed with SUPABASE_JWT_SECRET)
    ↓
Client stores in authStore
    ↓
Later: Each API request includes JWT in header
    ↓
FastAPI dependencies.py validates JWT
    ↓
Extracts user_id from token
    ↓
Passes to endpoint handlers
```

### Data Encryption Strategy

**2-Layer Encryption:**

1. **Client-side (Browser):** Web Crypto API
   - File content encrypted before upload
   - Chat messages encrypted before send
   - Key derived from user's password + salt

2. **Server-side (Backend):** AES-256-GCM
   - Additional layer for stored data
   - Encryption key from ENCRYPTION_SECRET env var
   - Database stores encrypted_raw_text

**Result:** Even if database is compromised, data remains encrypted.

---

## Request/Response Flow Example

### Blood Report Upload

```
1. User selects PDF in Upload.jsx
   ↓
2. Frontend encrypts file using Web Crypto API
   ↓
3. POST /api/reports/upload with:
   - JWT token in Authorization header
   - Multipart file data
   - Report date
   ↓
4. Backend (routers/reports.py):
   a. Validates JWT (dependencies.py)
   b. Validates file size/type
   c. Moves file to temp storage
   ↓
5. Calls services/extractor.py:
   a. Extracts text from PDF
   b. Calls GPT-4o to parse markers
   c. Returns structured JSON
   ↓
6. Calls services/normalizer.py:
   a. Normalizes marker names
   b. Maps to standard names
   ↓
7. Calls services/encryption.py:
   a. Encrypts parsed data
   ↓
8. Calls utils/supabase_client.py:
   a. Saves report metadata
   b. Saves markers with normalized names
   c. Triggers trend analysis
   ↓
9. Returns reportId + extracted markers
   ↓
10. Frontend navigates to Analysis page
```

### Trend Analysis Request

```
1. User clicks "View Analytics" on Dashboard
   ↓
2. Frontend: GET /api/trends/analysis (with JWT)
   ↓
3. Backend (routers/trends.py):
   a. Gets all reports for user
   b. Organizes markers over time
   ↓
4. Calls services/trend_engine.py:
   a. For each marker:
      - Fits line to historical values
      - Calculates slope (increasing/decreasing/stable)
      - Analyzes volatility
   b. Cross-marker patterns:
      - Checks for lipid profile patterns
      - Glucose control hints
      - Anemia indicators
   c. Stability score:
      - 0-100 scale
      - Considers all markers
   ↓
5. Returns trends + patterns + score
   ↓
6. Frontend displays in Analytics.jsx with charts
```

---

## Security Architecture

### Data Protection

| Layer | Method | Key |
|-------|--------|-----|
| **Client-Server** | HTTPS TLS 1.3 | Encrypted in transit |
| **Client-side** | Web Crypto AES-256-GCM | PBKDF2 derived from password |
| **Server-side** | AES-256-GCM | ENCRYPTION_SECRET env var |
| **Database** | Row-Level Security | PostgreSQL RLS policies |
| **Authentication** | JWT | SUPABASE_JWT_SECRET |

### Authentication & Authorization

**JWT Token Flow:**
1. User signs up → Supabase Auth creates user + issues JWT
2. JWT contains: user_id, exp (expiration), iss (issuer), etc.
3. Backend validates signature using SUPABASE_JWT_SECRET
4. RLS policies enforce: `auth.uid() = user_id`

**Middleware Chain:**
```python
Request
  ↓
CORS Check (allowed origins)
  ↓
Route Handler
  ↓
dependencies.get_current_user() - Validates JWT
  ↓
Extract user_id from token
  ↓
Pass to endpoint
  ↓
Endpoint builds query with WHERE user_id = extracted_id
  ↓
Database RLS ALSO checks: auth.uid() = user_id
  ↓
Response (or 401/403 error)
```

---

## AI & ML Components

### 1. **Marker Extraction (GPT-4o Vision)**

**Input:** PDF or image of blood report
**Process:**
- Tesseract OCR for text extraction
- PyMuPDF for PDF parsing
- GPT-4o vision to parse layout-agnostic
- Outputs: marker_name, value, unit, ref_ranges

**Code:** `services/extractor.py`

### 2. **Trend Detection (NumPy/SciPy)**

**Input:** Historical marker values over time
**Algorithms:**
- **Linear Regression:** Trend direction slope
- **Volatility Analysis:** Standard deviation of changes
- **Consistency Check:** How many samples in that trend
- **Change Percent:** (Latest - Oldest) / Oldest * 100

**Output:** Direction (↑/→/↓), %, stability

**Code:** `services/trend_engine.py`

### 3. **Pattern Analysis (Heuristics)**

**Cross-Marker Patterns:**
- Lipid profile: High triglycerides + high LDL
- Glucose control: High glucose + high HbA1c
- Anemia: Low hemoglobin + low red cells
- Liver health: Elevated ALT/AST

**Output:** "Possible pattern detected: X"

**Code:** `services/trend_engine.py` (detect_cross_marker_patterns)

### 4. **Natural Language Explanations (GPT-4o)**

**Input:** Markers, trends, patterns
**Prompt Engineering:**
- Master system prompt (25 safety rules)
- Prevents diagnosis ("not a diagnosis, educational only")
- Prevents alarming language
- Encourages lifestyle/doctor questions

**Output:** Educational explanation + follow-up questions

**Code:** `services/llm_brain.py`

### 5. **Voice Processing**

**Speech-to-Text:**
- OpenAI Whisper API
- Transcribes user question from audio

**Text-to-Speech:**
- ElevenLabs (primary) - Natural voices
- OpenAI TTS (fallback) - Simple backup
- Streams audio back as base64

**Code:** `services/voice_service.py`

---

## Performance Optimizations

### Backend

| Optimization | Implementation |
|--------------|-----------------|
| **Async I/O** | All operations use async/await |
| **Connection Pooling** | Supabase auto-pools SQL connections |
| **Database Indexes** | 10+ indexes on frequently queried columns |
| **Response Compression** | Uvicorn gzip middleware |
| **Caching** | Trend analysis cached in DB |
| **JWT Caching** | Token reused until expiration |

### Frontend

| Optimization | Implementation |
|--------------|-----------------|
| **Lazy Loading** | React Router lazy code splitting |
| **Image Optimization** | Vite auto-optimizes assets |
| **State Management** | Zustand (minimal overhead) |
| **CSS** | Tailwind PurgeCSS removes unused CSS |
| **Build** | Vite minification + tree shaking |

---

## Deployment Architecture

### Local Development
```
localhost:5173 (Frontend)
    ↓ (API calls)
localhost:8000/api (Backend)
    ↓ (Auth + DB)
Supabase (Cloud)
```

### Production

```
vercel.app (Frontend) ← Deployed on Vercel CI/CD
    ↓ (API calls)
railway.app (Backend) ← Deployed on Railway CI/CD
    ↓ (Auth + DB)
Supabase (Cloud) ← Single source of truth
```

**CI/CD:**
- Push to GitHub
- Vercel auto-deploys frontend
- Railway auto-deploys backend
- Environment variables injected at build time

---

## Error Handling

### Backend Exception Handling

```python
try:
    # Endpoint logic
except ValueError:
    raise HTTPException(400, "Invalid input")
except UnauthorizedError:
    raise HTTPException(401, "Not authenticated")
except PermissionError:
    raise HTTPException(403, "Not authorized")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(500, "Server error")
```

### Frontend Error Handling

```javascript
try {
    const data = await api.uploadReport(...)
    setReports([...reports, data])
} catch (error) {
    if (error.status === 401) {
        // Token expired, redirect to login
    } else if (error.status === 413) {
        // File too large
    } else {
        // Generic error
    }
}
```

---

## Monitoring & Logging

### Backend Logging

Configuration in `config.py`:
- **INFO:** Startup messages, API requests
- **ERROR:** Exceptions, validation failures
- **DEBUG:** Database queries, token validation

Logs stored in:
- Railway dashboard (production)
- Console (local development)

### Frontend Analytics (Optional)

Could add:
- PostHog or Mixpanel for user behavior
- Sentry for error tracking
- Google Analytics for traffic

---

## Future Enhancements

### Short Term
- [ ] PDF export of analysis
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Dark mode UI

### Medium Term
- [ ] Mobile app (React Native)
- [ ] Advanced visualizations (D3.js)
- [ ] Predictive ML models
- [ ] HIPAA compliance audit

### Long Term
- [ ] Federated learning (privacy-preserving)
- [ ] Blockchain for audit trail
- [ ] Integration with EHR systems
- [ ] Multi-tenant SaaS

---

## References

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev
- **Supabase Docs:** https://supabase.io/docs
- **OpenAI API:** https://platform.openai.com/docs
- **Tailwind CSS:** https://tailwindcss.com/docs

---

This document is your **technical blueprint**. Refer back to this when:
- Debugging issues
- Adding new features
- Optimizing performance
- Deploying to production

**Enjoy! 🚀**
