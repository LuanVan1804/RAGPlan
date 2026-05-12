"""Runtime configuration schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class ConfigResponse(BaseModel):
    """Current runtime configuration values."""
    llm_model: str
    llm_temperature: float
    rag_default_k: int = Field(description="Số lượng documents trả về khi RAG search")
    max_content_length: int = Field(description="Giới hạn độ dài nội dung ingest")
    allowed_categories: list[str]


class UpdateConfigRequest(BaseModel):
    """Request to update runtime configuration. Only provided fields are updated."""
    llm_temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nhiệt độ LLM (0.0 - 1.0)")
    rag_default_k: Optional[int] = Field(None, ge=1, le=10, description="Số documents RAG trả về (1-10)")
    max_content_length: Optional[int] = Field(None, ge=100, le=10000, description="Giới hạn nội dung (100-10000)")
