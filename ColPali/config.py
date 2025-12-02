"""Centralized configuration for ColPali application."""
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class ModelConfig:
    """Configuration for ML models."""
    retrieval_model_name: str = "vidore/colpali-v1.2"
    vl_model_name: str = "Qwen/Qwen3-VL-4B-Instruct"
    use_fast_processor: bool = False
    min_pixels: int = 224 * 224
    max_pixels: int = 1024 * 1024


@dataclass
class StorageConfig:
    """Configuration for file storage."""
    data_dir: str = "data"
    index_name: str = "image_index"
    supported_extensions: Tuple[str, ...] = (".pdf", ".png", ".jpg", ".jpeg")
    chunk_size: int = 8192


@dataclass
class RAGConfig:
    """Configuration for RAG operations."""
    default_top_k: int = 1
    default_max_new_tokens: int = 200
    # Page overlap: include adjacent pages for cross-page content
    pages_before: int = 1  # Number of pages to include before each result
    pages_after: int = 1   # Number of pages to include after each result


@dataclass
class AppConfig:
    """Main application configuration."""
    model: ModelConfig = field(default_factory=ModelConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)


# Default PDFs from local data directory
DEFAULT_PDFS: Dict[str, str] = {
    "ARCMIS_v5_Operation_Manual": "data/ARCMIS_v5_Operation_Manual.pdf",
    "IT_help_desk": "data/IT_help_desk.pdf",
}


def get_config() -> AppConfig:
    """Returns default application configuration."""
    return AppConfig()
