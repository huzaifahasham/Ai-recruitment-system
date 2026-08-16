import re
import unicodedata

def clean_cv_text(text: str) -> str:
    """
    Cleans and normalizes extracted text from candidate CVs.
    Handles:
    - Unicode normalization
    - Stripping non-printable ASCII control characters
    - Replacing tabs with single spaces
    - Collapsing duplicate horizontal whitespace
    - Removing redundant blank lines (more than 2 consecutive newlines)
    - Trimming leading and trailing whitespace
    """
    if not text:
        return ""
        
    # Unicode NFKD normalization
    text = unicodedata.normalize('NFKD', text)
    
    # Remove control characters except standard whitespace (\n, \r, \t)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    
    # Normalize carriage returns
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Replace horizontal spaces (2 or more) with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Clean space at the end/beginning of lines
    lines = [line.strip() for line in text.split('\n')]
    
    # Remove multiple consecutive blank lines (allow max 1 blank line between sections)
    cleaned_lines = []
    blank_count = 0
    for line in lines:
        if line == "":
            blank_count += 1
            if blank_count <= 1:
                cleaned_lines.append(line)
        else:
            blank_count = 0
            cleaned_lines.append(line)
            
    result = '\n'.join(cleaned_lines).strip()
    return result
