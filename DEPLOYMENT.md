# 🚀 Deployment Checklist - From Local to Production (30 Min)

## Phase 1: Pre-Deployment (5 min)

### Local Testing Complete?
- [ ] Backend runs without errors: `python -m uvicorn main:app --reload`
- [ ] Frontend runs without errors: `npm run dev`
- [ ] Can sign up on login page
- [ ] Can upload a test PDF/image
- [ ] Can see extracted markers
- [ ] Can chat with AI
- [ ] No console errors in browser dev tools

**If any fail:** Follow [TROUBLESHOOTING](#troubleshooting) section

---

## Phase 2: Create Cloud Accounts (5 min)

### 1. Supabase (Database + Auth)
- [ ] Sign up at https://supabase.com
- [ ] Create new project (name: `blood-report-ai`)
- [ ] Wait 2-3 minutes for database initialization
- [ ] Go to **Settings > API**
- [ ] **Copy and save these:**
  - `Project URL` → Looks like: `https://xxxxxxxxxxxx.supabase.co`
  - `anon key` → Looks like: `eyJhbG...`
  - `service_role key` → Save securely in password manager
  - Go to **Database Settings** and find `JWT Secret`

### 2. OpenAI (AI APIs)
- [ ] Sign up at https://platform.openai.com
- [ ] Go to **API keys**
- [ ] Create new secret key
- [ ] **Copy and save:** `sk-proj-...` (keep safe, don't commit)

### 3. Railway Account (Backend Hosting)
- [ ] Sign up at https://railway.app
- [ ] Connect your GitHub account
- [ ] Authorize access to your repo

### 4. Vercel Account (Frontend Hosting)
- [ ] Sign up at https://vercel.com
- [ ] Connect your GitHub account
- [ ] Authorize access to your repo

### 5. ElevenLabs (Voice - Optional)
- [ ] Sign up at https://elevenlabs.io
- [ ] Copy API key from **Settings**
- [ ] Optional: If budget is tight, voice will fallback to OpenAI TTS

---

## Phase 3: Run SQL Migration (3 min)

### Create Database Tables

1. Go to Supabase dashboard
2. Click **SQL Editor** (in sidebar)
3. Click **New query**
4. **Copy entire contents** of: `supabase/migrations/001_init.sql`
5. **Paste into SQL editor**
6. Click **Run** button

You should see:
```
Success - 8 queries executed
```

### Verify Tables Exist
1. Go to **Table Editor** (in sidebar)
2. You should see 7 tables:
   - [ ] users
   - [ ] blood_reports
   - [ ] blood_markers
   - [ ] trend_analysis
   - [ ] ai_conversations
   - [ ] knowledge_base
   - [ ] audit_log

---

## Phase 4: Configure Environment Variables (8 min)

### Backend Configuration

**1. Create `.env` file:**
```bash
cd blood-report-ai/backend
cp .env.example .env
```

**2. Edit `.env` and fill in all values:**

```env
# ====== SUPABASE ======
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_JWT_SECRET=super-secret-key-from-settings

# ====== OPENAI ======
OPENAI_API_KEY=sk-proj-...

# ====== ELEVENLABS (Optional) ======
ELEVENLABS_API_KEY=your_key_here

# ====== ENCRYPTION & SECURITY ======
# Generate using: python -c "import os; import binascii; print(binascii.hexlify(os.urandom(32)).decode())"
ENCRYPTION_SECRET=generate_this

# Generate using: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET=generate_this

# ====== CORS (for production) ======
# Update later with your Vercel URL
ALLOWED_ORIGINS=http://localhost:5173,https://yourdomain.vercel.app
```

**How to generate secrets:**
```bash
# In terminal:
python -c "import os; import binascii; print(binascii.hexlify(os.urandom(32)).decode())"
# Copy result to ENCRYPTION_SECRET

python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy result to JWT_SECRET
```

### Frontend Configuration

**1. Create `.env.local` file:**
```bash
cd blood-report-ai/frontend
cp .env.example .env.local
```

**2. Edit `.env.local`:**
```env
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
VITE_API_URL=http://localhost:8000/api
```

---

## Phase 5: Deploy Backend to Railway (8 min)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Complete Blood Report AI system"
git push origin main
```

### Step 2: Railway Deployment
1. Go to https://railway.app
2. Click **New Project**
3. Click **Deploy from GitHub**
4. Authorize GitHub access
5. Select your repo
6. Select `blood-report-ai/backend` folder
7. Railway auto-detects Python + FastAPI
8. Click **Deploy**

**Wait ~3-5 minutes for deployment**

### Step 3: Set Environment Variables
1. Go to your Railway project dashboard
2. Click **Variables** tab
3. Click **Add Variable** for each:

```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_JWT_SECRET=super-secret-key
OPENAI_API_KEY=sk-proj-...
ELEVENLABS_API_KEY=your_key (skip if using OpenAI fallback)
ENCRYPTION_SECRET=generated_secret
JWT_SECRET=generated_secret
ALLOWED_ORIGINS=https://yourdomain.vercel.app
```

4. Click **Deploy**

### Step 4: Get Your Backend URL
1. Go to **Settings** tab
2. Look for **Generate Domain**
3. Click to generate public URL
4. **Copy this** (looks like: `https://healthcare-prod.up.railway.app`)
5. **Keep this URL safe**, you'll need it for frontend

---

## Phase 6: Deploy Frontend to Vercel (8 min)

### Step 1: Update Backend URL

Before deploying frontend, update it to point to your Railway backend:

```bash
cd blood-report-ai/frontend
# Edit .env.local:
VITE_API_URL=https://healthcare-prod.up.railway.app/api
```

Push this change:
```bash
git add .env.local
git commit -m "Update API URL to production"
git push origin main
```

### Step 2: Vercel Deployment
1. Go to https://vercel.com
2. Click **Add New → Project**
3. Click **Import Git Repository**
4. Select your repo
5. Under **Root Directory**, select: `blood-report-ai/frontend`
6. Click **Deploy**

**Wait ~2-3 minutes for deployment**

### Step 3: Set Environment Variables
1. After deployment, go to **Settings**
2. Click **Environment Variables**
3. Add 3 variables:

```
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
VITE_API_URL=https://healthcare-prod.up.railway.app/api
```

4. Redeploy: Click **Deployments** tab → Click **Redeploy** on latest

### Step 4: Get Your Frontend URL
1. Deployment completes
2. You'll see a URL like: `https://healthcare-prod.vercel.app`
3. **Copy this**

---

## Phase 7: Final Production Setup (3 min)

### Update Backend CORS

Now that frontend is deployed:

1. Go back to Railway
2. Go to **Variables** tab
3. Find `ALLOWED_ORIGINS`
4. Update to:
```
https://your-vercel-app.vercel.app
```
5. Click **Deploy**

### Verify Everything Works

1. Go to your Vercel frontend URL
2. Refresh page
3. Try to sign up with test account
4. Try to upload a blood report
5. Check if trends load
6. Check if chat works

---

## Phase 8: Enable HTTPS (Already Done)

✅ Railways: Auto HTTPS
✅ Vercel: Auto HTTPS  
✅ Supabase: Auto HTTPS

All connections are encrypted by default.

---

## 🎉 Success Checklist

You've successfully deployed when:

- [ ] Frontend URL works in browser
- [ ] Can login with your test account
- [ ] API calls show in browser Network tab (no CORS errors)
- [ ] Can upload a blood report
- [ ] Markers are extracted
- [ ] Chat works
- [ ] Navigation between pages works
- [ ] No 401/403 errors

---

## 📊 Production Monitoring

### Check Backend Status
```bash
Visit: https://yourbackend.railway.app/api/health
```

You should see:
```json
{"status": "ok", "timestamp": "2024-01-10T12:34:56"}
```

### Check Logs
- **Railway:** Dashboard → Logs tab
- **Vercel:** Dashboard → Deployments → View Logs
- **Supabase:** Dashboard → Logs

---

## 💰 Cost Estimate

| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| Supabase | 500MB DB | ~$25/month |
| Railway | $5 credit | ~$10-20/month |
| Vercel | Unlimited | Free (hobby) |
| OpenAI | No free tier | ~$10-50/month |
| ElevenLabs | 10k chars free | ~$5-20/month |

**Total:** ~$35-95/month for small users

**Cost Optimization:**
- Use OpenAI TTS instead of ElevenLabs (save ~$10)
- Use Supabase free tier while <500MB
- Vercel is free for static builds

---

## 🔧 Troubleshooting Deployment

### "502 Bad Gateway" from Railway
**Cause:** Backend crashed or variables missing
**Fix:** 
1. Check Railway Logs
2. Verify all env vars are set
3. Restart deployment

### "CORS Error" in browser
**Cause:** Frontend URL not in ALLOWED_ORIGINS
**Fix:**
1. Get your Vercel URL
2. Go to Railway Variables
3. Update ALLOWED_ORIGINS
4. Redeploy

### "Cannot connect to API" from frontend
**Cause:** VITE_API_URL points to wrong backend
**Fix:**
1. Check Vercel env vars
2. Verify VITE_API_URL is your Railway URL
3. Redeploy

### "Database connection refused"
**Cause:** SUPABASE_URL or key is wrong
**Fix:**
1. Go to Supabase Settings → API
2. Copy correct values
3. Update Railway env vars
4. Redeploy

### "404 Not Found" for API routes
**Cause:** Backend not running or wrong URL
**Fix:**
1. Visit `VITE_API_URL/health`
2. Should return JSON (not 404)
3. If 404, backend likely crashed

---

## 📝 Post-Deployment Tasks

### Daily
- [ ] Monitor Supabase database usage
- [ ] Check error logs in Railway/Vercel

### Weekly
- [ ] Backup important user data
- [ ] Monitor API costs
- [ ] Check for security updates

### Monthly
- [ ] Update dependencies
- [ ] Review database size
- [ ] Optimize slow queries

---

## 🔐 Production Security Checklist

- [ ] All env vars set (never commit .env)
- [ ] ENCRYPTION_SECRET is unique (not shared)
- [ ] JWT_SECRET is secure (generated with secrets module)
- [ ] Database RLS policies enabled (verify in Supabase)
- [ ] Only HTTPS connections allowed
- [ ] CORS restricted to your domain only
- [ ] API keys not exposed in frontend code
- [ ] Audit logs enabled (verify in Supabase)

---

## 📱 What's Next?

After deployment works:

1. **Test More:** Upload real blood reports
2. **Add Features:** 
   - PDF export
   - Email notifications
   - More visualizations
3. **Scale Up:**
   - Add caching
   - Optimize database queries
   - Add background jobs (Celery)
4. **Marketing:**
   - Share with friends
   - Collect feedback
   - Iterate based on usage

---

## ⏱️ Timeline Summary

- Phase 1 (Testing): 5 min
- Phase 2 (Accounts): 5 min
- Phase 3 (Database): 3 min
- Phase 4 (Config): 8 min
- Phase 5 (Deploy Backend): 8 min
- Phase 6 (Deploy Frontend): 8 min
- Phase 7 (Final Setup): 3 min
- Phase 8 (Verification): 5 min

**Total: ~45 minutes from start to live system**

---

**You did it! Your AI health platform is now live! 🎉**

Share it with the world. Make health personal.
