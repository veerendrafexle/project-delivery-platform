"""Figma integration for UI design generation from requirements."""
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.ai_engine import call_llm
from config import settings
from utils.json_utils import write_json


def _build_ui_generation_prompt(requirements: List[str], pain_points: List[str]) -> str:
    """Build prompt for AI to generate UI screens from requirements."""
    return f"""Analyze these requirements and pain points to generate a UI screen structure for a web application.

Requirements:
{chr(10).join(f"- {req}" for req in requirements)}

Pain Points:
{chr(10).join(f"- {pp}" for pp in pain_points)}

Generate a JSON array of screen definitions. Each screen should have:
- "screen": descriptive name (string)
- "components": array of UI components (strings like "Table", "Form", "Button", "Chart", "Navigation", "Search", "Filter", "Modal", "Card", "List")
- "actions": array of user actions this screen supports (strings like "Create", "Edit", "Delete", "View", "Search", "Filter", "Export")
- "description": brief description of the screen's purpose (string)

Return ONLY valid JSON array, no markdown or explanation.

Example format:
[
  {{
    "screen": "User Dashboard",
    "components": ["Table", "Chart", "Navigation"],
    "actions": ["View", "Filter", "Export"],
    "description": "Main dashboard showing user metrics and data"
  }}
]
"""


def generate_ui_screens(
    requirements: List[str],
    pain_points: List[str],
    context_chunks: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Generate UI screen definitions from requirements using AI."""
    prompt = _build_ui_generation_prompt(requirements, pain_points)

    if context_chunks:
        from app.rag import build_rag_prompt
        prompt = build_rag_prompt(prompt, context_chunks)

    response = call_llm(
        prompt,
        model=settings.MODEL,
        api_key=settings.API_KEY,
        api_url=settings.API_URL,
        local_url=settings.LOCAL_LLM_URL,
        response_format="json",
    )

    if isinstance(response, dict) and "screens" in response:
        return response["screens"]
    elif isinstance(response, list):
        return response

    # Fallback structure
    return [
        {
            "screen": "Main Dashboard",
            "components": ["Table", "Navigation", "Search"],
            "actions": ["View", "Create", "Edit"],
            "description": "Primary interface for managing requirements",
        }
    ]


def _validate_ui_screen(screen: Dict[str, Any]) -> bool:
    """Validate a UI screen definition has required fields."""
    required_keys = {"screen", "components", "actions", "description"}
    if not all(key in screen for key in required_keys):
        return False

    if not isinstance(screen["screen"], str) or not screen["screen"].strip():
        return False

    if not isinstance(screen["components"], list) or not screen["components"]:
        return False

    if not isinstance(screen["actions"], list) or not screen["actions"]:
        return False

    if not isinstance(screen["description"], str) or not screen["description"].strip():
        return False

    return True


def validate_ui_screens(screens: List[Dict[str, Any]]) -> List[str]:
    """Validate UI screen definitions and return any issues."""
    issues = []
    if not screens:
        issues.append("No UI screens generated")
        return issues

    for i, screen in enumerate(screens):
        if not _validate_ui_screen(screen):
            issues.append(f"Screen {i+1} is missing required fields or has invalid data")

    return issues


def save_ui_screens(screens: List[Dict[str, Any]], output_path: Path) -> Path:
    """Save UI screen definitions to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_path, screens)
    return output_path


def convert_to_figma_format(screens: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Convert UI screens to Figma-compatible format (placeholder for future API integration)."""
    figma_data = {
        "name": "Generated UI Screens",
        "lastModified": "2024-01-01T00:00:00Z",
        "thumbnailUrl": "",
        "version": "1.0.0",
        "role": "owner",
        "editorType": "figma",
        "linkAccess": "inherit",
        "screens": screens,
    }
    return figma_data


def prepare_figma_payload(screens: List[Dict[str, Any]], project_name: str = "AI Generated UI") -> Dict[str, Any]:
    """Prepare payload for Figma API integration."""
    return {
        "project": project_name,
        "screens": screens,
        "metadata": {
            "generated_by": "AI Delivery Platform",
            "version": "1.0",
            "timestamp": "2024-01-01T00:00:00Z",
        },
    }


# Placeholder for future Figma API integration
def push_to_figma(screens: List[Dict[str, Any]], figma_token: Optional[str] = None, project_id: Optional[str] = None) -> Dict[str, Any]:
    """Push UI screens to Figma (placeholder implementation)."""
    if not figma_token or not project_id:
        return {
            "status": "skipped",
            "message": "Figma API integration not configured. Use FIGMA_TOKEN and FIGMA_PROJECT_ID environment variables.",
            "screens_count": len(screens),
        }

    # TODO: Implement actual Figma API calls
    # This would involve:
    # 1. Create Figma file or get existing file
    # 2. Convert screen definitions to Figma components
    # 3. Add components to the file
    # 4. Update file metadata

    return {
        "status": "placeholder",
        "message": "Figma API integration ready for implementation",
        "screens_count": len(screens),
        "project_id": project_id,
    }