"""AI engine integration for Ollama/OpenRouter."""
import json
import os
import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
import requests

load_dotenv()

DEFAULT_LOCAL_URL = "http://localhost:11434/api/generate"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
REQUEST_TIMEOUT = 30  # seconds
REQUIRED_KEYS = [
    "business_goals",
    "pain_points",
    "requirements",
    "current_state",
    "future_state",
]


def _log_error(message: str, error: Optional[Exception] = None) -> None:
    if error is not None:
        print(f"[AI ENGINE] {message}: {type(error).__name__} - {error}")
    else:
        print(f"[AI ENGINE] {message}")


def _development_fallback() -> Dict[str, List[str]]:
    return {
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


def _validate_json_schema(data: Any, required_keys: Optional[List[str]] = None) -> bool:
    if not isinstance(data, dict):
        return False

    required_keys = required_keys or REQUIRED_KEYS
    if set(data.keys()) != set(required_keys):
        return False

    for key in required_keys:
        value = data.get(key)
        if not isinstance(value, list) or not value:
            return False
        if not all(isinstance(item, str) and item.strip() for item in value):
            return False

    return True


def _parse_json_response(payload: str, required_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    parsed = json.loads(payload)
    if not _validate_json_schema(parsed, required_keys):
        raise ValueError("JSON response failed schema validation")
    return parsed


def _call_openrouter(prompt: str, model: str, api_key: str, api_url: str) -> str:
    url = api_url or "https://api.openrouter.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
    }
    response = requests.post(
        url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _call_local_ollama(prompt: str, model: str, local_url: str) -> str:
    response = requests.post(
        local_url,
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response", "")


def call_llm(
    prompt: str,
    model: str = "mistral",
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    local_url: Optional[str] = None,
    retries: int = MAX_RETRIES,
    required_keys: Optional[List[str]] = None,
    response_format: str = "schema",
) -> Any:
    """Call a local or remote LLM endpoint and return parsed JSON output."""
    api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    api_url = api_url or os.getenv("OPENROUTER_API_URL")
    local_url = local_url or os.getenv("LOCAL_LLM_URL") or DEFAULT_LOCAL_URL
    required_keys = required_keys or REQUIRED_KEYS

    last_error: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            if api_key or api_url:
                raw_response = _call_openrouter(prompt, model, api_key or "", api_url or "")
            else:
                raw_response = _call_local_ollama(prompt, model, local_url)

            if response_format == "json":
                return json.loads(raw_response)

            parsed_response = _parse_json_response(raw_response, required_keys)
            return parsed_response

        except (requests.RequestException, json.JSONDecodeError, KeyError, ValueError) as error:
            last_error = error
            _log_error(f"LLM attempt {attempt} failed", error)
            if attempt < retries:
                time.sleep(RETRY_DELAY * attempt)
            continue

    _log_error("All LLM attempts failed; using fallback", last_error)
    return _development_fallback()
