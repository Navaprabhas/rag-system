# Quick Reference Guide

Fast reference for common operations and commands.

## 🚀 Quick Start

```bash
# Setup and start (first time)
make setup && make start

# Access
# Frontend: http://localhost:8501
# API Docs: http://localhost:8000/docs
# Qdrant: http://localhost:6333/dashboard
```

## 📋 Common Commands

### Docker Operations

```bash
# Start all services
make start
docker-compose up -d

# Stop all services
make stop
docker-compose down

# Restart services
make restart
docker-compose restart

# View logs
make logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f fastapi
docker-compose logs -f qdrant
docker-compose logs -f ollama

# Rebuild images
make build
docker-compose build

# Clean everything
make clean
docker-compose down -v
```

### Development

```bash
# Install dependencies
make install
pip install -r requirements.txt

# Run locally (without Docker)
make dev
uvicorn app.main:app --reload

# Run tests
make test
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html

# Lint code
make lint
ruff check app/ tests/

# Format code
make format
black app/ tests/ frontend/
```

## 🔧 Configuration

### Environment Variables

```bash
# Edit configuration
nano .env

# Key settings
LLM_PROVIDER=ollama          # ollama, openai, anthropic
EMBEDDING_PROVIDER=ollama    # ollama, openai, cohere
CONFIDENCE_THRESHOLD=0.4     # 0.0-1.0
TOP_K=10                     # Retrieval count
CHUNK_SIZE=400               # Token count
```

### Ollama Models

```bash
# List installed models
docker exec rag-ollama ollama list

# Pull new model
docker exec rag-ollama ollama pull mistral
docker exec rag-ollama ollama pull phi3

# Remove model
docker exec rag-ollama ollama rm model_name
```

## 📡 API Quick Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Ingest Document
```bash
# Upload file
curl -X POST "http://localhost:8000/api/v1/ingest/file" \
  -F "file=@document.pdf"

# Ingest URL
curl -X POST "http://localhost:8000/api/v1/ingest/url" \
  -H "Content-Type: application/json" \
  -d '{"source_type": "url", "url": "https://example.com/article"}'

# Ingest text
curl -X POST "http://localhost:8000/api/v1/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{"source_type": "text", "content": "Your text here", "filename": "notes.txt"}'
```

### Query
```bash
# Standard query
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main features?",
    "llm_provider": "ollama",
    "model_name": "llama3"
  }'

# Streaming query
curl -N "http://localhost:8000/api/v1/query/stream?query=What+is+AI"
```

### Document Management
```bash
# List documents
curl http://localhost:8000/api/v1/documents

# Delete document
curl -X DELETE "http://localhost:8000/api/v1/documents/filename.pdf"
```

## 🐍 Python Client

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Ingest document
        with open("document.pdf", "rb") as f:
            response = await client.post(
                "http://localhost:8000/api/v1/ingest/file",
                files={"file": f}
            )
        print(response.json())
        
        # Query
        response = await client.post(
            "http://localhost:8000/api/v1/query",
            json={"query": "What is this about?"}
        )
        result = response.json()
        print(result["answer"])
        print(f"Confidence: {result['confidence']:.0%}")

asyncio.run(main())
```

## 🔍 Troubleshooting

### Service Won't Start

```bash
# Check if ports are in use
netstat -an | grep 8000
netstat -an | grep 6333
netstat -an | grep 11434

# Check Docker status
docker ps
docker-compose ps

# View error logs
docker-compose logs fastapi
docker-compose logs qdrant
docker-compose logs ollama
```

### Ollama Issues

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
docker-compose restart ollama

# Check models are downloaded
docker exec rag-ollama ollama list

# Re-download models
docker exec rag-ollama ollama pull nomic-embed-text
docker exec rag-ollama ollama pull llama3
```

### Qdrant Issues

```bash
# Check Qdrant health
curl http://localhost:6333/health

# List collections
curl http://localhost:6333/collections

# Check collection info
curl http://localhost:6333/collections/rag_documents

# Restart Qdrant
docker-compose restart qdrant
```

