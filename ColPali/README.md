# ColPali — Multimodal RAG for PDF Documents

A multimodal RAG (Retrieval-Augmented Generation) demo that answers questions about PDF documents (primarily IKEA assembly manuals). Uses ColPali for visual document retrieval and Qwen3-VL for vision-language understanding.

## Prerequisites

- Python 3.9+ (3.10/3.11 recommended)
- System package: `poppler-utils` (required by `pdf2image`)
  ```bash
  sudo apt install -y poppler-utils
  ```
- GPU with CUDA support recommended for reasonable performance

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
└── app.py                 # Gradio web interface
```

## Model Stack

- **Retrieval**: `vidore/colpali-v1.2` via byaldi library
- **Vision-Language**: `Qwen/Qwen3-VL-4B-Instruct` for answer generation

## Data Flow

1. PDFs/images stored in `data/` folder
2. `RAGService.index_documents()` indexes with ColPali and caches images
3. `RAGService.query()` → retrieval → VL model generates answer

## Notes

- The application downloads PDFs into the `data/` folder. Do not delete it if you want to persist data.
- GPU with CUDA support is highly recommended. Without a GPU, expect slow performance or memory errors.
- If you encounter `pdf2image` errors, confirm `poppler-utils` is installed and on your PATH.
