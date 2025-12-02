"""Main RAG evaluation orchestrator."""
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .config import EvaluationConfig
from .test_case import TestCase, TestDataset
from .metrics.generation_metrics import GenerationEvalResult, GenerationMetricsAggregator
from .metrics.retrieval_metrics import (
    RetrievalEvalResult,
    RetrievalMetricsAggregator,
    calculate_retrieval_metrics,
)
from .judges.base_judge import BaseJudge
from .judges.openai_judge import OpenAIJudge
from .judges.ollama_judge import OllamaJudge


@dataclass
class EvaluationResult:
    """Result for a single test case."""

    test_case_id: str
    question: str
    generated_answer: str
    expected_answer: str
    generation_metrics: Dict[str, Any]
    latency_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    retrieval_metrics: Optional[Dict[str, Any]] = None


@dataclass
class EvaluationReport:
    """Complete evaluation report."""

    dataset_name: str
    total_test_cases: int
    aggregate_generation_metrics: Dict[str, float]
    aggregate_retrieval_metrics: Dict[str, float]
    individual_results: List[EvaluationResult]
    evaluation_config: Dict[str, Any]
    timestamp: str


class RAGEvaluator:
    """Main evaluation orchestrator for RAG systems."""

    def __init__(
        self,
        rag_service,
        config: Optional[EvaluationConfig] = None,
    ):
        """Initialize evaluator.

        Args:
            rag_service: RAGService instance to evaluate
            config: Evaluation configuration
        """
        self.rag_service = rag_service
        self.config = config or EvaluationConfig()
        self._judge: Optional[BaseJudge] = None

    @property
    def judge(self) -> BaseJudge:
        """Lazy-load judge based on configuration."""
        if self._judge is None:
            if self.config.judge.judge_type == "ollama":
                self._judge = OllamaJudge(self.config.judge)
            else:
                self._judge = OpenAIJudge(self.config.judge)
        return self._judge

    def evaluate_single(self, test_case: TestCase) -> EvaluationResult:
        """Evaluate a single test case.

        Args:
            test_case: Test case to evaluate

        Returns:
            EvaluationResult with metrics
        """
        start_time = time.time()

        # Run RAG query with detailed results
        query_result = self.rag_service.query_with_details(test_case.question)

        latency_ms = (time.time() - start_time) * 1000

        # Evaluate generation quality with LLM judge
        gen_result = self.judge.evaluate_generation(
            question=test_case.question,
            expected_answer=test_case.expected_answer,
            generated_answer=query_result.answer,
        )

        # Calculate retrieval metrics
        # Always record retrieved pages; calculate full metrics if expected pages provided
        retrieval_result = calculate_retrieval_metrics(
            retrieved_pages=query_result.retrieved_pages,
            expected_pages=test_case.expected_pages or [],
        )
        retrieval_metrics = retrieval_result.to_dict()

        return EvaluationResult(
            test_case_id=test_case.id,
            question=test_case.question,
            generated_answer=query_result.answer,
            expected_answer=test_case.expected_answer,
            generation_metrics=gen_result.to_dict(),
            latency_ms=latency_ms,
            metadata=test_case.metadata,
            retrieval_metrics=retrieval_metrics,
        )

    def evaluate_dataset(
        self,
        dataset: TestDataset,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> EvaluationReport:
        """Evaluate entire test dataset.

        Args:
            dataset: Test dataset to evaluate
            progress_callback: Optional callback(current, total) for progress

        Returns:
            EvaluationReport with aggregate and individual results
        """
        results = []
        generation_agg = GenerationMetricsAggregator()
        retrieval_agg = RetrievalMetricsAggregator()

        for i, test_case in enumerate(dataset.test_cases):
            result = self.evaluate_single(test_case)
            results.append(result)

            # Aggregate generation metrics
            generation_agg.add_result(
                GenerationEvalResult(
                    correctness=result.generation_metrics["correctness"],
                    completeness=result.generation_metrics["completeness"],
                    relevance=result.generation_metrics["relevance"],
                    coherence=result.generation_metrics["coherence"],
                    overall_score=result.generation_metrics["overall_score"],
                    reasoning=result.generation_metrics["reasoning"],
                )
            )

            # Aggregate retrieval metrics
            retrieval_agg.add_result(
                RetrievalEvalResult(
                    retrieved_pages=[
                        (p["doc_id"], p["page_num"])
                        for p in result.retrieval_metrics["retrieved_pages"]
                    ],
                    expected_pages=[
                        (p["doc_id"], p["page_num"])
                        for p in result.retrieval_metrics["expected_pages"]
                    ],
                    hit=result.retrieval_metrics["hit"],
                    recall=result.retrieval_metrics["recall"],
                    precision=result.retrieval_metrics["precision"],
                    mrr=result.retrieval_metrics["mrr"],
                )
            )

            if progress_callback:
                progress_callback(i + 1, len(dataset.test_cases))

            # Save intermediate results
            if self.config.save_intermediate:
                self._save_intermediate(result)

        return EvaluationReport(
            dataset_name=dataset.dataset_name,
            total_test_cases=len(dataset.test_cases),
            aggregate_generation_metrics=generation_agg.aggregate(),
            aggregate_retrieval_metrics=retrieval_agg.aggregate(),
            individual_results=results,
            evaluation_config=self._config_to_dict(),
            timestamp=datetime.now().isoformat(),
        )

    def _save_intermediate(self, result: EvaluationResult) -> None:
        """Save intermediate result to file.

        Args:
            result: Single evaluation result
        """
        os.makedirs(self.config.output_dir, exist_ok=True)
        path = os.path.join(self.config.output_dir, f"{result.test_case_id}.json")

        data = {
            "test_case_id": result.test_case_id,
            "question": result.question,
            "generated_answer": result.generated_answer,
            "expected_answer": result.expected_answer,
            "generation_metrics": result.generation_metrics,
            "retrieval_metrics": result.retrieval_metrics,
            "latency_ms": result.latency_ms,
            "metadata": result.metadata,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert config to serializable dict."""
        return {
            "judge_type": self.config.judge.judge_type,
            "judge_model": self.config.judge.model_name,
            "output_dir": self.config.output_dir,
        }
