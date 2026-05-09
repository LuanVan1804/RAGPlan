"""System monitoring schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class ServerInfo(BaseModel):
    """Server runtime information."""
    status: str = Field(description="healthy | degraded")
    uptime_seconds: float
    python_version: str
    fastapi_version: str


class RAGInfo(BaseModel):
    """RAG vector store information."""
    vector_store_type: str
    total_documents: int
    destinations_covered: list[str]
    persistence_file: str
    persistence_file_size_kb: float
    last_updated: Optional[str] = None


class LLMInfo(BaseModel):
    """LLM provider information (API key is never exposed)."""
    provider: str
    model: str
    api_key_configured: bool = Field(description="True nếu API key đã được cấu hình")


class LangSmithInfo(BaseModel):
    """LangSmith tracing configuration."""
    project: str
    tracing_enabled: bool


class SystemStatusResponse(BaseModel):
    """Complete system status overview for the admin dashboard."""
    server: ServerInfo
    rag: RAGInfo
    llm: LLMInfo
    langsmith: LangSmithInfo
