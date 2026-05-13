"""Monitoring Router — endpoints giám sát hệ thống.

Tất cả endpoints đều public, không cần xác thực.
"""

from fastapi import APIRouter
from app.admin.schemas.monitoring import SystemStatusResponse
from app.admin.services import monitoring_service

router = APIRouter(prefix="/admin/monitoring", tags=["Admin — Monitoring"])


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Trạng thái tổng quan toàn hệ thống: server, RAG, LLM, LangSmith."""
    return monitoring_service.get_system_status()


@router.get("/destinations")
async def get_destinations():
    """Danh sách tất cả destinations đã có dữ liệu trong knowledge base."""
    destinations = monitoring_service.get_destinations()
    return {"destinations": destinations}


@router.get("/stats")
async def get_stats():
    """Thống kê chi tiết số lượng tài liệu theo từng destination."""
    return monitoring_service.get_docs_stats()
