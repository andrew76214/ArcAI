"""Direct ColPali embedding extraction."""
from typing import List, TYPE_CHECKING

import torch
from PIL import Image

if TYPE_CHECKING:
    from colpali_engine.models import ColPali, ColPaliProcessor


class ColPaliEmbedder:
    """Wrapper for direct ColPali embedding extraction.

    Generates multi-vector embeddings for images and text queries
    using the ColPali model.
    """

    def __init__(self, model: "ColPali", processor: "ColPaliProcessor"):
        """Initialize the embedder.

        Args:
            model: Loaded ColPali model
            processor: ColPali processor for image/text preprocessing
        """
        self._model = model
        self._processor = processor
        self._device = next(model.parameters()).device

    def embed_images(self, images: List[Image.Image]) -> List[torch.Tensor]:
        """Generate multi-vector embeddings for images.

        Args:
            images: List of PIL images

        Returns:
            List of embedding tensors, each shape (num_patches, embedding_dim)
        """
        if not images:
            return []

        # Process images in batch
        batch = self._processor.process_images(images).to(self._device)

        with torch.no_grad():
            embeddings = self._model(**batch)

        # Return list of individual embeddings
        return [emb for emb in embeddings]

    def embed_query(self, query: str) -> torch.Tensor:
        """Generate multi-vector embedding for a text query.

        Args:
            query: Query string

        Returns:
            Embedding tensor of shape (num_tokens, embedding_dim)
        """
        batch = self._processor.process_queries([query]).to(self._device)

        with torch.no_grad():
            embeddings = self._model(**batch)

        return embeddings[0]

    def embed_queries(self, queries: List[str]) -> List[torch.Tensor]:
        """Generate multi-vector embeddings for multiple text queries.

        Args:
            queries: List of query strings

        Returns:
            List of embedding tensors, each shape (num_tokens, embedding_dim)
        """
        if not queries:
            return []

        batch = self._processor.process_queries(queries).to(self._device)

        with torch.no_grad():
            embeddings = self._model(**batch)

        return [emb for emb in embeddings]
