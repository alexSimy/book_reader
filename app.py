# app.py

# Importing Gradio (used to build the UI)
import gradio as gr
from frontend_actions import generate_presentation, process_pdf, test_process_pdf
from promps import  DEFAULT_SUMMARY_PROMPT


summary_completed = """waiting for summary..."""

# === Gradio Interface ===
# Build a complete UI using Gradio Blocks (modern, flexible UI API)
with gr.Blocks(title="Local Book Summarizer AI") as ui:

    # Static HTML header with emojis
    gr.Markdown("# 📚 Local Book Summarizer (CPU)")

    # ------------- TAB 1: Summarize PDF ------------------
    with gr.Tab("1️⃣ Summarize Book"):

        summary_output = gr.Textbox(label="Generated Summary", lines=15, value=summary_completed)

        with gr.Accordion(open=False, label="Advanced Settings"):
            max_characters_perchunk = gr.Number(label="Characters per chunk", value=3000)  
            # chunk_prompt = gr.Textbox(label="Chunk prompt", value=DEFAULT_SUMMARY_PROMPT, lines=15, interactive=True)  
            summary_prompt = gr.Textbox(label="Summary prompt", value=DEFAULT_SUMMARY_PROMPT, lines=15, interactive=True, buttons="copy")  

    # ------------- TAB 2: Create Presentation ------------------
    with gr.Tab("2️⃣ Create Presentation Text"):

        # User manually pastes the summary from Tab 1
        summary_in = gr.Textbox(label="Paste AI Summary", lines=15)
        summary_output.change(lambda x: x, inputs=summary_output, outputs=summary_in)
        
        # User writes their impressions or thoughts
        impressions_in = gr.Textbox(label="Your Impressions", lines=10)

        # Output field to display generated presentation text
        presentation_out = gr.Textbox(label="Presentation Output", lines=20)

        # Button triggers presentation generation
        presentation_btn = gr.Button("Generate Presentation")

        # Link button click to function with I/O
        presentation_btn.click(
            generate_presentation,
            inputs=[summary_in, impressions_in],
            outputs=[presentation_out]
        )
    with gr.Sidebar():
        # Upload input for PDF file
        pdf_input = gr.File(label="Upload PDF Book")

        # Button that triggers processing
        summarize_btn = gr.Button("Summarize PDF")
        # Bind button -> function with input/output mapping
        summarize_btn.click(
            process_pdf,        # callback function
            inputs=[pdf_input, summary_prompt, summary_prompt, max_characters_perchunk], # list of UI inputs
            outputs=[summary_output]  # list of UI outputs
        )

        # Button that triggers processing
        test_summarize_btn = gr.Button("Test Summarizing process")
        test_summarize_btn.click(
            test_process_pdf,        # callback function
            inputs=[pdf_input, summary_prompt, summary_prompt, max_characters_perchunk], # list of UI inputs
            outputs=[summary_output]  # list of UI outputs
        )
# Launch the web server:
# - server_name="0.0.0.0" allows LAN access
# - server_port=7860 defines the port
ui.launch(server_name="0.0.0.0", server_port=7860)
