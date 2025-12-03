# llm_openAI.py

import os
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
from dotenv import load_dotenv

from src.constants.constants import DEFAULT_RESPONSE_TOKENS
from src.constants.prompt_constants import TASK_INSTRUCTION

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Point to LM Studio / llama.cpp OpenAI-compatible endpoint
if OPENAI_API_KEY is None:
    client = None
else:
    client = AsyncOpenAI(
        base_url= BASE_URL or None,
        api_key=OPENAI_API_KEY  # anything non-empty
)
    
agent_model = OpenAIChatCompletionsModel(
    model=MODEL_NAME, 
    openai_client=client
    )




print("Initialized OpenAI Async Client.")
print(f"Using MODEL_NAME={MODEL_NAME} with BASE_URL={BASE_URL}")

# -----------------------------------------------------
#  CHAT COMPLETION MODE
# -----------------------------------------------------
async def run_chat(messages, max_response_tokens=DEFAULT_RESPONSE_TOKENS):
    """
    Run an async chat completion using the AsyncOpenAI client.

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

async def run_openai_chat(prompt, user_prompt):
    """
    Run an async chat completion using the AsyncOpenAI client.
    """
    agent = Agent(
        name="Book Reader", 
        instructions=prompt, 
        model=agent_model
        )
    
    result = await Runner.run(agent, user_prompt)

    return result.final_output

async def run_summarize_llm(
        prompt, 
        user_prompt=TASK_INSTRUCTION, 
        max_response_tokens=DEFAULT_RESPONSE_TOKENS, 
        method="openai_agents"
    ) -> str:
    """
    Run summarization using the specified method.
    """
    
    if method == "openai_agents":
        return await run_openai_chat(prompt, user_prompt)
    else:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"""
                {user_prompt}
                """
            }
        ]
        if (MODEL_NAME == "medra27b-i1") or (MODEL_NAME == "mistral-7b"):
            messages = [
                {"role": "user", "content": f"""
                    {prompt} 
                    {user_prompt}
                    """
                }
            ]

        return await run_chat(messages, max_response_tokens=max_response_tokens)