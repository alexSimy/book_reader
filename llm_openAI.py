# llm_openAI.py

import asyncio
import os
from openai import OpenAI

from promps import TASK_INSTRUCTION

# Point to LM Studio / llama.cpp OpenAI-compatible endpoint
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"  # anything non-empty
)

MODEL_NAME = 'medra27b-i1' #"mistral-7b"

def write_to_file(index, content):
    try:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"promt_{index}_summary.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False
# -----------------------------------------------------
#  CHAT COMPLETION MODE
# -----------------------------------------------------
async def run_chat(messages, max_tokens=600, index='0'):
    def _sync_chat():
        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            response = resp.choices[0].message.content.strip()
            write_to_file(index=index, content=response)
            return response
        except Exception as e:
            return f"ERROR: Unexpected error: {e}"
    return await asyncio.to_thread(_sync_chat)


# Example helper to summarize text via chat completion
async def run_summarize_llm(prompt, max_tokens=600, index='0'):
    messages = [
        # {"role": "system", "content": prompt},
        {"role": "user", "content": f"""
            {prompt} 
            {TASK_INSTRUCTION}
            """
        }
    ]
    print("Running summarize LLM...")
    print(messages)
    return await run_chat(messages, max_tokens=max_tokens, index=index)