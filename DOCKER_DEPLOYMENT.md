# 🐳 Docker Deployment - Full RAG System

## Why Docker?

Streamlit Cloud is great for demos, but the **full RAG system** needs:
- ✅ Qdrant vector database
- ✅ Ollama LLM server
- ✅ FastAPI backend
- ✅ Streamlit frontend

**Docker Compose runs everything together!**

---

## 🚀 Quick Start (10 Minutes)

### Prerequisites

- Docker Desktop installed
- 8GB+ RAM available
- 20GB+ disk space

### Step 1: Clone Repository

```bash
git clone https://github.com/Navaprabhas/rag-system.git
cd rag-system
```

### Step 2: Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (optional)
# nano .env
```

### Step 3: Start Everything

```bash
# Using Makefile (recommended)
make setup
make start

# OR using Docker Compose directly
docker-compose up -d
```

### Step 4: Wait for Services (2-3 minutes)

```bash
# Watch the logs
docker-compose logs -f

# Wait for:
# ✅ Qdrant: "Qdrant gRPC listening on 6334"
# ✅ Ollama: Models downloaded
# ✅ FastAPI: "Application startup complete"
# ✅ Streamlit: "You can now view your Streamlit app"
```

### Step 5: Access Your System

Open in browser:
- **Frontend (Streamlit)**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## 📋 What Gets Deployed

### 4 Services Running:

1. **FastAPI Backend** (Port 8000)
   - Document ingestion
   - RAG query processing
   - API endpoints

2. **Qdrant Vector DB** (Port 6333)
   - Vector storage
   - Similarity search
   - Metadata filtering

3. **Ollama LLM** (Port 11434)
   - Local LLM inference
   - Embedding generation
   - Models: llama3, nomic-embed-text

4. **Streamlit Frontend** (Port 8501)
   - Web interface
   - Document upload
   - Chat interface

---

## 🎯 Using the System

### 1. Upload Documents

1. Go to http://localhost:8501
2. Sidebar → "Upload Document"
3. Choose PDF or TXT file
4. Click "Upload File"
5. Wait for processing (5-15 seconds)

### 2. Query Documents

1. Type question in chat input
2. Press Enter
3. Watch streaming response
4. See citations and confidence score

### 3. Manage Documents

1. Sidebar → "Ingested Documents"
2. Click "🔄 Refresh List"
3. View document details
4. Delete documents if needed

---

## 🛠️ Common Commands

### Start/Stop

```bash
# Start all services
make start
# OR
docker-compose up -d

# Stop all services
make stop
# OR
docker-compose down

# Restart services
make restart
# OR
docker-compose restart
```

### View Logs

```bash
# All services
make logs
# OR
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi
docker-compose logs -f qdrant
docker-compose logs -f ollama
docker-compose logs -f streamlit
```

### Check Status

```bash
# List running containers
docker-compose ps

# Check health
curl http://localhost:8000/api/v1/health
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (deletes data!)
docker-compose down -v

# Full cleanup
make clean
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# LLM Provider
LLM_PROVIDER=ollama              # ollama, openai, anthropic
EMBEDDING_PROVIDER=ollama        # ollama, openai, cohere

# Ollama Configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=llama3

# External API Keys (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
COHERE_API_KEY=...

# Qdrant Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=rag_documents

# Retrieval Settings
TOP_K=10
RERANK_TOP_N=5
CONFIDENCE_THRESHOLD=0.4

# Chunking
CHUNK_SIZE=400
CHUNK_OVERLAP=75

# Features
EMBEDDING_CACHE_ENABLED=true
ENABLE_STREAMING=true
LOG_LEVEL=INFO
```

### Change LLM Model

```bash
# Edit .env
OLLAMA_LLM_MODEL=mistral    # or phi3, llama3, etc.

# Restart services
docker-compose restart fastapi
```

### Use OpenAI Instead

```bash
# Edit .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# Restart
docker-compose restart fastapi
```

---

## 🐛 Troubleshooting

### Services Won't Start

**Check Docker is running:**
```bash
docker --version
docker-compose --version
```

**Check ports are available:**
```bash
# Windows
netstat -an | findstr "8000 8501 6333 11434"

