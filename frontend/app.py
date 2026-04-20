"""
Streamlit frontend for RAG system.
"""
import os
import json
from typing import Any

import streamlit as st
import httpx
import asyncio

# Configuration
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
API_BASE = f"{FASTAPI_URL}/api/v1"


# Page configuration
st.set_page_config(
    page_title="RAG System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "documents" not in st.session_state:
        st.session_state.documents = []


async def upload_file(file) -> dict[str, Any]:
    """Upload file to backend."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = await client.post(f"{API_BASE}/ingest/file", files=files)
        response.raise_for_status()
        return response.json()


async def ingest_url(url: str) -> dict[str, Any]:
    """Ingest URL."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{API_BASE}/ingest/url",
            json={"source_type": "url", "url": url}
        )
        response.raise_for_status()
        return response.json()


async def query_rag(
    query: str,
    llm_provider: str,
    model_name: str | None = None
) -> dict[str, Any]:
    """Query RAG system."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload = {
            "query": query,
            "llm_provider": llm_provider,
            "stream": False
        }
        if model_name:
            payload["model_name"] = model_name
        
        response = await client.post(f"{API_BASE}/query", json=payload)
        response.raise_for_status()
        return response.json()


async def list_documents() -> list[dict[str, Any]]:
    """List all documents."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{API_BASE}/documents")
        response.raise_for_status()
        data = response.json()
        return data.get("documents", [])


