import asyncio
from datetime import datetime
import shutil

from src.utils import pdf_utils


def test_chunk_text_splits():
    text = "Line\n" * 500
    chunks = pdf_utils.chunk_text(text, max_chars=200)
    assert isinstance(chunks, list)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 220
import asyncio
import os

from llm import DEFAULT_RESPONSE_TOKENS
import utils.pdf_utils as pdf_utils
import utils.summarize_utils as summarize_utils

from utils.summarize_utils import multi_pass_summarize


def test_chunk_text_basic():
    text = "Line\n" * 200
    chunks = pdf_utils.chunk_text(text, max_chars=100)
    assert isinstance(chunks, list)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 120


def test_multi_pass_summarize_with_mock():
    # Provide a fast async fake run_summarize_llm that returns deterministic text
    async def fake_run_summarize_llm(*args, **kwargs):
        max_response_tokens = kwargs.get('max_response_tokens') or kwargs.get('max_tokens') or DEFAULT_RESPONSE_TOKENS
        prompt = args[0] if args else kwargs.get('prompt','')
        return f"FAKE_SUMMARY tokens={max_response_tokens} len_prompt={len(prompt)}"

    # Patch the run_summarize_llm used in the summarizer module
    summarize_utils.run_summarize_llm = fake_run_summarize_llm

    # Use a moderately sized input so chunking creates multiple chunks
    text = "This is a sentence.\n" * 300

    # Run the async pipeline synchronously in the test
    final = asyncio.run(multi_pass_summarize(text, "testfile", max_chars=500))

    # The fake summary text should be present in the final result
    assert "FAKE_SUMMARY" in final
    # And the file should have been written to the output directory
    current_date = datetime.now().strftime("%d-%m-%Y_%H-%M")

    out_path = os.path.join("output", "archive",current_date, "result_testfile_summary.txt")
    assert os.path.exists(out_path)
    out_folder_path = os.path.join("output", "archive",current_date)
    if os.path.exists(out_folder_path) and os.path.isdir(out_folder_path):
        shutil.rmtree(out_folder_path)
        print(f"{out_folder_path} deleted successfully.")
    else:
        print(f"{out_folder_path} does not exist.")
