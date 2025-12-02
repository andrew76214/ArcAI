"""PDF and image conversion utilities."""
import os
from typing import Dict, List, Tuple

from pdf2image import convert_from_path
from PIL import Image


def list_available_files(
    folder: str,
    supported_extensions: Tuple[str, ...] = (".pdf", ".png", ".jpg", ".jpeg"),
) -> List[str]:
    """Return sorted list of supported files in folder.

    Args:
        folder: Directory to scan
        supported_extensions: File extensions to include

    Returns:
        Sorted list of filenames
    """
    if not os.path.exists(folder):
        return []
    return sorted(
        [f for f in os.listdir(folder) if f.lower().endswith(supported_extensions)]
    )


def convert_pdfs_to_images(
    folder: str,
    supported_extensions: Tuple[str, ...] = (".pdf", ".png", ".jpg", ".jpeg"),
) -> Dict[int, List[Image.Image]]:
    """Convert all supported files in folder to PIL Images.

    Args:
        folder: Directory containing PDFs/images
        supported_extensions: File extensions to process

    Returns:
        Mapping of doc_id -> list of PIL Images
    """
    files = list_available_files(folder, supported_extensions)
    all_images: Dict[int, List[Image.Image]] = {}

    for doc_id, filename in enumerate(files):
        path = os.path.join(folder, filename)
        if filename.lower().endswith(".pdf"):
            images = convert_from_path(path)
            all_images[doc_id] = images
        else:
            try:
                img = Image.open(path).convert("RGB")
                all_images[doc_id] = [img]
            except Exception:
                continue

    return all_images
