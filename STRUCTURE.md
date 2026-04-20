# Project Structure

Detailed explanation of the RAG System file structure and organization.

## 📁 Directory Tree

```
rag-system/
├── app/                          # Main application code
│   ├── api/                      # API layer
│   │   ├── routes/               # API route handlers
│   │   │   ├── documents.py      # Document management endpoints
│   │   │   ├── health.py         # Health check endpoint
│   │   │   ├── ingest.py         # Document ingestion endpoints
│   │   │   └── query.py          # Query endpoints (standard + streaming)
│   │   └── deps.py               # Dependency injection
│   │
│   ├── core/                     # Core configuration and utilities
│   │   ├── config.py             # Pydantic settings (env vars)
│   │   ├── exceptions.py         # Custom exception classes
│   │   └── logging.py            # Structured logging setup
│   │
│   ├── ingestion/                # Document processing
│   │   ├── parsers/              # File format parsers
│   │   │   ├── pdf_parser.py     # PDF extraction (PyMuPDF + pdfplumber)
│   │   │   ├── txt_parser.py     # Text file parsing
│   │   │   └── url_parser.py     # Web scraping (trafilatura)
│   │   └── chunker.py            # Semantic chunking logic
│   │
│   ├── llm/                      # LLM integrations
│   │   ├── base.py               # Abstract LLM interface
│   │   ├── anthropic_llm.py      # Anthropic Claude implementation
│   │   ├── ollama_llm.py         # Ollama local LLM implementation
│   │   └── openai_llm.py         # OpenAI GPT implementation
│   │
│   ├── models/                   # Pydantic data models
│   │   ├── request.py            # API request models
│   │   └── response.py           # API response models
│   │
│   ├── retrieval/                # Retrieval pipeline
│   │   ├── embedder.py           # Multi-provider embedding generation
│   │   ├── qdrant_client.py      # Qdrant vector DB operations
│   │   ├── query_rewriter.py     # Query expansion
│   │   └── reranker.py           # Cross-encoder re-ranking
│   │
│   ├── services/                 # Business logic services
│   │   ├── anti_hallucination.py # 4-layer validation engine
│   │   ├── context_builder.py    # Context assembly & prompt building
│   │   └── rag_service.py        # Main RAG orchestration
│   │
│   └── main.py                   # FastAPI application entry point
│
├── frontend/                     # Streamlit UI
│   └── app.py                    # Complete frontend application
│
├── tests/                        # Test suite
│   ├── test_ingestion.py         # Ingestion pipeline tests
│   ├── test_rag_service.py       # RAG service integration tests
│   └── test_retrieval.py         # Retrieval pipeline tests
│
├── data/                         # Runtime data (created on startup)
│   ├── cache/                    # Embedding cache
│   └── uploads/                  # Temporary file uploads
│
├── logs/                         # Application logs (created on startup)
│   └── rag_system.log            # Structured JSON logs
│
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
├── API.md                        # Complete API documentation
├── ARCHITECTURE.md               # System architecture guide
├── CHECKLIST.md                  # Deployment checklist
├── COMPLETION_STATUS.md          # Project completion tracking
├── DEPLOYMENT.md                 # Deployment guide
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # FastAPI container image
├── Dockerfile.streamlit          # Streamlit container image
├── Makefile                      # Common commands
├── PROJECT_SUMMARY.md            # Executive summary
├── pytest.ini                    # Pytest configuration
├── QUICK_REFERENCE.md            # Quick command reference
├── README.md                     # Main documentation
├── requirements.txt              # Python dependencies
├── setup.sh                      # Setup script
└── STRUCTURE.md                  # This file
```

## 📂 Detailed Component Breakdown

### `/app` - Main Application

The core application following clean architecture principles.

#### `/app/api` - API Layer

**Purpose:** HTTP interface for the RAG system

**Files:**
- `routes/health.py` - Health check endpoint
  - Returns service status
  - Checks Qdrant connectivity
  - Used by Docker healthchecks

- `routes/ingest.py` - Document ingestion
  - `POST /ingest/file` - Upload PDF/TXT files
  - `POST /ingest/url` - Scrape web URLs
  - `POST /ingest/text` - Direct text ingestion
  - Handles file validation, parsing, chunking, embedding

