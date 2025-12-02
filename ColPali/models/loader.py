"""Model loading utilities with lazy loading support."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from byaldi import RAGMultiModalModel
    from transformers import Qwen3VLForConditionalGeneration, Qwen3VLProcessor

from config import ModelConfig


class ModelLoadError(Exception):
    """Raised when model loading fails."""

    pass


class ModelLoader:
    """Handles lazy loading of ML models with proper error messages."""

    def __init__(self, config: ModelConfig):
        self.config = config

    def load_retrieval_model(self) -> "RAGMultiModalModel":
        """Load the ColPali retrieval model.

        Returns:
            Loaded RAGMultiModalModel

        Raises:
            ModelLoadError: If import or loading fails
        """
        try:
            from byaldi import RAGMultiModalModel
        except ImportError as e:
            raise ModelLoadError(
                "Failed to import 'byaldi'. Install it with: pip install byaldi"
            ) from e

        return RAGMultiModalModel.from_pretrained(self.config.retrieval_model_name)

    def load_vl_model(self) -> "Qwen3VLForConditionalGeneration":
        """Load the Qwen3 Vision-Language model.

        Returns:
            Loaded VL model on appropriate device

        Raises:
            ModelLoadError: If import or loading fails
        """
        try:
            from transformers import Qwen3VLForConditionalGeneration
            import torch
        except ImportError as e:
            raise ModelLoadError(
                "Failed to import transformers or torch. "
                "Install with: pip install transformers torch"
            ) from e

        dtype = torch.bfloat16 if hasattr(torch, "bfloat16") else torch.float16
        model = Qwen3VLForConditionalGeneration.from_pretrained(
            self.config.vl_model_name,
            torch_dtype=dtype,
        )

        if torch.cuda.is_available():
            model.cuda().eval()

        return model

    def load_vl_processor(self) -> "Qwen3VLProcessor":
        """Load the Qwen3 VL processor.

        Returns:
            Loaded processor

        Raises:
            ModelLoadError: If import or loading fails
        """
        try:
            from transformers import Qwen3VLProcessor
        except ImportError as e:
            raise ModelLoadError(
                "Failed to import Qwen3VLProcessor from transformers."
            ) from e

        return Qwen3VLProcessor.from_pretrained(
            self.config.vl_model_name,
            use_fast=self.config.use_fast_processor,
            min_pixels=self.config.min_pixels,
            max_pixels=self.config.max_pixels,
        )
