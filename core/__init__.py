"""
Shared interfaces for the chatbot project's core services.
"""

from .doc_ingest import DocumentBundle, DocumentIngestor
from .llm_client import OpenRouterClient, OpenRouterError
from .rag import RagConfig, RagPipeline, RagResult

__all__ = [
    "DocumentBundle",
    "DocumentIngestor",
    "OpenRouterClient",
    "OpenRouterError",
    "RagConfig",
    "RagPipeline",
    "RagResult",
]
