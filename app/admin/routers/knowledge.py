"""Knowledge Router — CRUD endpoints cho quản lý kiến thức RAG.

Tất cả endpoints đều public, không cần xác thực.
"""

from fastapi import APIRouter, Query
from typing import Optional
from app.admin.schemas.knowledge import (
    IngestRequest,
    IngestResponse,
    BulkIngestRequest,
    UpdateKnowledgeRequest,
    KnowledgeListResponse,
    DocumentInfo,
)
from app.admin.services import knowledge_service

router = APIRouter(prefix="/admin/knowledge", tags=["Admin — Knowledge"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(data: IngestRequest):
    """Thêm 1 tài liệu kiến thức mới vào hệ thống RAG."""
    return knowledge_service.ingest(data)


@router.post("/bulk-ingest", response_model=list[IngestResponse])
async def bulk_ingest_documents(data: BulkIngestRequest):
    """Thêm nhiều tài liệu cùng lúc (tối đa 50)."""
    return knowledge_service.bulk_ingest(data.documents)


@router.get("/list", response_model=KnowledgeListResponse)
async def list_documents(
    destination: Optional[str] = Query(None, description="Lọc theo điểm đến"),
    category: Optional[str] = Query(None, description="Lọc theo phân loại"),
):
    """Liệt kê tất cả tài liệu trong knowledge base (có filter tùy chọn)."""
    return knowledge_service.list_documents(destination=destination, category=category)


@router.get("/{doc_id}", response_model=DocumentInfo)
async def get_document(doc_id: str):
    """Xem chi tiết 1 tài liệu theo doc_id."""
    return knowledge_service.get_document(doc_id)


@router.put("/{doc_id}", response_model=DocumentInfo)
async def update_document(doc_id: str, updates: UpdateKnowledgeRequest):
    """Cập nhật nội dung hoặc metadata của 1 tài liệu."""
    return knowledge_service.update_document(doc_id, updates)


@router.post("/search", response_model=list[DocumentInfo])
async def search_documents(
    query: str = Query(..., description="Câu truy vấn tìm kiếm"),
    k: int = Query(3, ge=1, le=10, description="Số kết quả trả về"),
):
    """Tìm kiếm tài liệu tương tự (semantic search)."""
    return knowledge_service.search_similar(query=query, k=k)
