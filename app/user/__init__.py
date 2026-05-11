"""Module User — tổng hợp tất cả các router liên quan đến người dùng vào một router duy nhất.
"""

from fastapi import APIRouter
from app.user.routers.chat import router as chat_router

# Khởi tạo router chính cho User
user_router = APIRouter(prefix="/user", tags=["User"])

# Đăng ký các sub-router
user_router.include_router(chat_router)

__all__ = ["user_router"]