- `routes/query.py` - RAG queries
  - `POST /query` - Standard query with full response
  - `GET /query/stream` - Streaming query with SSE
  - Orchestrates retrieval and generation

- `routes/documents.py` - Document management
  - `GET /documents` - List all ingested documents
  - `DELETE /documents/{filename}` - Remove document and chunks

- `deps.py` - Dependency injection
  - Singleton service instances
  - Shared across requests
  - Proper lifecycle management

#### `/app/core` - Core Configuration

**Purpose:** Cross-cutting concerns and configuration

**Files:**
- `config.py` - Centralized configuration
  - Pydantic BaseSettings
  - Environment variable loading
  - Type-safe configuration
  - Default values
  - Validation rules

- `exceptions.py` - Custom exceptions
  - `RAGException` - Base exception
  - `DocumentProcessingError` - Ingestion failures
  - `EmbeddingError` - Embedding generation failures
  - `RetrievalError` - Search failures
  - `LLMError` - Generation failures
  - `InsufficientContextError` - Anti-hallucination trigger
  - Exception handlers for FastAPI

- `logging.py` - Structured logging
  - JSON formatter
  - File and console handlers
  - Log rotation
  - Contextual logging

#### `/app/ingestion` - Document Processing

**Purpose:** Convert documents into searchable chunks

**Files:**
- `parsers/pdf_parser.py` - PDF extraction
  - Uses PyMuPDF for text extraction
  - Falls back to pdfplumber for complex PDFs
  - Extracts metadata (title, author, page count)
  - Cleans extracted text

- `parsers/txt_parser.py` - Text file parsing
  - Encoding detection (chardet)
  - Supports UTF-8, Latin-1, etc.
  - Preserves formatting

- `parsers/url_parser.py` - Web scraping
  - Uses trafilatura for clean extraction
  - Falls back to BeautifulSoup
  - Removes navigation, ads, footers
  - Extracts title and metadata

- `chunker.py` - Semantic chunking
  - LangChain RecursiveCharacterTextSplitter
  - Configurable chunk size (default 400 tokens)
  - Configurable overlap (default 75 tokens)
  - Preserves sentence boundaries
  - Attaches metadata to each chunk
  - Content hashing for deduplication

#### `/app/llm` - LLM Integrations

**Purpose:** Abstract interface for multiple LLM providers

**Files:**
- `base.py` - Abstract interface
  - `BaseLLM` abstract class
  - `generate()` method for standard generation
  - `generate_stream()` method for streaming
  - Provider and model name properties

- `ollama_llm.py` - Ollama implementation
  - Local LLM inference
  - Supports llama3, mistral, phi3, etc.
  - Streaming support via ollama library
  - No API key required

- `openai_llm.py` - OpenAI implementation
  - GPT-4o, GPT-4o-mini support
  - Streaming via OpenAI SDK
  - Requires OPENAI_API_KEY

- `anthropic_llm.py` - Anthropic implementation
  - Claude 3 Haiku, Sonnet support
  - Streaming via Anthropic SDK
  - Requires ANTHROPIC_API_KEY

#### `/app/models` - Data Models

**Purpose:** Type-safe request/response models

**Files:**
- `request.py` - API request models
  - `QueryRequest` - Query parameters
  - `IngestRequest` - Ingestion parameters
  - Pydantic validation
  - Field constraints

- `response.py` - API response models
  - `RAGResponse` - Complete query response
  - `CitationItem` - Citation structure
  - `IngestResponse` - Ingestion result
  - `DocumentInfo` - Document metadata

#### `/app/retrieval` - Retrieval Pipeline

**Purpose:** Find relevant chunks for queries

**Files:**
- `embedder.py` - Embedding generation
  - Multi-provider support (Ollama, OpenAI, Cohere)
  - Disk-based caching (content hash → vector)
  - Batch processing support
  - Automatic dimension detection

- `qdrant_client.py` - Vector database
  - Collection management (create, delete)
  - Vector search with filters
  - Metadata filtering
  - Batch upsert operations
  - Document deletion

