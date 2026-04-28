# ✅ Render Deployment Checklist for ReliefSync-AI

Use this checklist to deploy your backend to Render step-by-step.

---

## 🎯 Target URLs

- **Backend**: `https://reliefsyncai.onrender.com` or `https://reliefsyncai1036.onrender.com`
- **API Docs**: `https://reliefsyncai.onrender.com/docs`
- **Health Check**: `https://reliefsyncai.onrender.com/health`

---

## 📋 Pre-Deployment Checklist

### ☑️ Supabase Setup
- [ ] Created Supabase project
- [ ] Ran `backend/supabase_schema.sql` in SQL Editor
- [ ] Copied Project URL
- [ ] Copied Anon Key
- [ ] Copied Service Role Key

### ☑️ API Keys Ready
- [ ] Gemini API Key from https://aistudio.google.com/app/apikey
- [ ] Google Maps API Key from https://console.cloud.google.com/apis/credentials
- [ ] Generated JWT Secret with `openssl rand -hex 32`

### ☑️ Repository Ready
- [ ] Code pushed to GitHub
- [ ] `.env` file is in `.gitignore` (NOT committed)
- [ ] `render.yaml` exists in root
- [ ] `backend/requirements.txt` updated with Supabase

---

## 🚀 Render Deployment Steps

### Step 1: Create Web Service

1. Go to https://render.com/dashboard
2. Click **"New +"** button (top right)
3. Select **"Web Service"**

### Step 2: Connect Repository

1. Click **"Connect GitHub"** (or use existing connection)
2. Search for: `ReliefSync-AI`
3. Click **"Connect"** on your repository

### Step 3: Configure Service

Fill in these **exact** values:

| Field | Value |
|-------|-------|
| **Name** | `reliefsyncai` (or `reliefsyncai1036` if taken) |
| **Region** | Oregon (US West) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

### Step 4: Add Environment Variables

Click **"Advanced"** → Scroll to **"Environment Variables"**

Add these **one by one**:

```env
APP_NAME=ReliefSync-AI
```
```env
APP_VERSION=1.0.0
```
```env
ENVIRONMENT=production
```
```env
DEBUG=False
```
```env
API_PREFIX=/api/v1
```
```env
SUPABASE_URL=https://xxxxx.supabase.co
```
```env
SUPABASE_ANON_KEY=eyJhbGc...
```
```env
SUPABASE_SERVICE_KEY=eyJhbGc...
```
```env
GEMINI_API_KEY=AIzaSy...
```
```env
GEMINI_MODEL=gemini-2.0-flash
```
```env
GOOGLE_MAPS_API_KEY=AIzaSy...
```
```env
JWT_SECRET_KEY=your-64-character-secret
```
```env
JWT_ALGORITHM=HS256
```
```env
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
```env
RATE_LIMIT_REQUESTS=100
```
```env
RATE_LIMIT_WINDOW_SECONDS=60
```
```env
CORS_ORIGINS=["https://reliefsyncai.vercel.app"]
```

### Step 5: Deploy!

1. Click **"Create Web Service"** (bottom)
2. Wait for build to complete (~5 minutes)
3. Watch the logs for any errors

---

## ✅ Post-Deployment Verification

### Test 1: Health Check

```bash
curl https://reliefsyncai.onrender.com/health
```

**Expected Response:**
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

### Test 2: API Documentation

Visit: `https://reliefsyncai.onrender.com/docs`

You should see interactive Swagger UI with all endpoints.

### Test 3: Root Endpoint

Visit: `https://reliefsyncai.onrender.com/`

**Expected Response:**
```json
{
  "service": "ReliefSync-AI",
  "version": "1.0.0",
  "description": "AI-powered crisis response and volunteer coordination",
  "docs": "/docs",
  "health": "/health"
}
```

---

## 🐛 Troubleshooting

### ❌ Build Failed

**Check:**
- [ ] `backend/requirements.txt` exists
- [ ] Root Directory is set to `backend`
- [ ] Python version is compatible (3.11+)

**Fix:**
- View build logs in Render dashboard
- Check for missing dependencies
- Verify file paths are correct

### ❌ Service Won't Start

**Check:**
- [ ] Start command is correct: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] All environment variables are set
- [ ] No syntax errors in code

**Fix:**
- View runtime logs in Render dashboard
- Test locally first: `cd backend && uvicorn app.main:app --reload`

### ❌ Database Connection Failed

**Check:**
- [ ] Supabase URL is correct
- [ ] Service Role Key is correct (not Anon Key)
- [ ] Schema was run successfully in Supabase

**Fix:**
- Test connection in Supabase SQL Editor
- Verify keys are copied correctly (no extra spaces)

### ❌ CORS Errors

**Check:**
- [ ] `CORS_ORIGINS` includes your frontend URL
- [ ] URL format is correct: `["https://domain.com"]`
- [ ] No trailing slashes in URLs

**Fix:**
- Update `CORS_ORIGINS` environment variable
- Redeploy service (automatic on env change)

### ❌ 500 Internal Server Error

**Check:**
- [ ] Gemini API key is valid
- [ ] Google Maps API key is valid
- [ ] All required APIs are enabled

**Fix:**
- Check Render logs for specific error
- Test API keys separately
- Verify all environment variables

---

## 🔄 Updating Your Deployment

### Code Changes

1. Push changes to GitHub
2. Render auto-deploys from `main` branch
3. Watch logs for successful deployment

### Environment Variable Changes

1. Go to Render dashboard → Your service
2. Click **"Environment"** tab
3. Edit/Add variables
4. Click **"Save Changes"**
5. Service auto-redeploys

### Manual Redeploy

1. Go to Render dashboard → Your service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## 📊 Monitoring

### View Logs

1. Go to Render dashboard → Your service
2. Click **"Logs"** tab
3. View real-time logs

### Check Metrics

1. Go to Render dashboard → Your service
2. Click **"Metrics"** tab
3. View CPU, Memory, Response times

### Set Up Alerts

1. Go to **"Settings"** → **"Notifications"**
2. Add email for deployment notifications
3. Get notified on failures

---

## 🎉 Success Criteria

- [ ] Health endpoint returns `"status": "healthy"`
- [ ] API docs are accessible at `/docs`
- [ ] No errors in Render logs
- [ ] Database queries work (test in `/docs`)
- [ ] CORS allows frontend requests
- [ ] All AI features are configured

---

## 📞 Support Resources

- **Render Status**: https://status.render.com
- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Supabase Status**: https://status.supabase.com
- **Project Issues**: https://github.com/Vk2245/ReliefSync-AI/issues

---

## 🚀 Next Steps

After successful deployment:

1. [ ] Deploy frontend to Vercel
2. [ ] Update CORS with frontend URL
3. [ ] Test end-to-end flow
4. [ ] Set up custom domain (optional)
5. [ ] Configure monitoring/alerts
6. [ ] Share with team! 🎉

---

**Your backend is now live at: `https://reliefsyncai.onrender.com` 🚀**
