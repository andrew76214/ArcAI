"""Qdrant vector store for ColPali embeddings.

Provides multi-vector storage and MaxSim retrieval using Qdrant's
native support for late interaction models.
"""
from typing import Any, Dict, List, Optional

import torch

from config import QdrantConfig


class QdrantVectorStore:
    """Qdrant wrapper for ColPali multi-vector storage."""

    def __init__(self, config: QdrantConfig):
        """Initialize the vector store.

        Args:
            config: Qdrant configuration
        """
        self._config = config
        self._client = None

    def initialize(self) -> None:
        """Initialize Qdrant client and create collection if needed."""
        from qdrant_client import QdrantClient
        from qdrant_client.models import (
            Distance,
            VectorParams,
            MultiVectorConfig,
            MultiVectorComparator,
        )

        if self._config.use_memory:
            # In-memory storage with optional persistence
            self._client = QdrantClient(
                path=self._config.persist_directory
                if self._config.persist_directory
                else ":memory:"
            )
        else:
            # Connect to Qdrant server
            self._client = QdrantClient(
                host=self._config.host,
                port=self._config.port,
            )

        # Check if collection exists
        collections = self._client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self._config.collection_name not in collection_names:
            # Create collection with multi-vector support
            self._client.create_collection(
                collection_name=self._config.collection_name,
                vectors_config=VectorParams(
                    size=self._config.vector_size,
                    distance=Distance.COSINE,
                    multivector_config=MultiVectorConfig(
                        comparator=MultiVectorComparator.MAX_SIM
                    ),
                ),
            )

    def add_document(
        self,
        point_id: int,
        doc_id: int,
        page_num: int,
        embeddings: torch.Tensor,
    ) -> None:
        """Add a document page with its multi-vector embeddings.

        Args:
            point_id: Unique point ID in Qdrant
            doc_id: Document ID
            page_num: Page number (1-indexed)
            embeddings: Multi-vector embeddings tensor (num_patches, embedding_dim)
        """
        from qdrant_client.models import PointStruct

        # Convert tensor to list of lists
        vectors = embeddings.cpu().float().tolist()

        self._client.upsert(
            collection_name=self._config.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vectors,
                    payload={
                        "doc_id": doc_id,
                        "page_num": page_num,
                    },
                )
            ],
        )

    def add_documents_batch(
        self,
        points: List[Dict[str, Any]],
    ) -> None:
        """Add multiple document pages in a batch.

        Args:
            points: List of dicts with 'point_id', 'doc_id', 'page_num', 'embeddings'
        """
        from qdrant_client.models import PointStruct

        qdrant_points = []
        for p in points:
            vectors = p["embeddings"].cpu().float().tolist()
            qdrant_points.append(
                PointStruct(
                    id=p["point_id"],
                    vector=vectors,
                    payload={
                        "doc_id": p["doc_id"],
                        "page_num": p["page_num"],
                    },
                )
            )

        self._client.upsert(
            collection_name=self._config.collection_name,
            points=qdrant_points,
        )

    def search(
        self,
        query_embedding: torch.Tensor,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """Search for relevant document pages using MaxSim.

        Args:
            query_embedding: Query multi-vector embedding (num_tokens, embedding_dim)
            top_k: Number of results to return

        Returns:
            List of results with 'doc_id', 'page_num', and 'score'
        """
        # Convert tensor to list of lists
        query_vectors = query_embedding.cpu().float().tolist()

        results = self._client.query_points(
            collection_name=self._config.collection_name,
            query=query_vectors,
            limit=top_k,
            with_payload=True,
        )

        return [
            {
                "doc_id": point.payload["doc_id"],
                "page_num": point.payload["page_num"],
                "score": point.score,
            }
            for point in results.points
        ]

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        if self._client:
            try:
                self._client.delete_collection(self._config.collection_name)
            except Exception:
                pass  # Collection might not exist

    def collection_exists(self) -> bool:
        """Check if collection exists and has documents.

        Returns:
            True if collection exists and has at least one point
        """
        if self._client is None:
            return False

        try:
            collections = self._client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self._config.collection_name not in collection_names:
                return False

            # Check if collection has points
            info = self._client.get_collection(self._config.collection_name)
            return info.points_count > 0
        except Exception:
            return False

    def get_point_count(self) -> int:
        """Get the number of points in the collection.

        Returns:
            Number of points, or 0 if collection doesn't exist
        """
        if self._client is None:
            return 0

        try:
            info = self._client.get_collection(self._config.collection_name)
            return info.points_count
        except Exception:
            return 0
