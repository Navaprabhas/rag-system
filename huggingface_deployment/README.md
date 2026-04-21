# RAG System - HuggingFace Space

This is a demo/documentation Space for the Production-Grade RAG System.

## About

A comprehensive Retrieval-Augmented Generation (RAG) system with:
- 🔍 Advanced retrieval with query rewriting and re-ranking
- 🤖 Multi-provider LLM support (Ollama, OpenAI, Anthropic)
- 🛡️ 4-layer anti-hallucination system
- 📄 Document processing (PDF, TXT, URL)
- 📊 Citation enforcement and confidence scoring

## Full System

For the complete interactive system with document upload and querying capabilities, please visit:

**GitHub Repository:** https://github.com/Navaprabhas/rag-system

### Quick Start (Docker)

```bash
git clone https://github.com/Navaprabhas/rag-system.git
cd rag-system
make setup
make start
```

Access:
- Frontend: http://localhost:8501
- API: http://localhost:8000/docs
- Qdrant: http://localhost:6333/dashboard

## Technology Stack

- **Backend:** FastAPI, Python 3.11
- **Vector DB:** Qdrant
- **LLM:** Ollama, OpenAI, Anthropic
- **Embeddings:** nomic-embed-text, OpenAI, Cohere
- **Frontend:** Streamlit, Gradio
- **Deployment:** Docker, Kubernetes-ready

## Features

### Document Processing
- PDF, TXT, and URL parsing
- Intelligent text chunking
- Multi-format support
- Metadata extraction

### Advanced Retrieval
- Query rewriting & expansion
- Dense vector search (Qdrant)
- Cross-encoder re-ranking
- Semantic similarity scoring

### Anti-Hallucination System
1. **Context Sufficiency Gate** - Rejects insufficient context
2. **Confidence Scoring** - Computes answer confidence
3. **Citation Enforcement** - Requires source citations
4. **Knowledge Boundary** - No external knowledge allowed

### Multi-Provider LLM
- Ollama (local deployment)
- OpenAI GPT models
- Anthropic Claude
- Flexible provider switching

## Performance

- **Query Latency:** 3-8 seconds (no cache), 2-5 seconds (cached)
- **Ingestion:** 5-15 seconds per 10-page PDF
- **Throughput:** 10-20 queries/minute (single instance)
- **Scalability:** Horizontal scaling ready

## Documentation

- [Complete README](https://github.com/Navaprabhas/rag-system/blob/main/README.md)
- [API Documentation](https://github.com/Navaprabhas/rag-system/blob/main/API.md)
- [Architecture Guide](https://github.com/Navaprabhas/rag-system/blob/main/ARCHITECTURE.md)
- [Deployment Guide](https://github.com/Navaprabhas/rag-system/blob/main/DEPLOYMENT.md)

## Author

**Navaprabhas**
- GitHub: [@Navaprabhas](https://github.com/Navaprabhas)
- Repository: [rag-system](https://github.com/Navaprabhas/rag-system)

## License

See the [GitHub repository](https://github.com/Navaprabhas/rag-system) for license information.

---

⭐ **Star the repository if you find it useful!**
