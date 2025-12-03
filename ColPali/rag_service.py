"""High-level RAG orchestration service.

Manages model lifecycle and provides clean API for RAG operations
using ColPali embeddings stored in Qdrant vector database.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from PIL import Image

from config import AppConfig, get_config
from models.loader import ModelLoader
from models.colpali_embedder import ColPaliEmbedder
from models.retrieval_model import RetrievalModel
from models.vision_model import VisionLanguageModel
from storage.vector_store import QdrantVectorStore
from storage.converter import convert_pdfs_to_images, list_available_files


@dataclass
class QueryResult:
    """Detailed result from a RAG query."""

    answer: str
    retrieved_images: List[Image.Image]
    # Retrieved pages before overlap expansion: List of (doc_id, page_num)
    retrieved_pages: List[Tuple[int, int]] = field(default_factory=list)
    # Retrieved pages after overlap expansion
    expanded_pages: List[Tuple[int, int]] = field(default_factory=list)


class RAGService:
    """High-level RAG orchestration service.

    Manages model lifecycle and provides unified API for:
    - Document indexing with ColPali + Qdrant
    - Query execution with retrieval and generation
    """

    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize RAG service.

        Args:
            config: Application configuration. Uses default if None.
        """
        self.config = config or get_config()
        self._loader = ModelLoader(self.config.model)
        self._retrieval_model: Optional[RetrievalModel] = None
        self._vl_model: Optional[VisionLanguageModel] = None
        self._all_images: Dict[int, List[Image.Image]] = {}

    @property
    def is_initialized(self) -> bool:
        """Check if retrieval model is loaded."""
        return self._retrieval_model is not None

    @property
    def is_indexed(self) -> bool:
        """Check if documents are indexed."""
        return self._retrieval_model is not None and self._retrieval_model.is_indexed

    def initialize_retrieval(self) -> None:
        """Load retrieval model and initialize Qdrant (lazy initialization)."""
        if self._retrieval_model is None:
            # Load ColPali model and processor
            model, processor = self._loader.load_colpali_model()
            embedder = ColPaliEmbedder(model, processor)

            # Initialize Qdrant vector store
            vector_store = QdrantVectorStore(self.config.qdrant)

            # Create retrieval model
            self._retrieval_model = RetrievalModel(embedder, vector_store)
            self._retrieval_model.initialize()

    def initialize_vl(self) -> None:
        """Load vision-language model (lazy initialization)."""
        if self._vl_model is None:
            model = self._loader.load_vl_model()
            processor = self._loader.load_vl_processor()
            self._vl_model = VisionLanguageModel(model, processor)

    def index_documents(
        self, folder: Optional[str] = None, overwrite: bool = False
    ) -> str:
        """Index documents in folder.

        Args:
            folder: Document folder (uses config default if None)
            overwrite: Whether to overwrite existing index

        Returns:
            Status message
        """
        folder = folder or self.config.storage.data_dir

        files = list_available_files(folder, self.config.storage.supported_extensions)
        if not files:
            return "No supported files found to index."

        # Initialize retrieval model if needed
        self.initialize_retrieval()

        # Convert PDFs/images to PIL images
        self._all_images = convert_pdfs_to_images(
            folder, self.config.storage.supported_extensions
        )

        # Index images with Qdrant
        self._retrieval_model.index(
            images=self._all_images,
            overwrite=overwrite,
        )

        return f"Indexed {len(files)} file(s) from {folder}."

    def query(
        self,
        text_query: str,
        top_k: Optional[int] = None,
        max_new_tokens: Optional[int] = None,
        pages_before: Optional[int] = None,
        pages_after: Optional[int] = None,
    ) -> Tuple[str, List[Image.Image]]:
        """Execute RAG query and return answer with retrieved images.

        Args:
            text_query: User question
            top_k: Number of pages to retrieve (uses config default if None)
            max_new_tokens: Maximum tokens for generation (uses config default if None)
            pages_before: Pages to include before each result (uses config default if None)
            pages_after: Pages to include after each result (uses config default if None)

        Returns:
            Tuple of (answer_text, retrieved_images)

        Raises:
            RuntimeError: If not indexed or models not loaded
        """
        top_k = top_k or self.config.rag.default_top_k
        max_new_tokens = max_new_tokens or self.config.rag.default_max_new_tokens

        if not self.is_indexed:
            raise RuntimeError(
                "Documents must be indexed first. Call index_documents()."
            )

        # Ensure VL model is loaded
        self.initialize_vl()

        # Retrieve relevant pages
        results = self._retrieval_model.search(text_query, k=top_k)

        # Expand results with adjacent pages for cross-page content
        expanded_results = self._expand_with_overlap(
            results, pages_before=pages_before, pages_after=pages_after
        )

        # Map results to images
        retrieved_images = self._get_images_from_results(expanded_results)

        # Generate answer
        texts = self._vl_model.generate(
            images=retrieved_images,
            text_query=text_query,
            max_new_tokens=max_new_tokens,
        )

        answer = texts[0] if texts else ""
        return answer, retrieved_images

    def query_with_details(
        self,
        text_query: str,
        top_k: Optional[int] = None,
        max_new_tokens: Optional[int] = None,
        pages_before: Optional[int] = None,
        pages_after: Optional[int] = None,
    ) -> QueryResult:
        """Execute RAG query and return detailed results including retrieval info.

        Args:
            text_query: User question
            top_k: Number of pages to retrieve (uses config default if None)
            max_new_tokens: Maximum tokens for generation (uses config default if None)
            pages_before: Pages to include before each result (uses config default if None)
            pages_after: Pages to include after each result (uses config default if None)

        Returns:
            QueryResult with answer, images, and retrieval information

        Raises:
            RuntimeError: If not indexed or models not loaded
        """
        top_k = top_k or self.config.rag.default_top_k
        max_new_tokens = max_new_tokens or self.config.rag.default_max_new_tokens

        if not self.is_indexed:
            raise RuntimeError(
                "Documents must be indexed first. Call index_documents()."
            )

        # Ensure VL model is loaded
        self.initialize_vl()

        # Retrieve relevant pages
        results = self._retrieval_model.search(text_query, k=top_k)

        # Extract retrieved pages as (doc_id, page_num) tuples
        retrieved_pages = [(r["doc_id"], r["page_num"]) for r in results]

        # Expand results with adjacent pages for cross-page content
        expanded_results = self._expand_with_overlap(
            results, pages_before=pages_before, pages_after=pages_after
        )

        # Extract expanded pages as tuples
        expanded_pages = [(r["doc_id"], r["page_num"]) for r in expanded_results]

        # Map results to images
        retrieved_images = self._get_images_from_results(expanded_results)

        # Generate answer
        texts = self._vl_model.generate(
            images=retrieved_images,
            text_query=text_query,
            max_new_tokens=max_new_tokens,
        )

        answer = texts[0] if texts else ""

        return QueryResult(
            answer=answer,
            retrieved_images=retrieved_images,
            retrieved_pages=retrieved_pages,
            expanded_pages=expanded_pages,
        )

    def _get_images_from_results(self, results: List[dict]) -> List[Image.Image]:
        """Map retrieval results to PIL images.

        Args:
            results: List of dicts with 'doc_id' and 'page_num' (1-indexed)

        Returns:
            List of PIL images
        """
        images = []
        for result in results:
            doc_id = result["doc_id"]
            page_num = result["page_num"]  # 1-indexed
            if doc_id in self._all_images:
                page_idx = page_num - 1
                if 0 <= page_idx < len(self._all_images[doc_id]):
                    images.append(self._all_images[doc_id][page_idx])
        return images

    def _expand_with_overlap(
        self,
        results: List[dict],
        pages_before: Optional[int] = None,
        pages_after: Optional[int] = None,
    ) -> List[dict]:
        """Expand search results to include adjacent pages.

        Args:
            results: Original search results with 'doc_id' and 'page_num'
            pages_before: Pages to include before each result (uses config if None)
            pages_after: Pages to include after each result (uses config if None)

        Returns:
            Expanded results with adjacent pages, deduplicated and sorted
        """
        pages_before = pages_before if pages_before is not None else self.config.rag.pages_before
        pages_after = pages_after if pages_after is not None else self.config.rag.pages_after

        # Skip if no overlap needed
        if pages_before == 0 and pages_after == 0:
            return results

        seen: set = set()
        expanded: List[dict] = []

        for result in results:
            doc_id = result["doc_id"]
            page_num = result["page_num"]

            # Get total pages for this document
            if doc_id not in self._all_images:
                continue
            total_pages = len(self._all_images[doc_id])

            # Calculate page range with boundary handling
            start_page = max(1, page_num - pages_before)
            end_page = min(total_pages, page_num + pages_after)

            # Add pages in range
            for p in range(start_page, end_page + 1):
                key = (doc_id, p)
                if key not in seen:
                    seen.add(key)
                    expanded.append({"doc_id": doc_id, "page_num": p})

        # Sort by document order (doc_id, then page_num)
        expanded.sort(key=lambda x: (x["doc_id"], x["page_num"]))

        return expanded
