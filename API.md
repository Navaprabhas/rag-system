# API Documentation

Complete API reference for the RAG System.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API is open. For production, implement JWT authentication (see DEPLOYMENT.md).

## Endpoints

### Health Check

#### GET /health

Check system health and service status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "qdrant": "healthy"
  }
}
```

---

### Document Ingestion

#### POST /ingest/file

Upload and ingest a document file.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field

**Supported formats:** PDF, TXT, MD

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/file" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "status": "success",
  "document_id": "abc123def456",
  "chunks_created": 42,
  "filename": "document.pdf",
  "file_type": "pdf",
  "metadata": {
    "page_count": 10,
    "title": "Document Title",
    "author": "John Doe",
    "file_hash": "sha256hash..."
  }
}
```

**Status Codes:**
- 200: Success
- 400: Invalid file type or duplicate content
- 500: Processing error

---

#### POST /ingest/url

Ingest content from a web URL.

**Request:**
```json
{
  "source_type": "url",
  "url": "https://example.com/article",
  "metadata": {
    "category": "news",
    "author": "Jane Doe"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "document_id": "xyz789",
  "chunks_created": 15,
  "filename": "example.com",
  "file_type": "url",
  "metadata": {
    "title": "Article Title",
    "domain": "example.com",
    "url": "https://example.com/article",
    "content_hash": "sha256hash..."
  }
}
```

**Status Codes:**
- 200: Success
- 400: Invalid URL or duplicate content
- 500: Fetch or processing error

---

#### POST /ingest/text

Ingest plain text content directly.

**Request:**
```json
{
  "source_type": "text",
  "content": "Your text content here...",
  "filename": "my_notes.txt",
  "metadata": {
    "category": "notes",
    "tags": ["important", "review"]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "document_id": "text123",
  "chunks_created": 8,
  "filename": "my_notes.txt",
  "file_type": "text",
  "metadata": {
    "category": "notes",
    "tags": ["important", "review"]
  }
}
```

---

### Query

#### POST /query

Query the RAG system with anti-hallucination guarantees.

**Request:**
```json
{
  "query": "What are the main features of the product?",
  "llm_provider": "ollama",
  "model_name": "llama3",
  "top_k": 10,
  "rerank_top_n": 5,
  "filters": {
    "category": "product_docs"
  },
  "stream": false
}
```

**Parameters:**
- `query` (required): User question (1-1000 characters)
- `llm_provider` (optional): "ollama", "openai", or "anthropic"
- `model_name` (optional): Specific model name
- `top_k` (optional): Number of chunks to retrieve (1-50, default: 10)
- `rerank_top_n` (optional): Chunks after reranking (1-20, default: 5)
- `filters` (optional): Metadata filters for retrieval
- `stream` (optional): Enable streaming (default: false)

**Response:**
```json
{
  "answer": "Based on the provided documents, the main features include: 1) Advanced analytics dashboard, 2) Real-time collaboration, 3) API integration capabilities...",
  "citations": [
    {
      "source": "product_guide.pdf",
      "chunk_id": "product_guide.pdf_5",
      "page": 3,
      "excerpt": "The product offers advanced features such as real-time analytics, collaborative workspaces, and seamless API integration...",
      "score": 0.89
    },
    {
      "source": "features.txt",
      "chunk_id": "features.txt_2",
      "page": null,
      "excerpt": "Key capabilities: dashboard customization, team collaboration tools, third-party integrations...",
      "score": 0.85
    }
  ],
  "confidence": 0.87,
  "retrieval_count": 5,
  "query_rewritten": "main features | key capabilities | primary functions",
  "llm_provider": "ollama",
  "model": "llama3"
}
```

**Fallback Response (insufficient context):**
```json
{
  "answer": "I don't have enough information from the provided sources",
  "citations": [],
  "confidence": 0.25,
  "retrieval_count": 2,
  "query_rewritten": "...",
  "llm_provider": "ollama",
  "model": "llama3"
}
```

**Status Codes:**
- 200: Success (including fallback responses)
- 400: Invalid request parameters
- 500: Processing error

---

#### GET /query/stream

Query with streaming response using Server-Sent Events (SSE).

**Request:**
```
GET /query/stream?query=What+are+the+features&llm_provider=ollama&top_k=10
```

**Parameters:** Same as POST /query (via query string)

**Response:** Server-Sent Events stream

```
data: {"type":"metadata","confidence":0.87,"retrieval_count":5,"query_rewritten":"..."}

data: {"type":"answer","content":"Based"}

data: {"type":"answer","content":" on"}

data: {"type":"answer","content":" the"}

data: {"type":"answer","content":" documents"}

...

data: {"type":"citations","citations":[{"source":"doc.pdf","chunk_id":"c1",...}]}
```

**Event Types:**
- `metadata`: Query metadata (sent first)
- `answer`: Answer text chunks (streamed)
- `citations`: Citation list (sent last)

**Example (Python):**
```python
import httpx

async with httpx.AsyncClient() as client:
    async with client.stream(
        "GET",
        "http://localhost:8000/api/v1/query/stream",
        params={"query": "What is AI?"}
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                if data["type"] == "answer":
                    print(data["content"], end="")
```

