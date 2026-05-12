from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from app.graph import app_graph
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Travel Plan Chatbot",
    version="1.0.0",
    description="AI-powered travel planning with LangGraph and LangServe"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def travel_chain(user_input: dict) -> dict:
    """Wrapper to convert input format for LangGraph."""
    logger.info(f"Processing request: {user_input}")
    message = user_input.get("message", user_input)
    result = app_graph.invoke({"user_input": str(message)})
    logger.info(f"Response complete. Final plan length: {len(result.get('final_plan', ''))}")
    return result

@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "Travel Plan Chatbot API",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/health",
            "travel_planner_invoke": "/travel-planner/invoke",
            "travel_planner_stream": "/travel-planner/stream",
            "travel_planner_batch": "/travel-planner/batch"
        },
        "langsmith_project": settings.LANGSMITH_PROJECT,
        "note": "Use /travel-planner/invoke or /travel-planner/stream"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "travel-chatbot",
        "langsmith_project": settings.LANGSMITH_PROJECT,
        "message": "Backend is running! Visit /docs for API documentation"
    }

add_routes(
    app,
    travel_chain,
    path="/travel-planner",
    enable_feedback_endpoint=True,
    enable_public_trace_link_endpoint=True
)

logger.info("LangServe application initialized")
logger.info(f"LangSmith Project: {settings.LANGSMITH_PROJECT}")
logger.info("Available endpoints:")
logger.info("   - /docs (Swagger UI)")
logger.info("   - /travel-planner/invoke")
logger.info("   - /travel-planner/stream")
logger.info("   - /travel-planner/batch")
