"""Knowledge Service — business logic layer cho quản lý kiến thức RAG."""

import logging
from typing import Optional
from fastapi import HTTPException, status
from langchain_core.documents import Document
from app.rag import rag
from app.admin.schemas.knowledge import (
    IngestRequest,
    IngestResponse,
    DocumentInfo,
    KnowledgeListResponse,
)

logger = logging.getLogger(__name__)


def _doc_to_info(doc: Document) -> DocumentInfo:
    """Chuyển đổi LangChain Document thành DocumentInfo schema."""
    meta = doc.metadata
    return DocumentInfo(
        doc_id=meta.get("doc_id", "legacy"),
        destination=meta.get("destination", "unknown"),
        category=meta.get("category", "travel_guide"),
        preview=doc.page_content[:100],
        created_at=meta.get("created_at", "N/A"),
        source=meta.get("source", "unknown"),
    )


def ingest(request: IngestRequest) -> IngestResponse:
    """Thêm 1 tài liệu mới vào knowledge base.

    Args:
        request: IngestRequest chứa content, destination, category, tags.

    Returns:
        IngestResponse với doc_id của tài liệu đã tạo.
    """
    metadata = {
        "destination": request.destination.lower(),
        "category": request.category.value,
        "tags": request.tags,
    }

    doc_id = rag.add_knowledge(request.content, metadata)
    logger.info(f"Ingested document: {doc_id} for destination={request.destination}")

    return IngestResponse(
        status="success",
        message=f"Đã thêm kiến thức cho {request.destination} thành công!",
        doc_id=doc_id,
        destination=request.destination,
    )


def list_documents(
    destination: Optional[str] = None,
    category: Optional[str] = None,
) -> KnowledgeListResponse:
    """Liệt kê tài liệu trong knowledge base với filter tùy chọn.

    Args:
        destination: Lọc theo điểm đến (optional).
        category: Lọc theo phân loại (optional).

    Returns:
        KnowledgeListResponse với danh sách DocumentInfo.
    """
    all_docs = rag.get_all_documents()
    filtered = all_docs

    if destination:
        dest_lower = destination.lower()
        filtered = [
            d for d in filtered
            if d.metadata.get("destination", "").lower() == dest_lower
        ]

    if category:
        filtered = [
            d for d in filtered
            if d.metadata.get("category", "") == category
        ]

    documents = [_doc_to_info(doc) for doc in filtered]
    return KnowledgeListResponse(total=len(documents), documents=documents)


def get_document(doc_id: str) -> DocumentInfo:
    """Lấy chi tiết 1 tài liệu theo doc_id.

    Args:
        doc_id: UUID của tài liệu.

    Raises:
        HTTPException 404 nếu không tìm thấy.

    Returns:
        DocumentInfo.
    """
    doc = rag.get_document_by_id(doc_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tài liệu với doc_id: {doc_id}",
        )
    return _doc_to_info(doc)


def search_similar(query: str, k: int = 3) -> list[DocumentInfo]:
    """Tìm kiếm semantic trong knowledge base.

    Args:
        query: Câu truy vấn tìm kiếm.
        k: Số kết quả trả về.

    Returns:
        Danh sách DocumentInfo phù hợp nhất.
    """
    docs = rag.query_documents(query=query, k=k)
    results = [_doc_to_info(doc) for doc in docs]
    return results
