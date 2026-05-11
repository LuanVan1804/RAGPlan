from fastapi import APIRouter, HTTPException, Header
from app.user.services.chat_service import ChatService
from app.user.schemas.chat import ChatRequest, ChatResponse
import logging

# Thiết lập logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/invoke", response_model=ChatResponse)
async def chat_invoke(request: ChatRequest):
    """
    Endpoint để gửi tin nhắn đến chatbot và nhận phản hồi.
    Hỗ trợ thread_id để duy trì ngữ cảnh cuộc hội thoại.
    """ 
    try:
        # Gọi service xử lý Chat (đã sửa lỗi chính tả proces_chat thành process_chat)
        response = await ChatService.process_chat(request)
        return response
    except Exception as e:
        # Trả về lỗi nếu có vấn đề trong quá trình xử lý
        logger.error(f"Error in chat_invoke: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
