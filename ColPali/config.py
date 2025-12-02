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


# Default IKEA PDFs for demo
DEFAULT_PDFS: Dict[str, str] = {
    "MALM": "https://www.ikea.com/us/en/assembly_instructions/malm-4-drawer-chest-white__AA-2398381-2-100.pdf",
    "BILLY": "https://www.ikea.com/us/en/assembly_instructions/billy-bookcase-white__AA-1844854-6-2.pdf",
    "BOAXEL": "https://www.ikea.com/us/en/assembly_instructions/boaxel-wall-upright-white__AA-2341341-2-100.pdf",
    "ADILS": "https://www.ikea.com/us/en/assembly_instructions/adils-leg-white__AA-844478-6-2.pdf",
    "MICKE": "https://www.ikea.com/us/en/assembly_instructions/micke-desk-white__AA-476626-10-100.pdf",
}


def get_config() -> AppConfig:
    """Returns default application configuration."""
    return AppConfig()
