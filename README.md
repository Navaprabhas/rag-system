# Production-Grade RAG System with Anti-Hallucination Guarantees

[![GitHub](https://img.shields.io/badge/GitHub-Navaprabhas%2Frag--system-blue?logo=github)](https://github.com/Navaprabhas/rag-system)
[![Streamlit](https://img.shields.io/badge/Streamlit-Deploy-FF4B4B?logo=streamlit)](https://share.streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A complete, production-ready Retrieval-Augmented Generation (RAG) system built with strict anti-hallucination controls, clean architecture, and deployment readiness.

**🚀 [Live Demo](https://share.streamlit.io/)** | **📖 [Documentation](https://github.com/Navaprabhas/rag-system#readme)** | **🐳 [Quick Start](#-quick-start)**

## 🎯 Core Features

- **Zero-Hallucination Design**: Strict validation ensures responses are grounded in retrieved documents
- **Multi-Provider Support**: Ollama (local), OpenAI, and Anthropic LLMs
- **Advanced Retrieval**: Query rewriting, dense retrieval, and cross-encoder re-ranking
- **Document Processing**: PDF, TXT, and web URL ingestion with clean text extraction
- **Vector Database**: Qdrant for efficient similarity search
- **Streaming Responses**: Server-Sent Events (SSE) for real-time answers
- **Production Ready**: Docker deployment, structured logging, comprehensive error handling

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Streamlit Frontend)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Ingestion  │  │   Retrieval  │  │   Generation │         │
│  │   Pipeline   │  │   Pipeline   │  │   Pipeline   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Qdrant     │    │    Ollama    │    │  Embedding   │
│   Vector DB  │    │     LLM      │    │    Cache     │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Pipeline Flow

```
1. INGESTION
   Document → Parser → Chunker → Embedder → Qdrant
   
2. RETRIEVAL
   Query → Rewriter → Embedder → Qdrant Search → Reranker
   
3. GENERATION
   Context Builder → Anti-Hallucination Checks → LLM → Response
```

## 📋 Anti-Hallucination Guarantees

The system implements **4 strict validation layers**:

### CHECK 1: Context Sufficiency Gate
- Rejects if no chunks retrieved
- Rejects if max similarity score < 0.35
- Rejects if total context tokens < 50

### CHECK 2: Confidence Scoring
- Computes confidence from top-3 similarity scores
- Rejects if confidence < threshold (default 0.4)
- Returns confidence score with every response

### CHECK 3: Citation Enforcement
- Every response must include structured citations
- Citations contain source, chunk_id, page, and excerpt
- Responses without citations are rejected

### CHECK 4: No External Knowledge
- System prompt explicitly forbids external knowledge
- Fallback message: "I don't have enough information from the provided sources"

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- 8GB+ RAM recommended
- 10GB+ disk space for models

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd rag-system
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your API keys if using external providers
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

This will start:
- FastAPI backend on `http://localhost:8000`
- Streamlit frontend on `http://localhost:8501`
- Qdrant on `http://localhost:6333`
- Ollama with models pre-loaded

4. **Access the application**
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

### Local Development (without Docker)

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Start Qdrant**
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant:latest
```

3. **Start Ollama**
```bash
# Install Ollama from https://ollama.ai
ollama serve
ollama pull nomic-embed-text
ollama pull llama3
```

4. **Start FastAPI backend**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Start Streamlit frontend**
```bash
streamlit run frontend/app.py --server.port 8501
```

## 📚 API Documentation

### Ingest Document (File)

```bash
curl -X POST "http://localhost:8000/api/v1/ingest/file" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "status": "success",
  "document_id": "abc123...",
  "chunks_created": 42,
  "filename": "document.pdf",
  "file_type": "pdf",
  "metadata": {
    "page_count": 10,
    "title": "Document Title"
  }
}
```

### Ingest from URL

```bash
curl -X POST "http://localhost:8000/api/v1/ingest/url" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "url",
    "url": "https://example.com/article"
  }'
```

### Query RAG System

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main features?",
    "llm_provider": "ollama",
    "model_name": "llama3",
    "top_k": 10,
    "rerank_top_n": 5
  }'
```

**Response:**
```json
{
  "answer": "Based on the provided documents, the main features include...",
  "citations": [
    {
      "source": "document.pdf",
      "chunk_id": "document.pdf_5",
      "page": 3,
      "excerpt": "The system provides advanced features such as...",
      "score": 0.89
    }
  ],
  "confidence": 0.87,
  "retrieval_count": 5,
  "query_rewritten": "main features | key capabilities | primary functions",
  "llm_provider": "ollama",
  "model": "llama3"
}
```

### Streaming Query

```bash
curl -N "http://localhost:8000/api/v1/query/stream?query=What+are+the+features"
```

Returns Server-Sent Events (SSE):
```
data: {"type":"metadata","confidence":0.87,"retrieval_count":5}

data: {"type":"answer","content":"Based on"}

data: {"type":"answer","content":" the documents"}

data: {"type":"citations","citations":[...]}
```

### List Documents

```bash
curl "http://localhost:8000/api/v1/documents"
```

### Delete Document

```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/document.pdf"
```

### Health Check

```bash
curl "http://localhost:8000/api/v1/health"
```

## ⚙️ Configuration

All configuration is managed through environment variables in `.env`:

### Core Settings

```bash
# LLM Provider (ollama, openai, anthropic)
LLM_PROVIDER=ollama

# Embedding Provider (ollama, openai, cohere)
EMBEDDING_PROVIDER=ollama

# Ollama Configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=llama3

# External API Keys (optional)
OPENAI_API_KEY=sk-...
COHERE_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
```

### Retrieval Settings

```bash
# Chunking
CHUNK_SIZE=400
CHUNK_OVERLAP=75

# Retrieval
TOP_K=10
RERANK_TOP_N=5
MAX_CONTEXT_TOKENS=3000
CONFIDENCE_THRESHOLD=0.4
```

### Feature Flags

```bash
EMBEDDING_CACHE_ENABLED=true
ENABLE_STREAMING=true
LOG_LEVEL=INFO
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## 📊 Monitoring & Logging

### Structured Logging

All logs are output in JSON format for easy parsing:

```json
{
  "asctime": "2024-01-15 10:30:45",
  "name": "rag_system",
  "levelname": "INFO",
  "message": "Retrieved 5 chunks from Qdrant"
}
```

Logs are written to:
- Console (stdout)
- File: `./logs/rag_system.log`

### Health Monitoring

Monitor service health:

```bash
curl http://localhost:8000/api/v1/health
```

## 🔧 Troubleshooting

### Ollama Connection Issues

**Problem:** Cannot connect to Ollama

**Solution:**
```bash
# Check Ollama is running
docker ps | grep ollama

# Check logs
docker logs rag-ollama

# Restart Ollama
docker-compose restart ollama
```

### Qdrant Connection Issues

**Problem:** Qdrant not accessible

**Solution:**
```bash
# Check Qdrant is running
curl http://localhost:6333/health

# Check logs
docker logs rag-qdrant

# Restart Qdrant
docker-compose restart qdrant
```

### Low Confidence Scores

**Problem:** All queries return fallback message

**Solution:**
1. Check if documents are ingested: `curl http://localhost:8000/api/v1/documents`
2. Lower confidence threshold in `.env`: `CONFIDENCE_THRESHOLD=0.3`
3. Increase retrieval: `TOP_K=20`

### Memory Issues

**Problem:** Out of memory errors

**Solution:**
1. Reduce chunk size: `CHUNK_SIZE=300`
2. Reduce context tokens: `MAX_CONTEXT_TOKENS=2000`
3. Increase Docker memory limit in `docker-compose.yml`

### Slow Responses

**Problem:** Queries take too long

**Solution:**
1. Enable embedding cache: `EMBEDDING_CACHE_ENABLED=true`
2. Reduce TOP_K: `TOP_K=5`
3. Use smaller model: `OLLAMA_LLM_MODEL=phi3`

## 🏗️ Project Structure

```
rag-system/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── ingest.py       # Document ingestion endpoints
│   │   │   ├── query.py        # Query endpoints
│   │   │   ├── documents.py    # Document management
│   │   │   └── health.py       # Health check
│   │   └── deps.py             # Dependency injection
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   ├── logging.py          # Structured logging
│   │   └── exceptions.py       # Custom exceptions
│   ├── ingestion/
│   │   ├── parsers/
│   │   │   ├── pdf_parser.py   # PDF parsing
│   │   │   ├── txt_parser.py   # Text parsing
│   │   │   └── url_parser.py   # Web scraping
│   │   └── chunker.py          # Semantic chunking
│   ├── retrieval/
│   │   ├── embedder.py         # Embedding generation
│   │   ├── qdrant_client.py    # Vector database ops
│   │   ├── reranker.py         # Cross-encoder reranking
│   │   └── query_rewriter.py   # Query expansion
│   ├── llm/
│   │   ├── base.py             # LLM interface
│   │   ├── ollama_llm.py       # Ollama implementation
│   │   ├── openai_llm.py       # OpenAI implementation
│   │   └── anthropic_llm.py    # Anthropic implementation
│   ├── services/
│   │   ├── rag_service.py      # Main RAG orchestration
│   │   ├── anti_hallucination.py # Validation engine
│   │   └── context_builder.py  # Context assembly
│   ├── models/
│   │   ├── request.py          # Request models
│   │   └── response.py         # Response models
│   └── main.py                 # FastAPI application
├── frontend/
│   └── app.py                  # Streamlit UI
├── tests/
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   └── test_rag_service.py
├── Dockerfile
├── Dockerfile.streamlit
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run linting: `ruff check app/`
5. Run tests: `pytest tests/`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with FastAPI, Streamlit, Qdrant, and LangChain
- Supports Ollama, OpenAI, and Anthropic LLMs
- Uses sentence-transformers for re-ranking

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See `/docs` endpoint
- Email: support@example.com

---

**Built with ❤️ for production deployments**
