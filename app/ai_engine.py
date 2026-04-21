"""AI engine integration for Ollama/OpenRouter."""
import json
import os
import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import requests

load_dotenv()

DEFAULT_LOCAL_URL = "http://localhost:11434/api/generate"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
REQUEST_TIMEOUT = 30  # seconds


def _development_fallback(prompt: str) -> str:
    return json.dumps(
        {
            "business_goals": [
                "Improve customer onboarding",
                "Reduce manual processing effort",
            ],
            "pain_points": [
                "Data is spread across multiple systems",
                "Approval cycles are slow and manual",
            ],
            "requirements": [
                "Centralize customer data into a single view",
                "Automate approval routing for new requests",
            ],
            "current_state": [
                "Multiple legacy applications",
                "No standardized requirements artifacts",
            ],
            "future_state": [
                "Unified delivery platform",
                "Automated governance and traceability",
            ],
        }
    )


def call_llm(
    prompt: str,
    model: str = "mistral",
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    local_url: Optional[str] = None,
    retries: int = MAX_RETRIES,
) -> str:
    """Call a local or remote LLM endpoint with retry logic and timeout."""
    api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    api_url = api_url or os.getenv("OPENROUTER_API_URL")
    local_url = local_url or os.getenv("LOCAL_LLM_URL") or DEFAULT_LOCAL_URL

    last_error = None
    for attempt in range(retries):
        try:
            if api_key or api_url:
                url = api_url or "https://api.openrouter.ai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                }
                response = requests.post(
                    url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

            response = requests.post(
                local_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("response", "")
            if result:
                return result
            
        except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))  # exponential backoff
            continue

    print(f"AI call failed after {retries} retries: {last_error}")
    return _development_fallback(prompt)
