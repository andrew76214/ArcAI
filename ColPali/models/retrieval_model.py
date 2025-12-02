"""Wrapper for ColPali retrieval model."""
from typing import Any, Dict, List, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from byaldi import RAGMultiModalModel


class RetrievalModel:
    """Wrapper for ColPali retrieval model with indexing state."""

    def __init__(self, model: "RAGMultiModalModel"):
        self._model = model
        self._indexed = False
        self._index_name = None

    @property
    def is_indexed(self) -> bool:
        """Check if documents have been indexed."""
        return self._indexed
    
    def _check_existing_index(self, index_name: str) -> bool:
        """Check if an index already exists.
        
        Args:
            index_name: Name of the index to check
            
        Returns:
            True if index exists, False otherwise
        """
        # BytalDI stores indices in a hidden directory
        index_dir = os.path.expanduser(f"~/.byaldi/{index_name}")
        return os.path.exists(index_dir)

    def index(
        self,
        input_path: str,
        index_name: str = "image_index",
        store_collection: bool = False,
        overwrite: bool = False,
    ) -> None:
        """Index documents in the given path.

        Args:
            input_path: Path to documents folder
            index_name: Name for the index
            store_collection: Whether to store collection with index
            overwrite: Whether to overwrite existing index
        """
        self._index_name = index_name
        
        # Check if index already exists (unless overwrite is True)
        if not overwrite and self._check_existing_index(index_name):
            self._indexed = True
            return
        
        self._model.index(
            input_path=input_path,
            index_name=index_name,
            store_collection_with_index=store_collection,
            overwrite=overwrite,
        )
        self._indexed = True

    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search indexed documents.

        Args:
            query: Search query text
            k: Number of results to return

        Returns:
            List of search results with doc_id and page_num

        Raises:
            RuntimeError: If documents haven't been indexed
        """
        if not self._indexed:
            raise RuntimeError(
                "Documents must be indexed before searching. Call index() first."
            )
        return self._model.search(query, k=k)
