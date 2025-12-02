"""A small Gradio demo that wraps the `colpali` module.

Usage:
  python app.py

Open http://localhost:7860 to interact. The app will attempt to download example
IKEA PDFs, convert them to images, and (if models are available) run the
multimodal RAG flow. If heavy models are missing, the UI will show a helpful
error message.
"""
import os
from typing import List, Tuple

import gradio as gr
from PIL import Image

import shutil
import requests
from urllib.parse import urlparse
from colpali import DEFAULT_PDFS, download_pdfs, convert_pdfs_to_images, answer_with_multimodal_rag, index_documents, list_available_files


DATA_DIR = "data"


def prepare_data() -> str:
    """Download PDFs (if needed) and convert them to images.

    Returns a short status message.
    """
    try:
        download_pdfs(DEFAULT_PDFS, DATA_DIR)
        _ = convert_pdfs_to_images(DATA_DIR)
        # Index the converted PDFs so searches return passages
        try:
            idx_msg = index_documents(DATA_DIR, overwrite=True)
            avail = list_available_files(DATA_DIR)
            return f"Data prepared and indexed. {idx_msg} Available files: {', '.join(avail)}"
        except Exception as ie:
            return f"Data converted but indexing failed: {ie}"
    except Exception as e:
        return f"Error preparing data: {e}"


def save_uploaded_files(uploaded_files) -> str:
    """Save uploaded PDF files (from Gradio) into `DATA_DIR` and return status."""
    if not uploaded_files:
        return "No files uploaded."
    os.makedirs(DATA_DIR, exist_ok=True)
    saved = []
    try:
        for f in uploaded_files:
            # Gradio may provide a path (str) or a temporary file-like object
            if isinstance(f, str):
                src = f
            elif hasattr(f, "name"):
                src = f.name
            elif isinstance(f, dict) and "name" in f:
                src = f["name"]
            else:
                # Fallback: try to stringify
                src = str(f)

            dest = os.path.join(DATA_DIR, os.path.basename(src))
            shutil.copy(src, dest)
            saved.append(dest)
        return f"Saved {len(saved)} uploaded file(s) to {DATA_DIR}."
    except Exception as e:
        return f"Failed saving uploaded files: {e}"


def save_and_prepare(uploaded_files) -> str:
    """Save uploaded files, convert them to images, and index the collection."""
    save_msg = save_uploaded_files(uploaded_files)
    if save_msg.startswith("Failed"):
        return save_msg

    try:
        _ = convert_pdfs_to_images(DATA_DIR)
    except Exception as e:
        return f"Saved files but conversion failed: {e}"

    try:
        idx_msg = index_documents(DATA_DIR, overwrite=True)
        return f"{save_msg} {idx_msg}"
    except Exception as e:
        return f"Saved and converted files but indexing failed: {e}"


def run_query(text_query: str, top_k: int, max_new_tokens: int) -> Tuple[str, List[Image.Image]]:
    """Run the RAG demo and return (answer_text, images).

    If an error occurs (e.g., missing model), returns the error message and an
    empty image list.
    """
    if not os.path.exists(DATA_DIR) or not any(f.endswith(".pdf") for f in os.listdir(DATA_DIR)):
        try:
            download_pdfs(DEFAULT_PDFS, DATA_DIR)
        except Exception as e:
            return f"Failed to download PDFs: {e}", []

    try:
        all_images = convert_pdfs_to_images(DATA_DIR)
    except Exception as e:
        return f"Failed to convert PDFs to images: {e}", []

    try:
        texts, images = answer_with_multimodal_rag(
            text_query, all_images, top_k=top_k, max_new_tokens=max_new_tokens
        )
        # Return first generated text (consistent with notebook) and images
        answer_text = texts[0] if isinstance(texts, (list, tuple)) and len(texts) > 0 else str(texts)
        return answer_text, images
    except Exception as e:
        return f"Error running multimodal RAG: {e}", []


