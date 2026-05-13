"""Knowledge management schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class CategoryEnum(str, Enum):
    """Allowed document categories."""
    TRAVEL_GUIDE = "travel_guide"
    TIPS = "tips"
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    ACTIVITY = "activity"


class IngestRequest(BaseModel):
    """Request to add a new knowledge document to the RAG system."""
    content: str = Field(..., min_length=10, description="Nội dung tài liệu (tối thiểu 10 ký tự)")
    destination: str = Field(..., min_length=2, description="Tên điểm đến (VD: paris, tokyo)")
    category: CategoryEnum = Field(default=CategoryEnum.TRAVEL_GUIDE, description="Phân loại tài liệu")
    tags: list[str] = Field(default_factory=list, description="Tags tùy chọn")


class IngestResponse(BaseModel):
    """Response after successfully ingesting a document."""
    status: str = "success"
    message: str
    doc_id: str = Field(description="UUID của tài liệu đã tạo")
    destination: str


class DocumentInfo(BaseModel):
    """Summary information about a stored document."""
    doc_id: str
    destination: str
    category: str
    preview: str = Field(description="100 ký tự đầu của nội dung")
    created_at: str = Field(description="Thời điểm tạo (ISO 8601)")
    source: str


class KnowledgeListResponse(BaseModel):
    """Paginated list of documents in the knowledge base."""
    total: int
    documents: list[DocumentInfo]
