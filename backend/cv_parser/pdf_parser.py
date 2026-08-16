import os

def parse_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at: {file_path}")
        
    text_content = []
    
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            if page_text:
                text_content.append(page_text)
        doc.close()
    except Exception as e:
        # Fallback using pypdf if PyMuPDF fails or is absent
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)
        except Exception as inner_e:
            raise RuntimeError(f"Failed to extract text from PDF: {str(e)} | Fallback error: {str(inner_e)}")
            
    extracted_text = "\n".join(text_content)
    if not extracted_text.strip():
        raise ValueError("PDF file appears to be empty or contains scanned images without extractable text.")
        
    return extracted_text
