"""High-level RAG orchestration service.

Replaces global _INDEXED_RAG state with proper encapsulation.
Manages model lifecycle and provides clean API for RAG operations.
"""
from typing import Dict, List, Optional, Tuple

from PIL import Image

from config import AppConfig, get_config
from models.loader import ModelLoader
from models.retrieval_model import RetrievalModel
from models.vision_model import VisionLanguageModel
from storage.converter import convert_pdfs_to_images, list_available_files


class RAGService:
    """High-level RAG orchestration service.

    Manages model lifecycle and provides unified API for:
    - Document indexing
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
        """Load retrieval model (lazy initialization)."""
        if self._retrieval_model is None:
            raw_model = self._loader.load_retrieval_model()
            self._retrieval_model = RetrievalModel(raw_model)

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

        self.initialize_retrieval()
        self._retrieval_model.index(
            input_path=folder,
            index_name=self.config.storage.index_name,
            overwrite=overwrite,
        )

        # Cache converted images for later retrieval
        self._all_images = convert_pdfs_to_images(
            folder, self.config.storage.supported_extensions
        )

        return f"Indexed {len(files)} file(s) from {folder}."

    def query(
        self,
        text_query: str,
        top_k: Optional[int] = None,
        max_new_tokens: Optional[int] = None,
    ) -> Tuple[str, List[Image.Image]]:
        """Execute RAG query and return answer with retrieved images.

        Args:
            text_query: User question
            top_k: Number of pages to retrieve (uses config default if None)
            max_new_tokens: Maximum tokens for generation (uses config default if None)

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

        # Map results to images
        retrieved_images = self._get_images_from_results(results)

        # Generate answer
        texts = self._vl_model.generate(
            images=retrieved_images,
            text_query=text_query,
            max_new_tokens=max_new_tokens,
        )

        answer = texts[0] if texts else ""
        return answer, retrieved_images

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
