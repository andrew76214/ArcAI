"""Configuration for evaluation module."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class JudgeConfig:
    """Configuration for LLM-as-a-Judge."""

    model_name: str = "gpt-4o"
    api_key_env_var: str = "OPENAI_API_KEY"
    temperature: float = 0.0
    max_retries: int = 3
    timeout: int = 60


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
