# pdf_utils.py
import fitz

from src.constants.constants import DEFAULT_MAX_CHARACTER_PER_CHUNK

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


def chunk_text(text, max_chars=DEFAULT_MAX_CHARACTER_PER_CHUNK):
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

