import asyncio


def test_summarize_and_validate_chunk_success(monkeypatch):
    """summarize_and_validate_chunk should return the summary and call write_to_file."""
    from src.utils import summarize_utils

    # Capture calls to write_to_file
    calls = []

    def fake_write_to_file(index, content):
        calls.append((index, content))

    async def fake_summarize_chunk(chunk, chunk_prompt=None, user_prompt=None, max_response_tokens=None):
        return "THIS IS A SUMMARY"

    monkeypatch.setattr(summarize_utils, 'write_to_file', fake_write_to_file)
    monkeypatch.setattr(summarize_utils, 'summarize_chunk', fake_summarize_chunk)

    result = asyncio.run(summarize_utils.summarize_and_validate_chunk(
        chunk="dummy chunk",
        index=0,
        chunk_prompt="cp",
        user_prompt="up",
        max_response_tokens=123
    ))

    assert result == "THIS IS A SUMMARY"
    assert len(calls) == 1
    assert calls[0][0] == "promt_1"
    assert calls[0][1] == "THIS IS A SUMMARY"


def test_summarize_and_validate_chunk_failure(monkeypatch):
    """If summarize_chunk returns empty or error text, helper should raise."""
    from src.utils import summarize_utils

    async def fake_summarize_chunk_empty(*args, **kwargs):
        return ""

    monkeypatch.setattr(summarize_utils, 'summarize_chunk', fake_summarize_chunk_empty)

    try:
        asyncio.run(summarize_utils.summarize_and_validate_chunk(
            chunk="d",
            index=1,
            chunk_prompt="cp",
            user_prompt="up",
            max_response_tokens=10
        ))
        raised = False
    except Exception as e:
        raised = True

    assert raised is True
