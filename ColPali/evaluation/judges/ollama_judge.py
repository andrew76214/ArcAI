"""Ollama-based LLM-as-a-Judge implementation."""
import os
import time
from typing import Optional

import requests

from .base_judge import BaseJudge
from ..metrics.generation_metrics import GenerationEvalResult
from ..config import JudgeConfig

# Default Ollama URL, can be overridden by OLLAMA_HOST environment variable
DEFAULT_OLLAMA_URL = "http://localhost:11434"


GENERATION_JUDGE_PROMPT = """You are an expert evaluator assessing the quality of AI-generated answers in a document question-answering system.

## Task
Evaluate the GENERATED ANSWER against the REFERENCE ANSWER for the given QUESTION.

## Evaluation Criteria
Score each dimension from 1-5:

### Correctness (1-5)
- 5: Completely accurate, all facts match reference
- 4: Mostly accurate, minor omissions
- 3: Partially accurate, some incorrect details
- 2: Mostly incorrect, few accurate points
- 1: Completely incorrect or irrelevant

### Completeness (1-5)
- 5: Covers all key points from reference
- 4: Covers most key points
- 3: Covers some key points
- 2: Missing most key points
- 1: Missing all key points

### Relevance (1-5)
- 5: Directly addresses the question
- 4: Mostly relevant with minor tangents
- 3: Somewhat relevant
- 2: Mostly irrelevant
- 1: Completely off-topic

### Coherence (1-5)
- 5: Clear, well-structured, easy to follow
- 4: Generally clear with minor issues
- 3: Understandable but disorganized
- 2: Difficult to follow
- 1: Incoherent

## Input
QUESTION: {question}

REFERENCE ANSWER: {expected_answer}

GENERATED ANSWER: {generated_answer}

## Output Format
Respond with a JSON object ONLY (no additional text):
{{
    "correctness": <1-5>,
    "completeness": <1-5>,
    "relevance": <1-5>,
    "coherence": <1-5>,
    "overall_score": <1-5>,
    "reasoning": "<brief explanation of scores>"
}}
"""


class OllamaJudge(BaseJudge):
    """LLM-as-a-Judge using Ollama API."""

    def __init__(self, config: Optional[JudgeConfig] = None):
        """Initialize Ollama judge.

        Args:
            config: Judge configuration. Uses defaults if None.

        Environment Variables:
            OLLAMA_HOST: Override Ollama server URL (e.g., http://192.168.1.100:11434)
        """
        self.config = config or JudgeConfig(
            model_name="llama3.1:8b",
            api_key_env_var="",  # Ollama doesn't need API key
        )
        # Priority: OLLAMA_HOST env var > config.base_url > default
        self.base_url = os.environ.get(
            "OLLAMA_HOST",
            getattr(self.config, "base_url", DEFAULT_OLLAMA_URL)
        )

    def _call_llm(self, prompt: str) -> str:
        """Call Ollama API with retry logic.

        Args:
            prompt: Prompt to send to the model

        Returns:
            Model response text

        Raises:
            Exception: If all retries fail
        """
        url = f"{self.base_url}/api/generate"

        for attempt in range(self.config.max_retries):
            try:
                response = requests.post(
                    url,
                    json={
                        "model": self.config.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.config.temperature,
                        },
                    },
                    timeout=self.config.timeout,
                )
                response.raise_for_status()
                return response.json()["response"]
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise
                # Exponential backoff
                time.sleep(2**attempt)

    def evaluate_generation(
        self,
        question: str,
        expected_answer: str,
        generated_answer: str,
    ) -> GenerationEvalResult:
        """Evaluate generation quality using Ollama.

        Args:
            question: The input question
            expected_answer: Ground truth answer
            generated_answer: Model-generated answer

        Returns:
            GenerationEvalResult with scores and reasoning
        """
        prompt = GENERATION_JUDGE_PROMPT.format(
            question=question,
            expected_answer=expected_answer,
            generated_answer=generated_answer,
        )

        response = self._call_llm(prompt)
        parsed = self._parse_json_response(response)

        return GenerationEvalResult(
            correctness=float(parsed["correctness"]),
            completeness=float(parsed["completeness"]),
            relevance=float(parsed["relevance"]),
            coherence=float(parsed["coherence"]),
            overall_score=float(parsed["overall_score"]),
            reasoning=parsed["reasoning"],
        )
