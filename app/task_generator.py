"""Generate user stories and tasks from requirements for Jira/DevOps."""
import json
from typing import Any, Dict, List, Optional

from app.ai_engine import call_llm


def _validate_task_structure(data: Any) -> bool:
    """Validate that generated tasks match expected schema."""
    if not isinstance(data, list):
        return False

    for task in data:
        if not isinstance(task, dict):
            return False

        required_keys = {"title", "description", "acceptance_criteria"}
        if not required_keys.issubset(task.keys()):
            return False

        # Validate types
        if not isinstance(task["title"], str) or not task["title"].strip():
            return False
        if not isinstance(task["description"], str) or not task["description"].strip():
            return False
        if not isinstance(task["acceptance_criteria"], list):
            return False
        if not all(isinstance(criterion, str) and criterion.strip() for criterion in task["acceptance_criteria"]):
            return False

    return True


def _sanitize_tasks(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean and normalize generated tasks."""
    sanitized = []

    for task in data:
        if not isinstance(task, dict):
            continue

        sanitized_task = {
            "title": str(task.get("title", "")).strip(),
            "description": str(task.get("description", "")).strip(),
            "acceptance_criteria": []
        }

        # Sanitize acceptance criteria
        criteria = task.get("acceptance_criteria", [])
        if isinstance(criteria, list):
            sanitized_task["acceptance_criteria"] = [
                str(criterion).strip()
                for criterion in criteria
                if criterion and str(criterion).strip()
            ]

        # Only add if we have required fields
        if sanitized_task["title"] and sanitized_task["description"]:
            sanitized.append(sanitized_task)

    return sanitized


def _build_task_generation_prompt(requirements: List[str], pain_points: List[str]) -> str:
    """Build a prompt for generating user stories and tasks."""
    requirements_text = "\n".join(f"- {req}" for req in requirements)
    pain_points_text = "\n".join(f"- {pp}" for pp in pain_points)

    return f"""You are a product owner and agile coach. Convert the following requirements and pain points into detailed user stories with acceptance criteria.

REQUIREMENTS:
{requirements_text}

PAIN POINTS:
{pain_points_text}

For each requirement, create a user story with:
1. TITLE: Clear, concise user story title (As a [user], I want [goal] so that [benefit])
2. DESCRIPTION: Detailed description explaining the story, context, and business value
3. ACCEPTANCE CRITERIA: Specific, testable conditions that must be met for the story to be complete

Return ONLY valid JSON array with this structure:
[
  {{
    "title": "As a user, I want to login so that I can access my account",
    "description": "Users need secure authentication to access personalized features...",
    "acceptance_criteria": [
      "User can enter email and password",
      "System validates credentials",
      "User is redirected to dashboard on success",
      "Error message shown for invalid credentials"
    ]
  }}
]

Focus on creating actionable, testable user stories that can be directly imported into Jira or Azure DevOps."""


def generate_user_stories(
    requirements: List[str],
    pain_points: Optional[List[str]] = None,
    context_chunks: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Generate user stories from requirements using AI."""
    if not requirements:
        return []

    pain_points = pain_points or []
    context_chunks = context_chunks or []

    prompt = _build_task_generation_prompt(requirements, pain_points)

    # Add context if available
    if context_chunks:
        context_text = "\n".join(f"Context: {chunk}" for chunk in context_chunks[:3])
        prompt += f"\n\nADDITIONAL CONTEXT:\n{context_text}"

    response = call_llm(prompt, response_format="json")

    if not response:
        return _fallback_task_generation(requirements, pain_points)

    try:
        # Parse JSON response
        if isinstance(response, str):
            parsed = json.loads(response)
        else:
            parsed = response

        # Validate and sanitize
        if _validate_task_structure(parsed):
            return _sanitize_tasks(parsed)
        else:
            print("[TASK GENERATOR] Invalid response format, using fallback")
            return _fallback_task_generation(requirements, pain_points)

    except (json.JSONDecodeError, TypeError) as e:
        print(f"[TASK GENERATOR] JSON parsing error: {e}, using fallback")
        return _fallback_task_generation(requirements, pain_points)


def _fallback_task_generation(requirements: List[str], pain_points: List[str]) -> List[Dict[str, Any]]:
    """Fallback task generation when AI fails."""
    tasks = []

    for i, requirement in enumerate(requirements, 1):
        # Create basic user story structure
        title = f"As a user, I want {requirement.lower().strip()}"

        description = f"This user story addresses the requirement: {requirement}"
        if pain_points:
            description += f"\n\nThis helps resolve: {pain_points[0] if pain_points else 'various pain points'}"

        acceptance_criteria = [
            f"System supports {requirement.lower()}",
            "Feature is tested and working",
            "Documentation is updated"
        ]

        tasks.append({
            "title": title,
            "description": description,
            "acceptance_criteria": acceptance_criteria
        })

    return tasks


def convert_to_jira_format(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert user stories to Jira-ready format."""
    jira_tasks = []

    for i, task in enumerate(tasks, 1):
        jira_task = {
            "fields": {
                "project": {"key": "PROJ"},
                "summary": task["title"],
                "description": task["description"],
                "issuetype": {"name": "Story"},
                "priority": {"name": "Medium"},
                "labels": ["user-story", "requirements"],
                "customfield_acceptance_criteria": "\n".join(f"- {criterion}" for criterion in task["acceptance_criteria"])
            }
        }
        jira_tasks.append(jira_task)

    return jira_tasks


def convert_to_azure_devops_format(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert user stories to Azure DevOps-ready format."""
    azure_tasks = []

    for i, task in enumerate(tasks, 1):
        azure_task = {
            "op": "add",
            "path": "/fields",
            "value": {
                "System.Title": task["title"],
                "System.Description": task["description"],
                "System.WorkItemType": "User Story",
                "Microsoft.VSTS.Common.Priority": 2,
                "Microsoft.VSTS.Common.AcceptanceCriteria": "\n".join(task["acceptance_criteria"]),
                "System.Tags": "user-story;requirements"
            }
        }
        azure_tasks.append(azure_task)

    return azure_tasks


def save_task_backlog(tasks: List[Dict[str, Any]], output_path: str) -> str:
    """Save the task backlog to a JSON file."""
    import json
    from pathlib import Path

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

    return str(output_path)


# Legacy function for backward compatibility
def generate_tasks(artifact: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Legacy function - convert artifact to basic tasks."""
    requirements = artifact.get("requirements", [])
    pain_points = artifact.get("pain_points", [])

    return generate_user_stories(requirements, pain_points)
