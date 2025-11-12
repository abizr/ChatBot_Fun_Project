from __future__ import annotations

import asyncio
import hashlib
from itertools import islice
from pathlib import Path
from typing import Iterable, List

import importlib

try:
    tiktoken = importlib.import_module("tiktoken")
except Exception:  # pragma: no cover - optional dependency
    tiktoken = None


def ensure_dir(path: str | Path) -> Path:
    """Create directory if missing and return it."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def hash_bytes(data: bytes) -> str:
    """Stable hash identifier for binary payloads."""
    return hashlib.sha256(data).hexdigest()


def chunk_text(
    text: str,
    chunk_size: int = 600,
    overlap: int = 80,
    tokenizer_name: str = "cl100k_base",
) -> List[str]:
    """
    Split text into overlapping chunks measured in tokens (or words as fallback).
    """
    text = text.strip()
    if not text:
        return []
    chunk_size = max(chunk_size, 1)
    overlap = max(min(overlap, chunk_size - 1), 0)

    if tiktoken:
        encoder = tiktoken.get_encoding(tokenizer_name)
        tokens = encoder.encode(text)
        chunks = []
        start = 0
        step = max(chunk_size - overlap, 1)
        while start < len(tokens):
            window = tokens[start : start + chunk_size]
            chunks.append(encoder.decode(window))
            start += step
        return chunks

    # Fallback to word-based splitting when tiktoken is unavailable
    words = text.split()
    chunks = []
    start = 0
    step = max(chunk_size - overlap, 1)
    while start < len(words):
        window = words[start : start + chunk_size]
        chunks.append(" ".join(window))
        start += step
    return chunks


def truncate_text(text: str, max_chars: int = 2000) -> str:
    """Trim long text to avoid blowing out prompts."""
    clean = text.strip()
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 3] + "..."


def batched(iterable: Iterable, size: int):
    """Yield items from iterable in fixed-size batches."""
    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, size))
        if not batch:
            return
        yield batch


def run_async(task):
    """
    Execute an awaitable from sync code, handling existing event loops gracefully.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # Fallback: create a new loop to avoid RuntimeError inside Streamlit.
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(task)
        finally:
            new_loop.close()
    return loop.run_until_complete(task)


__all__ = [
    "ensure_dir",
    "hash_bytes",
    "chunk_text",
    "truncate_text",
    "batched",
    "run_async",
]
