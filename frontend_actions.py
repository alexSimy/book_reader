import time
from book_agent import create_presentation
from pdf_utils import chunk_text, extract_pdf_text, multi_pass_summarize, summarize_chunk
from promps import DEFAULT_CHUNK_PROMPT, DEFAULT_SUMMARY_PROMPT


def process_pdf(pdf_file, chunk_prompt=DEFAULT_CHUNK_PROMPT, summary_prompt=DEFAULT_SUMMARY_PROMPT, max_chars=3000):
    """
    Called by the UI when user uploads a PDF.
    Extracts text and performs multi-pass summarization.
    """
    try:
        # pdf_file is a tempfile object from Gradio.
        # pdf_file.name gives its actual path.
        text = extract_pdf_text(pdf_file.name)

        # Perform a multi-pass summary on the entire text.
        summary = multi_pass_summarize(text, summary_file_name=pdf_file.name.split("\\")[-1].split(".")[0], chunk_prompt=chunk_prompt, summary_prompt=summary_prompt, max_chars=max_chars)

        # Return the summary to Gradio, which will display it.
        return summary

    except Exception as e:
        # Any error while reading/summarizing is returned as text in the UI.
        return f"ERROR extracting or summarizing: {e}"

def test_process_pdf(pdf_file, chunk_prompt=DEFAULT_CHUNK_PROMPT, summary_prompt=DEFAULT_SUMMARY_PROMPT, max_chars=3000):
    """
    Test function for processing PDF.
    """
    # print("===============================")
    # print("Starting test_process_pdf...")
    # print("===============================")

    # print(f"PDF file received: {pdf_file.name}")
    # print(f"Chunk prompt: {chunk_prompt}")
    # print(f"Summary prompt: {summary_prompt}")
    # print(f"Max characters per chunk: {max_chars}")
    # print("===============================")
    try:
        text = extract_pdf_text(pdf_file.name)
        chunks = chunk_text(text, max_chars)
        start = time.time()
        print("Starting chunking test...")
        summary = f"""
            Text from first chunk summary:  

            {summarize_chunk(chunk=chunks[0], chunk_prompt=chunk_prompt) }
            
            Single chunk time: {time.time() - start}
        """ 
        return summary
    except Exception as e:
        return f"ERROR extracting or summarizing: {e}"

def generate_presentation(summary, impressions):
    """
    UI callback: combines AI summary + user impressions.
    """
    try:
        # Pass both user text + AI summary to the LLM agent function.
        return create_presentation(summary, impressions)

    except Exception as e:
        # Return readable error to UI.
        return f"ERROR: {e}"
