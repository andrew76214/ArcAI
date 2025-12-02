"""Retrieval quality metrics for RAG evaluation."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class RetrievalEvalResult:
    """Result from retrieval evaluation for a single query."""

    # Retrieved pages: List of (doc_id, page_num) tuples
    retrieved_pages: List[Tuple[int, int]]
    # Expected pages: List of (doc_id, page_num) tuples (ground truth)
    expected_pages: List[Tuple[int, int]]
    # Metrics
    hit: bool  # Did we retrieve at least one expected page?
    recall: float  # Proportion of expected pages retrieved
    precision: float  # Proportion of retrieved pages that are relevant
    mrr: float  # Mean Reciprocal Rank of first relevant result

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "retrieved_pages": [
                {"doc_id": d, "page_num": p} for d, p in self.retrieved_pages
            ],
            "expected_pages": [
                {"doc_id": d, "page_num": p} for d, p in self.expected_pages
            ],
            "hit": self.hit,
            "recall": self.recall,
            "precision": self.precision,
            "mrr": self.mrr,
        }


def calculate_retrieval_metrics(
    retrieved_pages: List[Tuple[int, int]],
    expected_pages: List[Tuple[int, int]],
) -> RetrievalEvalResult:
    """Calculate retrieval metrics for a single query.

    Args:
        retrieved_pages: List of (doc_id, page_num) tuples that were retrieved
        expected_pages: List of (doc_id, page_num) tuples that should be retrieved

    Returns:
        RetrievalEvalResult with calculated metrics
    """
    if not expected_pages:
        # No ground truth - can't calculate meaningful metrics
        return RetrievalEvalResult(
            retrieved_pages=retrieved_pages,
            expected_pages=expected_pages,
            hit=False,
            recall=0.0,
            precision=0.0,
            mrr=0.0,
        )

    retrieved_set: Set[Tuple[int, int]] = set(retrieved_pages)
    expected_set: Set[Tuple[int, int]] = set(expected_pages)

    # Hit: did we retrieve at least one expected page?
    hits = retrieved_set & expected_set
    hit = len(hits) > 0

    # Recall: proportion of expected pages that were retrieved
    recall = len(hits) / len(expected_set) if expected_set else 0.0

    # Precision: proportion of retrieved pages that are relevant
    precision = len(hits) / len(retrieved_set) if retrieved_set else 0.0

    # MRR: reciprocal rank of first relevant result
    mrr = 0.0
    for rank, page in enumerate(retrieved_pages, start=1):
        if page in expected_set:
            mrr = 1.0 / rank
            break

    return RetrievalEvalResult(
        retrieved_pages=retrieved_pages,
        expected_pages=expected_pages,
        hit=hit,
        recall=recall,
        precision=precision,
        mrr=mrr,
    )


class RetrievalMetricsAggregator:
    """Aggregates retrieval metrics across test cases."""

    def __init__(self):
        self.results: List[RetrievalEvalResult] = []

    def add_result(self, result: RetrievalEvalResult) -> None:
        """Add a single evaluation result."""
        self.results.append(result)

    def aggregate(self) -> Dict[str, float]:
        """Calculate mean metrics across all results.

        Returns:
            Dictionary of aggregated metrics
        """
        if not self.results:
            return {}

        # Only include results that have expected pages (ground truth)
        valid_results = [r for r in self.results if r.expected_pages]

        if not valid_results:
            return {
                "hit_rate": 0.0,
                "mean_recall": 0.0,
                "mean_precision": 0.0,
                "mean_mrr": 0.0,
                "retrieval_coverage": 0.0,
            }

        n = len(valid_results)
        total = len(self.results)

        return {
            "hit_rate": sum(1 for r in valid_results if r.hit) / n,
            "mean_recall": sum(r.recall for r in valid_results) / n,
            "mean_precision": sum(r.precision for r in valid_results) / n,
            "mean_mrr": sum(r.mrr for r in valid_results) / n,
            "retrieval_coverage": n / total if total > 0 else 0.0,
        }

    def __len__(self) -> int:
        return len(self.results)
