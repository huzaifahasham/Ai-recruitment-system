import os

def parse_txt(file_path: str) -> str:
    """
    Extracts text from a plain TXT file with utf-8 or latin-1 fallback.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"TXT file not found at: {file_path}")
        
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                if content:
                    return content
        except (UnicodeDecodeError, Exception):
            continue
            
    raise ValueError("Failed to read TXT file with standard text encodings.")
