# file_utils.py
import os

def write_to_file(index, content):
    try:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{index}_summary.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False
