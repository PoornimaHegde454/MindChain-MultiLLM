"""
MultiLLM Router - Main Application Entry Point
Intelligent LLM routing system that selects optimal models based on prompt context
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api import chat, models, health, metrics, debug
from app.core.routing_engine import RoutingEngine
from app.config import settings
import uvicorn

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
)

# Initialize FastAPI app
app = FastAPI(
    title="MultiLLM Router",
    description="Intelligent LLM routing system that selects optimal models based on prompt context",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
app.include_router(debug.router, prefix="/api/v1", tags=["debug"])

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
