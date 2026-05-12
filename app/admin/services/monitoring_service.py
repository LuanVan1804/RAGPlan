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

    return SystemStatusResponse(
        server=ServerInfo(
            status="healthy",
            uptime_seconds=round(time.time() - _server_start_time, 2),
            python_version=sys.version.split()[0],
            fastapi_version=_get_fastapi_version(),
        ),
        rag=RAGInfo(
            vector_store_type="InMemoryVectorStore",
            total_documents=rag_stats["total_documents"],
            destinations_covered=rag_stats["destinations_covered"],
            persistence_file=rag_stats["persistence_file"],
            persistence_file_size_kb=rag_stats["persistence_file_size_kb"],
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
