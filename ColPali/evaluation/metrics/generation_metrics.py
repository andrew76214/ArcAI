"""Generation quality metrics."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class GenerationEvalResult:
    """Result from LLM-as-a-Judge evaluation."""

    correctness: float
    completeness: float
    relevance: float
    coherence: float
    overall_score: float
    reasoning: str
    faithfulness_score: Optional[float] = None
    unsupported_claims: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "correctness": self.correctness,
            "completeness": self.completeness,
            "relevance": self.relevance,
            "coherence": self.coherence,
            "overall_score": self.overall_score,
            "reasoning": self.reasoning,
        }
        if self.faithfulness_score is not None:
            result["faithfulness_score"] = self.faithfulness_score
        if self.unsupported_claims is not None:
            result["unsupported_claims"] = self.unsupported_claims
        return result


class GenerationMetricsAggregator:
    """Aggregates generation metrics across test cases."""

    def __init__(self):
        self.results: List[GenerationEvalResult] = []

    def add_result(self, result: GenerationEvalResult) -> None:
        """Add a single evaluation result."""
        self.results.append(result)

    def aggregate(self) -> Dict[str, float]:
        """Calculate mean metrics across all results.

        Returns:
            Dictionary of aggregated metrics
        """
        if not self.results:
            return {}

        n = len(self.results)

        metrics = {
            "mean_correctness": sum(r.correctness for r in self.results) / n,
            "mean_completeness": sum(r.completeness for r in self.results) / n,
            "mean_relevance": sum(r.relevance for r in self.results) / n,
            "mean_coherence": sum(r.coherence for r in self.results) / n,
            "mean_overall_score": sum(r.overall_score for r in self.results) / n,
        }

        # Calculate faithfulness if available
        faithfulness_results = [
            r.faithfulness_score for r in self.results if r.faithfulness_score is not None
        ]
        if faithfulness_results:
            metrics["mean_faithfulness"] = sum(faithfulness_results) / len(
                faithfulness_results
            )

        return metrics

    def __len__(self) -> int:
        return len(self.results)
