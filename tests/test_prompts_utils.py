from src.llm import prompts_utils


def test_get_chunk_and_summary_prompts():
    chunk_text = "This is chunk"
    combined = "one\ntwo"
    chunk_prompt = prompts_utils.getChunkPrompt(chunk_text)
    assert 'Source Material' in chunk_prompt or 'Source Material' in chunk_prompt
    summ_prompt = prompts_utils.getSummaryPromt(combined)
    assert 'Materialul' in summ_prompt or 'Source Material' in summ_prompt
