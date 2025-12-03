# presentation_utils.py


from constants.prompt_constants import PRESENTATION_TASK_INSTRUCTION
from llm.prompts_utils import getPresentationPrompt
import src.llm.llm_openAI as llm


async def create_presentation(summary, impressions):
    """
    Combines:
    - AI's final summary from multi-pass chunking
    - Your personal impressions
    Into a polished presentation text suitable for a report or talk.

    This function does NOT perform any PDF reading or multi-pass logic.
    It only coordinates the final presentation-generation prompt.
    """

    prompt = getPresentationPrompt(summary=summary, impressions=impressions)

    # Call the LLM and request up to 600 response tokens of output.
    return await llm.run_summarize_llm(prompt,user_prompt=PRESENTATION_TASK_INSTRUCTION, max_response_tokens=600)
