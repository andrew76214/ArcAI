"""Abstract base class for LLM judges."""
from abc import ABC, abstractmethod
from typing import Dict, Any
import json
import re

from ..metrics.generation_metrics import GenerationEvalResult


class BaseJudge(ABC):
    """Abstract base class for LLM-as-a-Judge implementations."""

    @abstractmethod
    def evaluate_generation(
        self,
        question: str,
        expected_answer: str,
        generated_answer: str,
    ) -> GenerationEvalResult:
        """Evaluate generation quality.

        Args:
            question: The input question
            expected_answer: Ground truth answer
            generated_answer: Model-generated answer

        Returns:
            GenerationEvalResult with scores and reasoning
        """
        pass

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response with error handling.

        Args:
            response: Raw LLM response text

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If JSON cannot be parsed
        """
        # Try direct JSON parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Extract JSON from markdown code block
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Last resort: find JSON-like structure
        json_match = re.search(r"\{[\s\S]*\}", response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Could not parse JSON from response: {response[:200]}")