async def delete_document(filename: str):
    """Delete a document."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(f"{API_BASE}/documents/{filename}")
        response.raise_for_status()
        return response.json()


def render_sidebar():
    """Render sidebar with document management."""
    st.sidebar.title("📚 Document Management")
    
    # File upload
    st.sidebar.subheader("Upload Document")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "md"],
        help="Upload PDF or text files"
    )
    
    if uploaded_file and st.sidebar.button("Upload File"):
        with st.spinner("Uploading and processing..."):
            try:
                result = asyncio.run(upload_file(uploaded_file))
                st.sidebar.success(
                    f"✅ Uploaded: {result['filename']}\n"
                    f"Chunks created: {result['chunks_created']}"
                )
                # Refresh documents list
                st.session_state.documents = asyncio.run(list_documents())
            except Exception as e:
                st.sidebar.error(f"❌ Upload failed: {str(e)}")
    
    # URL ingestion
    st.sidebar.subheader("Ingest from URL")
    url_input = st.sidebar.text_input("Enter URL", placeholder="https://example.com/article")
    
    if url_input and st.sidebar.button("Ingest URL"):
        with st.spinner("Fetching and processing..."):
            try:
                result = asyncio.run(ingest_url(url_input))
                st.sidebar.success(
                    f"✅ Ingested: {result['filename']}\n"
                    f"Chunks created: {result['chunks_created']}"
                )
                # Refresh documents list
                st.session_state.documents = asyncio.run(list_documents())
            except Exception as e:
                st.sidebar.error(f"❌ Ingestion failed: {str(e)}")
    
    # Document list
    st.sidebar.subheader("Ingested Documents")
    
    if st.sidebar.button("🔄 Refresh List"):
        st.session_state.documents = asyncio.run(list_documents())
    
    if st.session_state.documents:
        for doc in st.session_state.documents:
            with st.sidebar.expander(f"📄 {doc['filename']}"):
                st.write(f"**Type:** {doc['file_type']}")
                st.write(f"**Chunks:** {doc['chunk_count']}")
                st.write(f"**Ingested:** {doc['ingestion_timestamp'][:19]}")
                
                if st.button(f"🗑️ Delete", key=f"del_{doc['filename']}"):
                    try:
                        asyncio.run(delete_document(doc['filename']))
                        st.success(f"Deleted: {doc['filename']}")
                        st.session_state.documents = asyncio.run(list_documents())
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {str(e)}")
    else:
        st.sidebar.info("No documents ingested yet")
    
    # LLM Configuration
    st.sidebar.divider()
    st.sidebar.subheader("⚙️ LLM Configuration")
    
    llm_provider = st.sidebar.selectbox(
        "Provider",
        ["ollama", "openai", "anthropic"],
        help="Select LLM provider"
    )
    
    model_options = {
        "ollama": ["llama3", "mistral", "phi3"],
        "openai": ["gpt-4o-mini", "gpt-4o"],
        "anthropic": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229"]
    }
    
    model_name = st.sidebar.selectbox(
        "Model",
        model_options[llm_provider],
        help="Select model"
    )
    
    return llm_provider, model_name


def render_chat_interface(llm_provider: str, model_name: str):
    """Render main chat interface."""
    st.title("🔍 RAG System - Document Q&A")
    st.markdown("Ask questions about your ingested documents")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display citations if available
            if message["role"] == "assistant" and "citations" in message:
                with st.expander("📚 Citations"):
                    for i, citation in enumerate(message["citations"], 1):
                        st.markdown(f"**[{i}] {citation['source']}**")
                        if citation.get("page"):
                            st.markdown(f"*Page {citation['page']}*")
                        st.markdown(f"> {citation['excerpt']}")
                        st.markdown(f"*Relevance: {citation['score']:.2%}*")
                        st.divider()
                
                # Display metadata
                if "metadata" in message:
                    with st.expander("ℹ️ Response Metadata"):
                        meta = message["metadata"]
                        
                        # Confidence score with color
                        confidence = meta.get("confidence", 0.0)
                        if confidence >= 0.7:
                            color = "green"
                        elif confidence >= 0.4:
                            color = "orange"
                        else:
                            color = "red"
                        
                        st.markdown(f"**Confidence:** :{color}[{confidence:.1%}]")
                        st.progress(confidence)
                        
                        st.markdown(f"**Chunks Retrieved:** {meta.get('retrieval_count', 0)}")
                        st.markdown(f"**LLM:** {meta.get('llm_provider', 'N/A')} / {meta.get('model', 'N/A')}")
                        
                        if meta.get("query_rewritten"):
                            st.info(f"**Query Expansion:** {meta['query_rewritten']}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = asyncio.run(query_rag(prompt, llm_provider, model_name))
                    
                    # Display answer
                    st.markdown(response["answer"])
                    
                    # Store message with metadata
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "citations": response.get("citations", []),
                        "metadata": {
                            "confidence": response.get("confidence", 0.0),
                            "retrieval_count": response.get("retrieval_count", 0),
                            "llm_provider": response.get("llm_provider", ""),
                            "model": response.get("model", ""),
                            "query_rewritten": response.get("query_rewritten", "")
                        }
                    })
                    
                    # Display citations
                    if response.get("citations"):
                        with st.expander("📚 Citations"):
                            for i, citation in enumerate(response["citations"], 1):
                                st.markdown(f"**[{i}] {citation['source']}**")
                                if citation.get("page"):
                                    st.markdown(f"*Page {citation['page']}*")
                                st.markdown(f"> {citation['excerpt']}")
                                st.markdown(f"*Relevance: {citation['score']:.2%}*")
                                st.divider()
                    
                    # Display metadata
                    with st.expander("ℹ️ Response Metadata"):
                        confidence = response.get("confidence", 0.0)
                        if confidence >= 0.7:
                            color = "green"
                        elif confidence >= 0.4:
                            color = "orange"
                        else:
                            color = "red"
                        
                        st.markdown(f"**Confidence:** :{color}[{confidence:.1%}]")
                        st.progress(confidence)
                        
                        st.markdown(f"**Chunks Retrieved:** {response.get('retrieval_count', 0)}")
                        st.markdown(f"**LLM:** {response.get('llm_provider', 'N/A')} / {response.get('model', 'N/A')}")
                        
                        if response.get("query_rewritten"):
                            st.info(f"**Query Expansion:** {response['query_rewritten']}")
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


def main():
    """Main application."""
    init_session_state()
    
    # Load documents on first run
    if not st.session_state.documents:
        try:
            st.session_state.documents = asyncio.run(list_documents())
        except Exception as e:
            st.error(f"Failed to connect to backend: {str(e)}")
    
    # Render UI
    llm_provider, model_name = render_sidebar()
    render_chat_interface(llm_provider, model_name)
    
    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "RAG System v1.0.0 | Production-grade with Anti-Hallucination Guarantees"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
