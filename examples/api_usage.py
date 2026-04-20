"""
Example script demonstrating RAG System API usage.
"""
import asyncio
import httpx
from pathlib import Path


API_BASE = "http://localhost:8000/api/v1"


async def check_health():
    """Check system health."""
    print("🔍 Checking system health...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/health")
        data = response.json()
        
        print(f"Status: {data['status']}")
        print(f"Services: {data['services']}")
        print()


async def ingest_text():
    """Ingest plain text."""
    print("📝 Ingesting text content...")
    
    text_content = """
    Artificial Intelligence (AI) is transforming the world. 
    Machine learning, a subset of AI, enables computers to learn from data.
    Deep learning uses neural networks with multiple layers.
    Natural Language Processing (NLP) helps computers understand human language.
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE}/ingest/text",
            json={
                "source_type": "text",
                "content": text_content,
                "filename": "ai_basics.txt",
                "metadata": {
                    "category": "education",
                    "topic": "artificial intelligence"
                }
            }
        )
        data = response.json()
        
        print(f"✅ Ingested: {data['filename']}")
        print(f"Chunks created: {data['chunks_created']}")
        print(f"Document ID: {data['document_id']}")
        print()


async def ingest_url():
    """Ingest content from URL."""
    print("🌐 Ingesting from URL...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{API_BASE}/ingest/url",
            json={
                "source_type": "url",
                "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "metadata": {
                    "source": "wikipedia"
                }
            }
        )
        data = response.json()
        
        print(f"✅ Ingested: {data['filename']}")
        print(f"Chunks created: {data['chunks_created']}")
        print()


async def list_documents():
    """List all ingested documents."""
    print("📚 Listing documents...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/documents")
        data = response.json()
        
        print(f"Total documents: {data['total_count']}")
        for doc in data['documents']:
            print(f"  - {doc['filename']} ({doc['file_type']}, {doc['chunk_count']} chunks)")
        print()


async def query_basic():
    """Perform basic query."""
    print("❓ Querying: What is machine learning?")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{API_BASE}/query",
            json={
                "query": "What is machine learning?",
                "llm_provider": "ollama",
                "model_name": "llama3",
                "top_k": 5,
                "rerank_top_n": 3
            }
        )
        data = response.json()
        
        print(f"\n📖 Answer:")
        print(data['answer'])
        print(f"\n📊 Metadata:")
        print(f"  Confidence: {data['confidence']:.2%}")
        print(f"  Chunks retrieved: {data['retrieval_count']}")
        print(f"  LLM: {data['llm_provider']} / {data['model']}")
        
        if data['citations']:
            print(f"\n📚 Citations ({len(data['citations'])}):")
            for i, citation in enumerate(data['citations'], 1):
                print(f"  [{i}] {citation['source']}")
                print(f"      {citation['excerpt']}")
                print(f"      Score: {citation['score']:.2%}")
        print()


async def query_with_filters():
    """Query with metadata filters."""
    print("❓ Querying with filters...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{API_BASE}/query",
            json={
                "query": "Explain deep learning",
                "filters": {
                    "category": "education"
                },
                "top_k": 5
            }
        )
        data = response.json()
        
        print(f"\n📖 Answer:")
        print(data['answer'])
        print(f"\n📊 Confidence: {data['confidence']:.2%}")
        print()


async def query_streaming():
    """Query with streaming response."""
    print("❓ Streaming query: What is NLP?")
    print("\n📖 Answer (streaming):")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "GET",
            f"{API_BASE}/query/stream",
            params={"query": "What is Natural Language Processing?"}
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    import json
                    data = json.loads(line[6:])
                    
                    if data["type"] == "answer":
                        print(data["content"], end="", flush=True)
                    elif data["type"] == "metadata":
                        print(f"\n\n📊 Confidence: {data['confidence']:.2%}")
                    elif data["type"] == "citations":
                        print(f"\n\n📚 Citations: {len(data['citations'])}")
    print("\n")


async def delete_document():
    """Delete a document."""
    print("🗑️  Deleting document...")
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{API_BASE}/documents/ai_basics.txt")
        data = response.json()
        
        print(f"✅ {data['message']}")
        print()


async def main():
    """Run all examples."""
    print("=" * 60)
    print("RAG System API Usage Examples")
    print("=" * 60)
    print()
    
    try:
        # Check health
        await check_health()
        
        # Ingest documents
        await ingest_text()
        # await ingest_url()  # Uncomment to test URL ingestion
        
        # List documents
        await list_documents()
        
        # Query examples
        await query_basic()
        await query_with_filters()
        # await query_streaming()  # Uncomment to test streaming
        
        # Cleanup
        # await delete_document()  # Uncomment to test deletion
        
        print("=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except httpx.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
