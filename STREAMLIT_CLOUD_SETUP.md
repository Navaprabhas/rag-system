# 🚀 Streamlit Cloud Deployment - Step by Step

## ✅ Step 1: GitHub Repository (COMPLETED)

Your code is now live on GitHub:
**https://github.com/Navaprabhas/rag-system**

## 🎯 Step 2: Deploy to Streamlit Cloud

### Option A: Demo Version (Quick - 2 minutes)

This deploys a demo/documentation page:

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Click "Sign in" → Sign in with GitHub

2. **Create New App**
   - Click "New app" button
   - Repository: `Navaprabhas/rag-system`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - Click "Deploy!"

3. **Wait 2-3 minutes**
   - Streamlit will install dependencies
   - Your app will be live at: `https://[your-app-name].streamlit.app`

**Result:** A demo page showing project documentation and features.

---

### Option B: Full Interactive System (Advanced - 30 minutes)

This deploys the complete RAG system with backend:

#### Part 1: Deploy Backend (Choose One Platform)

##### Option B1: Deploy on Render.com (Recommended)

1. **Go to Render.com**
   - Visit: https://render.com
   - Sign up/Sign in with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select repository: `Navaprabhas/rag-system`

3. **Configure Service**
   ```
   Name: rag-backend
   Region: Choose closest to you
   Branch: main
   Root Directory: (leave empty)
   Runtime: Docker
   
   OR if using Python:
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables**
   Click "Environment" and add:
   ```
   LLM_PROVIDER=ollama
   EMBEDDING_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   LOG_LEVEL=INFO
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Copy your backend URL: `https://rag-backend.onrender.com`

##### Option B2: Deploy on Railway.app

1. **Go to Railway.app**
   - Visit: https://railway.app
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `Navaprabhas/rag-system`

3. **Add Services**
   - Add "Qdrant" from templates
   - Add "Ollama" (custom Docker image)
   - Add your FastAPI app

4. **Configure Environment**
   - Add all variables from `.env.example`
   - Update QDRANT_HOST and OLLAMA_BASE_URL to Railway internal URLs

5. **Deploy**
   - Railway deploys automatically
   - Copy your backend URL

##### Option B3: Deploy on Fly.io

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Login and Deploy**
   ```bash
   fly auth login
   fly launch
   # Follow prompts
   fly deploy
   ```

3. **Copy your backend URL**

#### Part 2: Deploy Frontend on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with GitHub

2. **Create New App**
   - Click "New app"
   - Repository: `Navaprabhas/rag-system`
   - Branch: `main`
   - Main file path: `frontend/app.py`

3. **Configure Secrets**
   - Click "Advanced settings"
   - Add to secrets:
   ```toml
   FASTAPI_URL = "https://your-backend-url.onrender.com"
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait 2-3 minutes

**Result:** Full interactive RAG system with document upload and querying!

---

## 🎯 Recommended Approach

### For Demo/Portfolio:
✅ **Use Option A** (Demo Version)
- Deploys in 2 minutes
- No backend needed
- Shows project capabilities
- Perfect for showcasing

### For Production Use:
✅ **Use Docker Locally or Cloud VM**
- Full control
- All features work
- Better performance
- See DEPLOYMENT.md

---

## 📊 Deployment Comparison

| Feature | Demo (Option A) | Full (Option B) | Docker Local |
|---------|----------------|-----------------|--------------|
| Setup Time | 2 min | 30 min | 10 min |
| Cost | Free | $0-15/mo | Free |
| Features | Docs only | Full system | Full system |
| Performance | N/A | Limited | Best |
| Recommended For | Portfolio | Testing | Production |

---

## 🔗 Your Links

After deployment, you'll have:

1. **GitHub Repository**
   - https://github.com/Navaprabhas/rag-system

2. **Streamlit App** (after deploying)
   - https://[your-app-name].streamlit.app

3. **Backend API** (if Option B)
   - https://[your-backend].onrender.com/docs

---

## 🐛 Troubleshooting

### Streamlit Cloud Issues

**"Module not found" error:**
- Check `requirements.txt` includes all dependencies
- Check `packages.txt` for system dependencies

**"Can't connect to backend":**
- Verify FASTAPI_URL in Streamlit secrets
- Check backend is running
- Test backend URL directly

**Slow loading:**
- Normal for free tier (cold starts)
- Consider paid tier for better performance

### Backend Issues

**Render.com free tier sleeps:**
- Free tier sleeps after 15 min inactivity
- First request takes 30-60 seconds to wake
- Upgrade to paid tier ($7/mo) for always-on

**Out of memory:**
- Reduce CHUNK_SIZE in environment
- Use smaller model
- Upgrade to larger instance

---

## 💰 Cost Breakdown

### Free Tier (Demo)
- Streamlit Cloud: Free (public apps)
- Total: **$0/month**

### Free Tier (Full System)
- Streamlit Cloud: Free
- Render.com: Free tier (sleeps after 15 min)
- Total: **$0/month** (with limitations)

### Paid Tier (Production)
- Streamlit Cloud: $20/month (private apps)
- Render.com: $7-25/month (always-on)
- Total: **$27-45/month**

### Self-Hosted (Best Value)
- VPS (DigitalOcean/Linode): $12-24/month
- Full control, best performance
- Total: **$12-24/month**

---

## ✅ Post-Deployment Checklist

- [ ] GitHub repository created and pushed
- [ ] Streamlit app deployed
- [ ] App loads without errors
- [ ] Links work correctly
- [ ] Documentation is readable
- [ ] (Optional) Backend deployed
- [ ] (Optional) Frontend connects to backend
- [ ] (Optional) Test document upload
- [ ] (Optional) Test query functionality

---

## 🎉 Success!

Your RAG system is now live! Share your links:

- **GitHub:** https://github.com/Navaprabhas/rag-system
- **Live Demo:** https://[your-app].streamlit.app

---

## 📞 Need Help?

1. Check Streamlit Cloud logs (in dashboard)
2. Check backend logs (in Render/Railway dashboard)
3. Review DEPLOYMENT.md for detailed guides
4. Open GitHub issue for support

---

## 🚀 Next Steps

1. **Share your project:**
   - Add to portfolio
   - Share on LinkedIn
   - Tweet about it

2. **Enhance the system:**
   - Add more document types
   - Improve UI/UX
   - Add authentication

3. **Scale up:**
   - Deploy to production
   - Add monitoring
   - Implement caching

---

**Deployment Status:** ✅ Ready to Deploy!

**Estimated Time:**
- Demo: 2 minutes
- Full: 30 minutes

**Your Repository:** https://github.com/Navaprabhas/rag-system

---

Good luck with your deployment! 🚀
