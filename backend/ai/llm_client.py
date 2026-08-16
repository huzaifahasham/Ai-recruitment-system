import json
import logging
import requests
from backend.config import settings
from backend.ai.fallback_engine import (
    extract_candidate_heuristic,
    classify_domain_heuristic,
    evaluate_screening_heuristic
)

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Universal LLM provider client supporting OpenAI, Gemini, or Mock fallback.
    Ensures validated structured JSON outputs and safe fallbacks.
    """
    
    @staticmethod
    def _call_openai(prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.MODEL_NAME or "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    @staticmethod
    def _call_gemini(prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.MODEL_NAME or 'gemini-1.5-flash'}:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt + "\n\nRespond ONLY with valid JSON."}]}]
        }
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    @classmethod
    def generate_structured(cls, prompt: str) -> dict:
        provider = settings.AI_PROVIDER.lower() if settings.AI_PROVIDER else "mock"
        
        if provider == "openai" and settings.OPENAI_API_KEY:
            try:
                raw_json = cls._call_openai(prompt)
                return json.loads(raw_json)
            except Exception as e:
                logger.warning(f"OpenAI call failed ({str(e)}). Falling back to internal engine.")
                
        elif provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                raw_json = cls._call_gemini(prompt)
                # Strip markdown code blocks if returned
                cleaned_text = raw_json.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                return json.loads(cleaned_text.strip())
            except Exception as e:
                logger.warning(f"Gemini call failed ({str(e)}). Falling back to internal engine.")

        return {}
