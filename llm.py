import os           # Used for path handling
import asyncio
from llama_cpp import Llama # Import the new Llama class

TOKEN_LIMIT = 6000  # Context length for the model

# Get the absolute directory of this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Relative path to llama.cpp executable (CPU version)
LLAMA_EXE = os.path.join(BASE_DIR, "llama_cpp", "llama-cli.exe")

# Relative path to GGUF model file 
# - qwen2-1_5b-instruct-q5_k_m.gguf 
# - mistral-7b-instruct-v0.2.Q4_K_M.gguf
# - lmstudio-community\gpt-oss-20b-GGUF\gpt-oss-20b-MXFP4.gguf
# MODEL_PATH = os.path.join("C:\\","Users","asimi",".lmstudio","models","qwen2-1_5b-instruct-q5_k_m.gguf") # os.path.join(BASE_DIR, "llama_cpp", "models", "qwen2-1_5b-instruct-q5_k_m.gguf")
# MODEL_PATH = os.path.join("C:\\","Users","asimi",".lmstudio","models","mistral-7b-instruct-v0.2.Q4_K_M.gguf") # os.path.join(BASE_DIR, "llama_cpp", "models", "qwen2-1_5b-instruct-q5_k_m.gguf")
MODEL_PATH = os.path.join("C:\\","Users","asimi",".lmstudio","models","lmstudio-community","gpt-oss-20b-GGUF","gpt-oss-20b-MXFP4.gguf")

# Load the model once globally when your script starts
# This avoids reloading the model for every single summary request
try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=TOKEN_LIMIT,  # Inference context size
        n_threads=os.cpu_count(), # os.cpu_count(), # Use all CPU cores (e.g., 16 threads)
        n_gpu_layers=0,      # Use CPU only
        verbose=False         # Suppress llama.cpp logging messages
    )
except FileNotFoundError:
    print(f"Error: Model not found at {MODEL_PATH}. Check your path.")
    exit()

def reconfigure_model(new_model_path, token_limit=6000):
    """
    Reconfigures the global LLM instance with a new model path and token limit.
    This allows switching models without restarting the application.
    """
    global llm
    try:
        llm = Llama(
            model_path=new_model_path,
            n_ctx=token_limit,
            n_gpu_layers=0,
            n_threads=os.cpu_count(),
            verbose=False
        )
        print(f"Model reconfigured to {new_model_path} with token limit {token_limit}.")
    except FileNotFoundError:
        print(f"Error: Model not found at {new_model_path}. Check your path.")

async def run_chat(messages, max_tokens=600):
    """
    messages = [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ]
    """

    def _sync_chat():
        resp = llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            top_k=40
        )
        return resp["choices"][0]["message"]["content"].strip()

    return await asyncio.to_thread(_sync_chat)


# Example helper to summarize text via chat completion
async def run_summarize_llm(prompt, max_tokens=600):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Your task is to synthesize a collection of individual, first-pass chapter/chunk summaries provided below into a single, cohesive, professional, and high-quality book summary."}
    ]
    return await run_chat(messages, max_tokens=max_tokens)