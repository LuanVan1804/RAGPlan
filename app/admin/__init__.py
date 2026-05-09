"""Admin module — aggregates all admin routers into a single router.

Usage in server.py:
    from app.admin import admin_router
    app.include_router(admin_router)
"""

from fastapi import APIRouter
from app.admin.routers.knowledge import router as knowledge_router
from app.admin.routers.monitoring import router as monitoring_router
from app.admin.routers.config import router as config_router

admin_router = APIRouter()
admin_router.include_router(knowledge_router)
admin_router.include_router(monitoring_router)
admin_router.include_router(config_router)

__all__ = ["admin_router"]
