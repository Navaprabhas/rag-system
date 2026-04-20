"""
Health check endpoint.
"""
from fastapi import APIRouter, Depends

from app.models.response import HealthResponse
from app.api.deps import get_qdrant_manager
from app.retrieval.qdrant_client import QdrantManager
from app.core.logging import logger

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    qdrant: QdrantManager = Depends(get_qdrant_manager)
) -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        Health status of the service and dependencies
    """
    services = {}
    
    # Check Qdrant
    try:
        collections = qdrant.client.get_collections()
        services["qdrant"] = "healthy"
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        services["qdrant"] = "unhealthy"
    
    # Overall status
    overall_status = "healthy" if all(
        s == "healthy" for s in services.values()
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        services=services
    )
