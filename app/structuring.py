"""Convert raw discovery input into structured JSON."""
import json
from typing import Any, Dict, List

from app.ai_engine import call_llm
from config import settings


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
        if not all(isinstance(item, str) for item in value):
            return False
        if not value:  # empty list
            return False
    
    return True


def _sanitize_structure(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Remove duplicates and normalize extracted data."""
    sanitized = {}
    for key in ["business_goals", "pain_points", "requirements", "current_state", "future_state"]:
        items = data.get(key, [])
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for item in items:
            normalized = str(item).strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique.append(normalized)
        sanitized[key] = unique or ["Not specified"]
    return sanitized


def extract_structure(raw_text: str) -> Dict[str, List[str]]:
    """Use the AI engine to extract structured JSON from raw text with schema validation."""
    if not raw_text or not raw_text.strip():
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

    response = call_llm(
        prompt,
        model=settings.MODEL,
        api_key=settings.API_KEY,
        api_url=settings.API_URL,
        local_url=settings.LOCAL_LLM_URL,
    )

    try:
        data = json.loads(response)
        if _validate_structure(data):
            return _sanitize_structure(data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to parse AI response as JSON: {e}")
    
    # Fallback to safe structure
    return {
        "business_goals": ["Failed to extract"],
        "pain_points": ["Failed to extract"],
        "requirements": ["Failed to extract"],
        "current_state": ["Failed to extract"],
        "future_state": ["Failed to extract"],
    }
