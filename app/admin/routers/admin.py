from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from app.rag import rag

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
) 

class IngestRequest(BaseModel):
    text: str
    destination: str

@router.post("/ingest")
async def ingest_data(data: IngestRequest, admin_key: str = Header(None)):
    """API cho phép admin đẩy thêm kiến thức vào Vector Store."""
    if admin_key != "admin123":
        raise HTTPException(
            status_code=403, 
            detail="Bạn không có quyền admin"
        )
    
    try:
        # Gọi hàm add_knowledge từ TravelRAG
        rag.add_knowledge(data.text, {"destination": data.destination, "source": "admin_upload"})
        return {
            "status": "success",
            "message": f"Đã cập nhật kiến thức cho {data.destination} thành công!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi nạp dữ liệu: {str(e)}")

@router.get("/status")
async def get_status(admin_key: str = Header(None)):
    """Kiểm tra trạng thái hệ thống RAG."""
    if admin_key != "admin123":
        raise HTTPException(status_code=403, detail="Bạn không có quyền admin")
    
    stats = rag.get_stats()
    return {
        "vector_store_type": stats["vector_store_type"],
        "pinecone_index": stats["pinecone_index"],
        "namespace": stats["namespace"],
        "current_destinations": stats["destinations_covered"],
        "enabled": stats["enabled"],
    }
