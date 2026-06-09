import os

# Root directory of prompts (parent of src/ directory)
PROMPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts"))

def load_prompt_template(filename: str) -> str:
    """
    Reads a prompt template file from the prompts directory.
    """
    filepath = os.path.join(PROMPTS_DIR, filename)
    if not os.path.exists(filepath):
        # Fallback to current working directory prompts
        filepath = os.path.join("prompts", filename)
        
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Prompt template file not found: {filename} (searched in {filepath})")
        
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
