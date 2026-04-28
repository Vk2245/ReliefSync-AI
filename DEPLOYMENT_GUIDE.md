# 🚀 ReliefSync-AI Deployment Guide

Complete guide to deploy ReliefSync-AI on **Render** (backend) + **Supabase** (database) + **Vercel** (frontend)

---

## 📋 Prerequisites

- GitHub account
- Render account (https://render.com)
- Supabase account (https://supabase.com)
- Vercel account (https://vercel.com) - optional for frontend
- Google Cloud account for API keys

---

## 🗄️ Step 1: Supabase Database Setup

### 1.1 Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click **"New Project"**
3. Fill in:
   - **Name**: `reliefsyncai`
   - **Database Password**: (save this securely)
   - **Region**: Choose closest to your users
4. Wait for project to initialize (~2 minutes)

### 1.2 Run Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Click **"New Query"**
3. Copy entire content from `backend/supabase_schema.sql`
4. Paste and click **"Run"**
5. You should see: ✅ Success message

### 1.3 Get API Credentials

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: `eyJhbGc...` (long string)
   - **service_role key**: `eyJhbGc...` (keep secret!)

---

## 🔑 Step 2: Get Google API Keys

### 2.1 Gemini AI API Key

1. Go to https://aistudio.google.com/app/apikey
2. Click **"Create API Key"**
3. Copy the key (starts with `AIza...`)

### 2.2 Google Maps API Key

1. Go to https://console.cloud.google.com/apis/credentials
2. Click **"Create Credentials"** → **"API Key"**
3. Enable these APIs:
   - Maps JavaScript API
   - Geocoding API
   - Directions API
4. Copy the API key

### 2.3 Generate JWT Secret

Run this command in terminal:
```bash
openssl rand -hex 32
```
Copy the output (64 character string)

---

## 🌐 Step 3: Deploy Backend to Render

### 3.1 Connect GitHub Repository

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect GitHub"** and authorize
4. Select your repository: `ReliefSync-AI`

### 3.2 Configure Service

Fill in these settings:

- **Name**: `reliefsyncai` (or `reliefsyncai1036` if taken)
- **Region**: Oregon (US West)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Plan**: Free

### 3.3 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

```
APP_NAME=ReliefSync-AI
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
API_PREFIX=/api/v1

SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-2.0-flash

GOOGLE_MAPS_API_KEY=your-maps-key

JWT_SECRET_KEY=your-64-char-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

CORS_ORIGINS=["https://reliefsyncai.vercel.app"]
```

### 3.4 Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (~5 minutes)
3. Your API will be live at: `https://reliefsyncai.onrender.com`

### 3.5 Test API

Visit: `https://reliefsyncai.onrender.com/health`

You should see:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "services": {
    "supabase": "connected",
    "gemini_ai": "configured",
    "google_maps": "configured"
  }
}
```

---

## 🎨 Step 4: Deploy Frontend (Optional)

### Option A: Vercel (Recommended)

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add environment variable:
   ```
   VITE_API_URL=https://reliefsyncai.onrender.com/api/v1
   ```
5. Click **"Deploy"**
6. Your site will be live at: `https://reliefsyncai.vercel.app`

### Option B: Netlify

1. Go to https://app.netlify.com/start
2. Connect GitHub repository
3. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
4. Add environment variable:
   ```
   VITE_API_URL=https://reliefsyncai.onrender.com/api/v1
   ```
5. Deploy

---

## 🔄 Step 5: Update CORS

After frontend is deployed, update backend CORS:

1. Go to Render dashboard → Your service
2. Go to **Environment** tab
3. Update `CORS_ORIGINS`:
   ```
   ["https://reliefsyncai.vercel.app","https://your-custom-domain.com"]
   ```
4. Save changes (auto-redeploys)

---

## ✅ Step 6: Verify Everything Works

### Backend Health Check
```bash
curl https://reliefsyncai.onrender.com/health
```

### API Documentation
Visit: `https://reliefsyncai.onrender.com/docs`

### Frontend
Visit: `https://reliefsyncai.vercel.app`

---

## 🔒 Security Checklist

- [ ] All API keys are set as environment variables (not in code)
- [ ] `.env` file is in `.gitignore`
- [ ] JWT secret is strong (64+ characters)
- [ ] Supabase RLS policies are enabled
- [ ] CORS is configured with specific domains (not `*`)
- [ ] Rate limiting is enabled
- [ ] HTTPS is enforced (automatic on Render/Vercel)

---

## 📊 Monitoring & Logs

### Render Logs
1. Go to your service dashboard
2. Click **"Logs"** tab
3. View real-time logs

### Supabase Logs
1. Go to Supabase dashboard
2. Click **"Logs"** → **"Postgres Logs"**

---

## 🐛 Troubleshooting

### Backend won't start
- Check Render logs for errors
- Verify all environment variables are set
- Test locally first: `cd backend && uvicorn app.main:app --reload`

### Database connection fails
- Verify Supabase URL and keys
- Check if schema was run successfully
- Test connection in Supabase SQL Editor

### CORS errors
- Update `CORS_ORIGINS` with your frontend URL
- Make sure URL has no trailing slash
- Redeploy backend after changes

### API returns 500 errors
- Check Render logs
- Verify Gemini API key is valid
- Test endpoints in `/docs` page

---

## 🚀 Custom Domain (Optional)

### Backend (Render)
1. Go to service **Settings**
2. Click **"Custom Domain"**
3. Add your domain: `api.reliefsyncai.com`
4. Update DNS records as shown

### Frontend (Vercel)
1. Go to project **Settings** → **Domains**
2. Add your domain: `reliefsyncai.com`
3. Update DNS records as shown

---

## 📈 Scaling

### Free Tier Limits
- **Render**: Spins down after 15 min inactivity
- **Supabase**: 500MB database, 2GB bandwidth
- **Vercel**: 100GB bandwidth

### Upgrade Options
- **Render**: $7/month for always-on
- **Supabase**: $25/month for Pro
- **Vercel**: $20/month for Pro

---

## 🎉 You're Live!

Your ReliefSync-AI platform is now deployed:

- **Backend API**: `https://reliefsyncai.onrender.com`
- **API Docs**: `https://reliefsyncai.onrender.com/docs`
- **Frontend**: `https://reliefsyncai.vercel.app`
- **Database**: Supabase dashboard

---

## 📞 Support

- **Issues**: https://github.com/Vk2245/ReliefSync-AI/issues
- **Render Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Vercel Docs**: https://vercel.com/docs

---

**Made with ❤️ for crisis response and disaster relief**
