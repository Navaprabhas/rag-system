# System Architecture

Detailed architecture documentation for the RAG System.

## Overview

The RAG System is built with a modular, layered architecture following clean architecture principles and SOLID design patterns.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                  (Streamlit Frontend)                        │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────▼────────────────────────────────┐
│                      API LAYER                               │
│                   (FastAPI Routes)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Ingest   │  │  Query   │  │Documents │  │  Health  │   │
│  │ Routes   │  │  Routes  │  │  Routes  │  │  Route   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    SERVICE LAYER                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              RAG Service (Orchestrator)              │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Anti-Halluc.  │  │   Context    │  │   Ingestion  │     │
│  │   Engine     │  │   Builder    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   DOMAIN LAYER                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Embedder  │  │  Qdrant  │  │Reranker  │  │  Query   │   │
│  │          │  │  Client  │  │          │  │ Rewriter │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │   LLM    │  │  Parsers │  │ Chunker  │                 │
│  │Providers │  │          │  │          │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Qdrant  │  │  Ollama  │  │  Cache   │  │  Logging │   │
│  │ Database │  │   LLM    │  │  (Disk)  │  │  System  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Presentation Layer

**Streamlit Frontend (`frontend/app.py`)**
- User interface for document management and querying
- Real-time streaming response display
- Citation and confidence visualization
- LLM provider configuration

**Responsibilities:**
- User interaction
- File upload handling
- Response rendering
- Configuration management

### 2. API Layer

**FastAPI Application (`app/main.py`)**
- RESTful API endpoints
- Request validation (Pydantic)
- Error handling
- CORS middleware
- Structured logging

**Routes:**
- `/api/v1/ingest/*` - Document ingestion
- `/api/v1/query` - RAG queries
- `/api/v1/documents` - Document management
- `/api/v1/health` - Health checks

**Responsibilities:**
- HTTP request/response handling
- Input validation
- Authentication (future)
- Rate limiting (future)

### 3. Service Layer

**RAG Service (`app/services/rag_service.py`)**
- Orchestrates complete RAG pipeline
- Coordinates retrieval and generation
- Manages streaming responses

**Anti-Hallucination Engine (`app/services/anti_hallucination.py`)**
- Context sufficiency validation
- Confidence scoring
- Citation enforcement
- Fallback decision logic

**Context Builder (`app/services/context_builder.py`)**
- Assembles context from chunks
- Token counting and management
- Prompt construction

**Responsibilities:**
- Business logic orchestration
- Pipeline coordination
- Validation enforcement

### 4. Domain Layer

**Embedder (`app/retrieval/embedder.py`)**
- Multi-provider embedding generation
- Embedding caching
- Batch processing

**Qdrant Client (`app/retrieval/qdrant_client.py`)**
- Vector database operations
- Collection management
- Search and filtering

**Query Rewriter (`app/retrieval/query_rewriter.py`)**
- Query expansion
- Alternative phrasing generation

**Reranker (`app/retrieval/reranker.py`)**
- Cross-encoder re-ranking
- Score normalization

**LLM Providers (`app/llm/`)**
- Abstract LLM interface
- Ollama, OpenAI, Anthropic implementations
- Streaming support

**Parsers (`app/ingestion/parsers/`)**
- PDF parsing (PyMuPDF, pdfplumber)
- Text parsing (encoding detection)
- URL parsing (trafilatura, BeautifulSoup)

**Chunker (`app/ingestion/chunker.py`)**
- Semantic-aware chunking
- Token counting
- Deduplication

**Responsibilities:**
- Core business logic
- Data transformations
- External service integration

### 5. Infrastructure Layer

**Qdrant Vector Database**
- Vector storage and retrieval
- Cosine similarity search
- Metadata filtering

**Ollama LLM**
- Local LLM inference
- Embedding generation
- Model management

**Disk Cache**
- Embedding caching
- Content hash storage

**Logging System**
- Structured JSON logging
- File and console output
- Log rotation

## Data Flow

### Ingestion Pipeline

```
1. Document Upload
   ↓
2. Parser Selection (PDF/TXT/URL)
   ↓
3. Text Extraction & Cleaning
   ↓
4. Semantic Chunking (400 tokens, 75 overlap)
   ↓
5. Metadata Attachment
   ↓
6. Content Hash Computation
   ↓
7. Deduplication Check
   ↓
8. Embedding Generation (with caching)
   ↓
9. Qdrant Storage
   ↓
10. Response with chunk count
```

### Query Pipeline

```
1. User Query
   ↓
2. Query Rewriting (2-3 variations)
   ↓
3. Embedding Generation (per variation)
   ↓
4. Dense Retrieval (top-K from Qdrant)
   ↓
5. Deduplication (by chunk_id)
   ↓
6. Cross-Encoder Re-ranking (top-N)
   ↓
7. Context Assembly (with token limit)
   ↓
8. Anti-Hallucination Checks
   │
   ├─ FAIL → Return Fallback Message
   │
   └─ PASS ↓
9. LLM Generation (with strict prompt)
   ↓
10. Citation Building
   ↓
11. Citation Validation
   ↓
12. Response with confidence score
```

