import uuid
import logging
from typing import Dict, Any, Optional
from app.graph import graph
from app.user.schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

class ChatService:
    @staticmethod
    async def process_chat(request: ChatRequest) -> ChatResponse:
        """
        Xử lý yêu cầu chat thông qua LangGraph với khả năng lưu trữ lịch sử.
        """
        thread_id = request.thread_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        # Chuẩn bị dữ liệu đầu vào cho graph
        # Graph mong đợi một dictionary với khóa 'user_input'
        inputs = {"user_input": request.message}
        
        try:
            # Chạy graph
            # Lưu ý: graph.invoke là đồng bộ, nhưng chúng ta bọc nó trong một service
            result = graph.invoke(inputs, config=config)
            
            return ChatResponse(
                final_plan=result.get("final_plan", "No plan generated."),
                is_travel_related=result.get("is_travel_related", False),
                thread_id=thread_id,
                metadata={
                    "parsed_query": result.get("parsed_query"),
                    "weather": result.get("weather_info"),
                    "cost": result.get("cost_estimate")
                }
            )
        except Exception as e:
            logger.error(f"Error in ChatService: {str(e)}")
            raise e

    @staticmethod
    async def get_history(thread_id: str) -> Dict[str, Any]:
        """
        Lấy lịch sử hội thoại cho một thread cụ thể.
        """
        config = {"configurable": {"thread_id": thread_id}}
        state = graph.get_state(config)
        
        # Trong triển khai thực tế với checkpointing, chúng ta có thể muốn lặp qua
        # lịch sử. Hiện tại, chúng ta trả về các giá trị trạng thái hiện hành.
        return {
            "thread_id": thread_id,
            "values": state.values if state else {}
        }
