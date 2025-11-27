# pdf_utils.py

# os is imported but not used; safe to keep for future file handling
import os

# fitz is PyMuPDF — used to open and read PDF files
import fitz  # PyMuPDF

# Import our custom LLM wrapper that calls llama.cpp
from llm import run_llama

# Import prompt templates
from promps import DEFAULT_CHUNK_PROMPT, DEFAULT_SUMMARY_PROMPT, getChunkPrompt, getSummaryPromt

def extract_pdf_text(pdf_path):
    """
    Extracts all text from a PDF using PyMuPDF.
    """
    text = ""                     # container for all extracted text
    doc = fitz.open(pdf_path)    # open the PDF file

    # Loop through every page in the PDF
    for page in doc:
        text += page.get_text()  # extract plain text from page and append

    return text                  # return complete text of book/document


def chunk_text(text, max_chars=3000):
    """
    Splits text into chunks with max length = max_chars.
    Ensures llama.cpp gets manageable input sizes.
    """
    chunks = []   # list of text chunks
    current = ""  # current chunk being built

    # Split text by newline to avoid breaking sentences weirdly
    for line in text.split("\n"):

        # If adding this line would exceed our limit:
        if len(current) + len(line) > max_chars:
            chunks.append(current)  # save current chunk
            current = ""            # start a new one

        # Add line to current chunk
        current += line + "\n"

    # After finishing the loop, add the last chunk if not empty
    if current.strip() != "":
        chunks.append(current)

    return chunks   # return list of chunks, each <= max_chars


def summarize_chunk(chunk, chunk_prompt=DEFAULT_CHUNK_PROMPT):
    """
    Summarizes one chunk using the LLM.
    """
    # Create a prompt instructing the model to summarize the given chunk.
    prompt = getChunkPrompt(chunk=chunk, chunk_prompt=chunk_prompt)
    # print("Chunk prompt created.")
    # print(prompt)
    # Ask our llama model to generate up to 300 tokens of summary
    return run_llama(prompt, max_tokens=300)


def multi_pass_summarize(text, summary_file_name, chunk_prompt=DEFAULT_CHUNK_PROMPT, summary_prompt=DEFAULT_SUMMARY_PROMPT, max_chars=3000):
    """
    Multi-pass chunk summarization:
    1) Break long text into chunks
    2) Summarize each chunk separately
    3) Combine chunk summaries
    4) Summarize the combined summaries again
    """

    # STEP 1: Split raw text into manageable chunks
    # STEP 1: Chunk text
    chunks = chunk_text(text, max_chars=max_chars) # [13:]  # Skip first 12 chunks for testing
    print(f"Total chunks: {len(chunks)}")

    summaries = [] * len(chunks)

    # STEP 2: Summarize each chunk using a simple for loop (NO THREADING)
    for i, chunk in enumerate(chunks):
        print(f"Trying to summarize chunk {i+1}...")
        try:
            summary = summarize_chunk(chunk,  chunk_prompt=chunk_prompt)
            summaries.append(summary)
            print(f"Chunk {i+1}/{len(chunks)} summarized successfully.")
            print(summary)
        except Exception as e:
            error_msg = f"ERROR: Chunk {i+1} failed: {e}"
            summaries.append(error_msg)
            print(error_msg)

    # STEP 3: Combine all first-pass summaries into one big text
    combined = "\n".join(summaries)

    # STEP 4: Ask LLM to summarize the combined summaries into a final result
    final_prompt = getSummaryPromt(combined, summary_prompt=summary_prompt)
    print("Combined summaries prompt created.")

    # Define the directory path relative to the current working directory
    output_dir = "output"
    # Ensure the output directory exists
    # 'exist_ok=True' prevents an error if the directory is already there
    os.makedirs(output_dir, exist_ok=True)
    
    # Backup: save the combined summaries prompt to a file for inspection
    file_path_prompt = os.path.join(output_dir, f"promt_{summary_file_name}_summary.txt")
    with open(file_path_prompt, "w") as f:
        f.write(final_prompt)
    print("Combined summaries prompt file created.")
    
    print("Generating final summary...")
    # Request a longer final summary (600 tokens)
    final_summary = run_llama(final_prompt, max_tokens=2048)
    
    # Backup: save final summary to a file for inspection
    print(f"Saving final summary to /output/{summary_file_name}_summary.txt")
    
    file_path = os.path.join(output_dir, f"{summary_file_name}_summary.txt")

    # Write the file using the full, safe path
    with open(file_path, "w") as f:
        f.write(final_summary)
    
    print("Final summary saved.")
    
    print("Multi-pass summarization complete. Returning final summary.")
    return final_summary.strip()   # cleanup formatting and return
