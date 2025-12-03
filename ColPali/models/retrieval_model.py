"""ColPali retrieval model with Qdrant backend.

Provides document indexing and retrieval using ColPali embeddings
stored in Qdrant vector database.
"""
from typing import Any, Dict, List, TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from models.colpali_embedder import ColPaliEmbedder
    from storage.vector_store import QdrantVectorStore


class RetrievalModel:
    """ColPali retrieval model with Qdrant storage.

    Generates multi-vector embeddings using ColPali and stores them
    in Qdrant for efficient MaxSim retrieval.
    """

    def __init__(
        self,
        embedder: "ColPaliEmbedder",
        vector_store: "QdrantVectorStore",
    ):
        """Initialize the retrieval model.

        Args:
            embedder: ColPali embedding generator
            vector_store: Qdrant vector store instance
        """
        self._embedder = embedder
        self._vector_store = vector_store
        self._indexed = False
        self._point_counter = 0

    @property
    def is_indexed(self) -> bool:
        """Check if documents have been indexed."""
        return self._indexed

    def initialize(self) -> None:
        """Initialize the vector store connection."""
        self._vector_store.initialize()
        # Check if existing index has documents
        if self._vector_store.collection_exists():
            self._indexed = True
            self._point_counter = self._vector_store.get_point_count()

    def index(
        self,
        images: Dict[int, List[Image.Image]],
        overwrite: bool = False,
    ) -> None:
        """Index document images.

        Args:
            images: Mapping of doc_id to list of page images
            overwrite: Whether to clear existing index first
        """
        if overwrite:
            self._vector_store.delete_collection()
            self._vector_store.initialize()
            self._point_counter = 0

        # Process each document
        for doc_id, pages in images.items():
            if not pages:
                continue

            # Generate embeddings for all pages in batch
            embeddings = self._embedder.embed_images(pages)

            # Prepare batch of points
            points = []
            for page_idx, page_embedding in enumerate(embeddings):
                page_num = page_idx + 1  # 1-indexed
                points.append({
                    "point_id": self._point_counter,
                    "doc_id": doc_id,
                    "page_num": page_num,
                    "embeddings": page_embedding,
                })
                self._point_counter += 1

            # Add to vector store in batch
            self._vector_store.add_documents_batch(points)

        self._indexed = True

    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search indexed documents.

        Args:
            query: Search query text
            k: Number of results to return

        Returns:
            List of search results with doc_id, page_num, and score

        Raises:
            RuntimeError: If documents haven't been indexed
        """
        if not self._indexed:
            raise RuntimeError(
                "Documents must be indexed before searching. Call index() first."
            )

        # Generate query embedding
        query_embedding = self._embedder.embed_query(query)

        # Search using MaxSim
        return self._vector_store.search(query_embedding, top_k=k)
