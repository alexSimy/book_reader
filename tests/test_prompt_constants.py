def test_prompt_constants_contents():
    import src.constants.prompt_constants as prompts

    assert 'Generează' in prompts.TASK_INSTRUCTION or isinstance(prompts.TASK_INSTRUCTION, str)
    assert 'rezumat' in prompts.DEFAULT_SUMMARY_PROMPT or isinstance(prompts.DEFAULT_SUMMARY_PROMPT, str)
