"""Quality and rule validation for structured artifacts."""
from typing import Dict, List


def validate_brd(data: Dict[str, object]) -> List[str]:
    """Validate extracted BRD fields for completeness and quality."""
    issues: List[str] = []

    # Check for required fields
    for field in ["business_goals", "pain_points", "requirements", "current_state", "future_state"]:
        if field not in data:
            issues.append(f"Missing field: {field}")
            continue
        
        value = data.get(field, [])
        if not isinstance(value, list):
            issues.append(f"{field} must be a list")
            continue
        
        if not value:
            issues.append(f"{field} is empty")
        elif len(value) == 1 and value[0] in ["Not specified", "Failed to extract"]:
            issues.append(f"{field} appears to have failed extraction")
        elif len(value) > 50:
            issues.append(f"{field} has too many items ({len(value)})")

    # Check minimum content
    total_items = sum(len(v) for v in data.values() if isinstance(v, list))
    if total_items < 5:
        issues.append("Insufficient content extracted from input")

    # Check for suspicious patterns (hallucinations)
    suspicious_phrases = ["lorem ipsum", "placeholder", "tbd", "todo", "example"]
    for field, items in data.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, str):
                if any(phrase in item.lower() for phrase in suspicious_phrases):
                    issues.append(f"Suspicious content in {field}: '{item}'")

    return issues
