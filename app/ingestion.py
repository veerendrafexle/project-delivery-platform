"""Ingestion utilities for loading input files."""
import os
from typing import Dict


def load_project_files(folder: str, extensions: tuple[str, ...] = (".txt", ".md")) -> Dict[str, str]:
    """Load text files from the inputs folder."""
    data: Dict[str, str] = {}
    for file_name in os.listdir(folder):
        path = os.path.join(folder, file_name)
        if os.path.isfile(path) and os.path.splitext(file_name)[1].lower() in extensions:
            with open(path, "r", encoding="utf-8") as f:
                data[file_name] = f.read()
    return data
