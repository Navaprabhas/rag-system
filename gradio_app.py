"""
Gradio App for RAG System - Hugging Face Spaces Deployment
Standalone demo version for Gradio/Hugging Face Spaces
"""
import gradio as gr

# Custom CSS for better styling
custom_css = """
.gradio-container {
    font-family: 'IBM Plex Sans', sans-serif;
}
.gr-button {
    color: white;
    border-color: #FF4B4B;
    background: #FF4B4B;
}
.gr-button:hover {
    border-color: #FF6B6B;
    background: #FF6B6B;
}
"""

def create_demo():
    with gr.Blocks(css=custom_css, theme=gr.themes.Soft(), title="RAG System") as demo:
        gr.Markdown("""
        # 🔍 Production-Grade RAG System
        ### With Anti-Hallucination Guarantees
        
        [![GitHub](https://img.shields.io/badge/GitHub-Navaprabhas%2Frag--system-blue?logo=github)](https://github.com/Navaprabhas/rag-system)
        [![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://www.python.org/)
        [![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
        """)
        
        with gr.Tabs():
            with gr.Tab("🏠 Overview"):
                gr.Markdown("""
                ## Welcome to the RAG System Demo
                
                This is a **production-grade** Retrieval-Augmented Generation system with strict anti-hallucination guarantees.
                
                ### ✨ Key Features
                
                - **📄 Document Ingestion**: PDF, TXT, and URL parsing with clean text extraction
                - **🔍 Advanced Retrieval**: Query rewriting, dense retrieval, cross-encoder re-ranking
                - **🤖 Multi-Provider LLM**: Ollama (local), OpenAI, Anthropic Claude
                - **🛡️ Anti-Hallucination**: 4-layer validation system ensures accuracy
                - **⚡ Streaming Responses**: Real-time answer generation
                - **📚 Citation Enforcement**: Every answer includes verifiable sources
                
                ### 🏗️ Architecture
                
                ```
                Document Upload → Parser → Chunker → Embedder → Qdrant Vector DB
                                                                        ↓
                User Query → Query Rewriter → Embedder → Search → Reranker
                                                                        ↓
                                            Context Builder → LLM → Answer + Citations
                ```
                
                ### 🛡️ Anti-Hallucination System
                
                The system implements **4 strict validation layers**:
                
                1. **Context Sufficiency Gate**
                   - Rejects if no chunks retrieved
                   - Rejects if max similarity score < 0.35
                   - Rejects if total context tokens < 50
                
                2. **Confidence Scoring**
                   - Computes confidence from top-3 similarity scores
                   - Rejects if confidence < threshold (default 0.4)
                   - Returns confidence score with every response
                
                3. **Citation Enforcement**
                   - Every response must include structured citations
                   - Citations contain source, chunk_id, page, and excerpt
                   - Responses without citations are rejected
                
                4. **No External Knowledge**
                   - System prompt explicitly forbids external knowledge
                   - Fallback: "I don't have enough information from the provided sources"
                """)
            
            with gr.Tab("🚀 Quick Start"):
                gr.Markdown("""
                ## Deploy the Full System
                
                This is a demo page. To run the complete interactive system:
                
                ### Option 1: Docker (Recommended - 10 minutes)
                
                ```bash
                # Clone repository
                git clone https://github.com/Navaprabhas/rag-system.git
                cd rag-system
                
                # Setup and start
                make setup
                make start
                
                # Access
                # Frontend: http://localhost:8501
                # API: http://localhost:8000/docs
                # Qdrant: http://localhost:6333/dashboard
                ```
                
                ### Option 2: Local Development
                
                ```bash
                # Install dependencies
                pip install -r requirements.txt
                
                # Start services
                docker-compose up -d qdrant ollama
                
                # Run backend
                uvicorn app.main:app --reload
                
                # Run frontend (separate terminal)
                streamlit run frontend/app.py
                ```
                
                ### Option 3: Cloud Deployment
                
                See `DEPLOYMENT.md` for:
                - Kubernetes deployment
                - AWS ECS
                - Google Cloud Run
                - Azure Container Instances
                """)
            
            with gr.Tab("📖 API Reference"):
                gr.Markdown("""
                ## API Endpoints
                
                Base URL: `http://localhost:8000/api/v1`
                
                ### Document Ingestion
                
                **Upload File:**
                ```bash
                curl -X POST "http://localhost:8000/api/v1/ingest/file" \\
                  -F "file=@document.pdf"
                ```
                
                **Ingest URL:**
                ```bash
                curl -X POST "http://localhost:8000/api/v1/ingest/url" \\
                  -H "Content-Type: application/json" \\
                  -d '{"source_type": "url", "url": "https://example.com/article"}'
                ```
                
                ### Query System
                
                **Standard Query:**
                ```bash
                curl -X POST "http://localhost:8000/api/v1/query" \\
                  -H "Content-Type: application/json" \\
                  -d '{
                    "query": "What are the main features?",
                    "llm_provider": "ollama",
                    "model_name": "llama3"
                  }'
                ```
                
                **Response Format:**
                ```json
                {
                  "answer": "Based on the provided documents...",
                  "citations": [
                    {
                      "source": "document.pdf",
                      "chunk_id": "doc_5",
                      "page": 3,
                      "excerpt": "First 120 chars...",
                      "score": 0.89
                    }
                  ],
                  "confidence": 0.87,
                  "retrieval_count": 5,
                  "query_rewritten": "main features | key capabilities",
                  "llm_provider": "ollama",
                  "model": "llama3"
                }
                ```
                
                **Streaming Query:**
                ```bash
                curl -N "http://localhost:8000/api/v1/query/stream?query=What+is+AI"
                ```
                
                ### Document Management
                
                **List Documents:**
                ```bash
                curl "http://localhost:8000/api/v1/documents"
                ```
                
                **Delete Document:**
                ```bash
                curl -X DELETE "http://localhost:8000/api/v1/documents/filename.pdf"
                ```
                """)
            
            with gr.Tab("🔧 Technology Stack"):
                gr.Markdown("""
                ## Technology Stack
                
                ### Backend
                - **Framework**: FastAPI 0.109.0 (Python 3.11+)
                - **Validation**: Pydantic v2
                - **Async**: Full async/await support
                
                ### Vector Database
                - **Database**: Qdrant (latest)
                - **Distance**: Cosine similarity
                - **Features**: Metadata filtering, HNSW indexing
                
                ### Embeddings
                - **Default**: Ollama (nomic-embed-text, 768-dim)
                - **Optional**: OpenAI (text-embedding-3-small), Cohere
                - **Caching**: Disk-based with content hashing
                
                ### LLMs
                - **Local**: Ollama (llama3, mistral, phi3)
                - **Cloud**: OpenAI (GPT-4o), Anthropic (Claude 3)
                - **Streaming**: SSE support for all providers
                
                ### Document Processing
                - **PDF**: PyMuPDF 1.23.8, pdfplumber 0.10.3
                - **Web**: trafilatura 1.6.3, BeautifulSoup4 4.12.3
                - **Chunking**: LangChain RecursiveCharacterTextSplitter
                - **Tokens**: tiktoken for accurate counting
                
                ### Re-ranking
                - **Model**: sentence-transformers cross-encoder
                - **Specific**: cross-encoder/ms-marco-MiniLM-L-6-v2
                
                ### Frontend
                - **UI**: Streamlit 1.30.0
                - **Demo**: Gradio (this app)
                
                ### Deployment
                - **Containers**: Docker, Docker Compose
                - **Orchestration**: Kubernetes manifests included
                - **Cloud**: AWS, GCP, Azure guides provided
                """)
            
            with gr.Tab("📊 Performance"):
                gr.Markdown("""
                ## Performance Characteristics
                
                ### Latency
                - **Query (no cache)**: 3-8 seconds
                - **Query (cached embeddings)**: 2-5 seconds
                - **Ingestion (10-page PDF)**: 5-15 seconds
                - **Streaming start**: < 2 seconds
                
                ### Throughput
                - **Queries**: 10-20 per minute (single instance)
                - **Ingestion**: 5-10 documents per minute
                - **Concurrent users**: 10-20 (single instance)
                
                ### Resource Usage
                - **Memory**: 2-4GB (base), 6-8GB (with models)
                - **CPU**: 2-4 cores recommended
                - **Disk**: 10GB+ for models and cache
                
                ### Scalability
                - **Horizontal**: Stateless design, can scale to multiple instances
                - **Vertical**: Efficient async I/O, supports 100+ concurrent requests
                - **Database**: Qdrant handles millions of vectors
                
                ### Optimization Tips
                1. Enable embedding cache (reduces computation by 70%)
                2. Use smaller models for faster responses (phi3 vs llama3)
                3. Adjust chunk size based on document type
                4. Implement Redis for distributed caching
                5. Use connection pooling for database
                """)
            
            with gr.Tab("📚 Documentation"):
                gr.Markdown("""
                ## Complete Documentation
                
                ### User Guides
                - **[README.md](https://github.com/Navaprabhas/rag-system/blob/main/README.md)** - Complete setup and usage guide
                - **[QUICK_REFERENCE.md](https://github.com/Navaprabhas/rag-system/blob/main/QUICK_REFERENCE.md)** - Command cheat sheet
                - **[API.md](https://github.com/Navaprabhas/rag-system/blob/main/API.md)** - Full API documentation
                
                ### Technical Documentation
                - **[ARCHITECTURE.md](https://github.com/Navaprabhas/rag-system/blob/main/ARCHITECTURE.md)** - System architecture and design patterns
                - **[STRUCTURE.md](https://github.com/Navaprabhas/rag-system/blob/main/STRUCTURE.md)** - File structure explanation
                - **[DEPLOYMENT.md](https://github.com/Navaprabhas/rag-system/blob/main/DEPLOYMENT.md)** - Production deployment guide
                
                ### Project Management
                - **[PROJECT_SUMMARY.md](https://github.com/Navaprabhas/rag-system/blob/main/PROJECT_SUMMARY.md)** - Executive summary
                - **[COMPLETION_STATUS.md](https://github.com/Navaprabhas/rag-system/blob/main/COMPLETION_STATUS.md)** - Progress tracking
                - **[CHECKLIST.md](https://github.com/Navaprabhas/rag-system/blob/main/CHECKLIST.md)** - Deployment checklist
                
                ### Total Documentation
                - **9 comprehensive guides**
                - **500+ pages** of documentation
                - **Complete API reference** with examples
                - **Architecture diagrams** and explanations
                - **Deployment guides** for multiple platforms
                """)
            
            with gr.Tab("🔗 Links & Contact"):
                gr.Markdown("""
                ## Links
                
                ### Repository
                - **GitHub**: [https://github.com/Navaprabhas/rag-system](https://github.com/Navaprabhas/rag-system)
                - **Clone**: `git clone https://github.com/Navaprabhas/rag-system.git`
                
                ### Live Demos
                - **Gradio**: This app (Hugging Face Spaces)
                - **Streamlit**: [Deploy your own](https://share.streamlit.io/)
                
                ### Documentation
                - **Main Docs**: [README.md](https://github.com/Navaprabhas/rag-system#readme)
                - **API Reference**: [API.md](https://github.com/Navaprabhas/rag-system/blob/main/API.md)
                - **Architecture**: [ARCHITECTURE.md](https://github.com/Navaprabhas/rag-system/blob/main/ARCHITECTURE.md)
                
                ### Contact
                - **GitHub**: [@Navaprabhas](https://github.com/Navaprabhas)
                - **Issues**: [GitHub Issues](https://github.com/Navaprabhas/rag-system/issues)
                
                ### Support
                For questions or support:
                1. Check the documentation
                2. Search existing GitHub issues
                3. Open a new issue with details
                
                ### Contributing
                Contributions are welcome! Please:
                1. Fork the repository
                2. Create a feature branch
                3. Make your changes with tests
                4. Submit a pull request
                """)
        
        gr.Markdown("""
        ---
        
        ## 🚀 Ready to Deploy?
        
        ### Quick Start (10 minutes)
        ```bash
        git clone https://github.com/Navaprabhas/rag-system.git
        cd rag-system
        make setup && make start
        ```
        
        **Access:**
        - Frontend: http://localhost:8501
        - API: http://localhost:8000/docs
        - Qdrant: http://localhost:6333/dashboard
        
        ---
        
        <div style='text-align: center; color: gray;'>
            <p><strong>RAG System v1.0.0</strong> | Production-grade with Anti-Hallucination Guarantees</p>
            <p>Built with ❤️ by <a href='https://github.com/Navaprabhas'>Navaprabhas</a></p>
            <p>⭐ Star on <a href='https://github.com/Navaprabhas/rag-system'>GitHub</a> if you find this useful!</p>
        </div>
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_demo()
    demo.launch(
        share=False,
        show_error=True,
        server_name="0.0.0.0",
        server_port=7860
    )
