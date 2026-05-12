from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from app.graph import app_graph
from app.config import settings
from langchain_core.runnables import RunnableLambda
from app.admin import admin_router
from app.user import user_router

app = FastAPI(
    title="Travel Plan Chatbot",
    version="1.0.0",
    description="AI-powered travel planning with LangGraph and LangServe"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def travel_chain(user_input: dict) -> dict:
    """Wrapper to convert input format for LangGraph."""
    message = user_input.get("message", user_input)
    return app_graph.invoke({"user_input": str(message)})

runnable_chain = RunnableLambda(travel_chain)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "travel-chatbot",
        "langsmith_project": settings.LANGSMITH_PROJECT
    }

add_routes(
    app,
    runnable_chain,
    path="/travel-planner",
    enable_feedback_endpoint=True,
    enable_public_trace_link_endpoint=True
)
# --- Admin routes (public, không cần đăng nhập) ---
app.include_router(admin_router)
# --- User routes (public, không cần đăng nhập) ---
app.include_router(user_router)

@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "Travel Plan Chatbot API",
        "endpoints": {
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/health",
            "travel_planner": "/travel-planner/invoke",
            "travel_planner_batch": "/travel-planner/batch",
            "travel_planner_stream": "/travel-planner/stream",
            "admin_knowledge": "/admin/knowledge/list",
            "admin_monitoring": "/admin/monitoring/status",
            "admin_config": "/admin/config",
        },
        "langsmith_tracing": settings.LANGSMITH_PROJECT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
