# Quick Start Guide - Frontend Setup

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd blood-report-ai/frontend
npm install
```

### Step 2: Configure Environment
```bash
# Copy example environment file
cp .env.example .env.local

# Edit .env.local and add your Supabase credentials
# VITE_SUPABASE_URL=https://your-project.supabase.co
# VITE_SUPABASE_ANON_KEY=your_key_here
```

### Step 3: Get Supabase Credentials
1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Create or select a project
3. Go to **Settings → API**
4. Copy:
   - **Project URL** → `VITE_SUPABASE_URL`
   - **Anon Key** → `VITE_SUPABASE_ANON_KEY`

### Step 4: Start Development Server
```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## ✅ Test the Authentication

1. **Create Account**
   - Click "Sign Up"
   - Enter email, password (8+ chars), full name
   - Click "Create Account"
   - Should see Dashboard

2. **Try Login**
   - Logout
   - Click "Sign In"
   - Enter credentials
   - Should see Dashboard again

3. **Protected Routes**
   - Try accessing `/upload` while logged out
   - Should redirect to SignIn

## 📁 Project Structure

```
frontend/
├── src/
│   ├── pages/              # All page components
│   │   ├── Home.jsx       # Landing page (public)
│   │   ├── SignUp.jsx     # Registration (public)
│   │   ├── SignIn.jsx     # Login (public)
│   │   ├── Dashboard.jsx  # Home (protected)
│   │   ├── Upload.jsx     # Report upload (protected)
│   │   ├── Analysis.jsx   # Report analysis (protected)
│   │   └── ...
│   ├── store/
│   │   └── authStore.js   # Auth state management (Zustand)
│   ├── lib/
│   │   ├── supabase.js   # Supabase client
│   │   ├── api.js        # Backend API client
│   │   └── encryption.js
│   ├── App.jsx           # Main router
│   └── main.jsx          # Entry point
├── .env.local            # Your secrets (create from .env.example)
├── package.json
└── vite.config.js
```

## 🔑 Key Features

### Public Pages (No Login Required)
- `/` - Home/Landing page
- `/signin` - Login page
- `/signup` - Registration page

### Protected Pages (Login Required)
- `/dashboard` - User home
- `/upload` - Upload blood reports
- `/analysis/:id` - View report analysis
- `/analytics` - View health trends
- `/chat` - Chat with AI
- `/settings` - User settings

## 🛠️ Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📚 Detailed Documentation

See [AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md) for:
- Complete architecture overview
- Auth flow diagrams
- API integration details
- Troubleshooting guide
- Production deployment

## Common Issues

### "Supabase URL not configured"
→ Check `.env.local` has `VITE_SUPABASE_URL`

### "Signup failed"
→ Use strong password (8+ chars) and valid email

### "Stuck on loading screen"
→ Check browser console (F12) for errors

### "Can't access protected routes"
→ Make sure you're logged in

## Next Steps

1. ✅ Frontend setup complete
2. Ensure backend is running on `http://localhost:8000`
3. Test report upload flow
4. Customize styling with Tailwind
5. Deploy to production (Vercel/Netlify)

## Need Help?

- Check browser console (F12) for error messages
- Verify Supabase credentials
- Ensure backend API is running
- See AUTHENTICATION_GUIDE.md for detailed docs

---

**You're all set! 🎉** The frontend is now ready for development and testing.
