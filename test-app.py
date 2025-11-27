from pdf_utils import extract_pdf_text, chunk_text, summarize_chunk
import time

text = extract_pdf_text("./test_resources/test.pdf")
chunks = chunk_text(text, 500)
start = time.time()
print("Starting chunking test...")
print("Number of chunks:", len(chunks))
print(summarize_chunk(chunks[0]))
end = time.time()
print("Single chunk time:", end - start)