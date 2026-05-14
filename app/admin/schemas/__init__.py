"""Admin schemas — Pydantic models for request/response validation."""

from app.admin.schemas.knowledge import (
    IngestRequest,
    IngestResponse,
    BulkIngestRequest,
    UpdateKnowledgeRequest,
    KnowledgeListResponse,
    DocumentInfo,
)
from app.admin.schemas.monitoring import SystemStatusResponse
from app.admin.schemas.config import ConfigResponse, UpdateConfigRequest

__all__ = [
    "IngestRequest",
    "IngestResponse",
    "BulkIngestRequest",
    "UpdateKnowledgeRequest",
    "KnowledgeListResponse",
    "DocumentInfo",
    "SystemStatusResponse",
    "ConfigResponse",
    "UpdateConfigRequest",
]
