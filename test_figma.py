"""Test script for Figma integration without network calls."""
import json
from pathlib import Path
from unittest.mock import patch

from app.figma_integration import generate_ui_screens, validate_ui_screens, save_ui_screens


def mock_call_llm(prompt: str, **kwargs) -> dict:
    """Mock LLM response for testing."""
    if "UI screens" in prompt:
        return {
            "ui_screens": [
                {
                    "screen_name": "LoginScreen",
                    "description": "User authentication screen",
                    "components": [
                        {
                            "type": "TextInput",
                            "label": "Email",
                            "placeholder": "Enter your email"
                        },
                        {
                            "type": "TextInput",
                            "label": "Password",
                            "placeholder": "Enter your password",
                            "secure": True
                        },
                        {
                            "type": "Button",
                            "label": "Login",
                            "action": "authenticate"
                        }
                    ]
                },
                {
                    "screen_name": "DashboardScreen",
                    "description": "Main dashboard after login",
                    "components": [
                        {
                            "type": "Header",
                            "title": "Welcome"
                        },
                        {
                            "type": "Card",
                            "title": "Projects",
                            "content": "View your active projects"
                        }
                    ]
                }
            ]
        }
    else:
        return {"error": "Mock response"}


def test_figma_integration():
    """Test the Figma integration module."""
    print("Testing Figma Integration...")

    # Mock requirements and pain points
    requirements = [
        "Users should be able to log in with email and password",
        "Dashboard should show active projects",
        "System should handle user authentication securely"
    ]

    pain_points = [
        "Current login process is confusing",
        "Dashboard doesn't show relevant information"
    ]

    context_chunks = [
        "The application needs a modern UI design",
        "Security is a top priority for user authentication"
    ]

    # Mock the AI call
    with patch('app.figma_integration.call_llm', side_effect=mock_call_llm):
        ui_screens = generate_ui_screens(
            requirements=requirements,
            pain_points=pain_points,
            context_chunks=context_chunks
        )

    print(f"Generated {len(ui_screens)} UI screens")

    # Validate the screens
    issues = validate_ui_screens(ui_screens)
    if issues:
        print("Validation issues:")
        for issue in issues:
            print(f"- {issue}")
        return False
    else:
        print("UI screens validation passed")

    # Save the screens
    output_path = Path("test_ui_screens.json")
    saved_path = save_ui_screens(ui_screens, output_path)
    print(f"UI screens saved to {saved_path}")

    # Verify the file was created and contains expected data
    if saved_path.exists():
        with open(saved_path, 'r') as f:
            data = json.load(f)
        print(f"Saved file contains {len(data)} screens")
        return True
    else:
        print("Failed to save UI screens")
        return False


if __name__ == "__main__":
    success = test_figma_integration()
    print(f"Test {'PASSED' if success else 'FAILED'}")