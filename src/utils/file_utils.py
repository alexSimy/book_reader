# file_utils.py
import os
import logging
import datetime
from typing import Optional

from pydot import Union

def write_to_file(index, content, base_dir: Union[str, os.PathLike] = "output") -> Optional[str]:
    try:
        # Get current date as YYYY-MM-DD
        current_date = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")
        
        # Create output directory with date
        output_dir = os.path.join(base_dir,"archive", current_date)

        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{index}_summary.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path
    except Exception as e:
        logging.error(f"ERROR: Unexpected error: {e}")
        return None
