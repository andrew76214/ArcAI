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
    default_top_k: int = 3
    default_max_new_tokens: int = 200


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
    "MALM": "data/MALM.pdf",
    "BILLY": "data/BILLY.pdf",
    "BOAXEL": "data/BOAXEL.pdf",
    "ADILS": "data/ADILS.pdf",
    "MICKE": "data/MICKE.pdf",
}


def get_config() -> AppConfig:
    """Returns default application configuration."""
    return AppConfig()
