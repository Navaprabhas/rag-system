# 🚀 Deploy to Gradio (Hugging Face) & Streamlit Cloud

Complete guide to deploy your RAG system on both platforms.

---

## 📋 Table of Contents

1. [Gradio (Hugging Face Spaces)](#gradio-hugging-face-spaces)
2. [Streamlit Cloud](#streamlit-cloud)
3. [Comparison](#comparison)
4. [Troubleshooting](#troubleshooting)

---

## 🤗 Gradio (Hugging Face Spaces)

### Step 1: Create Hugging Face Account

1. Go to https://huggingface.co/
2. Click "Sign Up" (or sign in with GitHub)
3. Verify your email

### Step 2: Create New Space

1. **Go to Spaces**
   - Visit: https://huggingface.co/spaces
   - Click "Create new Space"

2. **Configure Space**
   ```
   Space name: rag-system
   License: MIT
   Select SDK: Gradio
   Space hardware: CPU basic (free)
   Visibility: Public
   ```

3. **Click "Create Space"**

### Step 3: Upload Files

You have two options:

#### Option A: Git Clone (Recommended)

```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/rag-system
cd rag-system

# Copy files from your RAG system
cp /path/to/rag-system/gradio_app.py app.py
cp /path/to/rag-system/requirements_gradio.txt requirements.txt
cp /path/to/rag-system/README_HUGGINGFACE.md README.md

# Commit and push
git add .
git commit -m "Initial commit: RAG System demo"
git push
```

#### Option B: Web Upload

1. In your Space, click "Files" tab
2. Click "Add file" → "Upload files"
3. Upload these files:
   - `gradio_app.py` → rename to `app.py`
   - `requirements_gradio.txt` → rename to `requirements.txt`
   - `README_HUGGINGFACE.md` → rename to `README.md`
4. Click "Commit changes to main"

### Step 4: Wait for Build

- Hugging Face will automatically build your Space
- Takes 2-5 minutes
- Watch the build logs in the "Logs" tab

### Step 5: Access Your App

Your app will be live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/rag-system
```

### Step 6: Share Your Space

- Click "Share" button
- Get direct link
- Embed in your website
- Share on social media

---

## ☁️ Streamlit Cloud

### Step 1: Prepare Repository

Your repository is already ready! It's at:
```
https://github.com/Navaprabhas/rag-system
```

### Step 2: Sign Up for Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "Sign up"
3. Sign in with GitHub
4. Authorize Streamlit

### Step 3: Deploy New App

1. **Click "New app"**

2. **Configure Deployment**
   ```
   Repository: Navaprabhas/rag-system
   Branch: main
   Main file path: streamlit_app.py
   ```

3. **Advanced Settings (Optional)**
   - Python version: 3.11
   - Click "Deploy!"

### Step 4: Wait for Deployment

- Streamlit will install dependencies
- Takes 2-3 minutes
- Watch the deployment logs

### Step 5: Access Your App

Your app will be live at:
```
https://YOUR_APP_NAME.streamlit.app
```

### Step 6: Custom Domain (Optional)

1. Go to app settings
2. Click "Custom domain"
3. Follow instructions to add your domain

---

## 📊 Comparison

| Feature | Gradio (HF Spaces) | Streamlit Cloud |
|---------|-------------------|-----------------|
| **Setup Time** | 5 minutes | 2 minutes |
| **Free Tier** | ✅ Yes | ✅ Yes |
| **Custom Domain** | ✅ Yes (paid) | ✅ Yes (paid) |
| **GPU Support** | ✅ Yes (paid) | ❌ No |
| **Storage** | Persistent | Ephemeral |
| **Community** | Hugging Face | Streamlit |
| **Best For** | ML demos | Data apps |
| **URL Format** | huggingface.co/spaces/... | streamlit.app |

---

## 🎯 Which Should You Choose?

### Choose Gradio (Hugging Face) if:
- ✅ You want to be part of the ML community
- ✅ You need GPU support (paid tier)
- ✅ You want persistent storage
- ✅ You prefer Gradio's interface style
- ✅ You want to showcase ML models

### Choose Streamlit if:
- ✅ You prefer Streamlit's interface
- ✅ You want faster deployment
- ✅ You're already using Streamlit
- ✅ You want simpler configuration
- ✅ You prefer the Streamlit community

### Why Not Both? 🎉
Deploy to both platforms! They serve different audiences:
- **Gradio**: ML/AI community on Hugging Face
- **Streamlit**: Data science community

---

## 🚀 Quick Deploy Commands

### For Gradio (Hugging Face Spaces)

```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/rag-system
cd rag-system

# Copy files
cp ../rag-system/gradio_app.py app.py
cp ../rag-system/requirements_gradio.txt requirements.txt
cp ../rag-system/README_HUGGINGFACE.md README.md

# Deploy
git add .
git commit -m "Deploy RAG System"
git push
```

### For Streamlit Cloud

Already done! Just:
1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select `Navaprabhas/rag-system`
4. Main file: `streamlit_app.py`
5. Deploy!

---

## 🐛 Troubleshooting

### Gradio Issues

**"Module not found" error:**
```bash
# Check requirements.txt includes:
gradio==4.16.0
```

**Space not building:**
- Check logs in "Logs" tab
- Verify all files are uploaded
- Check file names (app.py, requirements.txt, README.md)

**App crashes on startup:**
- Check Python version compatibility
- Review error logs
- Simplify app.py if needed

### Streamlit Issues

**"Module not found" error:**
- Verify `requirements.txt` in repository
- Check file is named exactly `requirements.txt`
- Ensure all dependencies are listed

**App won't deploy:**
- Check main file path is correct: `streamlit_app.py`
- Verify branch name is `main`
- Check repository is public

**Slow loading:**
- Normal for free tier (cold starts)
- First load takes 30-60 seconds
- Subsequent loads are faster

---

## 📱 Share Your Deployments

### Social Media Templates

**For Gradio:**
```
🚀 Just deployed my RAG System on Hugging Face Spaces!

Check it out: https://huggingface.co/spaces/YOUR_USERNAME/rag-system

Features:
✅ Anti-hallucination guarantees
✅ Multi-provider LLM support
✅ Advanced retrieval pipeline

#AI #MachineLearning #HuggingFace #RAG
```

**For Streamlit:**
```
🚀 My RAG System is now live on Streamlit Cloud!

Try it: https://YOUR_APP.streamlit.app

Built with Python, FastAPI, and Qdrant
Full source: https://github.com/Navaprabhas/rag-system

#AI #Streamlit #Python #RAG
```

---

## 🎨 Customization

### Gradio Customization

Edit `gradio_app.py`:

```python
# Change theme
demo = gr.Blocks(theme=gr.themes.Soft())  # or Base, Monochrome

# Change colors
demo = gr.Blocks(theme=gr.themes.Soft(
    primary_hue="red",
    secondary_hue="orange"
))

# Add custom CSS
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
"""
demo = gr.Blocks(css=custom_css)
```

### Streamlit Customization

Edit `streamlit_app.py`:

```python
# Change page config
st.set_page_config(
    page_title="My RAG System",
    page_icon="🤖",
    layout="wide"
)

# Add custom CSS
st.markdown("""
<style>
.stButton>button {
    background-color: #FF4B4B;
    color: white;
}
</style>
""", unsafe_allow_html=True)
```

---

## 📊 Analytics

### Gradio (Hugging Face)

- View stats in Space settings
- See visitor count
- Track usage over time
- Monitor resource usage

### Streamlit Cloud

- View analytics in app dashboard
- See active users
- Monitor app health
- Track deployment history

---

## 💰 Upgrade Options

### Gradio (Hugging Face Spaces)

**Free Tier:**
- CPU basic
- 16GB RAM
- 50GB storage
- Public spaces only

**Paid Tiers:**
- CPU upgrade: $0.03/hour
- GPU T4: $0.60/hour
- GPU A10G: $1.05/hour
- Private spaces available

### Streamlit Cloud

**Free Tier:**
- 1GB RAM
- 1 CPU
- Public apps only
- Community support

**Paid Tiers:**
- Starter: $20/month
  - Private apps
  - 1GB RAM
  - Email support
  
- Team: $250/month
  - 4GB RAM
  - Priority support
  - Custom domains

---

## ✅ Post-Deployment Checklist

### For Both Platforms

- [ ] App deploys successfully
- [ ] All tabs/pages load
- [ ] Links work correctly
- [ ] Documentation is readable
- [ ] No errors in logs
- [ ] Share link works
- [ ] Add to portfolio
- [ ] Share on social media
- [ ] Update resume/CV
- [ ] Add to GitHub README

---

## 🎉 Success!

You now have your RAG system deployed on:

1. **GitHub**: https://github.com/Navaprabhas/rag-system
2. **Gradio**: https://huggingface.co/spaces/YOUR_USERNAME/rag-system
3. **Streamlit**: https://YOUR_APP.streamlit.app

Share your work and get feedback from the community!

---

## 📞 Need Help?

### Gradio Support
- [Gradio Documentation](https://gradio.app/docs/)
- [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Community Forum](https://discuss.huggingface.co/)

### Streamlit Support
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Community Forum](https://discuss.streamlit.io/)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)

### Project Support
- [GitHub Issues](https://github.com/Navaprabhas/rag-system/issues)
- [GitHub Discussions](https://github.com/Navaprabhas/rag-system/discussions)

---

**Deployment Status:** ✅ Ready to Deploy!

**Estimated Time:**
- Gradio: 5 minutes
- Streamlit: 2 minutes
- Both: 7 minutes

**Your Repository:** https://github.com/Navaprabhas/rag-system

Good luck with your deployments! 🚀
