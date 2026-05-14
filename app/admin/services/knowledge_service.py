"""Knowledge Service — business logic layer cho quản lý kiến thức RAG."""

import logging
import io
from typing import Optional
from fastapi import HTTPException, status, UploadFile
from langchain_core.documents import Document
from app.rag import rag
from app.admin.schemas.knowledge import (
    IngestRequest,
    IngestResponse,
    DocumentInfo,
    KnowledgeListResponse,
)
from pypdf import PdfReader

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


async def process_file_upload(
    file: UploadFile,
    destination: str,
    category: str
) -> IngestResponse:
    """Xử lý file upload (.pdf hoặc .txt), trích xuất text và nạp vào RAG."""
    try:
        filename = file.filename.lower()
        extracted_text = ""
        
        content = await file.read()
        
        if filename.endswith(".pdf"):
            pdf_reader = PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        elif filename.endswith(".txt"):
            try:
                extracted_text = content.decode("utf-8")
            except UnicodeDecodeError:
                # Thử decode với latin-1 nếu utf-8 lỗi
                extracted_text = content.decode("latin-1")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Định dạng file {filename} không được hỗ trợ. Chỉ hỗ trợ .pdf và .txt"
            )
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể trích xuất văn bản từ file này hoặc file trống."
            )
            
        # Tạo request object để reuse logic ingest có sẵn
        from app.admin.schemas.knowledge import CategoryEnum
        
        ingest_req = IngestRequest(
            content=extracted_text,
            destination=destination,
            category=CategoryEnum(category) if category else CategoryEnum.TRAVEL_GUIDE,
            tags=["file_upload", file.filename]
        )
        
        return ingest(ingest_req)
        
    except Exception as e:
        logger.error(f"Error processing file upload: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý file: {str(e)}"
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
