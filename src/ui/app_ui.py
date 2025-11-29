# app_ui.py

# Importing Gradio (used to build the UI)
import gradio as gr

from .ui_actions import generate_presentation, process_pdf, test_process_pdf
from src.constants.constants import DEFAULT_MAX_CHARACTER_PER_CHUNK, DEFAULT_RESPONSE_TOKENS, SUMMARY_PLACEHOLDER
from src.constants.prompt_constants import DEFAULT_SUMMARY_PROMPT, TASK_INSTRUCTION


def define_app_ui():
    # === Gradio Interface ===
    # Build a complete UI using Gradio Blocks (modern, flexible UI API)
    with gr.Blocks(title="Local Book Summarizer AI") as ui:

        # Static HTML header with emojis
        gr.Markdown("# 📚 Local Book Summarizer (CPU)")

        # ------------- TAB 1: Summarize PDF ------------------
        with gr.Tab("1️⃣ Summarize Book"):

            summary_output = gr.Textbox(label="Generated Summary", lines=15, value=SUMMARY_PLACEHOLDER)

            with gr.Accordion(open=False, label="Advanced Settings"):
                max_characters_perchunk = gr.Number(label="Characters per chunk", value=DEFAULT_MAX_CHARACTER_PER_CHUNK)  
                max_response_tokens = gr.Number(label="Maximum tokens for responses", value=DEFAULT_RESPONSE_TOKENS)  
                user_prompt = gr.Textbox(label="User prompt", value=TASK_INSTRUCTION, lines=2, interactive=True)  
                context_prompt = gr.Textbox(label="Context prompt", value=DEFAULT_SUMMARY_PROMPT, lines=15, interactive=True, buttons=["copy"])  

        # ------------- TAB 2: Create Presentation ------------------
        with gr.Tab("2️⃣ Create Presentation Text"):

            # User manually pastes the summary from Tab 1
            summary_in = gr.Textbox(label="Paste AI Summary", lines=15, value=SUMMARY_PLACEHOLDER)
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
                inputs=[pdf_input, context_prompt, context_prompt, user_prompt, max_characters_perchunk, max_response_tokens], # list of UI inputs
                outputs=[summary_output]  # list of UI outputs
            )

            # Button that triggers processing
            test_summarize_btn = gr.Button("Test Summarizing process")
            test_summarize_btn.click(
                test_process_pdf,        # callback function
                inputs=[pdf_input, context_prompt, user_prompt, max_characters_perchunk, max_response_tokens], # list of UI inputs
                outputs=[summary_output]  # list of UI outputs
            )
    return ui

