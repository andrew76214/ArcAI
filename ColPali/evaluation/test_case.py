"""Test case data structures for evaluation."""
from dataclasses import dataclass, field
from typing import List, Dict, Any
import json


@dataclass
class TestCase:
    """Single evaluation test case."""

    id: str
    question: str
    expected_answer: str
    metadata: Dict[str, Any] = field(default_factory=dict)


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
            test_cases.append(
                TestCase(
                    id=tc["id"],
                    question=tc["question"],
                    expected_answer=tc["expected_answer"],
                    metadata=tc.get("metadata", {}),
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
            "test_cases": [
                {
                    "id": tc.id,
                    "question": tc.question,
                    "expected_answer": tc.expected_answer,
                    "metadata": tc.metadata,
                }
                for tc in self.test_cases
            ],
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def __len__(self) -> int:
        return len(self.test_cases)

    def __iter__(self):
        return iter(self.test_cases)
