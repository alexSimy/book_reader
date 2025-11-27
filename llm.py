import os           # Used for path handling
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

# num_threads = 2 #os.cpu_count()  # 16 threads on your CPU
# timeout_seconds=1200  # Timeout for LLM response in seconds
STOP_SEQUENCE = "### END_OF_SUMMARY" # A unique string unlikely to appear naturally

# Load the model once globally when your script starts
# This avoids reloading the model for every single summary request
try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=TOKEN_LIMIT,  # Inference context size
        n_ctx_train=TOKEN_LIMIT,    # Training context size
        n_ctx_per_seq=TOKEN_LIMIT, # Per-sequence context size
        n_gpu_layers=0,      # Use CPU only
        n_threads=os.cpu_count(), # os.cpu_count(), # Use all CPU cores (e.g., 16 threads)
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
            n_ctx_train=token_limit,
            n_ctx_per_seq=token_limit,
            n_gpu_layers=0,
            n_threads=os.cpu_count(),
            verbose=False
        )
        print(f"Model reconfigured to {new_model_path} with token limit {token_limit}.")
    except FileNotFoundError:
        print(f"Error: Model not found at {new_model_path}. Check your path.")

def run_llama(prompt, max_tokens=512):
    """
    Runs Llama inference using the llama-cpp-python library binding.
    """
    
    # Define the stop sequence exactly as you did before
    STOP_SEQUENCE = "### END_OF_SUMMARY"
    
    # The library handles the prompt formatting and stop conditions much better internally
    output = llm.create_completion(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.7,        # Sampling parameters
        top_k=40,              # Sampling parameters
        top_p=0.95,            # Sampling parameters 
        stop=[STOP_SEQUENCE], # Pass the stop sequence as a list of strings
        echo=False             # Do not echo the prompt back in the output
    )

    # The result is a dictionary/JSON object, so we access the generated text directly
    generated_text = output['choices'][0]['text']
    
    # Clean up the output in case the stop sequence was partially generated/included
    if generated_text.endswith(STOP_SEQUENCE):
        generated_text = generated_text[:-len(STOP_SEQUENCE)].strip()

    return generated_text.strip()

# region Old subprocess-based implementation (commented out)
# def run_llama(prompt, max_tokens=512):
#     """
#     Runs llama-cli (CPU local model) with the provided prompt
#     and returns the generated text.
#     """

#     if not os.path.exists(LLAMA_EXE):
#         raise FileNotFoundError(f"llama executable not found at: {LLAMA_EXE}")

#     # Check if GGUF model exists
#     if not os.path.exists(MODEL_PATH):
#         raise FileNotFoundError(f"model not found at: {MODEL_PATH}")

#     prompt_with_stop = prompt.strip() + f"\n{STOP_SEQUENCE}\n"

#     # Command to execute llama.cpp
#     # llama-cli command as a list of arguments
#     command = [
#         LLAMA_EXE,
#         "-m", MODEL_PATH,        # model path
#         "-p", prompt_with_stop,            # the prompt to generate from
#         "--temp", "0.7",         # temperature (creativity)
#         "--top-k", "40",         # sampling parameter
#         "--top-p", "0.95",       # sampling parameter
#         "-n", str(max_tokens),   # max tokens to generate
#         "-t", str(num_threads),  # number of CPU threads to use
#         "-r", STOP_SEQUENCE      # stop generation at this sequence
#     ]

#     print("Running command:", " ".join(command))

#     try:
#         # Execute the command, capture output, merge stderr to stdout, set stdin to DEVNULL, and use a timeout
#         process = subprocess.Popen(
#             command,
#             stdout=subprocess.PIPE,   # Capture stdout via a pipe
#             stderr=subprocess.STDOUT, # Merge stderr into stdout
#             text=True,
#             encoding='utf-8', # Explicitly set encoding for text=True mode
#             stdin=subprocess.DEVNULL, # Prevent hangs if it waits for input
#         )

#     # Use the communicate() method with a timeout
#         # This returns a tuple: (stdout, stderr)
#         stdout_output, stderr_output = process.communicate(timeout=timeout_seconds)
#         # stderr_output will be None because we merged it into stdout

#     except subprocess.TimeoutExpired as e:
#         # If a timeout occurs, kill the process group immediately
#         print(f"LLM process timed out after {timeout_seconds} seconds. Terminating process.")
#         if process:
#             process.kill() # Force kill the process
#             # We need to communicate again *after* killing to get the output buffer
#             stdout_output, stderr_output = process.communicate() 
#             return stdout_output.strip() if stdout_output else "Timeout occurred. No output captured."
#         return "Timeout occurred. Process could not be terminated cleanly."
        
#     except Exception as e:
#         if process:
#             process.kill()
#         raise e

#     # Check the return code *after* communication is complete
#     if process.returncode != 0:
#         raise RuntimeError(f"LLM error (exit code {process.returncode}): {stdout_output}")

#     # Return raw text output
#     return stdout_output.strip()
# endregion