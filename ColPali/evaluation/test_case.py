"""Test case data structures for evaluation."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
import json


@dataclass
class TestCase:
    """Single evaluation test case."""

    id: str
    question: str
    expected_answer: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Expected pages for retrieval evaluation: list of (doc_id, page_num) tuples
    # page_num is 1-indexed to match the retrieval system
    expected_pages: Optional[List[Tuple[int, int]]] = None


@dataclass
class TestDataset:
    """Collection of test cases."""

    version: str
    dataset_name: str
    test_cases: List[TestCase]
    description: str = ""

    @classmethod
    def from_json(cls, path: str) -> "TestDataset":
        """Load dataset from JSON file.

        Args:
            path: Path to JSON file

        Returns:
            TestDataset instance
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        test_cases = []
        for tc in data["test_cases"]:
            # Parse expected_pages if present
            expected_pages = None
            if "expected_pages" in tc and tc["expected_pages"]:
                expected_pages = [
                    (p["doc_id"], p["page_num"]) for p in tc["expected_pages"]
                ]

            test_cases.append(
                TestCase(
                    id=tc["id"],
                    question=tc["question"],
                    expected_answer=tc["expected_answer"],
                    metadata=tc.get("metadata", {}),
                    expected_pages=expected_pages,
                )
            )

        return cls(
            version=data.get("version", "1.0"),
            dataset_name=data.get("dataset_name", "Unnamed"),
            test_cases=test_cases,
            description=data.get("description", ""),
        )

    def to_json(self, path: str) -> None:
        """Save dataset to JSON file.

        Args:
            path: Path to output JSON file
        """
        data = {
            "version": self.version,
            "dataset_name": self.dataset_name,
            "description": self.description,
            "test_cases": [],
        }

        for tc in self.test_cases:
            tc_data = {
                "id": tc.id,
                "question": tc.question,
                "expected_answer": tc.expected_answer,
                "metadata": tc.metadata,
            }
            # Include expected_pages if present
            if tc.expected_pages:
                tc_data["expected_pages"] = [
                    {"doc_id": doc_id, "page_num": page_num}
                    for doc_id, page_num in tc.expected_pages
                ]
            data["test_cases"].append(tc_data)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def __len__(self) -> int:
        return len(self.test_cases)

    def __iter__(self):
        return iter(self.test_cases)
