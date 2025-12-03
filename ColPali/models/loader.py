"""Model loading utilities with lazy loading support."""
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from colpali_engine.models import ColPali, ColPaliProcessor
    from transformers import Qwen3VLForConditionalGeneration, Qwen3VLProcessor

from config import ModelConfig


class ModelLoadError(Exception):
    """Raised when model loading fails."""

    pass


class ModelLoader:
    """Handles lazy loading of ML models with proper error messages."""

    def __init__(self, config: ModelConfig):
        self.config = config

    def load_colpali_model(self) -> Tuple["ColPali", "ColPaliProcessor"]:
        """Load the ColPali model and processor directly.

        Returns:
            Tuple of (model, processor)

        Raises:
            ModelLoadError: If import or loading fails
        """
        try:
            from colpali_engine.models import ColPali, ColPaliProcessor
            import torch
        except ImportError as e:
            raise ModelLoadError(
                "Failed to import colpali_engine. "
                "Install it with: pip install colpali-engine"
            ) from e

        dtype = torch.bfloat16 if hasattr(torch, "bfloat16") else torch.float16

        model = ColPali.from_pretrained(
            self.config.retrieval_model_name,
            dtype=dtype,
            device_map="auto",
        ).eval()

        processor = ColPaliProcessor.from_pretrained(
            self.config.retrieval_model_name
        )

        return model, processor

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
