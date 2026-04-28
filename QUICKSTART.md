# ⚡ ReliefSync-AI Quick Start

Get your ReliefSync-AI platform running in **15 minutes**!

---

## 🎯 What You'll Deploy

- **Backend API**: FastAPI + Supabase (PostgreSQL)
- **AI Services**: Google Gemini 2.0 Flash
- **Hosting**: Render (backend) + Vercel (frontend)
- **Database**: Supabase (free tier)

---

## 📝 Step-by-Step (15 mins)

### 1️⃣ Supabase Setup (3 mins)

```bash
# 1. Go to: https://supabase.com/dashboard
# 2. Create new project: "reliefsyncai"
# 3. Copy Project URL and API keys
# 4. Go to SQL Editor → New Query
# 5. Paste content from: backend/supabase_schema.sql
# 6. Click "Run"
```

**Save these:**
- Project URL: `https://xxxxx.supabase.co`
- Anon key: `eyJhbGc...`
- Service key: `eyJhbGc...`

---

### 2️⃣ Get API Keys (5 mins)

**Gemini AI:**
```bash
# Go to: https://aistudio.google.com/app/apikey
# Click "Create API Key"
# Copy key (starts with AIza...)
```

**Google Maps:**
```bash
# Go to: https://console.cloud.google.com/apis/credentials
# Create API Key
# Enable: Maps JavaScript API, Geocoding API, Directions API
```

**JWT Secret:**
```bash
# Run in terminal:
openssl rand -hex 32
# Copy the output
```

---

### 3️⃣ Deploy to Render (5 mins)

```bash
# 1. Go to: https://render.com/dashboard
# 2. New + → Web Service
# 3. Connect GitHub: Vk2245/ReliefSync-AI
# 4. Configure:
```

**Settings:**
- Name: `reliefsyncai` (or `reliefsyncai1036`)
- Region: Oregon
- Root Directory: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Plan: Free

**Environment Variables:**
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
GEMINI_API_KEY=your-gemini-key
GOOGLE_MAPS_API_KEY=your-maps-key
JWT_SECRET_KEY=your-64-char-secret
CORS_ORIGINS=["https://reliefsyncai.vercel.app"]
```

Click **"Create Web Service"** → Wait 5 mins

---

### 4️⃣ Test Backend (1 min)

```bash
# Visit: https://reliefsyncai.onrender.com/health

# Should see:
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "supabase": "connected",
    "gemini_ai": "configured"
  }
}
```

**API Docs:** `https://reliefsyncai.onrender.com/docs`

---

### 5️⃣ Deploy Frontend (1 min)

```bash
# 1. Go to: https://vercel.com/new
# 2. Import: Vk2245/ReliefSync-AI
# 3. Configure:
```

- Framework: Vite
- Root: `frontend`
- Build: `npm run build`
- Output: `dist`

**Environment Variable:**
```env
VITE_API_URL=https://reliefsyncai.onrender.com/api/v1
```

Click **"Deploy"** → Done!

---

## ✅ You're Live!

- **Backend**: `https://reliefsyncai.onrender.com`
- **Frontend**: `https://reliefsyncai.vercel.app`
- **Docs**: `https://reliefsyncai.onrender.com/docs`

---

## 🧪 Test the API

```bash
# Health check
curl https://reliefsyncai.onrender.com/health

# Create emergency (requires auth)
curl -X POST https://reliefsyncai.onrender.com/api/v1/emergencies \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Flood in Mumbai",
    "description": "Heavy rainfall causing flooding",
    "severity": "high",
    "location": {"lat": 19.0760, "lng": 72.8777}
  }'
```

---

## 🔧 Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your keys
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## 📚 Full Documentation

See **DEPLOYMENT_GUIDE.md** for:
- Detailed setup instructions
- Troubleshooting
- Custom domains
- Scaling options
- Security best practices

---

## 🆘 Need Help?

- **Issues**: https://github.com/Vk2245/ReliefSync-AI/issues
- **Render Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs

---

## 🎉 What's Next?

1. ✅ Test all API endpoints in `/docs`
2. ✅ Create your first emergency report
3. ✅ Register volunteers
4. ✅ Test AI severity prediction
5. ✅ Configure custom domain (optional)

---

**Built for crisis response. Powered by AI. 🚀**
