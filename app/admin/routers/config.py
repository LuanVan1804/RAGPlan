"""Config Router — endpoints quản lý cấu hình runtime.

Tất cả endpoints public, không cần xác thực.
Cấu hình lưu in-memory, sẽ reset khi restart server.
"""

from fastapi import APIRouter
from app.admin.schemas.config import ConfigResponse, UpdateConfigRequest
from app.admin.schemas.knowledge import CategoryEnum

router = APIRouter(prefix="/admin/config", tags=["Admin — Config"])

# --- Runtime config (in-memory, resets on restart) ---
_runtime_config = {
    "llm_model": "gpt-4",
    "llm_temperature": 0.3,
    "rag_default_k": 2,
    "max_content_length": 5000,
    "allowed_categories": [c.value for c in CategoryEnum],
}


def _get_config_response() -> ConfigResponse:
    return ConfigResponse(**_runtime_config)


@router.get("", response_model=ConfigResponse)
async def get_config():
    """Xem cấu hình runtime hiện tại."""
    return _get_config_response()


@router.patch("", response_model=ConfigResponse)
async def update_config(updates: UpdateConfigRequest):
    """Cập nhật cấu hình runtime (chỉ các field được gửi lên)."""
    if updates.llm_temperature is not None:
        _runtime_config["llm_temperature"] = updates.llm_temperature
    if updates.rag_default_k is not None:
        _runtime_config["rag_default_k"] = updates.rag_default_k
    if updates.max_content_length is not None:
        _runtime_config["max_content_length"] = updates.max_content_length

    return _get_config_response()
