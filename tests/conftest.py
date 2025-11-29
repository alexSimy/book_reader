import pytest
from src.llm import llm_openAI

class FakeAsyncOpenAI:
    async def chat_completions_create(self, **kwargs):
        return type("Resp", (), {"choices": [{"message": {"content": "FAKE SUMMARY"}}]})()

@pytest.fixture(autouse=True)
def mock_openai(monkeypatch):
    monkeypatch.setattr(llm_openAI, "client", FakeAsyncOpenAI())
