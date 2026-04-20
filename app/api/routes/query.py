"""
Query endpoints for RAG system.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.models.request import QueryRequest
from app.models.response import RAGResponse
from app.services.rag_service import RAGService
from app.api.deps import get_rag_service
from app.core.logging import logger

router = APIRouter()


@router.post("/query", response_model=RAGResponse)
async def query(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> RAGResponse:
    """
    Query the RAG system.
    
    Args:
        request: Query request with user question
        rag_service: RAG service instance
        
    Returns:
        RAG response with answer and citations
    """
    logger.info(f"Received query: {request.query[:100]}")
    
    response = await rag_service.query(
        query=request.query,
        llm_provider=request.llm_provider,
        model_name=request.model_name,
        top_k=request.top_k,
        rerank_top_n=request.rerank_top_n,
        filters=request.filters
    )
    
    return response


@router.get("/query/stream")
async def query_stream(
    query: str,
    llm_provider: str | None = None,
    model_name: str | None = None,
    top_k: int | None = None,
    rerank_top_n: int | None = None,
    rag_service: RAGService = Depends(get_rag_service)
) -> StreamingResponse:
    """
    Query the RAG system with streaming response.
    
    Args:
        query: User query
        llm_provider: Optional LLM provider
        model_name: Optional model name
        top_k: Number of chunks to retrieve
        rerank_top_n: Number of chunks after reranking
        rag_service: RAG service instance
        
    Returns:
        Streaming response with SSE
    """
    logger.info(f"Received streaming query: {query[:100]}")
    
    async def generate():
        async for chunk in rag_service.query_stream(
            query=query,
            llm_provider=llm_provider,
            model_name=model_name,
            top_k=top_k,
            rerank_top_n=rerank_top_n
        ):
            yield chunk
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
