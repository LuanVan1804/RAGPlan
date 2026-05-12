"""Monitoring Service — thu thập metrics hệ thống và RAG."""

import time
import sys
import os
import logging
from app.rag import rag
from app.config import settings
from app.admin.schemas.monitoring import (
    SystemStatusResponse,
    ServerInfo,
    RAGInfo,
    LLMInfo,
    LangSmithInfo,
)

logger = logging.getLogger(__name__)

# Ghi nhận thời điểm server khởi động
_server_start_time = time.time()


def get_system_status() -> SystemStatusResponse:
    """Thu thập và trả về trạng thái toàn bộ hệ thống."""
    rag_stats = rag.get_stats()
    rag_connected = bool(rag_stats.get("connected"))
    rag_enabled = bool(rag_stats.get("enabled"))
    server_status = "healthy" if (not rag_enabled or rag_connected) else "degraded"

    return SystemStatusResponse(
        server=ServerInfo(
            status=server_status,
            uptime_seconds=round(time.time() - _server_start_time, 2),
            python_version=sys.version.split()[0],
            fastapi_version=_get_fastapi_version(),
        ),
        rag=RAGInfo(
            vector_store_type=rag_stats["vector_store_type"],
            total_documents=rag_stats["total_documents"],
            destinations_covered=rag_stats["destinations_covered"],
            persistence_file=f"pinecone:{rag_stats['pinecone_index']}/{rag_stats['namespace']}",
            persistence_file_size_kb=0.0,
            last_updated=None,
        ),
        llm=LLMInfo(
            provider="openai",
            model="gpt-4",
            api_key_configured=bool(settings.OPENAI_API_KEY),
        ),
        langsmith=LangSmithInfo(
            project=settings.LANGSMITH_PROJECT,
            tracing_enabled=bool(settings.LANGSMITH_API_KEY),
        ),
    )


def get_destinations() -> list[str]:
    """Trả về danh sách các destinations đã có data."""
    stats = rag.get_stats()
    return stats["destinations_covered"]


def get_docs_stats() -> dict:
    """Trả về thống kê số documents theo destination."""
    stats = rag.get_stats()
    return {
        "total": stats["total_documents"],
        "docs_by_destination": stats["docs_by_destination"],
    }


def _get_fastapi_version() -> str:
    """Lấy version FastAPI đang chạy."""
    try:
        import fastapi
        return fastapi.__version__
    except Exception:
        return "unknown"