def build_interface():
    # Check for a local ArcAI logo image next to this script
    logo_path = os.path.join(os.path.dirname(__file__), "ArcAI_logo.jpg")

    with gr.Blocks() as demo:
        # Show logo (if present) and title side-by-side
        with gr.Row():
            if os.path.exists(logo_path):
                # Display a small logo (square) to keep the header compact
                gr.Image(value=logo_path, elem_id="ArcAI_logo", show_label=False, interactive=False, width=64, height=64)
            gr.Markdown("# ColPali — Multimodal RAG demo\nEnter a question about the example manuals and press Submit.")

        with gr.Row():
            query = gr.Textbox(label="Text query", value="How do I assemble the Micke desk?", lines=2)
            submit = gr.Button("Submit")

        # Accept any file types (not limited to PDFs) per user request.
        upload_files = gr.File(label="Upload files (any type)", file_count="multiple")

        # Add file by server-local path or remote URL (bypasses Gradio upload limits)
        path_or_url = gr.Textbox(label="Add file by local path or remote URL", placeholder="/absolute/path/to/file or https://host/path/to/file")
        add_path_btn = gr.Button("Add file from path/URL")

        with gr.Row():
            top_k = gr.Slider(minimum=1, maximum=5, step=1, value=3, label="Top-k retrieved pages")
            max_new_tokens = gr.Slider(minimum=32, maximum=1024, step=32, value=200, label="Max new tokens")

        with gr.Row():
            out_text = gr.Textbox(label="Answer", lines=8)

        # Some Gradio versions don't support `.style(grid=...)` on Gallery.
        # Create the gallery with `columns=3` which is widely supported.
        gallery = gr.Gallery(label="Retrieved pages", columns=3)

        prepare_btn = gr.Button("Prepare data (download + convert)")
        status = gr.Textbox(label="Status", lines=2)

        # Prepare using default PDFs
        prepare_btn.click(fn=prepare_data, inputs=None, outputs=status)

        # Also allow saving uploaded PDFs and converting them
        upload_save_btn = gr.Button("Save uploaded files and convert")
        upload_save_btn.click(fn=save_and_prepare, inputs=upload_files, outputs=status)

        def add_file_from_path_or_url(path_or_url_str: str) -> str:
            """Copy a local file into `DATA_DIR` or download a remote file into it.

            This bypasses Gradio's client upload and is useful for very large files.
            """
            if not path_or_url_str:
                return "No path or URL provided."

            os.makedirs(DATA_DIR, exist_ok=True)

            # Remote URL
            if path_or_url_str.startswith("http://") or path_or_url_str.startswith("https://"):
                try:
                    parsed = urlparse(path_or_url_str)
                    filename = os.path.basename(parsed.path) or "downloaded_file"
                    dest = os.path.join(DATA_DIR, filename)
                    with requests.get(path_or_url_str, stream=True) as r:
                        r.raise_for_status()
                        with open(dest, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                    return f"Downloaded {path_or_url_str} -> {dest}"
                except Exception as e:
                    return f"Failed to download URL: {e}"

            # Local path on the server
            if os.path.exists(path_or_url_str):
                try:
                    dest = os.path.join(DATA_DIR, os.path.basename(path_or_url_str))
                    shutil.copy(path_or_url_str, dest)
                    return f"Copied {path_or_url_str} -> {dest}"
                except Exception as e:
                    return f"Failed to copy local file: {e}"

            return "Provided path not found and not a valid URL."

        add_path_btn.click(fn=add_file_from_path_or_url, inputs=path_or_url, outputs=status)

        def _submit(q, k, m, uploaded):
            # If user uploaded files in this session, save them first
            if uploaded:
                save_msg = save_uploaded_files(uploaded)
                # attempt conversion; ignore convert error here and surface later
            # Ensure we have images converted and indexed
            try:
                _ = convert_pdfs_to_images(DATA_DIR)
            except Exception as e:
                return f"Failed to convert PDFs to images: {e}", []

            try:
                # Attempt to index if not already present; don't force overwrite here
                _ = index_documents(DATA_DIR, overwrite=False)
            except Exception:
                # If indexing fails, continue and let the RAG call report a helpful error
                pass

            txt, imgs = run_query(q, k, m)
            return txt, imgs

        submit.click(fn=_submit, inputs=[query, top_k, max_new_tokens, upload_files], outputs=[out_text, gallery])

    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch(share=True)
