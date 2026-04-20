# Streamlit Cloud Deployment Guide

## 🚀 Quick Deploy to Streamlit Cloud

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at https://streamlit.io/cloud)

### Step 1: Push to GitHub ✅
Already done! Repository: https://github.com/Navaprabhas/rag-system

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with GitHub

2. **Create New App**
   - Click "New app"
   - Select repository: `Navaprabhas/rag-system`
   - Branch: `main`
   - Main file path: `frontend/app.py`

3. **Configure Environment Variables**
   
   Click "Advanced settings" and add these secrets:
   
   ```toml
   # Required for Streamlit Cloud
   FASTAPI_URL = "https://your-backend-url.com"
   
   # Optional: If using external LLM providers
   OPENAI_API_KEY = "sk-..."
   ANTHROPIC_API_KEY = "sk-ant-..."
   COHERE_API_KEY = "..."
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait 2-3 minutes for deployment

### Step 3: Backend Deployment

⚠️ **Important:** Streamlit Cloud only hosts the frontend. You need to deploy the backend separately.

#### Option A: Deploy Backend on Render.com (Recommended)

1. Go to https://render.com
2. Create new "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Add all variables from `.env.example`

#### Option B: Deploy Backend on Railway.app

1. Go to https://railway.app
2. Create new project from GitHub
3. Add environment variables
4. Deploy automatically

#### Option C: Deploy Backend on Fly.io

1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Run: `fly launch`
3. Configure and deploy

### Step 4: Update Frontend Configuration

Once backend is deployed, update Streamlit secrets:

```toml
FASTAPI_URL = "https://your-backend-url.com"
```

### Architecture for Streamlit Cloud

```
┌─────────────────────────────────────┐
│   Streamlit Cloud (Frontend)        │
│   https://your-app.streamlit.app    │
└──────────────┬──────────────────────┘
               │ HTTP/REST
               ▼
┌─────────────────────────────────────┐
│   Backend (Render/Railway/Fly.io)   │
│   FastAPI + Qdrant + Ollama         │
└─────────────────────────────────────┘
```

## 🔧 Configuration Files for Streamlit Cloud

### Required Files (Already Created)
- ✅ `packages.txt` - System dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `frontend/app.py` - Main application

### Environment Variables

Add to Streamlit Cloud secrets (Settings → Secrets):

```toml
# Backend URL (required)
FASTAPI_URL = "https://your-backend.onrender.com"

# LLM Provider (optional, defaults to ollama)
LLM_PROVIDER = "openai"

# API Keys (optional, only if using external providers)
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
```

## 🎯 Simplified Deployment (Frontend Only)

If you want to deploy just the frontend for demo purposes:

1. **Modify `frontend/app.py`** to use mock data
2. **Deploy to Streamlit Cloud** as described above
3. **No backend needed** for static demo

## 📝 Post-Deployment Checklist

- [ ] Frontend deployed on Streamlit Cloud
- [ ] Backend deployed on Render/Railway/Fly.io
- [ ] Environment variables configured
- [ ] FASTAPI_URL updated in Streamlit secrets
- [ ] Test document upload
- [ ] Test query functionality
- [ ] Verify citations display
- [ ] Check streaming responses

## 🐛 Troubleshooting

### Frontend can't connect to backend
- Check FASTAPI_URL in Streamlit secrets
- Verify backend is running
- Check CORS settings in backend

### "Module not found" errors
- Verify all dependencies in `requirements.txt`
- Check `packages.txt` for system dependencies

### Slow performance
- Backend cold starts (normal for free tiers)
- Consider upgrading to paid plans
- Use caching in Streamlit

## 💰 Cost Estimates

### Free Tier (Suitable for MVP)
- **Streamlit Cloud:** Free (public apps)
- **Render.com:** Free tier available
- **Railway.app:** $5 credit/month free
- **Total:** $0-5/month

### Production Tier
- **Streamlit Cloud:** $20/month (private apps)
- **Render.com:** $7-25/month
- **Total:** $27-45/month

## 🔗 Useful Links

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Render Deployment](https://render.com/docs)
- [Railway Deployment](https://docs.railway.app/)
- [Fly.io Deployment](https://fly.io/docs/)

## 🆘 Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Check backend logs
3. Verify environment variables
4. Test backend API directly

---

**Your app will be live at:** `https://your-app-name.streamlit.app`

**Deployment time:** 5-10 minutes

**Status:** Ready to deploy! 🚀