---

### Document Management

#### GET /documents

List all ingested documents.

**Response:**
```json
{
  "documents": [
    {
      "document_id": "product_guide.pdf",
      "filename": "product_guide.pdf",
      "file_type": "pdf",
      "chunk_count": 42,
      "ingestion_timestamp": "2024-01-15T10:30:45",
      "metadata": {}
    },
    {
      "document_id": "features.txt",
      "filename": "features.txt",
      "file_type": "txt",
      "chunk_count": 15,
      "ingestion_timestamp": "2024-01-15T11:20:30",
      "metadata": {}
    }
  ],
  "total_count": 2
}
```

---

#### DELETE /documents/{filename}

Delete a document and all its chunks.

**Request:**
```
DELETE /documents/product_guide.pdf
```

**Response:**
```json
{
  "status": "success",
  "message": "Document 'product_guide.pdf' deleted successfully"
}
```

**Status Codes:**
- 200: Success
- 404: Document not found
- 500: Deletion error

---

## Response Models

### RAGResponse

```typescript
{
  answer: string;              // Generated answer
  citations: CitationItem[];   // Supporting citations
  confidence: number;          // 0.0-1.0
  retrieval_count: number;     // Chunks retrieved
  query_rewritten: string;     // Expanded query
  llm_provider: string;        // Provider used
  model: string;               // Model used
}
```

### CitationItem

```typescript
{
  source: string;      // Filename or URL
  chunk_id: string;    // Unique chunk identifier
  page: number | null; // Page number (if applicable)
  excerpt: string;     // First 120 chars
  score: number;       // Relevance score (0.0-1.0)
}
```

### IngestResponse

```typescript
{
  status: string;           // "success"
  document_id: string;      // Unique document ID
  chunks_created: number;   // Number of chunks
  filename: string;         // Document filename
  file_type: string;        // File type
  metadata: object;         // Document metadata
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": {
    "additional": "context"
  }
}
```

### Common Errors

**400 Bad Request:**
```json
{
  "error": "ValidationError",
  "message": "Invalid request parameters",
  "details": {
    "field": "query",
    "issue": "Query must be between 1 and 1000 characters"
  }
}
```

**500 Internal Server Error:**
```json
{
  "error": "InternalServerError",
  "message": "An unexpected error occurred",
  "details": null
}
```

---

## Rate Limits

Default limits (configurable):
- 100 requests per minute per IP
- 1000 requests per hour per IP

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642345678
```

---

## Best Practices

### 1. Query Optimization

**Good:**
```json
{
  "query": "What are the security features?",
  "top_k": 10,
  "rerank_top_n": 5
}
```

**Better:**
```json
{
  "query": "What are the security features?",
  "top_k": 15,
  "rerank_top_n": 5,
  "filters": {
    "category": "security"
  }
}
```

### 2. Handling Low Confidence

Always check the confidence score:

```python
response = await query_rag(query)

if response["confidence"] < 0.5:
    print("⚠️ Low confidence answer")
    print("Consider:")
    print("- Ingesting more relevant documents")
    print("- Rephrasing your question")
    print("- Checking if documents contain the information")
```

### 3. Citation Usage

Always display citations to users:

```python
for i, citation in enumerate(response["citations"], 1):
    print(f"[{i}] {citation['source']} (page {citation['page']})")
    print(f"    {citation['excerpt']}")
    print(f"    Relevance: {citation['score']:.0%}")
```

### 4. Error Handling

```python
try:
    response = await client.post("/api/v1/query", json=request)
    response.raise_for_status()
    data = response.json()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 400:
        print("Invalid request:", e.response.json()["message"])
    elif e.response.status_code == 500:
        print("Server error, please try again")
except httpx.RequestError as e:
    print("Connection error:", str(e))
```

---

## SDK Examples

### Python

```python
import httpx
import asyncio

class RAGClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def query(self, query: str, **kwargs):
        response = await self.client.post(
            f"{self.base_url}/query",
            json={"query": query, **kwargs}
        )
        response.raise_for_status()
        return response.json()
    
    async def ingest_file(self, file_path: str):
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = await self.client.post(
                f"{self.base_url}/ingest/file",
                files=files
            )
        response.raise_for_status()
        return response.json()

# Usage
client = RAGClient()
result = await client.query("What is AI?")
print(result["answer"])
```

### JavaScript

```javascript
class RAGClient {
  constructor(baseUrl = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl;
  }

  async query(query, options = {}) {
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, ...options })
    });
    
    if (!response.ok) throw new Error('Query failed');
    return await response.json();
  }

  async ingestFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.baseUrl}/ingest/file`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) throw new Error('Ingestion failed');
    return await response.json();
  }
}

// Usage
const client = new RAGClient();
const result = await client.query('What is AI?');
console.log(result.answer);
```

---

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Document ingestion (PDF, TXT, URL)
- RAG query with anti-hallucination
- Streaming responses
- Multi-provider LLM support

---

## Support

- Documentation: http://localhost:8000/docs
- GitHub: [repository-url]
- Email: support@example.com
