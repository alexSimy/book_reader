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
