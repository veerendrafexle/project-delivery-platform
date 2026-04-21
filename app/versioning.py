"""Version control utilities for generated artifacts and structured data."""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.json_utils import read_json, write_json


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _get_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _load_history(history_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    if not history_path.exists():
        return {}
    return read_json(history_path)


def _save_history(history_path: Path, history: Dict[str, List[Dict[str, Any]]]) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(history_path, history)


def get_latest_version(base_name: str, history_path: Path) -> Optional[Dict[str, Any]]:
    history = _load_history(history_path)
    entries = history.get(base_name, [])
    return entries[-1] if entries else None


def _next_version(base_name: str, history_path: Path) -> int:
    latest = get_latest_version(base_name, history_path)
    return latest["version"] + 1 if latest else 1


def _format_versioned_filename(base_name: str, version: int, extension: str) -> str:
    if not extension.startswith("."):
        extension = f".{extension}"
    return f"{base_name}_v{version}{extension}"


def _register_history_entry(
    base_name: str,
    filename: str,
    history_path: Path,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    history = _load_history(history_path)
    entries = history.setdefault(base_name, [])
    entry = {
        "version": len(entries) + 1,
        "filename": filename,
        "timestamp": _get_timestamp(),
        "metadata": metadata or {},
    }
    entries.append(entry)
    _save_history(history_path, history)


def save_versioned_text(
    base_name: str,
    content: str,
    output_dir: Path,
    extension: str,
    history_path: Path,
    metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    version = _next_version(base_name, history_path)
    filename = _format_versioned_filename(base_name, version, extension)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    _register_history_entry(base_name, filename, history_path, metadata)
    return output_path


def save_versioned_json(
    base_name: str,
    data: Any,
    output_dir: Path,
    extension: str,
    history_path: Path,
    metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    version = _next_version(base_name, history_path)
    filename = _format_versioned_filename(base_name, version, extension)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    _ensure_dir(output_path)
    write_json(output_path, data)
    _register_history_entry(base_name, filename, history_path, metadata)
    return output_path
