"""
Qdrant vector database client for document storage and retrieval.
"""
from typing import Any
from datetime import datetime

from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings
from app.core.exceptions import RetrievalError
from app.core.logging import logger


class QdrantManager:
    """Manage Qdrant vector database operations."""
    
    def __init__(self):
        """Initialize Qdrant client and ensure collection exists."""
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        self.collection_name = settings.qdrant_collection
        self.vector_size = settings.get_embedding_dimension()
        
        self._ensure_collection()
        logger.info(f"Initialized Qdrant: collection={self.collection_name}")
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                
                # Create payload index for filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="source",
                    field_schema=models.PayloadSchemaType.KEYWORD
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="file_type",
                    field_schema=models.PayloadSchemaType.KEYWORD
                )
                
        except Exception as e:
            raise RetrievalError(
                f"Failed to ensure collection: {str(e)}",
                details={"collection": self.collection_name}
            )
    
    async def upsert_chunks(
        self,
        chunks: list[dict[str, Any]],
        embeddings: list[list[float]]
    ) -> int:
        """
        Insert or update chunks in Qdrant.
        
        Args:
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors
            
        Returns:
            Number of chunks upserted
            
        Raises:
            RetrievalError: If upsert fails
        """
        try:
            points = []
            
            for chunk, embedding in zip(chunks, embeddings):
                point = models.PointStruct(
                    id=hash(chunk["chunk_id"]) % (2**63),  # Convert to valid ID
                    vector=embedding,
                    payload={
                        "chunk_id": chunk["chunk_id"],
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "source_url": chunk.get("source_url", ""),
                        "file_type": chunk["file_type"],
                        "page_number": chunk.get("page_number"),
                        "chunk_index": chunk["chunk_index"],
                        "content_hash": chunk["content_hash"],
                        "ingestion_timestamp": chunk["ingestion_timestamp"],
                        "token_count": chunk["token_count"]
                    }
                )
                points.append(point)
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
            
            logger.info(f"Upserted {len(points)} chunks to Qdrant")
            return len(points)
            
        except Exception as e:
            raise RetrievalError(
                f"Failed to upsert chunks: {str(e)}",
                details={"chunk_count": len(chunks)}
            )
    
    async def search(
        self,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        """
        Search for similar chunks.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of search results with scores
            
        Raises:
            RetrievalError: If search fails
        """
        try:
            # Build filter conditions
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )
                if conditions:
                    query_filter = models.Filter(must=conditions)
            
            # Perform search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=query_filter
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "chunk_id": result.payload["chunk_id"],
                    "text": result.payload["text"],
                    "source": result.payload["source"],
                    "source_url": result.payload.get("source_url", ""),
                    "file_type": result.payload["file_type"],
                    "page_number": result.payload.get("page_number"),
                    "score": result.score,
                    "chunk_index": result.payload["chunk_index"]
                })
            
            logger.info(f"Retrieved {len(formatted_results)} chunks from Qdrant")
            return formatted_results
            
        except Exception as e:
            raise RetrievalError(
                f"Failed to search: {str(e)}",
                details={"top_k": top_k}
            )
    
    async def get_existing_hashes(self) -> set[str]:
        """
        Get all existing content hashes for deduplication.
        
        Returns:
            Set of content hashes
        """
        try:
            # Scroll through all points to get hashes
            hashes = set()
            offset = None
            
            while True:
                results, offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=100,
                    offset=offset,
                    with_payload=["content_hash"],
                    with_vectors=False
                )
                
                for point in results:
                    if "content_hash" in point.payload:
                        hashes.add(point.payload["content_hash"])
                
                if offset is None:
                    break
            
            logger.info(f"Retrieved {len(hashes)} existing hashes")
            return hashes
            
        except Exception as e:
            logger.warning(f"Failed to get existing hashes: {e}")
            return set()
    
    async def list_documents(self) -> list[dict[str, Any]]:
        """
        List all unique documents in the collection.
        
        Returns:
            List of document information
        """
        try:
            documents = {}
            offset = None
            
            while True:
                results, offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                
                for point in results:
                    source = point.payload.get("source", "")
                    if source and source not in documents:
                        documents[source] = {
                            "filename": source,
                            "file_type": point.payload.get("file_type", ""),
                            "source_url": point.payload.get("source_url", ""),
                            "ingestion_timestamp": point.payload.get("ingestion_timestamp", ""),
                            "chunk_count": 0
                        }
                    
                    if source:
                        documents[source]["chunk_count"] += 1
                
                if offset is None:
                    break
            
            return list(documents.values())
            
        except Exception as e:
            raise RetrievalError(f"Failed to list documents: {str(e)}")
    
    async def delete_document(self, filename: str) -> int:
        """
        Delete all chunks for a document.
        
        Args:
            filename: Document filename to delete
            
        Returns:
            Number of chunks deleted
        """
        try:
            # Delete points matching the filename
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="source",
                                match=models.MatchValue(value=filename)
                            )
                        ]
                    )
                )
            )
            
            logger.info(f"Deleted document: {filename}")
            return 1  # Return success
            
        except Exception as e:
            raise RetrievalError(
                f"Failed to delete document: {str(e)}",
                details={"filename": filename}
            )
