# Book Reader

A small toolkit for extracting, summarizing and generating presentation materials from books and PDFs using LLMs. The repository contains utilities for PDF extraction, chunked summarization (multi-pass), and a thin orchestration layer that calls LLM backends asynchronously.

This README covers how to set up the project, run it locally, run tests, and contributes guidelines.

**Key features**
- Chunked multi-pass summarization to handle long PDFs/texts
- Asynchronous LLM wrapper (`src/llm/llm_openAI.py`) with support for OpenAI-compatible endpoints
- Utilities for building prompts and generating presentation text
- Test harness and CI integration with `runtest.py` and GitHub Actions

**Project layout**

- `src/` — main package code (LLM wrappers, prompts, utilities)
  - `src/llm/` — LLM wrappers and prompt helpers
  - `src/utils/` — chunking, file I/O, summarization helpers
  - `src/constants/` — configuration constants used by the code
- `tests/` — pytest test suite (includes async tests and mocks)
- `runtest.py` — helper script to run tests with `src` on `PYTHONPATH`
- `.env` — environment defaults (not auto-loaded by shells; loaded by `runtest.py`)

Getting started (development)
-----------------------------

Prerequisites
- Python 3.10+ (project tests run on 3.10/3.11 in CI)
- Virtual environment recommended

Quick setup (Windows PowerShell example)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the app (local development)

```powershell
python app.py
```

Run the test suite

Use the provided helper which ensures `src` is on `PYTHONPATH`:

```powershell
$env:PYTHONPATH="C:\projects\book_reader\src"
C:/projects/book_reader/.venv/Scripts/python.exe runtest.py -q
```

Or simply (from a shell where the venv is active):

```bash
python runtest.py
```

Environment variables
---------------------

This project reads values from `.env` when running `runtest.py` or when modules call `dotenv`. Recommended variables:

- `MODEL_NAME` — naming of the model used by the wrapper (e.g., `gpt-4o-mini` or a local model name)
- `OPENAI_API_KEY` — API key for OpenAI-compatible endpoints
- `BASE_URL` — base URL for OpenAI-compatible endpoints (LM Studio, private LLM server)
- `PYTHONPATH` — used by `runtest.py` to ensure `src/` on imports; `.env` contains `PYTHONPATH=src` by default

Testing & CI
-------------

- Pre-commit runs: this repo uses `pre-commit` to run tests on each commit (configured in `.pre-commit-config.yaml`).
- CI: GitHub Actions workflow at `.github/workflows/ci.yml` runs `runtest.py` and caches pip packages.

Contributing
------------

- Add unit tests for new functionality under `tests/`.
- Keep LLM interactions behind `src/llm/` wrappers so tests can be mocked.
- Avoid committing secrets. Use `.env` for developer defaults and GitHub Actions secrets for CI.

Troubleshooting
---------------

- If imports fail while running tests, ensure `PYTHONPATH` includes `src` (the `runtest.py` loader and `.env` handle this). In PowerShell, load `.env` values into the environment or use the `runtest.py` script.
- To run only a subset of tests, use `pytest -k <expr>` or point to a single test file.

License
-------

See `LICENSE` in the repository root.

Questions
---------

If you'd like me to add more examples (e.g., sample CLI usage, a dockerfile, or step-by-step LLM setup), tell me which you'd prefer and I can scaffold it.
# book_reader

A local, CPU-based book summarizer that converts PDFs into concise multi-pass summaries using an LLM. The project splits documents into chunks, summarizes each chunk, and then combines those summaries into a final high-quality summary. A lightweight Gradio web UI is provided for interacting with the summarization pipeline and generating presentation-ready text.

**Key Features**
- **Local-first**: Runs on CPU with local LLM backends (no cloud API keys required).
- **Multi-pass summarization**: Chunk-level summaries merged into a final coherent summary.
- **Gradio UI**: Simple web interface for uploading PDFs, running summarization, and exporting results.
- **Extensible**: Modular code for swapping LLM backends, tuning chunking, and customizing prompts.

**Quick Start**

1. Clone the repository and change to the project directory:

```powershell
git clone <repo-url>
cd book_reader
```

2. (Optional) Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies (if a `requirements.txt` is present):

```powershell
pip install -r requirements.txt
```

4. Start the app (example — adjust if your environment uses a different entrypoint):

```powershell
python app.py
```

Then open the Gradio UI link printed in the console (usually `http://127.0.0.1:7860`).

**Usage**
- Upload a PDF via the Gradio interface.
- Configure chunk size / overlap and summarization options if available.
- Run the summarizer to produce chunk summaries and a final combined summary.
- Export or copy the generated presentation text as needed.

**Project Layout (important files)**
- `app.py`: App entrypoint that launches the Gradio UI.
- `book_agent.py`: Orchestrates document processing and summarization steps.
- `pdf_utils.py`: PDF parsing and text extraction helpers.
- `llm.py`: LLM backend wrapper(s) and inference utilities.
- `promps.py`: Prompt templates used by the summarization pipeline.
- `frontend_actions.py`: UI helper functions for the Gradio frontend.

**Development Tips**
- Keep virtual environments named `.venv` and add them to `.gitignore` (already configured).
- If a `.venv` folder was tracked by Git, remove it from the index: `git rm -r --cached .venv` and commit.
- Add a `requirements.txt` for reproducible installs or a `pyproject.toml` for modern packaging.

**Contributing**
Contributions are welcome. Please open an issue to discuss large changes before submitting a PR. Keep changes focused, add tests where appropriate, and follow the existing code style.

**License**
The repository includes a `LICENSE` file — please review it for licensing terms.

**Next Steps (suggested)**
- Add `requirements.txt` or `pyproject.toml` describing runtime dependencies.
- Add a lightweight example PDF to `test_resources/` and a small test that runs the pipeline.
- Add CI to run linting and basic smoke tests on pushes.

----
_If you want, I can add a `requirements.txt`, wire up a small example PDF in `test_resources/`, or commit this README update for you._
