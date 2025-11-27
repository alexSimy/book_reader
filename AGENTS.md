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
