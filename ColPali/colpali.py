"""Utility module extracted from `main.ipynb` to support a Gradio demo.

Provides:
- `download_pdfs` to download example IKEA PDFs
- `convert_pdfs_to_images` to rasterize PDFs to PIL images
- `get_grouped_images` to map search results to images
- `answer_with_multimodal_rag` thin wrapper around the notebook generation flow

This module uses lazy loading for heavy model imports and raises helpful errors
if models are not available in the environment.
"""
from typing import Dict, List, Any, Tuple
import os
import requests
from pdf2image import convert_from_path
from PIL import Image

DEFAULT_PDFS: Dict[str, str] = {
    "MALM": "https://www.ikea.com/us/en/assembly_instructions/malm-4-drawer-chest-white__AA-2398381-2-100.pdf",
    "BILLY": "https://www.ikea.com/us/en/assembly_instructions/billy-bookcase-white__AA-1844854-6-2.pdf",
    "BOAXEL": "https://www.ikea.com/us/en/assembly_instructions/boaxel-wall-upright-white__AA-2341341-2-100.pdf",
    "ADILS": "https://www.ikea.com/us/en/assembly_instructions/adils-leg-white__AA-844478-6-2.pdf",
    "MICKE": "https://www.ikea.com/us/en/assembly_instructions/micke-desk-white__AA-476626-10-100.pdf",
}

# Holds a RAG model instance that has been indexed via `index_documents`.
# This allows subsequent calls to reuse the same retrieval model (and index)
# instead of loading a fresh model without an index.
_INDEXED_RAG = None


def download_pdfs(pdfs: Dict[str, str], output_dir: str = "data") -> Dict[str, str]:
    """Download PDF files to `output_dir`. Returns mapping name->path."""
    os.makedirs(output_dir, exist_ok=True)
    saved = {}
    for name, url in pdfs.items():
        pdf_path = os.path.join(output_dir, f"{name}.pdf")
        if not os.path.exists(pdf_path):
            resp = requests.get(url, stream=True)
            resp.raise_for_status()
            with open(pdf_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
        saved[name] = pdf_path
    return saved


def convert_pdfs_to_images(pdf_folder: str) -> Dict[int, List[Image.Image]]:
    """Convert all supported files in `pdf_folder` to lists of PIL Images.

    Supports PDFs and common image formats (png, jpg, jpeg). Returns a
    mapping doc_id -> list[PIL.Image]. Doc ids are assigned by enumerating a
    stable sorted list of supported files in the folder.
    """
    supported_exts = (".pdf", ".png", ".jpg", ".jpeg")
    files = sorted([f for f in os.listdir(pdf_folder) if f.lower().endswith(supported_exts)])
    all_images: Dict[int, List[Image.Image]] = {}
    for doc_id, filename in enumerate(files):
        path = os.path.join(pdf_folder, filename)
        if filename.lower().endswith(".pdf"):
            images = convert_from_path(path)
            all_images[doc_id] = images
        else:
            # Treat a single image file as a 1-page document
            try:
                img = Image.open(path).convert("RGB")
                all_images[doc_id] = [img]
            except Exception:
                # Skip files we can't open and continue
                continue
    return all_images


def get_grouped_images(results: List[Dict[str, Any]], all_images: Dict[int, List[Image.Image]]) -> List[Image.Image]:
    """Map retrieval results (list with 'doc_id' and 'page_num') to PIL images.

    Note: the RAG search used in the notebook returns page_num 1-indexed.
    """
    grouped_images: List[Image.Image] = []
    for result in results:
        doc_id = result["doc_id"]
        page_num = result["page_num"]
        # page_num is 1-indexed in the byaldi output
        grouped_images.append(all_images[doc_id][page_num - 1])
    return grouped_images


def _lazy_load_models():
    """Lazy-load RAG and VL models used in the notebook.

    Returns a tuple: (docs_retrieval_model, vl_model, vl_model_processor)
    Raises RuntimeError with an actionable message if imports fail.
    """
    global _INDEXED_RAG

    # If we've previously indexed documents and stored the RAG instance,
    # reuse it so searches use the existing index. Otherwise load a new one.
    docs_retrieval_model = None
    if _INDEXED_RAG is not None:
        docs_retrieval_model = _INDEXED_RAG
    else:
        try:
            from byaldi import RAGMultiModalModel
        except Exception as e:  # pragma: no cover - runtime environment dependent
            raise RuntimeError(
                "Failed to import 'byaldi'. Install it or ensure it's on PYTHONPATH."
            ) from e

        try:
            from transformers import Qwen3VLForConditionalGeneration, Qwen3VLProcessor
            import torch
        except Exception as e:  # pragma: no cover - runtime environment dependent
            raise RuntimeError(
                "Failed to import Qwen3 VL model classes or torch. Ensure 'transformers' and 'torch' are installed and GPU-friendly build is used if necessary."
            ) from e

        # Load models (this may be slow / require GPU memory)
        docs_retrieval_model = RAGMultiModalModel.from_pretrained("vidore/colpali-v1.2")

    vl_model = Qwen3VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen3-VL-4B-Instruct",
        torch_dtype=torch.bfloat16 if hasattr(torch, "bfloat16") else torch.float16,
    )
    if torch.cuda.is_available():
        vl_model.cuda().eval()

    vl_model_processor = Qwen3VLProcessor.from_pretrained(
        "Qwen/Qwen3-VL-4B-Instruct",
        # The saved model used a (slower) non-fast processor. Explicitly
        # set `use_fast=False` to preserve behavior and avoid the advisory
        # message about `use_fast` changing defaults in future versions.
        use_fast=False,
        min_pixels=224 * 224,
        max_pixels=1024 * 1024,
    )

    return docs_retrieval_model, vl_model, vl_model_processor


