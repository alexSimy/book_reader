# book_agent.py

# Import the helper function that sends prompts to llama.cpp
from llm import run_llama  # Import the LLM wrapper function


def create_presentation(summary, impressions):
    """
    Combines:
    - AI's final summary from multi-pass chunking
    - Your personal impressions
    Into a polished presentation text suitable for a report or talk.

    This function does NOT perform any PDF reading or multi-pass logic.
    It only coordinates the final presentation-generation prompt.
    """

    # Build a detailed prompt for the model.
    # Notes:
    # - f-string inserts the user summary + impressions
    # - Triple quotes ensure chunked text is safely delimited
    # - The model is instructed to create a clean, structured output
    prompt = f"""
    You are a professional writer.

    Write a polished, well-structured presentation text about a book.

    Use:
    1. This book summary:
    \"\"\"{summary}\"\"\"

    2. These personal impressions:
    \"\"\"{impressions}\"\"\"

    Your task:
    - Combine them smoothly
    - Maintain neutral, professional tone
    - Use clear structure (introduction, key ideas, conclusion)
    - Make it suitable for a presentation or report

    OUTPUT:
    """

    # Call the LLM and request up to 500 tokens of output.
    # run_llama() handles building the llama.cpp command and returning text.
    return run_llama(prompt, max_tokens=500)
