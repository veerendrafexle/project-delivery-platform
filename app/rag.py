"""RAG (retrieval-augmented generation) support with ChromaDB."""
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.utils import embedding_functions

from utils.json_utils import write_json

DEFAULT_RAG_DIR = Path("rag_store")
DEFAULT_COLLECTION_NAME = "requirements"


class SimpleEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, dim: int = 128):
        self.dim = dim

    def name(self) -> str:
        return "simple_local_embedding"

    @property
    def space(self) -> str:
        return "cosine"

    def _embed_text(self, text: str) -> List[float]:
        vector = [0.0] * self.dim
        for idx, char in enumerate(text):
            vector[ord(char) % self.dim] += (idx + 1) * 0.1
        norm = math.sqrt(sum(value * value for value in vector))
        if norm > 0:
            vector = [value / norm for value in vector]
        return vector

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_text(str(text)) for text in texts]


def _load_texts(source_dir: Path, extensions: tuple[str, ...] = (".txt", ".md")) -> Dict[str, str]:
    documents: Dict[str, str] = {}
    if not source_dir.exists():
        return documents

    for path in source_dir.iterdir():
        if path.is_file() and path.suffix.lower() in extensions:
            documents[path.name] = path.read_text(encoding="utf-8")
    return documents


def _chunk_text(text: str, chunk_size: int = 250, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks: List[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start = end - overlap
    return chunks


def _get_client(persist_directory: Optional[Path] = None) -> chromadb.PersistentClient:
    persist_directory = persist_directory or DEFAULT_RAG_DIR
    persist_directory.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_directory))


def build_vector_store(
    source_dir: Path,
    persist_directory: Optional[Path] = None,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> Dict[str, Any]:
    """Build or update the ChromaDB vector store from source documents."""
    documents = _load_texts(source_dir)
    if not documents:
        return {"status": "no_documents", "source_dir": str(source_dir)}

    client = _get_client(persist_directory)
    # Use default embedding function for now
    collection = client.get_or_create_collection(
        name=collection_name,
    )

    ids: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    texts: List[str] = []

    for file_name, content in documents.items():
        for index, chunk in enumerate(_chunk_text(content)):
            doc_id = f"{file_name}_{index}"
            ids.append(doc_id)
            metadatas.append({"source_file": file_name, "chunk_index": index})
            texts.append(chunk)

    collection.upsert(documents=texts, metadatas=metadatas, ids=ids)
    return {
        "status": "vector_store_built",
        "collection": collection_name,
        "documents_indexed": len(texts),
        "source_dir": str(source_dir),
    }


def query_vector_store(
    query: str,
    top_n: int = 3,
    persist_directory: Optional[Path] = None,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> List[Dict[str, Any]]:
    """Query the RAG store for top relevant chunks."""
    client = _get_client(persist_directory)
    collection = client.get_collection(name=collection_name)
    results = collection.query(query_texts=[query], n_results=top_n)

    hits: List[Dict[str, Any]] = []
    for doc_id, doc_text, metadata, score in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results.get("distances", [[]])[0],
    ):
        hits.append(
            {
                "id": doc_id,
                "text": doc_text,
                "metadata": metadata,
                "score": score,
            }
        )
    return hits


def build_rag_prompt(base_prompt: str, context_chunks: List[str]) -> str:
    """Build an LLM prompt augmented with retrieved context."""
    context = "\n\n".join(context_chunks)
    return (
        "Use the following context to answer the question. "
        "If the context does not contain enough information, be honest and use only what is available.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{base_prompt}"
    )


def save_query_context(query: str, results: List[Dict[str, Any]], path: Optional[Path] = None) -> Path:
    path = path or Path("data/rag_query_history.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "query": query,
        "retrieved": results,
    }
    write_json(path, payload)
    return path
