from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str = Field(..., example="Plan a 3-day trip to Da Lat")
    thread_id: Optional[str] = Field(None, description="ID của thread để duy trì lịch sử hội thoại")

class ChatResponse(BaseModel):
    final_plan: str
    is_travel_related: bool
    thread_id: str
    metadata: Optional[Dict[str, Any]] = None

class HistoryResponse(BaseModel):
    thread_id: str
    messages: List[Dict[str, Any]]