- `query_rewriter.py` - Query expansion
  - Generates 2-3 query variations
  - Uses LLM for paraphrasing
  - Improves recall

- `reranker.py` - Cross-encoder re-ranking
  - Uses sentence-transformers
  - Model: cross-encoder/ms-marco-MiniLM-L-6-v2
  - Reranks top-K to top-N
  - More accurate than cosine similarity

#### `/app/services` - Business Logic

**Purpose:** Orchestrate components into complete workflows

**Files:**
- `rag_service.py` - Main RAG orchestration
  - 12-step query pipeline
  - Query rewriting → retrieval → reranking → generation
  - Streaming support
  - LLM provider selection
  - Citation building

- `anti_hallucination.py` - Validation engine
  - **CHECK 1:** Context sufficiency gate
    - No chunks → fallback
    - Low similarity → fallback
    - Insufficient tokens → fallback
  - **CHECK 2:** Confidence scoring
    - Mean of top-3 scores
    - Threshold enforcement (default 0.4)
  - **CHECK 3:** Citation enforcement
    - Validates citation structure
    - Ensures citations present
  - **CHECK 4:** System prompt
    - Forbids external knowledge
    - Enforces strict grounding

- `context_builder.py` - Context assembly
  - Formats chunks with metadata
  - Token counting (tiktoken)
  - Respects max_context_tokens (3000)
  - Builds final prompt

### `/frontend` - User Interface

**Purpose:** Streamlit-based web UI

**Files:**
- `app.py` - Complete frontend
  - Document upload interface
  - URL ingestion form
  - Chat interface
  - Streaming response display
  - Citation visualization
  - Confidence score display
  - LLM provider selection
  - Document list management

### `/tests` - Test Suite

**Purpose:** Ensure code quality and correctness

**Files:**
- `test_ingestion.py` - Ingestion tests
  - Parser tests (PDF, TXT, URL)
  - Chunking tests
  - Deduplication tests
  - Metadata extraction tests

- `test_retrieval.py` - Retrieval tests
  - Embedding generation tests
  - Qdrant operations tests
  - Query rewriting tests
  - Reranking tests
  - Caching tests

- `test_rag_service.py` - Integration tests
  - End-to-end RAG pipeline
  - Anti-hallucination checks
  - Confidence scoring
  - Citation generation
  - Streaming responses
  - Fallback scenarios

## 🏗️ Architecture Patterns

### Clean Architecture Layers

```
Presentation (Frontend, API Routes)
    ↓
Application (Services)
    ↓
Domain (Retrieval, LLM, Ingestion)
    ↓
Infrastructure (Qdrant, Ollama, Cache)
```

### Dependency Flow

- **Outer layers depend on inner layers**
- **Inner layers never depend on outer layers**
- **Domain logic is independent of frameworks**

### Design Patterns Used

1. **Dependency Injection** - `app/api/deps.py`
2. **Strategy Pattern** - `app/llm/` (multiple LLM providers)
3. **Factory Pattern** - Parser selection in ingestion
4. **Singleton Pattern** - Service instances
5. **Template Method** - Anti-hallucination validation steps

## 📦 External Dependencies

### Core Framework
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### Document Processing
- **PyMuPDF** - PDF parsing
- **pdfplumber** - Alternative PDF parser
- **trafilatura** - Web scraping
- **BeautifulSoup4** - HTML parsing
- **LangChain** - Text splitting

### Vector Database
- **Qdrant** - Vector storage and search

### Embeddings & LLM
- **Ollama** - Local LLM and embeddings
- **OpenAI** - GPT models
- **Anthropic** - Claude models
- **sentence-transformers** - Re-ranking

### Utilities
- **tiktoken** - Token counting
- **chardet** - Encoding detection
- **httpx** - Async HTTP client
- **python-dotenv** - Environment variables

### Frontend
- **Streamlit** - Web UI framework

### Testing
- **pytest** - Test framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting

## 🔄 Data Flow

### Ingestion Flow