# Linux/Mac
lsof -i :8000,8501,6333,11434
```

**Solution:**
```bash
# Stop conflicting services
# OR change ports in docker-compose.yml
```

### Ollama Models Not Downloading

**Check logs:**
```bash
docker-compose logs ollama
```

**Manual download:**
```bash
docker exec rag-ollama ollama pull nomic-embed-text
docker exec rag-ollama ollama pull llama3
```

### Qdrant Connection Error

**Check Qdrant is running:**
```bash
curl http://localhost:6333/health
```

**Restart Qdrant:**
```bash
docker-compose restart qdrant
```

### Out of Memory

**Increase Docker memory:**
- Docker Desktop → Settings → Resources
- Increase Memory to 8GB+

**Use smaller model:**
```bash
# Edit .env
OLLAMA_LLM_MODEL=phi3  # Smaller than llama3
```

### Slow Responses

**Enable caching:**
```bash
# Edit .env
EMBEDDING_CACHE_ENABLED=true
```

**Reduce chunk size:**
```bash
# Edit .env
CHUNK_SIZE=300
TOP_K=5
```

---

## 📊 Resource Usage

### Typical Usage

- **Memory**: 6-8GB
- **CPU**: 2-4 cores
- **Disk**: 15-20GB (with models)

### Per Service

| Service | Memory | CPU | Disk |
|---------|--------|-----|------|
| FastAPI | 500MB | 0.5 | 100MB |
| Qdrant | 1-2GB | 0.5 | 1-5GB |
| Ollama | 4-6GB | 2-3 | 10-15GB |
| Streamlit | 200MB | 0.2 | 50MB |

---

## 🚀 Production Deployment

### For Production Use:

1. **Use docker-compose.prod.yml**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Add Nginx reverse proxy**
   - See DEPLOYMENT.md for configuration

3. **Enable HTTPS**
   - Use Let's Encrypt certificates
   - Configure in Nginx

4. **Add authentication**
   - Implement JWT tokens
   - See DEPLOYMENT.md

5. **Set up monitoring**
   - Prometheus + Grafana
   - Health checks
   - Alerts

---

## 🌐 Deploy to Cloud

### AWS EC2

```bash
# Launch EC2 instance (t3.large or bigger)
# Install Docker
sudo yum install docker -y
sudo service docker start

# Clone and run
git clone https://github.com/Navaprabhas/rag-system.git
cd rag-system
make setup && make start
```

### Google Cloud VM

```bash
# Create VM (e2-standard-4 or bigger)
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone and run
git clone https://github.com/Navaprabhas/rag-system.git
cd rag-system
make setup && make start
```

### DigitalOcean Droplet

```bash
# Create Droplet (4GB+ RAM)
# Docker pre-installed on Docker Droplet

# Clone and run
git clone https://github.com/Navaprabhas/rag-system.git
cd rag-system
make setup && make start
```

---

## 📱 Access from Other Devices

### Local Network

1. **Find your IP:**
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```

2. **Access from other devices:**
   ```
   http://YOUR_IP:8501  (Frontend)
   http://YOUR_IP:8000  (API)
   ```

### Internet (with ngrok)

```bash
# Install ngrok
# https://ngrok.com/download

# Expose Streamlit
ngrok http 8501

# Share the ngrok URL
```

---

## 🎓 Development Mode

### Run with Hot Reload

```bash
# Backend (auto-reload on code changes)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (auto-reload)
streamlit run frontend/app.py --server.port 8501
```

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 📦 Update System

### Pull Latest Changes

```bash
# Stop services
docker-compose down

# Pull updates
git pull origin main

# Rebuild and start
docker-compose build
docker-compose up -d
```

### Update Models

```bash
# Pull new Ollama model
docker exec rag-ollama ollama pull mistral

# Update .env to use new model
OLLAMA_LLM_MODEL=mistral

# Restart
docker-compose restart fastapi
```

---

## 🎉 Success Checklist

- [ ] Docker Desktop installed
- [ ] Repository cloned
- [ ] `.env` file created
- [ ] Services started with `make start`
- [ ] All 4 containers running
- [ ] Frontend accessible at http://localhost:8501
- [ ] API docs at http://localhost:8000/docs
- [ ] Document uploaded successfully
- [ ] Query returns answer with citations
- [ ] Confidence score displayed

---

## 📞 Need Help?

### Documentation
- **README.md** - Main documentation
- **QUICK_REFERENCE.md** - Command reference
- **DEPLOYMENT.md** - Production deployment
- **TROUBLESHOOTING.md** - Common issues

### Support
- **GitHub Issues**: https://github.com/Navaprabhas/rag-system/issues
- **Discussions**: https://github.com/Navaprabhas/rag-system/discussions

---

## 🎊 You're All Set!

Your full RAG system is now running locally with Docker!

**Access:**
- Frontend: http://localhost:8501
- API: http://localhost:8000/docs
- Qdrant: http://localhost:6333/dashboard

**Next steps:**
1. Upload a document
2. Ask questions
3. See the anti-hallucination system in action!

---

**Deployment time:** 10 minutes  
**Status:** Production-ready ✅  
**Your repository:** https://github.com/Navaprabhas/rag-system

Enjoy your RAG system! 🚀
