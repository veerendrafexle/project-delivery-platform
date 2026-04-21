"""Manage traceability links across artifacts."""
from typing import Dict, List


def create_trace_links(source_files: List[str], output_files: List[str]) -> Dict[str, List[Dict[str, str]]]:
    """Generate simple traceability links between source and output files."""
    links: List[Dict[str, str]] = []
    for source in source_files:
        for output in output_files:
            links.append(
                {
                    "source": source,
                    "target": output,
                    "type": "generated_from",
                }
            )
    return {"links": links}
