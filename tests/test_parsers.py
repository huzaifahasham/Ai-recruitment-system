import os
import pytest
from backend.cv_parser.pdf_parser import parse_pdf
from backend.cv_parser.docx_parser import parse_docx
from backend.cv_parser.txt_parser import parse_txt
from backend.cv_parser.text_cleaner import clean_cv_text

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_cvs"))

def test_pdf_parsing():
    pdf_file = os.path.join(SAMPLE_DIR, "sample_cyber_security.pdf")
    if os.path.exists(pdf_file):
        text = parse_pdf(pdf_file)
        assert "Ali Ahmed" in text
        assert "Cyber Security" in text or "Penetration Testing" in text

def test_docx_parsing():
    docx_file = os.path.join(SAMPLE_DIR, "sample_aiml_engineer.docx")
    if os.path.exists(docx_file):
        text = parse_docx(docx_file)
        assert "Sara Khan" in text
        assert "TensorFlow" in text or "PyTorch" in text

def test_txt_parsing():
    txt_file = os.path.join(SAMPLE_DIR, "sample_web_developer.txt")
    if os.path.exists(txt_file):
        text = parse_txt(txt_file)
        assert "Zubair Raza" in text
        assert "React" in text or "Node.js" in text

def test_text_cleaning():
    raw = "   Ali Ahmed   \n\n\n\nEmail:\tali@test.com  \r\n   Phone:  12345   "
    cleaned = clean_cv_text(raw)
    assert "   " not in cleaned
    assert "ali@test.com" in cleaned
    assert "\t" not in cleaned
