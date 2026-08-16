import os
from backend.ai.llm_client import LLMClient
from backend.ai.fallback_engine import extract_candidate_heuristic

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "cv_extraction.txt")

def extract_cv_information(cleaned_text: str) -> dict:
    """
    Extracts structured candidate details from cleaned CV text.
    Uses LLM API if configured, with automatic fallback to heuristic engine.
    """
    if not cleaned_text:
        return extract_candidate_heuristic("")
        
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            template = f.read()
        prompt = template.format(cv_text=cleaned_text)
        
        result = LLMClient.generate_structured(prompt)
        
        if result and isinstance(result, dict) and "candidate_name" in result:
            # Ensure missing fields fallback to 'Not Provided'
            defaults = {
                "candidate_name": "Not Provided",
                "email": "Not Provided",
                "phone": "Not Provided",
                "location": "Not Provided",
                "education": [],
                "skills": [],
                "programming_languages": [],
                "frameworks_tools": [],
                "work_experience": [],
                "internships": [],
                "projects": [],
                "certifications": [],
                "years_of_experience": 0.0
            }
            for key, default in defaults.items():
                if key not in result or result[key] is None:
                    result[key] = default
            return result
    except Exception as e:
        pass
        
    # Heuristic fallback
    return extract_candidate_heuristic(cleaned_text)
