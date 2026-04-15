# 📂 Project File Guide - What's Everything?

**Complete map of your AI-powered blood report system**

---

## 📖 Start Here (Read in This Order)

1. **[README.md](README.md)** - Project overview (5 min)
2. **[QUICKSTART.md](QUICKSTART.md)** - Get running locally (5 min)
3. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup & troubleshooting (30 min)
4. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy to production (45 min)
5. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical deep dive (reference)

---

## 🗂️ Root Directory Structure

```
healthcare-app/
├── README.md                 # ← START HERE
├── QUICKSTART.md            # Get running in 5 min
├── SETUP_GUIDE.md           # Complete setup
├── DEPLOYMENT.md            # Production deployment
├── ARCHITECTURE.md          # Technical reference
├── FILE_GUIDE.md            # This file
│
├── blood-report-ai/         # Main application
│   ├── backend/             # Python FastAPI
│   ├── frontend/            # React + Vite
│   └── supabase/            # Database migrations
│
├── main.py                  # Placeholder (ignore)
├── train.ipynb              # Placeholder (ignore)
├── package.json             # Root workspace config
└── kantesti_global_health_insights_2025_2026.csv # Sample data

myenv/                        # Old Python env (can delete)
```

---

## 🔧 Backend: `blood-report-ai/backend/`

### Configuration Files

| File | Purpose | Size |
|------|---------|------|
| **main.py** | FastAPI app entry point | 250 lines |
| **config.py** | Environment & settings | 60 lines |
| **dependencies.py** | JWT auth middleware | 50 lines |
| **requirements.txt** | Python package list | 30 lines |
| **.env.example** | Template env variables | 70 lines |
| **.env** | Your actual env (create from .env.example) | To fill |

**How it works:**
1. `main.py` starts FastAPI app
2. Imports routers from `routers/` folder
3. Each request goes through JWT middleware in `dependencies.py`
4. Settings come from `config.py` (which reads from `.env`)

### Models: `blood-report-ai/backend/models/`

| File | Purpose | Contents |
|------|---------|----------|
| **schemas.py** | Request/response validation | 50+ Pydantic models |
| **db_models.py** | Database table documentation | 8 table schemas |

**Example models:**
```python
class SignUpRequest:
    email: str
    password: str
    full_name: str

class BloodMarkerResponse:
    marker_name: str
    value: float
    unit: str
    is_abnormal: bool
```

### Routers: `blood-report-ai/backend/routers/`

HTTP API endpoints. Each file handles one domain.

| File | Endpoints | Purpose |
|------|-----------|---------|
| **auth.py** | POST /signup, /login, /refresh | User authentication |
| **reports.py** | POST /upload, GET /history | Blood reports |
| **trends.py** | GET /analysis, /marker/{name} | Trend analysis |
| **chat.py** | POST /message, GET /history | Chat with AI |
| **voice.py** | POST /transcribe, /synthesize | Voice interaction |

**Example endpoint:**
```python
@router.post("/upload")
async def upload_report(
    file: UploadFile,
    report_date: date,
    current_user = Depends(get_current_user)
):
    # Extract markers from PDF/PNG
    # Normalize names
    # Encrypt data
    # Save to database
    # Trigger trend analysis
    return {"report_id": "123", "markers": [...]}
```

### Services: `blood-report-ai/backend/services/`

Business logic & AI integration

| File | Purpose | Key Functions |
|------|---------|---|
| **encryption.py** | AES-256-GCM crypto | `encrypt_data()`, `decrypt_data()` |
| **extractor.py** | PDF/image → JSON | `extract_report()` |
| **normalizer.py** | Marker name mapping | `normalize_marker_name()` |
| **trend_engine.py** | Statistical analysis | `detect_trend_direction()`, `run_full_analysis()` |
| **llm_brain.py** | GPT-4o integration | `explain_report()`, `general_chat()` |
| **voice_service.py** | Whisper + TTS | `transcribe_audio()`, `synthesize_speech()` |

**How they work together:**
```
Upload Report
  ↓
extractor.py (GPT-4o) → Extract markers
  ↓
normalizer.py → Map marker names
  ↓
encryption.py → Encrypt data
  ↓
supabase_client.py → Save to database
  ↓
trend_engine.py → Analyze trends
  ↓
llm_brain.py → Generate explanation
```

