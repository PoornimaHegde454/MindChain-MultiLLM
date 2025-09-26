"""
MultiLLM Router - Main Application Entry Point
Intelligent LLM routing system that selects optimal models based on prompt context
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, models, health, metrics
from app.core.routing_engine import RoutingEngine
from app.config import settings
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="MultiLLM Router",
    description="Intelligent LLM routing system that selects optimal models based on prompt context",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize routing engine
routing_engine = RoutingEngine()

# Include API routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(models.router, prefix="/api/v1", tags=["models"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])

@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "MultiLLM Router API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
