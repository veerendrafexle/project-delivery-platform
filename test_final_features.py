"""Test script for Task Generation and Logging functionality."""
import json
import os
from pathlib import Path
from unittest.mock import patch

from app.task_generator import generate_user_stories, convert_to_jira_format, convert_to_azure_devops_format
from app.logging_config import logger, log_pipeline_step, LoggedOperation


def mock_call_llm(prompt: str, **kwargs) -> dict:
    """Mock LLM response for testing."""
    if "user stories" in prompt.lower() or "user story" in prompt.lower():
        return [
            {
                "title": "As a user, I want to login with email and password",
                "description": "Users need secure authentication to access their accounts and personalized features. The login process should be simple and secure.",
                "acceptance_criteria": [
                    "User can enter email and password on login screen",
                    "System validates credentials against user database",
                    "User is redirected to dashboard upon successful login",
                    "Clear error message displayed for invalid credentials",
                    "Password field masks input for security"
                ]
            },
            {
                "title": "As a sales manager, I want to view opportunity pipeline",
                "description": "Sales managers need visibility into the sales pipeline to track deal progress and forecast revenue.",
                "acceptance_criteria": [
                    "Dashboard displays all opportunities by stage",
                    "Opportunities show amount, close date, and probability",
                    "Pipeline view is filterable by date range and owner",
                    "Total pipeline value is calculated and displayed",
                    "Opportunities can be sorted by various criteria"
                ]
            }
        ]
    else:
        return {"error": "Mock response"}


def test_task_generation():
    """Test the task generation functionality."""
    print("Testing Task Generation...")

    requirements = [
        "Users should be able to log in with email and password",
        "Sales managers need to view opportunity pipeline",
        "System should track customer interactions"
    ]

    pain_points = [
        "Current login process is confusing",
        "No visibility into sales pipeline"
    ]

    context_chunks = [
        "Security is a top priority",
        "Sales team needs better tools"
    ]

    # Mock the AI call
    with patch('app.task_generator.call_llm', side_effect=mock_call_llm):
        user_stories = generate_user_stories(
            requirements=requirements,
            pain_points=pain_points,
            context_chunks=context_chunks
        )

    print(f"Generated {len(user_stories)} user stories")

    # Verify structure
    for i, story in enumerate(user_stories, 1):
        print(f"\nStory {i}:")
        print(f"  Title: {story['title']}")
        print(f"  Description: {story['description'][:100]}...")
        print(f"  Acceptance Criteria: {len(story['acceptance_criteria'])} items")

        # Verify required fields
        assert "title" in story and story["title"], "Title is required"
        assert "description" in story and story["description"], "Description is required"
        assert "acceptance_criteria" in story and isinstance(story["acceptance_criteria"], list), "Acceptance criteria must be a list"
        assert len(story["acceptance_criteria"]) > 0, "At least one acceptance criterion required"

    # Test Jira format conversion
    jira_tasks = convert_to_jira_format(user_stories)
    print(f"\nConverted to {len(jira_tasks)} Jira tasks")
    assert len(jira_tasks) == len(user_stories), "Jira conversion should preserve task count"

    # Test Azure DevOps format conversion
    azure_tasks = convert_to_azure_devops_format(user_stories)
    print(f"Converted to {len(azure_tasks)} Azure DevOps tasks")
    assert len(azure_tasks) == len(user_stories), "Azure DevOps conversion should preserve task count"

    # Save test results
    test_output = {
        "user_stories": user_stories,
        "jira_format": jira_tasks,
        "azure_devops_format": azure_tasks
    }

    output_path = Path("test_task_generation.json")
    with open(output_path, 'w') as f:
        json.dump(test_output, f, indent=2)

    print(f"✅ Task generation test results saved to {output_path}")
    return True


def test_logging():
    """Test the logging functionality."""
    print("\nTesting Logging System...")

    # Test basic logging
    logger.info("Testing info logging")
    logger.warning("Testing warning logging")
    logger.error("Testing error logging")

    # Test pipeline step logging
    log_pipeline_step("Test Step", True, 1.5)
    log_pipeline_step("Failed Step", False, 0.8, "Test error")

    # Test LoggedOperation context manager
    with LoggedOperation("Test Operation"):
        import time
        time.sleep(0.1)  # Simulate some work

    # Test with exception
    try:
        with LoggedOperation("Failing Operation"):
            raise ValueError("Test exception")
    except ValueError:
        pass  # Expected

    # Check if log file was created
    log_file = Path("logs/delivery_platform.log")
    if log_file.exists():
        print(f"✅ Log file created at {log_file}")
        with open(log_file, 'r') as f:
            log_content = f.read()
            assert "Testing info logging" in log_content, "Info log not found"
            assert "Test Step" in log_content, "Pipeline step log not found"
            assert "Test Operation" in log_content, "Operation log not found"
        print("✅ Log content verification passed")
        return True
    else:
        print("❌ Log file was not created")
        return False


if __name__ == "__main__":
    success1 = test_task_generation()
    success2 = test_logging()

    if success1 and success2:
        print("\n🎉 All tests PASSED - Task Generation and Logging are working!")
    else:
        print("\n❌ Some tests FAILED")