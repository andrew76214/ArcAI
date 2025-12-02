#!/usr/bin/env python3
"""CLI for running RAG evaluation."""
import argparse
import sys

from config import get_config
from rag_service import RAGService
from evaluation.config import EvaluationConfig, JudgeConfig
from evaluation.test_case import TestDataset
from evaluation.evaluator import RAGEvaluator
from evaluation.report import ReportGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate ColPali RAG system using LLM-as-a-Judge"
    )
    parser.add_argument(
        "--test-file",
        "-t",
        required=True,
        help="Path to test dataset JSON file",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="evaluation_results",
        help="Output directory for reports (default: evaluation_results)",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="gpt-4o",
        help="OpenAI model for judge (default: gpt-4o)",
    )
    parser.add_argument(
        "--data-dir",
        "-d",
        help="Documents directory (overrides config default)",
    )
    parser.add_argument(
        "--no-intermediate",
        action="store_true",
        help="Don't save intermediate results",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing index",
    )

    args = parser.parse_args()

    # Load test dataset
    print(f"Loading test dataset from {args.test_file}...")
    try:
        dataset = TestDataset.from_json(args.test_file)
    except FileNotFoundError:
        print(f"Error: Test file not found: {args.test_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading test file: {e}")
        sys.exit(1)

    print(f"Loaded {len(dataset)} test cases from '{dataset.dataset_name}'")

    # Initialize RAG service
    print("Initializing RAG service...")
    app_config = get_config()
    if args.data_dir:
        app_config.storage.data_dir = args.data_dir

    rag_service = RAGService(app_config)

    # Check if documents need indexing
    if not rag_service.is_indexed or args.overwrite:
        print(f"Indexing documents from {app_config.storage.data_dir}...")
        try:
            msg = rag_service.index_documents(overwrite=args.overwrite)
            print(msg)
        except Exception as e:
            print(f"Error indexing documents: {e}")
            sys.exit(1)

    # Configure evaluation
    eval_config = EvaluationConfig(
        judge=JudgeConfig(model_name=args.model),
        output_dir=args.output_dir,
        save_intermediate=not args.no_intermediate,
    )

    # Run evaluation
    print(f"\nStarting evaluation with {args.model} as judge...")
    print("-" * 50)

    evaluator = RAGEvaluator(rag_service, eval_config)

    def progress(current, total):
        pct = (current / total) * 100
        print(f"Progress: {current}/{total} ({pct:.1f}%)", end="\r")

    try:
        report = evaluator.evaluate_dataset(dataset, progress_callback=progress)
    except Exception as e:
        print(f"\nError during evaluation: {e}")
        sys.exit(1)

    print("\n")

    # Generate reports
    print("Generating reports...")
    generator = ReportGenerator(report)
    generator.save_all(args.output_dir)

    # Print summary
    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Dataset: {report.dataset_name}")
    print(f"Test Cases: {report.total_test_cases}")
    print(f"Judge Model: {args.model}")

    print("\nGeneration Metrics:")
    for metric, value in report.aggregate_generation_metrics.items():
        print(f"  {metric}: {value:.4f}")

    if report.aggregate_retrieval_metrics:
        print("\nRetrieval Metrics:")
        for metric, value in report.aggregate_retrieval_metrics.items():
            print(f"  {metric}: {value:.4f}")

    # Calculate average latency
    avg_latency = sum(r.latency_ms for r in report.individual_results) / len(
        report.individual_results
    )
    print(f"\nAverage Latency: {avg_latency:.1f} ms")

    print(f"\nReports saved to {args.output_dir}/")
    print("  - report.json (full results)")
    print("  - report.md (readable summary)")
    print("  - metrics.csv (spreadsheet format)")


if __name__ == "__main__":
    main()
