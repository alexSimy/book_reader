

# summarize_utils.py

from .pdf_utils import chunk_text
from .file_utils import write_to_file
from src.llm.llm_openAI import run_summarize_llm
from src.llm.prompts_utils import getChunkPrompt, getSummaryPromt
from src.constants.constants import DEFAULT_MAX_CHARACTER_PER_CHUNK, DEFAULT_RESPONSE_TOKENS, NUMBER_OF_RETRIES
from src.constants.prompt_constants import DEFAULT_SUMMARY_PROMPT, TASK_INSTRUCTION


async def summarize_chunk(chunk, chunk_prompt=DEFAULT_SUMMARY_PROMPT, user_prompt=TASK_INSTRUCTION, max_response_tokens=DEFAULT_RESPONSE_TOKENS):
    """
    Summarizes one chunk using the LLM asynchronously.
    """
    prompt = getChunkPrompt(chunk=chunk, chunk_prompt=chunk_prompt)
    return await run_summarize_llm(prompt, user_prompt=user_prompt, max_response_tokens=max_response_tokens)


async def summarize_and_validate_chunk(chunk, index, chunk_prompt, user_prompt, max_response_tokens):
    """
    Helper: summarize a single chunk, validate result, write to file and return summary.\n
    Raises Exception on empty or error responses so caller can handle retries.
    """

    errorList = ["ERROR", "error", "Error", "unexpected", "Unexpected", "failed", "Failed", "FAKE_SUMMARY"]

    summary = await summarize_chunk(
        chunk=chunk,
        chunk_prompt=chunk_prompt,
        user_prompt=user_prompt,
        max_response_tokens=max_response_tokens
    )

    # Validate summary: not None, not empty, and does not contain known error markers
    if summary is None or summary.strip() == "" or any(err in summary for err in errorList):
        raise Exception("Empty summary or error detected.")

    write_to_file(index=f"promt_{index+1}", content=summary)
    print(f"Chunk {index+1} summarized successfully.")
    return summary

async def multi_pass_summarize(
    text, summary_file_name, 
    chunk_prompt=DEFAULT_SUMMARY_PROMPT, 
    summary_prompt=DEFAULT_SUMMARY_PROMPT, 
    user_prompt=TASK_INSTRUCTION, 
    max_chars=DEFAULT_MAX_CHARACTER_PER_CHUNK, 
    max_response_tokens=DEFAULT_RESPONSE_TOKENS
):
    """
    Multi-pass chunk summarization:\n
    1) Break long text into chunks\n
    2) Summarize each chunk separately\n
    3) Combine chunk summaries\n
    4) Summarize the combined summaries again
    """
    summaries = []
    chunks_to_be_retried = []


    # STEP 1: Split raw text into manageable chunks
    chunks = chunk_text(text, max_chars=max_chars) # [13:]  # Skip first 12 chunks for testing
    print(f"Total chunks: {len(chunks)}")

    # STEP 2: Summarize each chunk using a simple for loop (NO THREADING)
    for i, chunk in enumerate(chunks):
        print(f"Trying to summarize chunk {i+1}...")
        try:
            summary = await summarize_and_validate_chunk(
                chunk=chunk,
                index=i,
                chunk_prompt=chunk_prompt,
                user_prompt=user_prompt,
                max_response_tokens=max_response_tokens
            )
            summaries.append((i, summary))

        except Exception as e:
            print(f"ERROR: Chunk {i+1} failed: {e}")
            chunks_to_be_retried.append(i)
    
    # STEP 2.5: Retry failed chunks
    for chunk_index in chunks_to_be_retried:
        print(f"Retrying chunk {chunk_index+1}...")

        retries = 0
        success  = False

        while retries < NUMBER_OF_RETRIES and not success:
            try:
                summary = await summarize_and_validate_chunk(
                    chunk=chunks[chunk_index],
                    index=chunk_index,
                    chunk_prompt=chunk_prompt,
                    user_prompt=user_prompt,
                    max_response_tokens=max_response_tokens
                )
                summaries.append((chunk_index, summary))
                success = True

            except Exception as e:
                retries += 1
                print(f"ERROR: Retry {retries} for chunk {chunk_index+1} retry failed: {e}")

    # STEP 3: Combine all first-pass summaries into one big text
    summaries.sort(key=lambda x: x[0])   # sort by chunk index
    combined_list = [s for _, s in summaries]  # extract only summaries
    combined = "\n".join(combined_list)        # join cleanly with newline


    # STEP 4: Ask LLM to summarize the combined summaries into a final result
    final_prompt = getSummaryPromt(combined, summary_prompt=summary_prompt)
    write_to_file(index=f"promt_{summary_file_name}", content=final_prompt)
    print("Combined summaries prompt created.")
    
    print("Generating final summary...")
    final_summary = await run_summarize_llm(
        final_prompt, 
        user_prompt=user_prompt, 
        max_response_tokens=max_response_tokens
    )
    
    # Backup: save final summary to a file for inspection
    print(f"Saving final summary to /output/{summary_file_name}_summary.txt")
    write_to_file(index=summary_file_name, content=final_summary)
    print("Final summary saved.")
    
    print("Multi-pass summarization complete. Returning final summary.")
    return final_summary.strip()   # cleanup formatting and return
