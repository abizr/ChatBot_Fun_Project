from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np

from .utils import ensure_dir, hash_bytes, truncate_text

try:  # pragma: no cover - embedding model dependency
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception as exc:
    SentenceTransformer = None  # type: ignore
    SENTENCE_TRANSFORMERS_IMPORT_ERROR = exc
else:
    SENTENCE_TRANSFORMERS_IMPORT_ERROR = None

try:  # pragma: no cover - faiss may be missing locally
    import faiss  # type: ignore
except Exception:
    faiss = None


@dataclass
class RagConfig:
    storage_dir: str = "data/rag_cache"
    chunk_size: int = 600
    chunk_overlap: int = 100
    top_k: int = 4
    max_context_chars: int = 2200


@dataclass
class RagResult:
    text: str
    score: float
    metadata: Dict


class RagPipeline:
    """Minimal FAISS-backed RAG pipeline."""

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", config: Optional[RagConfig] = None):
        self.embedding_model = embedding_model
        self.config = config or RagConfig()
        self.base_dir = ensure_dir(self.config.storage_dir)
        self._embedder: Optional[Any] = None
        self._index_cache: Dict[str, Tuple[Optional[Any], List[Dict], np.ndarray]] = {}

    def _get_embedder(self) -> Any:
        if SentenceTransformer is None:  # pragma: no cover - only when dependency missing
            raise RuntimeError(
                "sentence-transformers is required for RAG embeddings. "
                f"Original import error: {SENTENCE_TRANSFORMERS_IMPORT_ERROR}"
            )
        if self._embedder is None:
            self._embedder = SentenceTransformer(self.embedding_model)
        return self._embedder

    def _doc_dir(self, doc_id: str) -> Path:
        return ensure_dir(self.base_dir / doc_id)

    def _paths(self, doc_id: str) -> Tuple[Path, Path, Path]:
        doc_dir = self._doc_dir(doc_id)
        return (
            doc_dir / "index.faiss",
            doc_dir / "metadata.json",
            doc_dir / "embeddings.npy",
        )

    def upsert(self, doc_id: str, chunks: List[str], metadata: Optional[Dict] = None) -> None:
        if not chunks:
            raise ValueError("Cannot index empty chunk list.")

        embedder = self._get_embedder()
        embeddings = embedder.encode(chunks, show_progress_bar=False, normalize_embeddings=True)
        embeddings = embeddings.astype("float32")
        doc_meta = [
            {
                "text": chunk,
                "metadata": {"chunk_index": idx, **(metadata or {})},
            }
            for idx, chunk in enumerate(chunks)
        ]

        index_path, meta_path, npy_path = self._paths(doc_id)
        np.save(npy_path, embeddings)
        with meta_path.open("w", encoding="utf-8") as handle:
            json.dump({"chunks": doc_meta, "embedding_model": self.embedding_model}, handle, ensure_ascii=False, indent=2)

        index_obj = None
        if faiss is not None:
            index_obj = faiss.IndexFlatIP(embeddings.shape[1])
            index_obj.add(embeddings)
            faiss.write_index(index_obj, str(index_path))

        self._index_cache[doc_id] = (index_obj, doc_meta, embeddings)

    def _load_index(self, doc_id: str):
        if doc_id in self._index_cache:
            return self._index_cache[doc_id]

        index_path, meta_path, npy_path = self._paths(doc_id)
        if not meta_path.exists() or not npy_path.exists():
            raise FileNotFoundError(f"No RAG cache found for {doc_id}.")

        with meta_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        embeddings = np.load(npy_path)

        index_obj = None
        if faiss is not None and index_path.exists():
            index_obj = faiss.read_index(str(index_path))

        doc_meta = payload["chunks"]
        self._index_cache[doc_id] = (index_obj, doc_meta, embeddings)
        return self._index_cache[doc_id]

    def retrieve(self, doc_id: str, query: str, top_k: Optional[int] = None) -> List[RagResult]:
        if not query.strip():
            return []
        try:
            index_obj, doc_meta, embeddings = self._load_index(doc_id)
        except FileNotFoundError:
            return []

        embedder = self._get_embedder()
        query_vec = embedder.encode([query], normalize_embeddings=True).astype("float32")
        k = top_k or self.config.top_k
        k = min(k, len(doc_meta))

        if index_obj is not None:
            scores, indices = index_obj.search(query_vec, k)
            idxs = indices[0]
            sims = scores[0]
        else:
            similarities = embeddings @ query_vec.T
            sims = similarities.flatten()
            idxs = np.argsort(-sims)[:k]

        results = []
        for i, score in zip(idxs, sims):
            if i < 0 or i >= len(doc_meta):
                continue
            meta_entry = doc_meta[i]
            results.append(RagResult(text=meta_entry["text"], score=float(score), metadata=meta_entry["metadata"]))
        return results

    def build_context_prompt(self, query: str, doc_id: str, top_k: Optional[int] = None) -> str:
        retrieved = self.retrieve(doc_id, query, top_k=top_k)
        if not retrieved:
            return ""
        context_lines = []
        remaining = self.config.max_context_chars
        for idx, result in enumerate(retrieved, start=1):
            snippet = truncate_text(result.text, max_chars=min(remaining, self.config.max_context_chars))
            block = f"Source {idx} (score {result.score:.3f}):\n{snippet}"
            block_len = len(block) + 2
            if block_len > remaining and context_lines:
                break
            context_lines.append(block)
            remaining -= block_len
        context = "\n\n".join(context_lines)
        return (
            "Use the retrieved context snippets below to answer the user. "
            "If the answer is not contained within the context, say you don't know.\n"
            f"Context:\n{context}\n"
            f"User question: {query}"
        )

    @staticmethod
    def make_doc_id(file_bytes: bytes, file_name: str) -> str:
        return hash_bytes(file_bytes + file_name.encode("utf-8"))


__all__ = ["RagPipeline", "RagConfig", "RagResult"]
