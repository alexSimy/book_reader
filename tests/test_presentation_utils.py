import asyncio


async def _fake_run(prompt, max_tokens=600, **kwargs):
    return "PRESENTATION_FAKE"


def test_create_presentation_monkeypatch(monkeypatch):
    monkeypatch.setattr('src.llm.llm_openAI.run_summarize_llm', _fake_run)
    from src.utils.presentation_utils import create_presentation

    result = asyncio.run(create_presentation('summary text', 'my impressions'))
    assert 'PRESENTATION_FAKE' in result
