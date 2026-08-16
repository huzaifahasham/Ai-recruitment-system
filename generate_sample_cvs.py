"""
generate_sample_cvs.py — Tool to generate sample PDF CVs for testing the recruitment system.
"""

import os

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def create_sample_pdf(filename: str, name: str, email: str, phone: str, education: str, skills: str, experience: str, certs: str):
    uploads_dir = os.path.join(os.path.dirname(__file__), "sample_cvs")
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, filename)

    text_content = (
        f"CURRICULUM VITAE\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n\n"
        f"EDUCATION\n{education}\n\n"
        f"TECHNICAL SKILLS\n{skills}\n\n"
        f"WORK EXPERIENCE\n{experience}\n\n"
        f"CERTIFICATIONS\n{certs}\n"
    )

    if fitz:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), text_content, fontsize=12)
        doc.save(file_path)
        doc.close()
    else:
        # Simple plain text fallback saved with .pdf or .txt extension
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)

    print(f"Generated sample CV: {file_path}")
    return file_path


if __name__ == "__main__":
    create_sample_pdf(
        "ali_khan_cv.pdf",
        "Ali Khan",
        "ali.khan@gmail.com",
        "0300-1234567",
        "BS Computer Science, NUST University",
        "Python, SQL, FastApi, JavaScript, Git",
        "1 Year Software Engineer Intern at TechCorp",
        "AWS Certified Cloud Practitioner"
    )
    create_sample_pdf(
        "sara_ahmed_cv.pdf",
        "Sara Ahmed",
        "sara.ahmed@example.com",
        "0312-9876543",
        "MS Data Science, FAST University",
        "Python, PyTorch, SQL, Machine Learning, Tableau",
        "2 Years Junior Data Analyst at Analytics Co",
        "TensorFlow Developer Certificate"
    )
