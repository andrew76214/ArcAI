"""OpenAI-based LLM-as-a-Judge implementation."""
import os
import time
from typing import Optional

from .base_judge import BaseJudge
from ..metrics.generation_metrics import GenerationEvalResult
from ..config import JudgeConfig


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


class OpenAIJudge(BaseJudge):
    """LLM-as-a-Judge using OpenAI API."""

    def __init__(self, config: Optional[JudgeConfig] = None):
        """Initialize OpenAI judge.

        Args:
            config: Judge configuration. Uses defaults if None.
        """
        self.config = config or JudgeConfig()
        self._client = None

    @property
    def client(self):
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError(
                    "openai package required. Install with: pip install openai"
                )

            api_key = os.environ.get(self.config.api_key_env_var)
            if not api_key:
                raise ValueError(
                    f"API key not found in environment variable: {self.config.api_key_env_var}"
                )
            self._client = OpenAI(api_key=api_key)
        return self._client

    def _call_llm(self, prompt: str) -> str:
        """Call OpenAI API with retry logic.

        Args:
            prompt: Prompt to send to the model

        Returns:
            Model response text

        Raises:
            Exception: If all retries fail
        """
        for attempt in range(self.config.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    timeout=self.config.timeout,
                )
                return response.choices[0].message.content
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
        """Evaluate generation quality using GPT-4o.

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
