import os
import json
from backend.ai.llm_client import LLMClient
from backend.ai.fallback_engine import evaluate_screening_heuristic

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "screening_evaluation.txt")

VALID_RECOMMENDATIONS = ["Strong Match", "Potential Match", "Needs HR Review", "Low Match"]

def evaluate_candidate_screening(extracted_info: dict, domain_info: dict) -> dict:
    """
    Evaluates preliminary 0-100 screening score and HR recommendation.
    Enforces strict bias protection logic (stripping non-job relevant demographic fields).
    """
    # Sanitize input to remove any non-job relevant demographic attributes
    safe_profile = {
        "education": extracted_info.get("education", []),
        "skills": extracted_info.get("skills", []),
        "programming_languages": extracted_info.get("programming_languages", []),
        "frameworks_tools": extracted_info.get("frameworks_tools", []),
        "work_experience": extracted_info.get("work_experience", []),
        "projects": extracted_info.get("projects", []),
        "certifications": extracted_info.get("certifications", []),
        "years_of_experience": extracted_info.get("years_of_experience", 0.0),
        "classified_domain": domain_info.get("primary_domain"),
        "domain_confidence": domain_info.get("confidence")
    }

    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            template = f.read()
            
        candidate_data_str = json.dumps(safe_profile, indent=2)
        prompt = template.format(candidate_data=candidate_data_str)
        
        result = LLMClient.generate_structured(prompt)
        
        if result and isinstance(result, dict) and "screening_score" in result:
            score = int(result.get("screening_score", 70))
            score = max(0, min(100, score))
            
            recommendation = result.get("recommendation", "Needs HR Review")
            if recommendation not in VALID_RECOMMENDATIONS:
                recommendation = "Needs HR Review"
                
            summary = result.get("summary", "AI Preliminary Screening completed.")
            breakdown = result.get("score_breakdown", {})
            
            return {
                "score": score,
                "recommendation": recommendation,
                "summary": summary,
                "score_breakdown": breakdown
            }
    except Exception:
        pass
        
    return evaluate_screening_heuristic(extracted_info, domain_info)
