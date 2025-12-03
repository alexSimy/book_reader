# prompts_utils.py

from src.constants.prompt_constants import DEFAULT_PRESENTATION_PROMPT, DEFAULT_SUMMARY_PROMPT

def getPresentationPrompt (summary, impressions, presentation_prompt=DEFAULT_PRESENTATION_PROMPT) :
  prompt = f"""
    {presentation_prompt}
    1. Rezumatul cărții:
    \"\"\"{summary}\"\"\"

    2. Impresiile și observațiile personale:
    \"\"\"{impressions}\"\"\"
    """
  return prompt

def getSummaryPromt (combined, summary_prompt=DEFAULT_SUMMARY_PROMPT) : 
  prompt = f"""
    {summary_prompt}
    ### Materialul sursă:
    \"\"\"{combined}\"\"\"
    """
  return prompt

def getChunkPrompt (chunk, chunk_prompt=DEFAULT_SUMMARY_PROMPT) : 
  prompt = f"""
    {chunk_prompt}
    ### Materialul sursă:
    \"\"\"{chunk}\"\"\"
    """
  return prompt