```
User Upload
    ↓
API Route (ingest.py)
    ↓
Parser Selection (pdf/txt/url)
    ↓
Text Extraction
    ↓
Chunker (chunker.py)
    ↓
Embedder (embedder.py)
    ↓
Qdrant Storage (qdrant_client.py)
    ↓
Response
```

### Query Flow

```
User Query
    ↓
API Route (query.py)
    ↓
RAG Service (rag_service.py)
    ↓
Query Rewriter (query_rewriter.py)
    ↓
Embedder (embedder.py)
    ↓
Qdrant Search (qdrant_client.py)
    ↓
Reranker (reranker.py)
    ↓
Context Builder (context_builder.py)
    ↓
Anti-Hallucination Checks (anti_hallucination.py)
    ↓
LLM Generation (ollama/openai/anthropic)
    ↓
Citation Building
    ↓
Response
```

## 🗂️ Configuration Files

### `.env.example`
Template for environment variables. Copy to `.env` and customize.

### `docker-compose.yml`
Defines 4 services:
- `fastapi` - Backend API
- `qdrant` - Vector database
- `ollama` - Local LLM
- `streamlit` - Frontend UI

### `Dockerfile`
FastAPI container:
- Base: python:3.11-slim
- System deps: libpoppler-cpp-dev, tesseract-ocr
- Python deps from requirements.txt
- Exposes port 8000

### `Dockerfile.streamlit`
Streamlit container:
- Base: python:3.11-slim
- Python deps from requirements.txt
- Exposes port 8501

### `Makefile`
Common commands:
- `make setup` - Initial setup
- `make start` - Start services
- `make stop` - Stop services
- `make test` - Run tests
- `make clean` - Clean up

### `pytest.ini`
Pytest configuration:
- Test discovery patterns
- Coverage settings
- Async support

### `requirements.txt`
All Python dependencies with pinned versions.

## 📝 Documentation Files

### User Documentation
- `README.md` - Main documentation
- `QUICK_REFERENCE.md` - Command reference
- `API.md` - API documentation

### Technical Documentation
- `ARCHITECTURE.md` - System architecture
- `STRUCTURE.md` - This file
- `DEPLOYMENT.md` - Deployment guide

### Project Management
- `PROJECT_SUMMARY.md` - Executive summary
- `COMPLETION_STATUS.md` - Progress tracking
- `CHECKLIST.md` - Deployment checklist

## 🎯 Key Design Decisions

### Why Clean Architecture?
- **Testability** - Easy to test components in isolation
- **Maintainability** - Clear separation of concerns
- **Flexibility** - Easy to swap implementations
- **Scalability** - Can split into microservices

### Why Pydantic?
- **Type Safety** - Catch errors at validation time
- **Documentation** - Auto-generated API docs
- **Performance** - Fast validation with Rust core

### Why Async/Await?
- **Concurrency** - Handle multiple requests efficiently
- **I/O Bound** - Most operations are network/disk I/O
- **Streaming** - Natural fit for SSE responses

### Why Multiple LLM Providers?
- **Flexibility** - Choose based on cost/performance
- **Redundancy** - Fallback if one provider fails
- **Local Option** - Ollama for privacy/cost

### Why Qdrant?
- **Performance** - Fast HNSW indexing
- **Features** - Metadata filtering, quantization
- **Ease of Use** - Simple API, good docs
- **Open Source** - Can self-host

## 🔍 Finding Your Way Around

### "I want to add a new LLM provider"
→ Create new file in `app/llm/` implementing `BaseLLM`

### "I want to add a new document format"
→ Create new parser in `app/ingestion/parsers/`

### "I want to modify the anti-hallucination logic"
→ Edit `app/services/anti_hallucination.py`

### "I want to change the API response format"
→ Edit models in `app/models/response.py`

### "I want to add a new API endpoint"
→ Add route in `app/api/routes/` and include in `app/main.py`

### "I want to customize the UI"
→ Edit `frontend/app.py`

### "I want to change configuration defaults"
→ Edit `app/core/config.py`

## 📚 Further Reading

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [RAG Best Practices](https://www.anthropic.com/index/retrieval-augmented-generation)

---

**Last Updated:** 2024-01-15
**Version:** 1.0.0