### Utils: `blood-report-ai/backend/utils/`

| File | Purpose | Key Functions |
|------|---------|---|
| **supabase_client.py** | Database operations | `save_report()`, `get_trends()`, `save_chat_message()` |

**Example function:**
```python
async def save_report(user_id: str, report_data: dict):
    """Save blood report to Supabase"""
    response = await supabase.table("blood_reports").insert({
        "user_id": user_id,
        "report_date": report_data["date"],
        "encrypted_raw_text": report_data["encrypted_text"],
        ...
    }).execute()
    return response
```

---

## 🎨 Frontend: `blood-report-ai/frontend/`

### Configuration

| File | Purpose |
|------|---------|
| **package.json** | Dependencies & scripts |
| **vite.config.js** | Vite bundler config |
| **tailwind.config.js** | Tailwind CSS config |
| **eslint.config.js** | Linting rules |
| **.env.example** | Template env vars |
| **.env.local** | Your actual env (create from .env.example) |
| **index.html** | HTML entry point |

### Pages: `blood-report-ai/frontend/src/pages/`

Complete pages the user sees

| File | Route | Purpose |
|------|-------|---------|
| **Login.jsx** | `/login` | Sign up & login page |
| **Dashboard.jsx** | `/dashboard` | Home page with stats |
| **Upload.jsx** | `/upload` | Drag-and-drop file upload |
| **Analysis.jsx** | `/analysis/:reportId` | View report + chat |
| **Analytics.jsx** | `/analytics` | Health insights dashboard |

**Example page structure:**
```jsx
export default function Dashboard() {
  const { user } = useAuthStore()
  const [reports, setReports] = useState([])
  
  useEffect(() => {
    // Fetch reports from API
    api.getReports().then(setReports)
  }, [])
  
  return (
    <div>
      <h1>Welcome, {user.email}</h1>
      <StatCard title="Total Reports" value={reports.length} />
      {/* ... */}
    </div>
  )
}
```

### Libraries: `blood-report-ai/frontend/src/lib/`

Core utilities

| File | Purpose | Key Export |
|------|---------|---|
| **supabase.js** | Supabase client | `supabase`, `signup()`, `login()` |
| **api.js** | HTTP client | `APIClient` class with all endpoints |
| **encryption.js** | AES-256-GCM | `encrypt()`, `decrypt()` |

**How they interact:**
```javascript
// 1. User logs in with Supabase
const { user } = await supabase.auth.signInWithPassword({...})

// 2. User uploads file
const reportId = await api.uploadReport({
  file: pdf,
  date: new Date()
})

// 3. Frontend encrypts chat messages
const encrypted = await encryption.encrypt(message, key)

// 4. API client adds JWT to all requests
api.headers.Authorization = `Bearer ${user.token}`
```

### Store: `blood-report-ai/frontend/src/store/`

| File | Purpose | State |
|------|---------|-------|
| **authStore.js** | User session (Zustand) | `user`, `session`, `loading` |

**Example:**
```javascript
// Get user auth state
const { user, isAuthenticated, login } = useAuthStore()

// Subscribe to changes
useEffect(() => {
  const unsub = authStore.subscribe(state => {
    console.log("Auth changed:", state.user)
  })
  return unsub
}, [])
```

### Components (Optional): `blood-report-ai/frontend/src/components/`

**Currently:** Empty (pages are self-contained)

**To add:** Reusable components like:
- `StatCard.jsx` (stat boxes)
- `NavBar.jsx` (navigation)
- `ChatBubble.jsx` (chat messages)

### Styling: `blood-report-ai/frontend/src/`

| File | Purpose |
|------|---------|
| **index.css** | Global styles + Tailwind imports |
| **App.css** | App-level styles |

**Tailwind usage:**
```jsx
<div className="grid grid-cols-4 gap-6 md:gap-8">
  <div className="bg-blue-500 rounded-lg p-4">
    <h2 className="text-xl font-bold text-white">Title</h2>
  </div>
</div>
```

---

## 💾 Database: `blood-report-ai/supabase/`

### Migrations: `supabase/migrations/`

| File | Purpose |
|------|---------|
| **001_init.sql** | Create all tables, indexes, RLS, triggers |

