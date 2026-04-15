# ⚡ Quick Start - 5 Minutes to Running

Just want to get it running? Start here.

## 1️⃣ Clone & Install (2 minutes)

```bash
# Clone repo
git clone <your-repo>
cd healthcare-app

# Backend setup
cd blood-report-ai/backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

# Frontend setup (new terminal)
cd blood-report-ai/frontend
npm install
```

## 2️⃣ Get the Keys (2 minutes)

**From Supabase (https://supabase.com):**
1. Create account
2. New project
3. Wait 2-3 min for DB
4. Settings → API → Copy:
   - Project URL → `SUPABASE_URL`
   - Anon key → `SUPABASE_ANON_KEY`
   - Service role key → `SUPABASE_SERVICE_KEY`
   - JWT Secret → `SUPABASE_JWT_SECRET`

**From OpenAI (https://platform.openai.com/api-keys):**
1. Create API key
2. Copy → `OPENAI_API_KEY`

## 3️⃣ Create .env Files (1 minute)

**Backend:**
```bash
cd blood-report-ai/backend
cp .env.example .env
```

Edit `.env`:
```
SUPABASE_URL=paste_here
SUPABASE_SERVICE_KEY=paste_here
SUPABASE_ANON_KEY=paste_here
SUPABASE_JWT_SECRET=paste_here
OPENAI_API_KEY=paste_here
ENCRYPTION_SECRET=generate_with: python -c "import os; import binascii; print(binascii.hexlify(os.urandom(32)).decode())"
JWT_SECRET=generate_with: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Frontend:**
```bash
cd blood-report-ai/frontend
cp .env.example .env.local
```

Edit `.env.local`:
```
VITE_SUPABASE_URL=paste_URL
VITE_SUPABASE_ANON_KEY=paste_key
VITE_API_URL=http://localhost:8000/api
```

## 4️⃣ Setup Database (1 minute)

1. Go to Supabase → SQL Editor
2. Copy entire file: `supabase/migrations/001_init.sql`
3. Paste into SQL Editor
4. Click "Run"
5. Wait for completion ✓

## 5️⃣ Run It!

**Terminal 1 - Backend:**
```bash
cd blood-report-ai/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd blood-report-ai/frontend
npm run dev
```

Open browser: http://localhost:5173

## ✅ You're Done!

Sign up, upload a blood report PDF, and see the AI magic happen.

---

## Stuck?

1. **"ModuleNotFoundError"** → Run `pip install -r requirements.txt`
2. **"Cannot find module"** → Run `npm install` in frontend folder
3. **"Supabase connection refused"** → Check SUPABASE_URL is correct
4. **"CORS error"** → Backend might not be running, check Terminal 1

Full guide: See `SETUP_GUIDE.md`
