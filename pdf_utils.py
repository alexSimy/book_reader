# pdf_utils.py

# os is imported but not used; safe to keep for future file handling
import os

# fitz is PyMuPDF — used to open and read PDF files
import fitz  # PyMuPDF
# import asyncio

# Import our custom LLM wrapper that calls llama.cpp
from llm_openAI import run_summarize_llm, write_to_file

# Import prompt templates
from promps import DEFAULT_SUMMARY_PROMPT, getChunkPrompt, getSummaryPromt

summaries = []


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

async def summarize_chunk(chunk, chunk_prompt=DEFAULT_SUMMARY_PROMPT):
    """
    Summarizes one chunk using the LLM asynchronously.
    """
    prompt = getChunkPrompt(chunk=chunk, chunk_prompt=chunk_prompt)
    return await run_summarize_llm(prompt, max_tokens=600)


async def multi_pass_summarize(text, summary_file_name, chunk_prompt=DEFAULT_SUMMARY_PROMPT, summary_prompt=DEFAULT_SUMMARY_PROMPT, max_chars=3000):
    """
    Multi-pass chunk summarization:
    1) Break long text into chunks
    2) Summarize each chunk separately
    3) Combine chunk summaries
    4) Summarize the combined summaries again
    """

    # STEP 1: Split raw text into manageable chunks
    chunks = chunk_text(text, max_chars=max_chars) # [13:]  # Skip first 12 chunks for testing
    print(f"Total chunks: {len(chunks)}")

    # STEP 2: Summarize each chunk using a simple for loop (NO THREADING)
    for i, chunk in enumerate(chunks):
        print(f"Trying to summarize chunk {i+1}...")
        try:
            summary = await summarize_chunk(chunk, chunk_prompt=chunk_prompt)
            write_to_file(index=f"""{i+1}""", content=summary)

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
    
    print("Generating final summary...")
    final_summary = await run_summarize_llm(final_prompt, max_tokens=600)
    write_to_file(index=f"promt_{summary_file_name}", content=final_summary)
    
    # Backup: save final summary to a file for inspection
    print(f"Saving final summary to /output/{summary_file_name}_summary.txt")
    write_to_file(index=summary_file_name, content=final_summary)
    print("Final summary saved.")
    
    print("Multi-pass summarization complete. Returning final summary.")
    return final_summary.strip()   # cleanup formatting and return