**What it does:**
1. Creates 8 tables (users, blood_reports, blood_markers, etc.)
2. Sets up Row-Level Security policies
3. Creates indexes for performance
4. Adds triggers for auto-updating timestamps
5. Inserts sample knowledge base entries

**To use:**
1. Go to Supabase dashboard
2. SQL Editor
3. Copy-paste entire 001_init.sql
4. Run
5. All tables appear in Table Editor

### Functions (Optional): `supabase/functions/`

**Currently:** Empty (no serverless functions)

**To add:** Database triggers, auth webhooks, scheduled tasks

---

## 📋 Configuration Files (Root)

| File | Purpose |
|------|---------|
| **package.json** | Root workspace config |
| **README.md** | Project overview |
| **QUICKSTART.md** | 5-minute setup |
| **SETUP_GUIDE.md** | Complete setup |
| **DEPLOYMENT.md** | Production deployment |
| **ARCHITECTURE.md** | Technical reference |
| **FILE_GUIDE.md** | This file |

---

## 🚀 Quick Navigation

### "How do I...?"

**Add a new API endpoint?**
1. Open `backend/routers/yourrouter.py`
2. Add function with `@router.post()` decorator
3. Import in `backend/main.py`
4. `app.include_router(yourrouter.router)`

**Add a database operation?**
1. Add async function in `backend/utils/supabase_client.py`
2. Call from router: `await supabase_client.your_function()`

**Add a new page?**
1. Create `frontend/src/pages/YourPage.jsx`
2. Import in `frontend/src/App.jsx`
3. Add route: `<Route path="/your" element={<YourPage />} />`

**Add a new table to database?**
1. Create SQL in `supabase/migrations/002_add_table.sql`
2. Run in Supabase SQL Editor
3. Document in `backend/models/db_models.py`

**Make API call from React?**
1. Use `api.yourEndpoint()` from `frontend/src/lib/api.js`
2. Wrap in `try/catch`
3. Handle errors

**Encrypt/decrypt data?**
1. **Client:** `await encryption.encrypt(data, key)`
2. **Server:** Call `services/encryption.py` functions

**Pull data from Supabase?**
1. Use `supabase_client.your_function()` from backend
2. Or call `api.your_endpoint()` from frontend
3. Both use JWT for auth

---

## 🔐 Environment Variables Guide

### Backend (.env)

```env
# Supabase (Required)
SUPABASE_URL=                    # Project URL
SUPABASE_SERVICE_KEY=            # Service role key
SUPABASE_ANON_KEY=               # Anon key
SUPABASE_JWT_SECRET=             # JWT secret

# OpenAI (Required)
OPENAI_API_KEY=                  # sk-proj-...

# ElevenLabs (Optional)
ELEVENLABS_API_KEY=              # For voice

# Encryption & Security (Required)
ENCRYPTION_SECRET=               # 64-char hex string
JWT_SECRET=                      # Random string

# CORS (Update for production)
ALLOWED_ORIGINS=http://localhost:5173

# Optional
ELEVENLABS_VOICE_ID=en-US-1
OPENAI_MODEL=gpt-4o
LOG_LEVEL=INFO
```

### Frontend (.env.local)

```env
# Supabase (Required)
VITE_SUPABASE_URL=               # Project URL
VITE_SUPABASE_ANON_KEY=          # Anon key

# API (Required)
VITE_API_URL=http://localhost:8000/api
```

---

## 📊 Data Flow Example: Upload Report

```
Frontend (React)
├─ User selects PDF
├─ Show preview
└─ Click "Upload"
   ↓
[Upload.jsx]
├─ Validate file
├─ Call: api.uploadReport(file, date)
└─ Show progress
   ↓
Browser → HTTPS → POST /api/reports/upload
   ↓
[routers/reports.py]
├─ Validate JWT
├─ Validate file size
├─ Save to temp storage
├─ Extract markers
│  └─ [services/extractor.py] uses GPT-4o
├─ Normalize names
│  └─ [services/normalizer.py]
├─ Encrypt content
│  └─ [services/encryption.py]
├─ Save to database
│  └─ [utils/supabase_client.py] inserts row
├─ Trigger trend analysis
│  └─ [services/trend_engine.py]
└─ Return result
   ↓
Browser receives: { reportId, markers: [...] }
   ↓
[Analysis.jsx]
├─ Navigate to /analysis/{reportId}
├─ Display extracted markers
├─ Show AI explanation
│  └─ [services/llm_brain.py] GPT-4o response
└─ Enable chat
```

