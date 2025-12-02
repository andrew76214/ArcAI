# ColPali — Multimodal RAG for PDF Documents

A multimodal RAG (Retrieval-Augmented Generation) demo that answers questions about PDF documents (primarily IKEA assembly manuals). Uses ColPali for visual document retrieval and Qwen3-VL for vision-language understanding.

## Prerequisites

- Python 3.9+ (3.10/3.11 recommended)
- System package: `poppler-utils` (required by `pdf2image`)
  ```bash
  sudo apt install -y poppler-utils
  ```
- GPU with CUDA support recommended for reasonable performance
- (Optional) Ollama for evaluation: https://ollama.ai

## Quick Start

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Run the Gradio web interface:
   ```bash
   python app.py
   ```
   Opens at http://localhost:7860 with `share=True` for public URL.

## Architecture

```
ColPali/
├── config.py              # Configuration and constants
├── models/
│   ├── loader.py          # ModelLoader for lazy model loading
│   ├── retrieval_model.py # RetrievalModel wrapper for ColPali
│   └── vision_model.py    # VisionLanguageModel wrapper for Qwen3-VL
├── storage/
│   ├── downloader.py      # File download utilities
│   └── converter.py       # PDF/image conversion
├── rag_service.py         # RAGService - high-level orchestration
├── app.py                 # Gradio web interface
├── evaluation/            # Evaluation framework
│   ├── config.py          # Evaluation configuration
│   ├── evaluator.py       # RAGEvaluator orchestrator
│   ├── test_case.py       # TestCase and TestDataset classes
│   ├── report.py          # Report generation (JSON/Markdown/CSV)
│   ├── judges/            # LLM-as-a-Judge implementations
│   │   ├── ollama_judge.py   # Ollama-based judge (default)
│   │   └── openai_judge.py   # OpenAI-based judge
│   └── metrics/           # Evaluation metrics
│       ├── generation_metrics.py  # Answer quality metrics
│       └── retrieval_metrics.py   # Retrieval quality metrics
├── test_data/             # Test datasets
└── evaluation_results/    # Evaluation output
```

## Model Stack

- **Retrieval**: `vidore/colpali-v1.2` via byaldi library
- **Vision-Language**: `Qwen/Qwen3-VL-4B-Instruct` for answer generation

## Configuration

### RAG Configuration (`config.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `default_top_k` | 3 | Number of pages to retrieve |
| `pages_before` | 1 | Adjacent pages before each result (for cross-page content) |
| `pages_after` | 1 | Adjacent pages after each result |

### Page Overlap

The system automatically includes adjacent pages to handle cross-page content:

```python
# Example: retrieve page 5 with overlap
# Result: pages 4, 5, 6 (with deduplication and sorting)
```

## Evaluation

### Running Evaluation

```bash
python run_evaluation.py
```

### Evaluation Metrics

**Generation Metrics** (scored 1-5 by LLM Judge):
| Metric | Description |
|--------|-------------|
| Correctness | Factual accuracy compared to reference |
| Completeness | Coverage of key points |
| Relevance | Direct answer to the question |
| Coherence | Clarity and structure |

**Retrieval Metrics**:
| Metric | Description |
|--------|-------------|
| Hit Rate | Retrieved at least one correct page |
| Recall@k | Proportion of correct pages retrieved |
| Precision@k | Proportion of retrieved pages that are correct |
| MRR | Mean Reciprocal Rank of first correct result |

### LLM Judge Configuration

Default: Ollama (local LLM)

**Using Ollama (default):**
```bash
# Set remote Ollama host (optional)
export OLLAMA_HOST=http://192.168.1.100:11434

python run_evaluation.py
```

**Using OpenAI:**
```python
from evaluation import EvaluationConfig
from evaluation.config import JudgeConfig

config = EvaluationConfig(
    judge=JudgeConfig(
        judge_type="openai",
        model_name="gpt-4o",
    )
)
```

### Test Dataset Format

```json
{
  "test_cases": [
    {
      "id": "test-001",
      "question": "What is the first step?",
      "expected_answer": "Open the box",
      "expected_pages": [{"doc_id": 0, "page_num": 1}],
      "metadata": {"source": "manual.pdf"}
    }
  ]
}
```

## Data Flow

1. PDFs/images stored in `data/` folder
2. `RAGService.index_documents()` indexes with ColPali and caches images
3. `RAGService.query()`:
   - Retrieve top-k pages
   - Expand with adjacent pages (overlap)
   - VL model generates answer

## Notes

- The application downloads PDFs into the `data/` folder. Do not delete it if you want to persist data.
- GPU with CUDA support is highly recommended. Without a GPU, expect slow performance or memory errors.
- If you encounter `pdf2image` errors, confirm `poppler-utils` is installed and on your PATH.