## Design Patterns

### 1. Dependency Injection

```python
# app/api/deps.py
def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

# Usage in routes
@router.post("/query")
async def query(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    return await rag_service.query(request.query)
```

### 2. Strategy Pattern (LLM Providers)

```python
# app/llm/base.py
class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

# Implementations
class OllamaLLM(BaseLLM): ...
class OpenAILLM(BaseLLM): ...
class AnthropicLLM(BaseLLM): ...

# Selection
def _get_llm(provider: str):
    if provider == "ollama":
        return OllamaLLM()
    elif provider == "openai":
        return OpenAILLM()
    ...
```

### 3. Factory Pattern (Parsers)

```python
def get_parser(file_type: str):
    if file_type == ".pdf":
        return PDFParser()
    elif file_type in [".txt", ".md"]:
        return TXTParser()
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
```

### 4. Singleton Pattern (Services)

```python
# Global singleton instances
_rag_service: RAGService | None = None
_qdrant_manager: QdrantManager | None = None
```

### 5. Template Method Pattern (Anti-Hallucination)

```python
class AntiHallucinationEngine:
    def should_return_fallback(self, chunks, tokens, confidence):
        # Template method defining validation steps
        if not self.validate_context(chunks, tokens)[0]:
            return True, "Context insufficient"
        if not self.validate_confidence(confidence)[0]:
            return True, "Confidence too low"
        return False, ""
```

## Configuration Management

**Centralized Configuration (`app/core/config.py`)**

```python
class Settings(BaseSettings):
    # All settings loaded from environment variables
    # Type-safe with Pydantic validation
    # Default values provided
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
```

**Benefits:**
- Single source of truth
- Type safety
- Environment-based configuration
- Easy testing with overrides

## Error Handling Strategy

**Layered Error Handling:**

1. **Domain Layer**: Raises specific exceptions
   ```python
   raise EmbeddingError("Failed to generate embedding")
   ```

2. **Service Layer**: Catches and enriches errors
   ```python
   try:
       embedding = await embedder.embed_text(text)
   except EmbeddingError as e:
       logger.error(f"Embedding failed: {e}")
       raise
   ```

3. **API Layer**: Converts to HTTP responses
   ```python
   @app.exception_handler(RAGException)
   async def handler(request, exc):
       return JSONResponse(
           status_code=500,
           content={"error": type(exc).__name__, "message": exc.message}
       )
   ```

## Security Architecture

### Current Implementation

1. **Input Validation**: Pydantic models
2. **File Type Validation**: Whitelist approach
3. **Content Sanitization**: Text cleaning in parsers
4. **Error Masking**: Detailed errors only in DEBUG mode

### Future Enhancements

1. **Authentication**: JWT tokens
2. **Authorization**: Role-based access control
3. **Rate Limiting**: Per-user quotas
4. **Audit Logging**: All operations logged
5. **Encryption**: At-rest and in-transit

## Scalability Considerations

### Horizontal Scaling

**Stateless Design:**
- No session state in API
- Shared Qdrant database
- Distributed caching (Redis)

**Load Balancing:**
```
                    ┌─────────────┐
                    │Load Balancer│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │FastAPI 1│       │FastAPI 2│       │FastAPI 3│
   └────┬────┘       └────┬────┘       └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Qdrant    │
                    └─────────────┘
```

### Vertical Scaling

**Resource Optimization:**
- Embedding cache reduces computation
- Batch processing for ingestion
- Connection pooling
- Async I/O throughout

### Database Scaling

**Qdrant Optimization:**
- HNSW index for fast search
- Quantization for memory reduction
- Sharding for large collections
- Replication for high availability

## Monitoring Architecture

### Metrics Collection

```python
from prometheus_client import Counter, Histogram

query_counter = Counter('rag_queries_total', 'Total queries')
query_duration = Histogram('rag_query_duration_seconds', 'Query duration')
confidence_gauge = Gauge('rag_confidence_score', 'Confidence scores')
```

### Logging Strategy

**Structured Logging:**
```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "INFO",
  "service": "rag_system",
  "component": "retrieval",
  "message": "Retrieved 5 chunks",
  "context": {
    "query_id": "abc123",
    "confidence": 0.87
  }
}
```

### Health Checks

**Liveness Probe:**
- API responds to /health

**Readiness Probe:**
- Qdrant accessible
- Ollama responsive
- Sufficient resources

## Testing Strategy

### Unit Tests
- Individual component testing
- Mocked dependencies
- Fast execution

### Integration Tests
- Component interaction testing
- Real dependencies (test containers)
- End-to-end flows

### Performance Tests
- Load testing
- Latency measurement
- Resource usage profiling

## Future Architecture Enhancements

1. **Microservices**: Split into ingestion, retrieval, generation services
2. **Event-Driven**: Use message queue for async processing
3. **Multi-Tenancy**: Isolated collections per tenant
4. **Hybrid Search**: Combine dense and sparse retrieval
5. **Active Learning**: Feedback loop for model improvement

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangChain Documentation](https://python.langchain.com/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
