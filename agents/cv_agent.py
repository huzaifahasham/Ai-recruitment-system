"""
agents/cv_agent.py — Agent 1: CV Screening Agent

Role:
1. Read uploaded CV file (PDF, DOCX, or TXT).
2. Extract candidate information using LLM AI or advanced multi-section text parsing.
3. Replace missing details with 'Not Available'.
4. Store unique candidate details in database for HR dashboard display.
"""

import os
import re
from llm_service import call_llm_json
from database import create_candidate

# PDF Reader
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# DOCX Reader
try:
    import docx
except ImportError:
    docx = None


class CVScreeningAgent:
    """Agent 1: Responsible for CV text extraction and structured parsing."""

    def extract_text_from_file(self, file_path: str) -> str:
        """Extracts text content from PDF, DOCX, or TXT files."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CV file not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        extracted_text = ""

        # 1. PDF Extraction
        if ext == ".pdf":
            if fitz:
                try:
                    doc = fitz.open(file_path)
                    for page in doc:
                        extracted_text += page.get_text() + "\n"
                    doc.close()
                except Exception as e:
                    print(f"[Agent 1] PyMuPDF extraction error: {e}")
            
            # Fallback for plain text PDF reading if fitz failed
            if not extracted_text.strip():
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        extracted_text = f.read()
                except Exception:
                    pass

        # 2. DOCX Extraction
        elif ext in [".docx", ".doc"]:
            if docx and ext == ".docx":
                try:
                    doc = docx.Document(file_path)
                    extracted_text = "\n".join([p.text for p in doc.paragraphs if p.text])
                except Exception as e:
                    print(f"[Agent 1] DOCX extraction error: {e}")

        # 3. Plain Text Extraction
        else:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read()
            except Exception as e:
                print(f"[Agent 1] TXT extraction error: {e}")

        if not extracted_text.strip():
            filename = os.path.basename(file_path)
            extracted_text = f"Candidate File: {filename}"

        return extracted_text.strip()

    def parse_cv_with_ai(self, raw_text: str, filename: str) -> dict:
        """Calls LLM to extract structured fields or uses smart rule fallback."""
        system_prompt = (
            "You are Agent 1 — CV Screening Agent in an AI Recruitment System. "
            "Extract structured candidate information from the CV text. "
            "Return JSON with exact keys: name, email, phone, education, skills, experience, certifications. "
            "If any field is missing or not mentioned, set its value strictly to 'Not Available'."
        )
        user_prompt = f"Extract information from this CV:\n\n{raw_text[:4000]}"

        ai_result = call_llm_json(system_prompt, user_prompt)

        if not ai_result or not isinstance(ai_result, dict):
            # Advanced Heuristic & Section-based Parser
            ai_result = self._advanced_section_parser(raw_text, filename)

        # Standardize missing fields to 'Not Available'
        required_fields = ["name", "email", "phone", "education", "skills", "experience", "certifications"]
        final_info = {}
        for field in required_fields:
            val = ai_result.get(field)
            if not val or str(val).strip().lower() in ["none", "null", "n/a", "unknown", "not mentioned", ""]:
                final_info[field] = "Not Available"
            else:
                final_info[field] = str(val).strip()

        final_info["cv_filename"] = filename
        final_info["status"] = "Pending"
        return final_info

    def _advanced_section_parser(self, text: str, filename: str) -> dict:
        """
        Parses actual CV content section-by-section to extract real, unique information
        without hardcoded generic placeholders.
        """
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # 1. EMAIL Extraction
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        email = email_match.group(0) if email_match else "Not Available"

        # 2. PHONE Extraction
        phone_match = re.search(r'(\+?\d{1,4}[\s.-]?)?\(?\d{2,5}\)?[\s.-]?\d{3,5}[\s.-]?\d{3,5}', text)
        phone = phone_match.group(0) if phone_match else "Not Available"

        # 3. NAME Extraction
        name = "Not Available"
        # Look for explicit Name label
        name_label_match = re.search(r'(?:Name|Full Name|Candidate Name):\s*([^\n\r,]+)', text, re.IGNORECASE)
        if name_label_match:
            name = name_label_match.group(1).strip()
        else:
            # Filter lines that are headers or emails/phones
            for l in lines[:10]:
                if "@" in l or re.search(r'\d{5,}', l):
                    continue
                if any(kw in l.upper() for kw in ["CURRICULUM", "VITAE", "RESUME", "CV", "PROFILE", "SUMMARY", "PAGE"]):
                    continue
                if 2 <= len(l.split()) <= 4 and len(l) <= 40:
                    name = l
                    break

        if name == "Not Available":
            # Clean filename as candidate name fallback
            clean_fn = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()
            name = clean_fn if len(clean_fn) > 2 else "Candidate User"

        # 4. SECTION EXTRACTION (Education, Skills, Experience, Certifications)
        sections = self._extract_text_sections(text)

        # EDUCATION
        education = sections.get("education")
        if not education:
            # Regex match common degrees
            degree_matches = re.findall(r'\b(BS|MS|PhD|B\.S\.|M\.S\.|Bachelor|Master|Diploma|BSc|MSc|Matric|Intermediate)\b[^\n,.]*', text, re.IGNORECASE)
            if degree_matches:
                education = ", ".join(list(set(degree_matches))[:3])
            else:
                education = "Not Available"

        # SKILLS
        skills = sections.get("skills")
        if not skills:
            # Look for technology keywords in raw text
            common_skills = ["Python", "Java", "C++", "JavaScript", "HTML", "CSS", "SQL", "React", "Node", "FastAPI", "Flask", "Django", "Git", "Docker", "AWS", "Linux", "Excel", "Data Analysis", "Machine Learning"]
            found_skills = [s for s in common_skills if re.search(r'\b' + re.escape(s) + r'\b', text, re.IGNORECASE)]
            if found_skills:
                skills = ", ".join(found_skills)
            else:
                skills = "Not Available"

        # EXPERIENCE
        experience = sections.get("experience")
        if not experience:
            exp_match = re.search(r'(\d+\+?\s*(?:years?|yrs?|months?)\s*(?:of)?\s*(?:experience|work)?)', text, re.IGNORECASE)
            if exp_match:
                experience = exp_match.group(1).strip()
            else:
                experience = "Not Available"

        # CERTIFICATIONS
        certifications = sections.get("certifications")
        if not certifications:
            cert_match = re.search(r'(?:certified|certification|certificate):\s*([^\n]+)', text, re.IGNORECASE)
            if cert_match:
                certifications = cert_match.group(1).strip()
            else:
                certifications = "Not Available"

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "education": education[:120],
            "skills": skills[:150],
            "experience": experience[:120],
            "certifications": certifications[:120]
        }

    def _extract_text_sections(self, text: str) -> dict:
        """Helper to break raw text into section blocks based on headers."""
        section_keywords = {
            "education": ["EDUCATION", "ACADEMICS", "QUALIFICATION", "DEGREES"],
            "skills": ["SKILLS", "TECHNICAL SKILLS", "EXPERTISE", "TECHNOLOGIES", "COMPETENCIES"],
            "experience": ["EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT", "WORK HISTORY", "INTERNSHIPS", "PROJECTS"],
            "certifications": ["CERTIFICATIONS", "CERTIFICATES", "COURSES", "LICENSES", "ACHIEVEMENTS"]
        }

        found_sections = {}
        lines = text.split("\n")
        current_section = None
        buffer = []

        for line in lines:
            clean_line = line.strip()
            upper_line = clean_line.upper()

            # Check if line matches a header
            matched_header = None
            for sec_key, keywords in section_keywords.items():
                if any(kw in upper_line for kw in keywords) and len(clean_line) < 40:
                    matched_header = sec_key
                    break

            if matched_header:
                if current_section and buffer:
                    found_sections[current_section] = " ".join(buffer).strip()
                current_section = matched_header
                buffer = []
            elif current_section and clean_line:
                buffer.append(clean_line)

        if current_section and buffer:
            found_sections[current_section] = " ".join(buffer).strip()

        return found_sections

    def process_cv(self, file_path: str) -> dict:
        """Main execution flow for Agent 1."""
        filename = os.path.basename(file_path)
        raw_text = self.extract_text_from_file(file_path)
        candidate_info = self.parse_cv_with_ai(raw_text, filename)
        
        # Save to database
        candidate_id = create_candidate(candidate_info)
        candidate_info["id"] = candidate_id
        
        print(f"[Agent 1] Processed CV for {candidate_info['name']} (ID: {candidate_id})")
        return candidate_info
