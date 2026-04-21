"""Governance and approval logic for delivery phases."""
from typing import Dict, Any


def can_move_to_design(project: Dict[str, Any]) -> bool:
    """Return true when BRD and URS are both approved."""
    return (
        project.get("artifacts", {}).get("BRD") == "Approved"
        and project.get("artifacts", {}).get("URS") == "Approved"
    )


def evaluate_phase(project: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "phase": project.get("phase", "Discovery"),
        "can_move_to_design": can_move_to_design(project),
    }
