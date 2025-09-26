"""
Health check API endpoints for MultiLLM Router
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import time
from app.core.routing_engine import RoutingEngine
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize routing engine
routing_engine = RoutingEngine()

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    
    Returns:
        Health status and basic system information
    """
    try:
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": settings.APP_VERSION,
            "uptime": "unknown",  # TODO: Implement uptime tracking
            "message": "MultiLLM Router is running"
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with component status
    
    Returns:
        Detailed health information for all components
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "version": settings.APP_VERSION,
            "components": {}
        }
        
        # Check routing engine
        try:
            # Test routing engine with a simple request
            test_analysis = await routing_engine.prompt_analyzer.analyze("test message")
            health_status["components"]["routing_engine"] = {
                "status": "healthy",
                "message": "Routing engine is functioning"
            }
        except Exception as e:
            health_status["components"]["routing_engine"] = {
                "status": "unhealthy",
                "message": f"Routing engine error: {str(e)}"
            }
            health_status["status"] = "degraded"
        
        # Check providers
        try:
            provider_health = await routing_engine.provider_manager.health_check()
            available_providers = [p for p, healthy in provider_health.items() if healthy]
            health_status["components"]["providers"] = {
                "status": "healthy" if available_providers else "unhealthy",
                "message": f"Providers: {', '.join(available_providers) if available_providers else 'None available'}",
                "details": provider_health
            }
            if not available_providers:
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["providers"] = {
                "status": "unhealthy",
                "message": f"Provider health check error: {str(e)}"
            }
            health_status["status"] = "degraded"
        
        # Check performance tracker
        try:
            stats = await routing_engine.get_routing_stats()
            health_status["components"]["performance_tracker"] = {
                "status": "healthy",
                "message": "Performance tracker is functioning"
            }
        except Exception as e:
            health_status["components"]["performance_tracker"] = {
                "status": "unhealthy",
                "message": f"Performance tracker error: {str(e)}"
            }
            health_status["status"] = "degraded"
        
        # Check configuration
        health_status["components"]["configuration"] = {
            "status": "healthy",
            "debug_mode": settings.DEBUG,
            "log_level": settings.LOG_LEVEL,
            "message": "Configuration loaded successfully"
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Detailed health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detailed health check failed: {str(e)}")

@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/container orchestration
    
    Returns:
        Ready status for load balancer health checks
    """
    try:
        # Check if all critical components are ready
        models = await routing_engine.get_available_models()
        
        if len(models) == 0:
            return {
                "status": "not_ready",
                "message": "No models available",
                "timestamp": time.time()
            }
        
        return {
            "status": "ready",
            "message": "Service is ready to accept requests",
            "timestamp": time.time(),
            "models_available": len(models)
        }
        
    except Exception as e:
        logger.error(f"Readiness check error: {str(e)}")
        return {
            "status": "not_ready",
            "message": f"Service not ready: {str(e)}",
            "timestamp": time.time()
        }

@router.get("/health/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration
    
    Returns:
        Live status for container health checks
    """
    try:
        return {
            "status": "alive",
            "message": "Service is alive and responding",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Liveness check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Liveness check failed: {str(e)}")
