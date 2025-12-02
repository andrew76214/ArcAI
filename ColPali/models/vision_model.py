"""Wrapper for Qwen3 Vision-Language model."""
from typing import List, TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from transformers import Qwen3VLForConditionalGeneration, Qwen3VLProcessor


class VisionLanguageModel:
    """Wrapper for Qwen3 Vision-Language model.

    Consolidates chat template building and generation logic.
    """

    def __init__(
        self,
        model: "Qwen3VLForConditionalGeneration",
        processor: "Qwen3VLProcessor",
    ):
        self._model = model
        self._processor = processor

    def build_chat_template(
        self, images: List[Image.Image], text_query: str
    ) -> List[dict]:
        """Build chat template for VL model input.

        Args:
            images: List of PIL images for context
            text_query: User question text

        Returns:
            Chat template structure for the processor
        """
        return [
            {
                "role": "user",
                "content": [{"type": "image", "image": image} for image in images]
                + [{"type": "text", "text": text_query}],
            }
        ]

    def generate(
        self,
        images: List[Image.Image],
        text_query: str,
        max_new_tokens: int = 200,
    ) -> List[str]:
        """Generate text response from images and query.

        Args:
            images: List of PIL images for context
            text_query: User question
            max_new_tokens: Maximum tokens to generate

        Returns:
            List of generated text responses

        Raises:
            RuntimeError: If qwen_vl_utils is not available
        """
        try:
            from qwen_vl_utils import process_vision_info
            import torch
        except ImportError as e:
            raise RuntimeError(
                "Failed to import qwen_vl_utils. "
                "Install with: pip install qwen_vl_utils"
            ) from e

        chat_template = self.build_chat_template(images, text_query)

        text = self._processor.apply_chat_template(
            chat_template, tokenize=False, add_generation_prompt=True
        )
        image_inputs, _ = process_vision_info(chat_template)

        inputs = self._processor(
            text=[text], images=image_inputs, padding=True, return_tensors="pt"
        )

        if torch.cuda.is_available():
            inputs = inputs.to("cuda")

        generated_ids = self._model.generate(**inputs, max_new_tokens=max_new_tokens)

        generated_ids_trimmed = [
            out_ids[len(in_ids) :]
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]

        return self._processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
