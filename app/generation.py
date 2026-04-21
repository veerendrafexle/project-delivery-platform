"""Document generation for BRD / URS output."""
from typing import Any, Dict, List


def _normalize_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def build_brd_content(data: Dict[str, Any]) -> str:
    """Build BRD content as plain text."""
    content = "Business Requirements Document\n\n"

    content += "Business Objectives:\n"
    for item in _normalize_list(data.get("business_goals")):
        content += f"- {item}\n"

    content += "\nPain Points:\n"
    for item in _normalize_list(data.get("pain_points")):
        content += f"- {item}\n"

    content += "\nRequirements:\n"
    for item in _normalize_list(data.get("requirements")):
        content += f"- {item}\n"

    return content


def build_urs_content(data: Dict[str, Any]) -> str:
    """Build URS content as plain text."""
    content = "User Requirements Specification\n\n"

    content += "Current State:\n"
    for item in _normalize_list(data.get("current_state")):
        content += f"- {item}\n"

    content += "\nFuture State:\n"
    for item in _normalize_list(data.get("future_state")):
        content += f"- {item}\n"

    return content


def generate_brd(data: Dict[str, Any], output_path: str) -> None:
    """Generate a Business Requirements Document (.txt for demo)."""
    content = build_brd_content(data)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def generate_urs(data: Dict[str, Any], output_path: str) -> None:
    """Generate a User Requirements Specification (.txt for demo)."""
    content = build_urs_content(data)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
