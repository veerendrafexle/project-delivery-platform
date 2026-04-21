"""Manage traceability links across requirements and source inputs."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.json_utils import read_json, write_json

NODE_TYPES = {"source", "pain_point", "requirement", "artifact"}
DEFAULT_TRACE_PATH = Path("traceability.json")


def _node_id(node_type: str, key: str) -> str:
    return f"{node_type}:{key.strip()}"


def _normalize_text(text: str) -> str:
    return text.strip()


class TraceabilityGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []

    def _create_node(self, node_type: str, key: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        if node_type not in NODE_TYPES:
            raise ValueError(f"Unsupported node type: {node_type}")
        normalized_key = _normalize_text(key)
        node_id = _node_id(node_type, normalized_key)
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "type": node_type,
                "key": normalized_key,
                "metadata": metadata or {},
            }
        return node_id

    def add_source(self, source_name: str, content: str) -> str:
        return self._create_node("source", source_name, {"content": content})

    def add_pain_point(self, text: str) -> str:
        return self._create_node("pain_point", text)

    def add_requirement(self, text: str) -> str:
        return self._create_node("requirement", text)

    def add_artifact(self, artifact_name: str, version: Optional[str] = None) -> str:
        label = f"{artifact_name}" if version is None else f"{artifact_name}_{version}"
        return self._create_node("artifact", label)

    def add_edge(self, source_id: str, target_id: str, relation: str) -> None:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Both source and target nodes must exist before adding an edge.")
        edge = {"from": source_id, "to": target_id, "relation": relation}
        if edge not in self.edges:
            self.edges.append(edge)

    def add_mapping(
        self,
        source_name: str,
        source_content: str,
        pain_point: str,
        requirement: str,
        brd_artifact: str,
        brd_version: Optional[str] = None,
    ) -> None:
        source_id = self.add_source(source_name, source_content)
        pain_point_id = self.add_pain_point(pain_point)
        requirement_id = self.add_requirement(requirement)
        artifact_id = self.add_artifact(brd_artifact, brd_version)

        self.add_edge(source_id, pain_point_id, "contains")
        self.add_edge(pain_point_id, requirement_id, "informs")
        self.add_edge(requirement_id, artifact_id, "documented_in")

    def query_sources_for_requirement(self, requirement: str) -> List[Dict[str, Any]]:
        requirement_id = _node_id("requirement", requirement)
        results: List[Dict[str, Any]] = []
        for edge in self.edges:
            if edge["to"] == requirement_id and edge["relation"] == "informs":
                pain_point_id = edge["from"]
                for parent_edge in self.edges:
                    if parent_edge["to"] == pain_point_id and parent_edge["relation"] == "contains":
                        source_id = parent_edge["from"]
                        results.append(self.nodes[source_id])
        return results

    def query_requirements_for_source(self, source_name: str) -> List[Dict[str, Any]]:
        source_id = _node_id("source", source_name)
        requirements: List[Dict[str, Any]] = []
        for edge in self.edges:
            if edge["from"] == source_id and edge["relation"] == "contains":
                pain_point_id = edge["to"]
                for child_edge in self.edges:
                    if child_edge["from"] == pain_point_id and child_edge["relation"] == "informs":
                        requirements.append(self.nodes[child_edge["to"]])
        return requirements

    def get_trace_graph(self) -> Dict[str, Any]:
        return {"nodes": self.nodes, "edges": self.edges}

    def save(self, path: Optional[Path] = None) -> Path:
        path = path or DEFAULT_TRACE_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, self.get_trace_graph())
        return path

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "TraceabilityGraph":
        path = path or DEFAULT_TRACE_PATH
        graph = cls()
        if not path.exists():
            return graph
        raw = read_json(path)
        graph.nodes = raw.get("nodes", {})
        graph.edges = raw.get("edges", [])
        return graph


def build_traceability_graph(
    source_texts: Dict[str, str],
    structured_data: Dict[str, Any],
    brd_name: str = "BRD",
    brd_version: Optional[str] = None,
) -> TraceabilityGraph:
    graph = TraceabilityGraph()
    graph.add_artifact(brd_name, brd_version)

    pain_point_nodes = {}
    for pain_point in structured_data.get("pain_points", []):
        pain_point_nodes[pain_point] = graph.add_pain_point(pain_point)

    requirement_nodes = {}
    for requirement in structured_data.get("requirements", []):
        requirement_nodes[requirement] = graph.add_requirement(requirement)

    for source_name, content in source_texts.items():
        source_id = graph.add_source(source_name, content)
        for pain_point, pain_id in pain_point_nodes.items():
            if pain_point.lower() in content.lower() or any(word in content.lower() for word in pain_point.lower().split() if len(word) > 4):
                graph.add_edge(source_id, pain_id, "contains")

        for requirement, req_id in requirement_nodes.items():
            if requirement.lower() in content.lower() or any(word in content.lower() for word in requirement.lower().split() if len(word) > 4):
                matching_pain_ids = [pain_id for pain_point, pain_id in pain_point_nodes.items() if any(word in pain_point.lower() for word in requirement.lower().split() if len(word) > 4)]
                if not matching_pain_ids:
                    matching_pain_ids = list(pain_point_nodes.values())
                for pain_id in matching_pain_ids:
                    graph.add_edge(pain_id, req_id, "informs")

    artifact_id = graph.add_artifact(brd_name, brd_version)
    for req_id in requirement_nodes.values():
        graph.add_edge(req_id, artifact_id, "documented_in")

    return graph


def save_traceability_graph(
    source_texts: Dict[str, str],
    structured_data: Dict[str, Any],
    output_path: Optional[Path] = None,
    brd_name: str = "BRD",
    brd_version: Optional[str] = None,
) -> Path:
    graph = build_traceability_graph(source_texts, structured_data, brd_name, brd_version)
    return graph.save(output_path)
