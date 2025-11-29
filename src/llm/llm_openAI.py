# llm_openAI.py

import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

from src.constants.constants import DEFAULT_RESPONSE_TOKENS
from src.constants.prompt_constants import TASK_INSTRUCTION

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")

# Point to LM Studio / llama.cpp OpenAI-compatible endpoint
client = AsyncOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"  # anything non-empty
)

# -----------------------------------------------------
#  CHAT COMPLETION MODE
# -----------------------------------------------------
async def run_chat(messages, max_response_tokens=DEFAULT_RESPONSE_TOKENS):
    """Run an async chat completion using the AsyncOpenAI client.

    `max_response_tokens` controls the `max_tokens` parameter sent to the
    remote endpoint. The client is already async, so we await it directly.
    """
    try:
        resp = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=max_response_tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: Unexpected error: {e}"

# Example helper to summarize text via chat completion
async def run_summarize_llm(prompt, user_prompt=TASK_INSTRUCTION, max_response_tokens=DEFAULT_RESPONSE_TOKENS):
    messages = [
        # {"role": "system", "content": prompt},
        {"role": "user", "content": f"""
            {prompt} 
            {user_prompt}
            """
        }
    ]
    return await run_chat(messages, max_response_tokens=max_response_tokens)