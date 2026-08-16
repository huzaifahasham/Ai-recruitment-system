# AI Recruitment System — Agent 1: CV Screening & Domain Classification Module

A production-ready MVP for automated HR resume screening, structured information extraction, 12-domain classification, confidence scoring, evidence-based reasoning, preliminary screening scoring, and HR recommendation generation.

---

## 🌟 Architecture & Workflow

```text
HR uploads CV (PDF / DOCX / TXT)
       ↓
Validate & Sanitize File
       ↓
Extract Readable Text (PyMuPDF / python-docx / txt)
       ↓
Clean & Normalize Text (text_cleaner)
       ↓
Structured Candidate Extraction (AI Layer / Offline Fallback Engine)
       ↓
12-Domain Classification & Confidence Scoring
       ↓
Extract Evidence-Based Reasoning Points
       ↓
Generate Preliminary Screening Score (0–100) & HR Recommendation
       ↓
Persist Record to Database (SQLite / SQLAlchemy)
       ↓
Render HR Recruitment Dashboard & Inter-Agent Export API
```

---

## 🚀 Supported Tech Domains (Taxonomy)

1. **Artificial Intelligence / Machine Learning**
2. **Data Science / Data Analytics**
3. **Cyber Security**
4. **Software Development**
5. **Web Development**
6. **Mobile App Development**
7. **Cloud / DevOps**
8. **Networking**
9. **Database / SQL**
10. **UI/UX Design**
11. **Quality Assurance / Testing**
12. **Other**

---

## ⚙️ Installation & Setup

### Prerequisites
- **Python**: Version 3.10+
- **pip** package manager

### 1. Clone & Set Environment
Navigate to the project root:
```bash
cd "C:\Users\Huzaifa Hasham\.gemini\antigravity\scratch\ai-recruitment-system"
```

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Generate Sample CVs (Optional)
Generate PDF, DOCX, and TXT sample resumes for testing:
```bash
python generate_sample_cvs.py
```

---

## 🏃 Running the Application

Start the FastAPI application server:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

- Interactive HR Dashboard: `http://127.0.0.1:8000/`
- Interactive OpenAPI / Swagger Documentation: `http://127.0.0.1:8000/docs`

---

## 🧪 Running Automated Tests

Run the full `pytest` suite covering parsers, domain classification, API endpoints, and security checks:

```bash
python -m pytest tests/ -v
```

---

## 🔌 Inter-Agent Export Contract (Agent 2 Integration)

Agent 1 exposes a clean export contract for downstream **Agent 2 (AI Interview & Candidate Evaluation)** consumption:

`GET /api/candidates/{id}/agent1-export`

**Response Payload Contract**:
```json
{
  "candidate_id": "CAND-A1B2C3D4",
  "candidate_name": "Ali Ahmed",
  "email": "ali.ahmed@securitymail.com",
  "primary_domain": "Cyber Security",
  "domain_confidence": 92.5,
  "skills": ["Kali Linux", "Wireshark", "Nmap", "Burp Suite", "OWASP", "SIEM"],
  "screening_score": 85,
  "recommendation": "Strong Match"
}
```

---

## ⚖️ Bias & Fairness Compliance

The system strictly adheres to fair recruitment practices:
- Demographic attributes (gender, age, religion, race, ethnicity, marital status, photograph/appearance) are **strictly excluded** from score calculations.
- Scores and recommendations are computed exclusively from job-relevant qualifications, skills, education, projects, certifications, and domain alignment.
- HR recommendations are explicitly marked as **"AI-assisted preliminary screening recommendations"**.