def list_available_files(pdf_folder: str) -> List[str]:
    """Return a sorted list of all supported files in `pdf_folder`.

    Supported: PDFs and images (.png, .jpg, .jpeg).
    """
    supported_exts = (".pdf", ".png", ".jpg", ".jpeg")
    if not os.path.exists(pdf_folder):
        return []
    return sorted([f for f in os.listdir(pdf_folder) if f.lower().endswith(supported_exts)])


def index_documents(pdf_folder: str, index_name: str = "image_index", overwrite: bool = False) -> str:
    """Index all supported files (PDFs + images) under `pdf_folder` with the RAG retrieval model.

    This loads only the retrieval model (`byaldi.RAGMultiModalModel`) and
    creates/updates an index so `search()` will return passages. Indexes PDFs
    and image files (.png, .jpg, .jpeg).
    """
    try:
        from byaldi import RAGMultiModalModel
    except Exception as e:  # pragma: no cover - runtime environment dependent
        raise RuntimeError("Failed to import 'byaldi' for indexing. Install it or ensure it's on PYTHONPATH.") from e

    # List all supported files
    supported_files = list_available_files(pdf_folder)
    if not supported_files:
        return "No supported files (PDF, PNG, JPG, JPEG) found to index."

    rag = RAGMultiModalModel.from_pretrained("vidore/colpali-v1.2")
    rag.index(
        input_path=pdf_folder,
        index_name=index_name,
        store_collection_with_index=False,
        overwrite=overwrite,
    )
    # Persist the indexed RAG instance so later searches reuse the index
    global _INDEXED_RAG
    _INDEXED_RAG = rag
    return f"Indexed {len(supported_files)} file(s) from {pdf_folder} into index '{index_name}'."


def answer_with_multimodal_rag(
    text_query: str,
    all_images: Dict[int, List[Image.Image]],
    docs_retrieval_model=None,
    vl_model=None,
    vl_model_processor=None,
    top_k: int = 3,
    max_new_tokens: int = 200,
) -> Tuple[List[str], List[Image.Image]]:
    """Run the multimodal RAG flow to answer `text_query` and return (texts, images).

    If any of the model parameters are None, models will be lazy-loaded. The
    function returns a tuple: (decoded_texts, grouped_images).
    """
    # Lazy load models if not provided
    if docs_retrieval_model is None or vl_model is None or vl_model_processor is None:
        docs_retrieval_model, vl_model, vl_model_processor = _lazy_load_models()

    # Ensure we have an indexed RAG model; if not, raise a helpful error
    if docs_retrieval_model is None:
        raise RuntimeError(
            "No retrieval model available. Ensure `index_documents` has been called "
            "or the RAG model is properly initialized."
        )

    # Retrieve relevant pages
    results = docs_retrieval_model.search(text_query, k=top_k)

    grouped_images = get_grouped_images(results, all_images)

    # Build chat template used by the VL processor
    chat_template = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image} for image in grouped_images
            ]
            + [{"type": "text", "text": text_query}],
        }
    ]

    # Import the vision helper at runtime for clearer error messages
    try:
        from qwen_vl_utils import process_vision_info
    except Exception as e:  # pragma: no cover - runtime environment dependent
        raise RuntimeError(
            "Failed to import 'qwen_vl_utils'. Install it or ensure it's on PYTHONPATH."
        ) from e

    # Prepare inputs and generate
    text = vl_model_processor.apply_chat_template(chat_template, tokenize=False, add_generation_prompt=True)
    image_inputs, _ = process_vision_info(chat_template)

    inputs = vl_model_processor(
        text=[text], images=image_inputs, padding=True, return_tensors="pt"
    )
    # Move to CUDA if available
    try:
        import torch

        if torch.cuda.is_available():
            inputs = inputs.to("cuda")
    except Exception:
        pass

    generated_ids = vl_model.generate(**inputs, max_new_tokens=max_new_tokens)

    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]

    output_text = vl_model_processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )

    return output_text, grouped_images


def answer_with_multimodal_rag_notebook_signature(
    vl_model,
    docs_retrieval_model,
    vl_model_processor,
    grouped_images,
    text_query: str,
    top_k: int = 3,
    max_new_tokens: int = 200,
) -> List[str]:
    """Compatibility wrapper matching the notebook function signature.

    This implements the same flow as the notebook's `answer_with_multimodal_rag`:
    - accepts already-loaded models (`vl_model`, `docs_retrieval_model`, `vl_model_processor`)
    - accepts `grouped_images` as a list of PIL images
    - builds the chat template, prepares inputs, runs generation, and returns
      the decoded texts (list of strings).

    It raises RuntimeError with an actionable message if a required helper
    (like `qwen_vl_utils.process_vision_info`) is not available.
    """
    # Build chat template exactly like the notebook
    chat_template = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image} for image in grouped_images
            ]
            + [{"type": "text", "text": text_query}],
        }
    ]

    try:
        from qwen_vl_utils import process_vision_info
    except Exception as e:
        raise RuntimeError(
            "Failed to import 'qwen_vl_utils'. Install it or ensure it's on PYTHONPATH."
        ) from e

    text = vl_model_processor.apply_chat_template(chat_template, tokenize=False, add_generation_prompt=True)
    image_inputs, _ = process_vision_info(chat_template)

    inputs = vl_model_processor(
        text=[text], images=image_inputs, padding=True, return_tensors="pt"
    )

    try:
        import torch
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")
            vl_model = vl_model.to("cuda")
    except Exception:
        pass

    generated_ids = vl_model.generate(**inputs, max_new_tokens=max_new_tokens)

    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]

    output_text = vl_model_processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )

    return output_text


if __name__ == "__main__":
    print("This module provides helper functions. Import and call them from your app.")
