"""Configuration for evaluation module."""
from dataclasses import dataclass, field
from typing import List, Literal


@dataclass
class JudgeConfig:
    """Configuration for LLM-as-a-Judge."""

    # Judge type: "ollama" or "openai"
    judge_type: Literal["ollama", "openai"] = "ollama"
    # Model name (e.g., "llama3.1:8b" for Ollama, "gpt-4o" for OpenAI)
    model_name: str = "llama3.1:8b"
    # API key environment variable (only for OpenAI)
    api_key_env_var: str = "OPENAI_API_KEY"
    # Ollama server URL
    base_url: str = "http://localhost:11434"
    temperature: float = 0.0
    max_retries: int = 3
    timeout: int = 120


@dataclass
class GenerationMetricsConfig:
    """Configuration for generation evaluation."""

    evaluate_correctness: bool = True
    evaluate_completeness: bool = True
    evaluate_relevance: bool = True
    evaluate_coherence: bool = True
    evaluate_faithfulness: bool = True


@dataclass
class EvaluationConfig:
    """Main evaluation configuration."""

    judge: JudgeConfig = field(default_factory=JudgeConfig)
    generation: GenerationMetricsConfig = field(default_factory=GenerationMetricsConfig)
    batch_size: int = 10
    output_dir: str = "evaluation_results"
    save_intermediate: bool = True


def get_evaluation_config() -> EvaluationConfig:
    """Returns default evaluation configuration."""
    return EvaluationConfig()
