

# summarize_utils.py

import asyncio
import logging
from typing import Optional, Tuple
from .pdf_utils import chunk_text
from .file_utils import write_to_file
from src.llm.llm_openAI import run_summarize_llm
from src.llm.prompts_utils import getChunkPrompt, getSummaryPromt
from src.constants.constants import DEFAULT_MAX_CHARACTER_PER_CHUNK, DEFAULT_RESPONSE_TOKENS, NUMBER_OF_RETRIES
from src.constants.prompt_constants import DEFAULT_SUMMARY_PROMPT, TASK_INSTRUCTION


async def summarize_chunk(
        chunk, 
        chunk_prompt=DEFAULT_SUMMARY_PROMPT, 
        user_prompt=TASK_INSTRUCTION, 
        max_response_tokens=DEFAULT_RESPONSE_TOKENS
    )-> str:
    """
    Summarizes one chunk using the LLM asynchronously.
    """
    prompt = getChunkPrompt(chunk=chunk, chunk_prompt=chunk_prompt)
    return await run_summarize_llm(prompt, user_prompt=user_prompt, max_response_tokens=max_response_tokens)

async def summarize_and_validate_chunk(
        chunk, 
        index, 
        chunk_prompt, 
        user_prompt, 
        max_response_tokens
    )-> str:
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
    if summary is None or summary.strip() == "" or any(err.lower() in summary.lower() for err in errorList):
        logging.error(f"Empty summary or error detected for {index+1}.")
        raise Exception("Empty summary or error detected.")

    await asyncio.to_thread(write_to_file, index=f"promt_{index+1}", content=summary)

    logging.info(f"Chunk {index+1} summarized successfully.")
    return summary

single_pass_semaphore = asyncio.Semaphore(5)  # limit concurrency to 5

async def single_pass_summarize(
        chunk, 
        index, 
        chunk_prompt=DEFAULT_SUMMARY_PROMPT, 
        user_prompt=TASK_INSTRUCTION, 
        max_response_tokens=DEFAULT_RESPONSE_TOKENS
    ) -> Tuple[int, Optional[str]]:
    """
    Single-pass summarization (for short texts fitting in one chunk).
    """
    logging.info(f"Trying to summarize chunk {index+1}...")
    try:
        async with single_pass_semaphore:
            summary = await summarize_and_validate_chunk(
                chunk=chunk,
                index=index,
                chunk_prompt=chunk_prompt,
                user_prompt=user_prompt,
                max_response_tokens=max_response_tokens
            )
        return index, summary

    except Exception as e:
        logging.error(f"ERROR: Chunk {index+1} failed: {e}")
        return index, None

retry_semaphore = asyncio.Semaphore(5)  # limit concurrency to 5

async def retry_chunk(
        chunk_index, 
        chunks, 
        chunk_prompt, 
        user_prompt, 
        max_response_tokens
    ) -> Tuple[int, Optional[str]]:
    """
    Retry summarization for a failed chunk up to NUMBER_OF_RETRIES times.
    """

    logging.info(f"Retrying chunk {chunk_index+1}...")
    retries = 0

    while retries < NUMBER_OF_RETRIES:
        try:
            async with retry_semaphore:
                summary = await summarize_and_validate_chunk(
                    chunk=chunks[chunk_index],
                    index=chunk_index,
                    chunk_prompt=chunk_prompt,
                    user_prompt=user_prompt,
                    max_response_tokens=max_response_tokens
                )
            return chunk_index, summary
        except Exception as e:
            retries += 1
            logging.error(f"Retry {retries} failed for chunk {chunk_index+1}: {e}")
    logging.info(f"Chunk {chunk_index+1} failed after retries.")
    return chunk_index, None


async def multi_pass_summarize(
    text, summary_file_name, 
    chunk_prompt=DEFAULT_SUMMARY_PROMPT, 
    summary_prompt=DEFAULT_SUMMARY_PROMPT, 
    user_prompt=TASK_INSTRUCTION, 
    max_chars=DEFAULT_MAX_CHARACTER_PER_CHUNK, 
    max_response_tokens=DEFAULT_RESPONSE_TOKENS
)-> str:
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
    chunks = chunk_text(text, max_chars=max_chars)
    logging.info(f"Total chunks: {len(chunks)}")

    # STEP 2: Summarize each chunk concurrently
        # Create tasks for all chunks
    tasks = [asyncio.create_task(single_pass_summarize(chunk, i, chunk_prompt, user_prompt, max_response_tokens)) for i, chunk in enumerate(chunks)]

        # Await tasks and collect results
    results = await asyncio.gather(*tasks)
        # Process results
    for idx, summary in results:
        if summary is None:
            chunks_to_be_retried.append(idx)
        else:
            summaries.append((idx, summary))
        

    # STEP 2.5: Retry failed chunks
    # Run retries concurrently
    retry_tasks = [asyncio.create_task(retry_chunk(i, chunks, chunk_prompt, user_prompt, max_response_tokens)) for i in chunks_to_be_retried]
    retry_results = await asyncio.gather(*retry_tasks)

    # Collect successful summaries
    for idx, summary in retry_results:
        if summary:
            summaries.append((idx, summary))

    # STEP 3: Combine all first-pass summaries into one big text
    summaries.sort(key=lambda x: x[0])   # sort by chunk index
    combined_list = [s for _, s in summaries]  # extract only summaries
    combined = "\n".join(combined_list)        # join cleanly with newline


    # STEP 4: Ask LLM to summarize the combined summaries into a final result
    final_prompt = getSummaryPromt(combined, summary_prompt=summary_prompt)
    await asyncio.to_thread(write_to_file, index=f"promt_{summary_file_name}", content=final_prompt)
    logging.info("Combined summaries prompt created.")
    
    logging.info("Generating final summary...")
    final_summary = await run_summarize_llm(
        final_prompt, 
        user_prompt=user_prompt, 
        max_response_tokens=max_response_tokens
    )
    
    # Backup: save final summary to a file for inspection
    logging.info(f"Saving final summary to /output/{summary_file_name}_summary.txt")
    await asyncio.to_thread(write_to_file, index=f"result_{summary_file_name}", content=final_summary)
    logging.info("Final summary saved.")
    
    logging.info("Multi-pass summarization complete. Returning final summary.")
    return final_summary.strip()   # cleanup formatting and return
