"""
llm_service.py — Unified LLM Service for AI Recruitment System.
Supports Gemini API, OpenAI API, and includes a smart Mock Fallback Mode 
so the application works out-of-the-box even without active API keys.
"""

import os
import json
import logging
import requests

logger = logging.getLogger("llm_service")

# Check for API Keys in environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Calls Gemini API, OpenAI API, or falls back to smart mock response.
    Returns parsed JSON dictionary.
    """
    # 1. Try Gemini API if key exists
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{
                    "parts": [{"text": f"{system_prompt}\n\n{user_prompt}\n\nReturn strictly valid JSON format only."}]
                }],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception as e:
            logger.warning(f"Gemini API call failed, falling back to mock mode: {e}")

    # 2. Try OpenAI API if key exists
    if OPENAI_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": f"{system_prompt} Return valid JSON."},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                text = res.json()["choices"][0]["message"]["content"]
                return json.loads(text)
        except Exception as e:
            logger.warning(f"OpenAI API call failed, falling back to mock mode: {e}")

    # 3. Smart Mock Fallback Mode
    logger.info("Using LLM Smart Mock Fallback Mode")
    return None
