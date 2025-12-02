# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Shell Tools Usage Guidelines
**IMPORTANT**: Use the following specialized tools instead of traditional Unix commands: (Install if missing)
| Task Type | Must Use | Do Not Use |
ーーーーーーーーーーーーーーーーー
IFind Files I 'fd' I'find'， "Is-R' l
| Search Text | rg' (ripgrep) | 'grep', '
'ag'l
| Analyze Code Structure | 'ast-grep | 'grep', 'sed' | Interactive Selection | 'fzf | Manual filtering | | Process JSON | "ja'| 'python -m json.tool' | | Process YAML/XML | yq' | Manual parsing |
ニニニニ

## Project Overview

ColPali is a multimodal RAG (Retrieval-Augmented Generation) demo that answers questions about PDF documents (primarily IKEA assembly manuals). It uses ColPali for visual document retrieval and Qwen3-VL for vision-language understanding.

## Prerequisites

- Python 3.9+ (3.10/3.11 recommended)
- System package: `poppler-utils` (required by `pdf2image`)
  ```bash
  sudo apt install -y poppler-utils
  ```
- GPU with CUDA support recommended for reasonable performance

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Application

**Gradio Web Interface:**
```bash
python app.py
```
Opens at http://localhost:7860 with `share=True` for public URL.

## Architecture

```
ColPali/
├── config.py              # Configuration and constants (ModelConfig, StorageConfig, RAGConfig)
├── models/
│   ├── loader.py          # ModelLoader class for lazy model loading
│   ├── retrieval_model.py # RetrievalModel wrapper for ColPali
│   └── vision_model.py    # VisionLanguageModel wrapper for Qwen3-VL
├── storage/
│   ├── downloader.py      # File download utilities (download_pdfs, add_file_to_storage)
│   └── converter.py       # PDF/image conversion (convert_pdfs_to_images)
├── rag_service.py         # RAGService - high-level orchestration, manages model lifecycle
└── app.py                 # Gradio web interface (UI only)
```

### Core Modules

- **config.py**: Centralized configuration using dataclasses
  - `ModelConfig`: Model names, processor settings
  - `StorageConfig`: Data directory, supported extensions
  - `RAGConfig`: Default top_k, max_new_tokens
  - `DEFAULT_PDFS`: Example IKEA PDF URLs

- **rag_service.py**: Main service class (`RAGService`)
  - `index_documents()`: Index documents in a folder
  - `query()`: Execute RAG query, returns (answer, images)
  - Manages model lifecycle with lazy initialization

- **models/**: Model wrappers with clean interfaces
  - `ModelLoader`: Handles lazy loading with proper error messages
  - `RetrievalModel`: Wraps byaldi model, tracks indexing state
  - `VisionLanguageModel`: Wraps Qwen3-VL, consolidates chat template logic

- **storage/**: File operations
  - `download_pdfs()`: Batch download PDFs
  - `add_file_to_storage()`: Add file from path or URL
  - `convert_pdfs_to_images()`: Convert documents to PIL images

- **app.py**: Gradio UI using RAGService singleton

### Model Stack

1. **Retrieval**: `vidore/colpali-v1.2` via byaldi library
2. **Vision-Language**: `Qwen/Qwen3-VL-4B-Instruct` for answer generation

### Data Flow

1. PDFs/images stored in `data/` folder
2. `RAGService.index_documents()` indexes with ColPali and caches images
3. `RAGService.query()` → retrieval → VL model generates answer

### Key Dependencies

- `byaldi`: ColPali RAG model wrapper
- `qwen_vl_utils`: Vision processing for Qwen3-VL
- `pdf2image`: PDF to image conversion (requires poppler)
- `gradio`: Web UI framework