---

## 🎯 File Sizes & Complexity

### Backend (Total: ~2500 lines)

| File | Lines | Complexity |
|------|-------|-----------|
| services/trend_engine.py | 140 | ⭐⭐⭐ |
| utils/supabase_client.py | 280 | ⭐⭐⭐ |
| routers/reports.py | 200 | ⭐⭐⭐ |
| routers/chat.py | 230 | ⭐⭐⭐ |
| routers/voice.py | 180 | ⭐⭐⭐ |
| services/llm_brain.py | 150 | ⭐⭐⭐ |
| models/schemas.py | 170 | ⭐⭐ |
| main.py | 80 | ⭐ |
| config.py | 60 | ⭐ |
| dependencies.py | 50 | ⭐⭐ |

### Frontend (Total: ~1500 lines)

| File | Lines | Complexity |
|------|-------|-----------|
| pages/Analysis.jsx | 200 | ⭐⭐⭐ |
| pages/Analytics.jsx | 200 | ⭐⭐⭐ |
| lib/api.js | 200 | ⭐⭐⭐ |
| pages/Dashboard.jsx | 200 | ⭐⭐ |
| store/authStore.js | 100 | ⭐⭐ |
| pages/Upload.jsx | 200 | ⭐⭐ |
| lib/encryption.js | 80 | ⭐⭐ |
| pages/Login.jsx | 130 | ⭐⭐ |
| lib/supabase.js | 50 | ⭐ |
| App.jsx | 60 | ⭐ |

### Database (Total: ~250 lines)

| Component | Complexity |
|-----------|-----------|
| 8 Tables | ⭐⭐⭐ |
| 7 RLS Policies | ⭐⭐⭐ |
| 10+ Indexes | ⭐⭐ |
| Triggers | ⭐ |

---

## 🧪 Testing Your System

### Unit Test Ideas

**Backend:**
```python
def test_encryption():
    encrypted = encrypt_data("test", key)
    assert encrypted != "test"
    decrypted = decrypt_data(encrypted, key)
    assert decrypted == "test"

def test_normalizer():
    assert normalize("HB") == "hemoglobin"
    assert normalize("Glucose") == "glucose"
```

**Frontend:**
```javascript
test('login redirects to dashboard', async () => {
  render(<App />)
  const emailInput = screen.getByLabelText('Email')
  await userEvent.type(emailInput, 'test@example.com')
  // ... etc
})
```

### Integration Test Ideas

1. Sign up → Login → Can see dashboard
2. Upload file → Markers extracted → Trend analysis runs
3. Send chat message → Encrypted → Response returned
4. Delete report → Removed from database

### Deployment Test

Follow [DEPLOYMENT.md](DEPLOYMENT.md) checklist

---

## 📚 Learning Resources

**FastAPI:**
- Docs: https://fastapi.tiangolo.com
- Tutorial: https://fastapi.tiangolo.com/tutorial/
- Advanced: async patterns, dependency injection

**React:**
- Docs: https://react.dev
- Hooks: useState, useEffect, useContext
- Pattern: Compound components, custom hooks

**Supabase:**
- Docs: https://supabase.io/docs
- RLS Guide: Row-level security tutorial
- Examples: Real-time, auth, storage

**OpenAI:**
- API: https://platform.openai.com/docs
- GPT-4o: https://platform.openai.com/docs/guides/vision
- Prompt: Techniques for better outputs

---

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| Project Root | `/healthcare-app/` |
| Backend | `/healthcare-app/blood-report-ai/backend/` |
| Frontend | `/healthcare-app/blood-report-ai/frontend/` |
| Database | `supabase.com` (cloud) |
| Deployment | `railway.app` + `vercel.com` |

---

## ✅ Verification Checklist

After reading this, you should understand:

- [ ] Where each file is and what it does
- [ ] How data flows from frontend to backend to database
- [ ] Where to add new features (routers, services, pages)
- [ ] How to configure the system (.env files)
- [ ] How to deploy (DEPLOYMENT.md)
- [ ] Where to find relevant code for any feature

---

**You now have a complete map of the system!**

Next step: Follow [QUICKSTART.md](QUICKSTART.md) to get it running locally.
