# Agents in this repository

This document describes the agent components in this repository, their responsibilities, and how to extend or add new agents.

Overview
--------

The project contains small autonomous "agents"—coordinating modules that implement higher-level behaviors by composing utility functions and LLM calls. Agents are lightweight orchestration layers rather than full agent frameworks.

Common responsibilities of an agent
- Accept structured inputs (file paths, text fragments, user options)
- Coordinate I/O (read PDFs, write output files)
- Split work into tasks (chunking, summarization passes)
- Call the LLM wrapper asynchronously and gather results
- Handle retries, logging, and error recovery
- Produce the final output artifact (summary, presentation, report)

Existing agents
----------------

- `book_agent.py` / `src/agents/book_agent.py` (may exist in the repository):
  - Orchestrates a multi-pass summarization of a book or PDF.
  - Calls utilities in `src/utils/` for chunking, summarization, and writing outputs.
  - Designed to be callable from the CLI or from the UI layer.

- `presentation` agent (`src/utils/presentation_utils.py`):
  - Builds a presentation text from a final summary and user impressions.
  - Uses `src/llm/llm_openAI.py` wrapper to request a polished presentation.

Design principles
-----------------

- Keep agents thin: move pure utilities into `src/utils/` and keep agents focused on orchestration.
- Agents should be async-friendly: LLM calls and I/O should not block the event loop.
- Agents should accept high-level primitives (text, file paths) and return plain data (strings, dicts) so they are easy to test.
- Avoid side effects in the core agent logic—write files in a small wrapper layer so the core is easier to unit test.

Extending or adding an agent
----------------------------

1. Create a new module under `src/agents/` or `agents/` following existing naming conventions.
2. Implement a single public async function (for example `async def run(args) -> str`) that performs the orchestration and returns a result.
3. Use utilities from `src/utils/` for chunking, summarization, prompt building and file I/O.
4. Keep all LLM interactions behind `src/llm/` wrappers so tests can monkeypatch or mock them.
5. Add unit tests under `tests/` that use monkeypatch to stub `src/llm.*` functions and validate orchestration logic.

Testing agents
--------------

- Use `pytest` and `pytest-asyncio` for async tests.
- Patch LLM calls with deterministic async functions; assert that the agent:
  - Calls the expected utilities
  - Retries failed subtasks according to the retry policy
  - Produces the expected final artifact

Examples and snippets
---------------------

Example of a minimal agent function:

```py
async def run_book_summary(path: str, max_chars: int = 3000):
    text = await read_pdf_text_async(path)
    summary = await multi_pass_summarize(text, "summary", max_chars=max_chars)
    return summary
```

Deployment considerations
------------------------

- For production use, previously mocked LLM wrappers must be pointed to a stable endpoint and proper API keys.
- Use environment variables (`.env`) to store `BASE_URL`, `OPENAI_API_KEY`, and `MODEL_NAME` used by `src/llm/llm_openAI.py`.

Security
--------

- Do not commit API keys or secrets into the repository. Use environment variables or secret management in CI.

Related files
-------------

- `runtest.py` — test runner to run pytest with `src` on `PYTHONPATH`.
- `README.md` — project usage and setup (see repository root).

Questions or contributions
-------------------------

If you want a template for a new agent, or an example unit test for agent behavior, ask and I will create a scaffold and tests for you.
# Agents

This document explains the logical "agents" (components) used in the `book_reader` project, their responsibilities, how they interact, and how to add or extend agents.

**Purpose**: Agents are the small, focused components that perform distinct responsibilities in the pipeline (PDF parsing, chunking, LLM interaction, UI handling, orchestration). Treat an "agent" as a module or class with a clear input/output contract.

**Agents in this repository**
- **BookAgent** (`book_agent.py`): Orchestrates the end-to-end summarization flow — receives parsed text, splits into chunks, calls the LLM wrapper for chunk summaries, and merges chunk summaries to create the final summary.
- **LLM wrappers** (`llm.py`): Provide a thin abstraction around model backends (local `llama_cpp`, other local or remote models). Responsible for prompt construction, batching, and model invocation.
- **PDF utilities** (`pdf_utils.py`): Handles PDF loading and text extraction, cleaning, and simple pre-processing.
- **Frontend actions** (`frontend_actions.py`): Bridges the Gradio UI and backend logic — handles UI events, parameter parsing, and formatting results for display.
- **App entrypoint** (`app.py`): Configures and launches the Gradio app, wires agents together, and exposes endpoints.

**Agent responsibilities (general)**
- Accept a clearly typed input (e.g., file path, plain text, config dict).
- Validate inputs and fail fast with helpful error messages.
- Return structured outputs (dictionaries or dataclasses) rather than raw strings when multiple fields are needed.
- Keep side effects minimal and explicit (e.g., only the App should start servers; agents should not open sockets).

**Interfaces and patterns**
Use simple, consistent function / class methods so agents are easy to swap.

Example expected methods (illustrative):

```python
class PdfAgent:
    def load(self, path: str) -> str:
        """Return extracted plain text from `path`"""

class SummarizerAgent:
    def summarize_chunk(self, chunk_text: str, config: dict) -> str:
        """Return a short summary for `chunk_text`"""

    def merge_summaries(self, summaries: list[str], config: dict) -> str:
        """Combine chunk summaries into a final summary"""
```

Where possible prefer returning `dict` or a small dataclass so the caller can access metadata (token counts, timings, prompts used).

**How to add a new agent**
1. Create a new module (for example `my_agent.py`) or add a class to an existing module.
2. Implement the required methods and keep the public API minimal and documented with a short docstring.
3. Add unit tests that exercise the new agent in isolation (mock downstream/upstream agents as needed).
4. Wire the agent into `app.py` or `book_agent.py` — prefer dependency injection (pass the agent instance into the orchestrator) instead of importing directly.
5. Update `AGENTS.md` and `README.md` to document the new component.

Example wiring (pseudo):

```python
from book_agent import BookAgent
from my_agent import MySummarizer

llm = MySummarizer(config)
orchestrator = BookAgent(summarizer=llm)
```

**Testing agents**
- Test agents in isolation with unit tests.
- Use small fixture PDFs in `test_resources/` to test `pdf_utils.py` and higher-level integration tests.
- For LLM wrappers, provide a small deterministic backend or mock to avoid long-running model calls during CI.

**Debugging tips**
- Log inputs/outputs at the agent boundary (don’t log secrets or full model prompts in CI logs).
- Add small `if __name__ == "__main__"` snippets to agents for quick manual checks.

**Extensibility**
- Keep agents small and focused so swapping one (e.g., a different summarizer) is low friction.
- Prefer composition over inheritance: pass collaborators into agent constructors.

**Contributing**
- Add a short docstring to any new agent and include tests.
- Keep public APIs stable: prefer adding new methods rather than changing existing ones.

If you'd like, I can:
- Add an example `agents/` package with small base classes that define the interfaces above,
- Add a mocked LLM backend for faster local testing, or
- Create a simple unit test demonstrating how to test a new agent using `pytest`.
