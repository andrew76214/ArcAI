# ColPali — Notebook project

Short setup and run instructions for the `main.ipynb` notebook.

Prerequisites (Linux):

- Python 3.9+ (3.10/3.11 recommended)
- System package: `poppler-utils` (required by `pdf2image`) — install via your package manager, e.g. `sudo apt install -y poppler-utils`

Quick start:

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Upgrade pip and install Python requirements:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Open the notebook:

```bash
jupyter lab  # or jupyter notebook
```

Notes:
- The notebook downloads PDFs into the `data/` folder. If you want to persist or share `data/`, do not delete it.
- Some model artifacts (e.g., Qwen/Qwen3-VL) require a GPU and a compatible `torch` build. If you do not have a GPU, expect slow performance or memory errors.
- If you run into `pdf2image` errors, confirm `poppler` is installed and on your PATH.

If you want, I can also add a small `env_setup.sh` script to automate steps 1–2.

---
Created files:
- `requirements.txt`
- `.gitignore`
