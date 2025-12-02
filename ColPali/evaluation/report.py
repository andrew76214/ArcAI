"""Report generation utilities."""
import csv
import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .evaluator import EvaluationReport


class ReportGenerator:
    """Generates evaluation reports in multiple formats."""

    def __init__(self, report: "EvaluationReport"):
        """Initialize report generator.

        Args:
            report: Evaluation report to generate output from
        """
        self.report = report

    def to_json(self, path: str) -> None:
        """Save full report as JSON.

        Args:
            path: Output file path
        """
        data = {
            "dataset_name": self.report.dataset_name,
            "total_test_cases": self.report.total_test_cases,
            "timestamp": self.report.timestamp,
            "aggregate_generation_metrics": self.report.aggregate_generation_metrics,
            "evaluation_config": self.report.evaluation_config,
            "individual_results": [
                {
                    "test_case_id": r.test_case_id,
                    "question": r.question,
                    "generated_answer": r.generated_answer,
                    "expected_answer": r.expected_answer,
                    "generation_metrics": r.generation_metrics,
                    "latency_ms": r.latency_ms,
                    "metadata": r.metadata,
                }
                for r in self.report.individual_results
            ],
        }

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def to_markdown(self, path: str) -> None:
        """Generate human-readable markdown report.

        Args:
            path: Output file path
        """
        lines = [
            f"# Evaluation Report: {self.report.dataset_name}",
            "",
            f"**Generated:** {self.report.timestamp}",
            f"**Total Test Cases:** {self.report.total_test_cases}",
            "",
            "## Aggregate Generation Metrics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
        ]

        for metric, value in self.report.aggregate_generation_metrics.items():
            lines.append(f"| {metric} | {value:.4f} |")

        lines.extend(
            [
                "",
                "## Individual Results Summary",
                "",
                "| Test Case | Overall Score | Correctness | Completeness | Latency (ms) |",
                "|-----------|---------------|-------------|--------------|--------------|",
            ]
        )

        for r in self.report.individual_results:
            gm = r.generation_metrics
            lines.append(
                f"| {r.test_case_id} | {gm.get('overall_score', 'N/A')} | "
                f"{gm.get('correctness', 'N/A')} | {gm.get('completeness', 'N/A')} | "
                f"{r.latency_ms:.1f} |"
            )

        lines.extend(
            [
                "",
                "## Detailed Results",
                "",
            ]
        )

        for r in self.report.individual_results:
            lines.extend(
                [
                    f"### {r.test_case_id}",
                    "",
                    f"**Question:** {r.question}",
                    "",
                    f"**Expected Answer:** {r.expected_answer}",
                    "",
                    f"**Generated Answer:** {r.generated_answer}",
                    "",
                    f"**Reasoning:** {r.generation_metrics.get('reasoning', 'N/A')}",
                    "",
                    "---",
                    "",
                ]
            )

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def to_csv(self, path: str) -> None:
        """Export metrics to CSV for analysis.

        Args:
            path: Output file path
        """
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header
            headers = [
                "test_case_id",
                "question",
                "latency_ms",
                "correctness",
                "completeness",
                "relevance",
                "coherence",
                "overall_score",
            ]
            writer.writerow(headers)

            # Data rows
            for r in self.report.individual_results:
                gm = r.generation_metrics
                row = [
                    r.test_case_id,
                    r.question[:100],  # Truncate long questions
                    f"{r.latency_ms:.1f}",
                    gm.get("correctness", ""),
                    gm.get("completeness", ""),
                    gm.get("relevance", ""),
                    gm.get("coherence", ""),
                    gm.get("overall_score", ""),
                ]
                writer.writerow(row)

    def save_all(self, output_dir: str) -> None:
        """Save all report formats to output directory.

        Args:
            output_dir: Directory to save reports
        """
        os.makedirs(output_dir, exist_ok=True)

        self.to_json(os.path.join(output_dir, "report.json"))
        self.to_markdown(os.path.join(output_dir, "report.md"))
        self.to_csv(os.path.join(output_dir, "metrics.csv"))
