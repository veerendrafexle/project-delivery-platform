"""Generate Jira tickets or tasks from requirements."""
from typing import Any, Dict, List


def generate_tasks(artifact: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create task definitions from structured requirements."""
    tasks: List[Dict[str, Any]] = []
    for index, requirement in enumerate(artifact.get("requirements", []), start=1):
        tasks.append(
            {
                "summary": requirement,
                "status": "To Do",
                "type": "Requirement",
                "priority": "Medium",
                "task_id": f"REQ-{index}",
            }
        )
    return tasks