### Low Confidence Scores

```bash
# Check documents are ingested
curl http://localhost:8000/api/v1/documents

# Lower threshold temporarily
# Edit .env: CONFIDENCE_THRESHOLD=0.3

# Increase retrieval
# Edit .env: TOP_K=20

# Restart services
docker-compose restart fastapi
```

### Memory Issues

```bash
# Check memory usage
docker stats

# Reduce chunk size
# Edit .env: CHUNK_SIZE=300

# Reduce context tokens
# Edit .env: MAX_CONTEXT_TOKENS=2000

# Use smaller model
# Edit .env: OLLAMA_LLM_MODEL=phi3
```

## 📊 Monitoring

### Check Service Health

```bash
# All services
curl http://localhost:8000/api/v1/health

# Qdrant
curl http://localhost:6333/health

# Ollama
curl http://localhost:11434/api/tags
```

### View Logs

```bash
# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f fastapi

# Follow new logs only
docker-compose logs -f --since 1m
```

### Resource Usage

```bash
# Real-time stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

## 🗄️ Database Operations

### Qdrant Backup

```bash
# Create snapshot
curl -X POST http://localhost:6333/collections/rag_documents/snapshots

# List snapshots
curl http://localhost:6333/collections/rag_documents/snapshots

# Download snapshot
curl http://localhost:6333/collections/rag_documents/snapshots/snapshot_name \
  -o backup.snapshot
```

### Qdrant Restore

```bash
# Upload snapshot
curl -X PUT http://localhost:6333/collections/rag_documents/snapshots/upload \
  -F 'snapshot=@backup.snapshot'
```

### Clear All Data

```bash
# Delete collection
curl -X DELETE http://localhost:6333/collections/rag_documents

# Recreate (will happen automatically on next ingest)
# Or restart services
docker-compose restart fastapi
```

## 🔐 Security

### Change Default Ports

Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Change 8000 to 8080
```

### Add API Key (Future)

```bash
# Generate key
openssl rand -hex 32

# Add to .env
API_KEY=your_generated_key

# Use in requests
curl -H "Authorization: Bearer your_generated_key" \
  http://localhost:8000/api/v1/query
```

### Enable HTTPS

See DEPLOYMENT.md for Nginx SSL configuration.

## 📈 Performance Tuning

### Increase Workers

Edit `docker-compose.yml`:
```yaml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Enable Redis Cache

```bash
# Add Redis service to docker-compose.yml
# Update .env
REDIS_ENABLED=true
REDIS_HOST=redis
REDIS_PORT=6379
```

### Optimize Qdrant

```bash
# Enable quantization (reduces memory)
# See DEPLOYMENT.md for configuration
```

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_ingestion.py -v
pytest tests/test_retrieval.py::test_embedder -v
```

### Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

## 📦 Deployment

### Production Deployment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# With environment
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n rag-system
kubectl get services -n rag-system

# View logs
kubectl logs -f deployment/fastapi -n rag-system
```

## 🆘 Emergency Commands

### Stop Everything

```bash
docker-compose down
docker stop $(docker ps -aq)
```

### Reset Everything

```bash
make clean
docker-compose down -v
docker system prune -a -f
rm -rf data/ logs/
make setup
make start
```

### Backup Before Reset

```bash
# Backup Qdrant data
docker cp rag-qdrant:/qdrant/storage ./qdrant_backup

# Backup logs
cp -r logs/ logs_backup/

# Backup uploaded files
cp -r data/ data_backup/
```

## 📞 Support

- **Documentation:** http://localhost:8000/docs
- **GitHub Issues:** [repository-url]/issues
- **Email:** support@example.com

## 🔗 Useful Links

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Ollama Docs](https://ollama.ai/docs)
- [Streamlit Docs](https://docs.streamlit.io/)

---

**Tip:** Bookmark this page for quick access to common commands!
