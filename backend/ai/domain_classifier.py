import os
import json
from backend.ai.llm_client import LLMClient
from backend.ai.fallback_engine import classify_domain_heuristic, DOMAINS_TAXONOMY

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "domain_classification.txt")

def classify_candidate_domain(extracted_info: dict, raw_text: str) -> dict:
    """
    Classifies candidate into one of 12 tech domains, calculates confidence scores,
    top 3 candidate domains, and supporting evidence.
    """
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            template = f.read()
            
        profile_json = json.dumps(extracted_info, indent=2)
        prompt = template.format(candidate_profile=profile_json)
        
        result = LLMClient.generate_structured(prompt)
        
        if result and isinstance(result, dict) and "primary_domain" in result:
            primary = result.get("primary_domain", "Other")
            if primary not in DOMAINS_TAXONOMY:
                primary = "Other"
                
            confidence = float(result.get("confidence", 75.0))
            secondaries = result.get("secondary_domains", [])
            evidence = result.get("evidence", [])
            
            return {
                "primary_domain": primary,
                "confidence": round(confidence, 1),
                "secondary_domains": secondaries,
                "evidence": evidence
            }
    except Exception:
        pass
        
    return classify_domain_heuristic(extracted_info, raw_text)
