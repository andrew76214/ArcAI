"""Gradio web interface for ColPali multimodal RAG demo.

Usage:
    python app.py

Opens at http://localhost:7860 with share=True for public URL.
"""
import os
import shutil
from typing import List, Optional, Tuple

import gradio as gr
from PIL import Image

from config import get_config, DEFAULT_PDFS
from storage import add_file_to_storage, list_available_files
from rag_service import RAGService

# Single service instance for the application
_service: Optional[RAGService] = None


def get_service() -> RAGService:
    """Get or create RAG service singleton."""
    global _service
    if _service is None:
        _service = RAGService()
    return _service


def prepare_data() -> str:
    """Load local PDFs from data directory and index them."""
    config = get_config()
    try:
        service = get_service()
        
        # Check if already indexed
        if service.is_indexed:
            files = list_available_files(config.storage.data_dir)
            return f"Data already indexed. Files: {', '.join(files)}"
        
        # Verify local PDF files exist
        missing = []
        for name, path in DEFAULT_PDFS.items():
            if not os.path.exists(path):
                missing.append(f"{name} ({path})")
        
        if missing:
            return f"Missing files: {', '.join(missing)}"
        
        msg = service.index_documents(overwrite=False)
        files = list_available_files(config.storage.data_dir)
        return f"Data prepared. {msg} Files: {', '.join(files)}"
    except Exception as e:
        return f"Error: {e}"


def save_uploaded_files(uploaded_files) -> str:
    """Save uploaded files to data directory."""
    if not uploaded_files:
        return "No files uploaded."

    config = get_config()
    os.makedirs(config.storage.data_dir, exist_ok=True)

    saved = []
    try:
        for f in uploaded_files:
            if isinstance(f, str):
                src = f
            elif hasattr(f, "name"):
                src = f.name
            elif isinstance(f, dict) and "name" in f:
                src = f["name"]
            else:
                src = str(f)

            dest = os.path.join(config.storage.data_dir, os.path.basename(src))
            shutil.copy(src, dest)
            saved.append(dest)
        return f"Saved {len(saved)} file(s)."
    except Exception as e:
        return f"Failed saving files: {e}"


def save_and_index(uploaded_files) -> str:
    """Save files and re-index."""
    msg = save_uploaded_files(uploaded_files)
    if msg.startswith("No") or msg.startswith("Failed"):
        return msg

    try:
        idx_msg = get_service().index_documents(overwrite=True)
        return f"{msg} {idx_msg}"
    except Exception as e:
        return f"{msg} Indexing failed: {e}"


def add_from_path_or_url(path_or_url: str) -> str:
    """Add file from local path or URL."""
    config = get_config()
    try:
        return add_file_to_storage(path_or_url, config.storage.data_dir)
    except Exception as e:
        return f"Failed: {e}"


def run_query(
    query: str, top_k: int, max_tokens: int
) -> Tuple[str, List[Image.Image]]:
    """Execute RAG query."""
    try:
        service = get_service()
        if not service.is_indexed:
            # Auto-prepare if not indexed
            prepare_data()

        answer, images = service.query(query, top_k=top_k, max_new_tokens=max_tokens)
        return answer, images
    except Exception as e:
        return f"Error: {e}", []


def build_interface() -> gr.Blocks:
    """Build Gradio interface."""
    logo_path = os.path.join(os.path.dirname(__file__), "ArcAI_logo.jpg")

    # Auto-initialize data on startup
    try:
        if not get_service().is_indexed:
            prepare_data()
    except Exception as e:
        print(f"Warning: Failed to auto-index data on startup: {e}")

    with gr.Blocks() as demo:
        with gr.Row():
            if os.path.exists(logo_path):
                gr.Image(
                    value=logo_path,
                    elem_id="ArcAI_logo",
                    show_label=False,
                    interactive=False,
                    width=64,
                    height=64,
                )
            gr.Markdown(
                "# ColPali - Multimodal RAG Demo\n"
                "Enter a question about the example manuals and press Submit."
            )

        with gr.Row():
            query = gr.Textbox(
                label="Query", value="How do I assemble the Micke desk?", lines=2
            )
            submit = gr.Button("Submit")

        upload_files = gr.File(label="Upload files (any type)", file_count="multiple")
        path_or_url = gr.Textbox(
            label="Add file by local path or remote URL",
            placeholder="/absolute/path/to/file or https://host/path/to/file",
        )
        add_btn = gr.Button("Add file from path/URL")

        with gr.Row():
            top_k = gr.Slider(1, 5, step=1, value=3, label="Top-k retrieved pages")
            max_tokens = gr.Slider(32, 1024, step=32, value=200, label="Max new tokens")

        out_text = gr.Textbox(label="Answer", lines=8)
        gallery = gr.Gallery(label="Retrieved pages", columns=3)

        prepare_btn = gr.Button("Prepare data (download + convert)")
        save_btn = gr.Button("Save uploaded files and convert")
        status = gr.Textbox(label="Status", lines=2)

        # Event handlers
        prepare_btn.click(fn=prepare_data, outputs=status)
        save_btn.click(fn=save_and_index, inputs=upload_files, outputs=status)
        add_btn.click(fn=add_from_path_or_url, inputs=path_or_url, outputs=status)
        submit.click(
            fn=run_query,
            inputs=[query, top_k, max_tokens],
            outputs=[out_text, gallery],
        )

    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch(share=True)
