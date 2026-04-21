"""AI engine integration for Ollama with retry and JSON safety."""
import json
import logging
import os
import time
from typing import Any, Dict, Optional

import requests

DEFAULT_LOCAL_URL = "http://localhost:11434/api/generate"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
REQUEST_TIMEOUT = 30  # seconds

logger = logging.getLogger("ai_engine")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


def call_llm(
    prompt: str,
    model: str = "mistral",
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    local_url: Optional[str] = None,
    retries: int = MAX_RETRIES,
    required_keys: Optional[Any] = None,
    response_format: str = "schema",
    **kwargs: Any,
) -> Any:
    """Call an LLM endpoint and return raw or parsed output depending on response_format."""
    local_url = local_url or os.getenv("LOCAL_LLM_URL") or DEFAULT_LOCAL_URL
    api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    api_url = api_url or os.getenv("OPENROUTER_API_URL")

    if api_key or api_url:
        return _call_openrouter(prompt, model, api_key or "", api_url or "")

    payload = {"model": model, "prompt": prompt, "stream": False}
    logger.debug("Calling local Ollama API")
    response = requests.post(local_url, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    data = response.json()
    if isinstance(data, dict) and "response" in data:
        raw_response = data["response"]
    else:
        raw_response = json.dumps(data)

    if response_format == "json":
        return json.loads(raw_response)

    return raw_response


def safe_json_parse(response_text: str) -> Optional[Dict[str, Any]]:
    """Parse a JSON string safely, returning None if parsing fails."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as error:
        logger.error("JSON parse error: %s", error)
        return None


def call_with_retry(prompt: str, retries: int = MAX_RETRIES) -> Optional[Dict[str, Any]]:
    """Call the LLM with retry logic and return parsed JSON if successful."""
    last_error: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            raw_response = call_llm(prompt)
            parsed = safe_json_parse(raw_response)
            if parsed is not None:
                logger.info("LLM call succeeded on attempt %d", attempt)
                return parsed

            raise ValueError("Invalid JSON response")

        except Exception as error:
            last_error = error
            logger.warning("LLM attempt %d failed: %s", attempt, error)
            if attempt < retries:
                time.sleep(RETRY_DELAY)
                continue

    logger.error("LLM failed after %d attempts: %s", retries, last_error)
    return None

