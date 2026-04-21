"""Convert raw discovery input into structured JSON."""
import logging
from typing import Any, Dict, List, Optional

from app.ai_engine import call_with_retry
from app.rag import build_rag_prompt
from config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


def _validate_structure(data: Any) -> bool:
    """Validate that extracted data matches expected schema."""
    if not isinstance(data, dict):
        return False

    required_keys = {"business_goals", "pain_points", "requirements", "current_state", "future_state"}
    if not required_keys.issubset(data.keys()):
        return False

    for key in required_keys:
        value = data[key]
        if not isinstance(value, list):
            return False
        if not value:
            return False
        if not all(isinstance(item, str) and item.strip() for item in value):
            return False

    return True


def _sanitize_structure(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Remove duplicates and normalize extracted data."""
    sanitized = {}
    for key in ["business_goals", "pain_points", "requirements", "current_state", "future_state"]:
        items = data.get(key, [])
        seen = set()
        unique = []
        for item in items:
            normalized = str(item).strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique.append(normalized)
        sanitized[key] = unique or ["Not specified"]
    return sanitized


def extract_structure(raw_text: str, context_chunks: Optional[List[str]] = None) -> Dict[str, List[str]]:
    """Use the AI engine to extract structured JSON from raw text with schema validation."""
    if not raw_text or not raw_text.strip():
        logger.warning("Empty raw text provided to extract_structure")
        return {
            "business_goals": ["Not specified"],
            "pain_points": ["Not specified"],
            "requirements": ["Not specified"],
            "current_state": ["Not specified"],
            "future_state": ["Not specified"],
        }

    prompt = f"""Extract structured JSON with these EXACT keys:
- business_goals (list of business objectives)
- pain_points (list of current problems)
- requirements (list of functional requirements)
- current_state (list of current system states)
- future_state (list of desired future states)

Return ONLY valid JSON, no markdown, no explanation.

Input text:
{raw_text}
"""

    if context_chunks:
        prompt = build_rag_prompt(prompt, context_chunks)

    logger.info("Requesting structured extraction from AI")
    response = call_with_retry(prompt)

    if response is None:
        logger.error("Structured extraction failed after retries")
        return {
            "business_goals": ["Failed to extract"],
            "pain_points": ["Failed to extract"],
            "requirements": ["Failed to extract"],
            "current_state": ["Failed to extract"],
            "future_state": ["Failed to extract"],
        }

    if _validate_structure(response):
        return _sanitize_structure(response)

    logger.error("AI response did not match expected structure")
    return {
        "business_goals": ["Failed to extract"],
        "pain_points": ["Failed to extract"],
        "requirements": ["Failed to extract"],
        "current_state": ["Failed to extract"],
        "future_state": ["Failed to extract"],
    }
