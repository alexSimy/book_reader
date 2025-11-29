# prompts_utils.py

from src.constants.prompt_constants import DEFAULT_SUMMARY_PROMPT

def getSummaryPromt (combined, summary_prompt=DEFAULT_SUMMARY_PROMPT) : 
  prompt = f"""
    {summary_prompt}
    ### Materialul sursă:
    \"\"\"{combined}\"\"\"
    """
  # f"""
  #   {summary_prompt}
  #   ### Source Material:
  #   \"\"\"{combined}\"\"\"
  #   """
  return prompt

def getChunkPrompt (chunk, chunk_prompt=DEFAULT_SUMMARY_PROMPT) : 
  prompt = f"""
    {chunk_prompt}
    ### Source Material:
    \"\"\"{chunk}\"\"\"
    """
  return prompt