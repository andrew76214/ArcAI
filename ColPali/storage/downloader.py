"""File download operations."""
import os
import shutil
from typing import Dict
from urllib.parse import urlparse

import requests


def download_file(url: str, dest_path: str, chunk_size: int = 8192) -> str:
    """Download a file from URL to destination path.

    Args:
        url: Remote URL to download
        dest_path: Local path to save file
        chunk_size: Download chunk size in bytes

    Returns:
        Path to downloaded file

    Raises:
        requests.HTTPError: If download fails
    """
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
    return dest_path


def download_pdfs(pdfs: Dict[str, str], output_dir: str) -> Dict[str, str]:
    """Download multiple PDF files to output directory.

    Args:
        pdfs: Mapping of name -> URL
        output_dir: Directory to save PDFs

    Returns:
        Mapping of name -> local path
    """
    os.makedirs(output_dir, exist_ok=True)
    saved = {}
    for name, url in pdfs.items():
        pdf_path = os.path.join(output_dir, f"{name}.pdf")
        if not os.path.exists(pdf_path):
            download_file(url, pdf_path)
        saved[name] = pdf_path
    return saved


def add_file_to_storage(path_or_url: str, data_dir: str) -> str:
    """Add a file to storage from local path or remote URL.

    Args:
        path_or_url: Local file path or remote URL
        data_dir: Target directory

    Returns:
        Status message

    Raises:
        ValueError: If path/URL is invalid or empty
        FileNotFoundError: If local path doesn't exist
    """
    if not path_or_url:
        raise ValueError("No path or URL provided")

    os.makedirs(data_dir, exist_ok=True)

    # Remote URL
    if path_or_url.startswith(("http://", "https://")):
        parsed = urlparse(path_or_url)
        filename = os.path.basename(parsed.path) or "downloaded_file"
        dest = os.path.join(data_dir, filename)
        download_file(path_or_url, dest)
        return f"Downloaded {path_or_url} -> {dest}"

    # Local path
    if os.path.exists(path_or_url):
        dest = os.path.join(data_dir, os.path.basename(path_or_url))
        shutil.copy(path_or_url, dest)
        return f"Copied {path_or_url} -> {dest}"

    raise FileNotFoundError(f"Path not found: {path_or_url}")
