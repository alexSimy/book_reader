import asyncio

import book_agent


def test_create_presentation_mock():
    async def fake_run_summarize_llm(prompt, max_tokens=600):
        return "PRESENTATION_TEXT_FAKE"

    # Patch the run_summarize_llm used inside book_agent
    book_agent.run_summarize_llm = fake_run_summarize_llm

    result = asyncio.run(book_agent.create_presentation("summary text", "my impressions"))
    assert "PRESENTATION_TEXT_FAKE" in result
