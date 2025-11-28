import sys
import types


def _ensure_fitz_mock():
    if 'fitz' in sys.modules:
        return

    class _Page:
        def get_text(self):
            return "DUMMY PAGE TEXT"

    class _Doc(list):
        def __init__(self):
            super().__init__([_Page()])

    fitz_mod = types.ModuleType('fitz')
    fitz_mod.open = lambda path: _Doc()
    sys.modules['fitz'] = fitz_mod


def _ensure_llm_mock():
    if 'llm' in sys.modules:
        return

    async def run_summarize_llm(prompt, max_tokens=600):
        return f"MOCK_LLAMA_OUTPUT tokens={max_tokens} len_prompt={len(prompt)}"

    llm_mod = types.ModuleType('llm')
    llm_mod.run_summarize_llm = run_summarize_llm
    sys.modules['llm'] = llm_mod


_ensure_fitz_mock()
_ensure_llm_mock()
