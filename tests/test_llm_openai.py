import asyncio


def test_run_summarize_calls_run_chat(monkeypatch):
    import src.llm.llm_openAI as llm

    async def fake_run_chat(*args, **kwargs):
        return "LLM_FAKE"

    monkeypatch.setattr(llm, 'run_chat', fake_run_chat)

    result = asyncio.run(llm.run_summarize_llm(prompt='hello', user_prompt='x', max_response_tokens=123, method="other_method"))
    assert result == 'LLM_FAKE'
