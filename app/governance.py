"""Governance engine for project lifecycle management."""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.json_utils import read_json, write_json

PHASES = ["Discovery", "Design", "Build", "Test", "Deploy"]
ARTIFACTS = ["BRD", "URS"]
ARTIFACT_STATUSES = ["Draft", "Under Review", "Approved", "Rejected"]
DEFAULT_GOVERNANCE_FILE = Path("governance.json")


def _ensure_state_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        write_json(path, _default_governance_state())


def _default_governance_state() -> Dict[str, Any]:
    return {
        "phase": "Discovery",
        "artifacts": {artifact: "Draft" for artifact in ARTIFACTS},
        "history": [
            {
                "phase": "Discovery",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "reason": "Project created",
            }
        ],
    }


def load_governance_state(path: Optional[Path] = None) -> Dict[str, Any]:
    path = path or DEFAULT_GOVERNANCE_FILE
    _ensure_state_file(path)
    return read_json(path)


def save_governance_state(state: Dict[str, Any], path: Optional[Path] = None) -> None:
    path = path or DEFAULT_GOVERNANCE_FILE
    _ensure_state_file(path)
    write_json(path, state)


def get_current_phase(state: Dict[str, Any]) -> str:
    return state.get("phase", "Discovery")


def get_artifact_status(state: Dict[str, Any], artifact: str) -> str:
    return state.get("artifacts", {}).get(artifact, "Draft")


def update_artifact_status(
    artifact: str,
    status: str,
    state_path: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if artifact not in ARTIFACTS:
        raise ValueError(f"Unknown artifact: {artifact}")
    if status not in ARTIFACT_STATUSES:
        raise ValueError(f"Invalid artifact status: {status}")

    state_path = state_path or DEFAULT_GOVERNANCE_FILE
    state = load_governance_state(state_path)
    state.setdefault("artifacts", {})[artifact] = status
    state.setdefault("artifact_history", []).append(
        {
            "artifact": artifact,
            "status": status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {},
        }
    )
    save_governance_state(state, state_path)
    return state


def _phase_index(phase: str) -> int:
    if phase not in PHASES:
        raise ValueError(f"Unknown phase: {phase}")
    return PHASES.index(phase)


def _validate_phase_transition(state: Dict[str, Any], target_phase: str) -> None:
    current_phase = get_current_phase(state)
    if target_phase == current_phase:
        raise ValueError(f"Project is already in phase '{current_phase}'")

    current_index = _phase_index(current_phase)
    target_index = _phase_index(target_phase)

    if target_index != current_index + 1:
        raise ValueError(
            f"Invalid phase transition from {current_phase} to {target_phase}. "
            f"Only forward progression to the next phase is allowed."
        )

    if target_phase == "Design" and get_artifact_status(state, "BRD") != "Approved":
        raise ValueError("Cannot move to Design unless BRD is Approved.")
    if target_phase == "Build" and (
        get_artifact_status(state, "BRD") != "Approved"
        or get_artifact_status(state, "URS") != "Approved"
    ):
        raise ValueError("Cannot move to Build unless BRD and URS are Approved.")
    if target_phase == "Test" and current_phase != "Build":
        raise ValueError("Cannot move to Test until Build is complete.")
    if target_phase == "Deploy" and current_phase != "Test":
        raise ValueError("Cannot move to Deploy until Test is complete.")


def transition_phase(
    target_phase: str,
    state_path: Optional[Path] = None,
    reason: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    state_path = state_path or DEFAULT_GOVERNANCE_FILE
    state = load_governance_state(state_path)
    _validate_phase_transition(state, target_phase)

    state["phase"] = target_phase
    state.setdefault("history", []).append(
        {
            "phase": target_phase,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "reason": reason or "Phase advanced",
            "metadata": metadata or {},
        }
    )
    save_governance_state(state, state_path)
    return state


def can_transition_to_phase(state: Dict[str, Any], target_phase: str) -> bool:
    try:
        _validate_phase_transition(state, target_phase)
        return True
    except ValueError:
        return False


def get_governance_overview(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "current_phase": get_current_phase(state),
        "artifacts": state.get("artifacts", {}),
        "history": state.get("history", []),
    }


def can_move_to_design(project: Dict[str, Any]) -> bool:
    return (
        project.get("artifacts", {}).get("BRD") == "Approved"
        and project.get("artifacts", {}).get("URS") == "Approved"
    )


def evaluate_phase(project: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "phase": project.get("phase", "Discovery"),
        "can_move_to_design": can_move_to_design(project),
    }
