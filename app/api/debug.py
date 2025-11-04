"""
Debug API endpoints for MultiLLM Router
"""

from fastapi import APIRouter, HTTPException
import logging
from app.core.routing_engine import RoutingEngine
from app.schemas.chat_request import ChatRequest

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize routing engine
routing_engine = RoutingEngine()

@router.post("/routing-debug")
async def routing_debug(request: ChatRequest):
    """
    Debug endpoint to see routing decision without generating response
    
    This endpoint analyzes the prompt and shows which model would be selected
    and why, without actually calling the LLM API.
    """
    try:
        # Analyze the prompt
        analysis = await routing_engine.prompt_analyzer.analyze(
            request.message
        )
        
        # Get model selection decision
        model_decision = await routing_engine.model_selector.select_model(
            analysis
        )
        
        # Get available models
        available_models = await routing_engine.get_available_models()
        
        # Get provider information
        provider = routing_engine.provider_manager.get_provider_for_model(
            model_decision["model"]
        )
        is_provider_available = routing_engine.provider_manager.is_provider_available(
            provider or ""
        )
        
        # Get routing statistics
        stats = await routing_engine.get_routing_stats()
        
        return {
            "message": request.message,
            "analysis": analysis,
            "model_decision": {
                **model_decision,
                "provider": provider,
                "provider_available": is_provider_available
            },
            "available_models": available_models,
            "routing_stats": stats,
            "debug_info": {
                "analyzer_version": "1.0",
                "selector_version": "1.0",
                "available_providers": routing_engine.provider_manager.get_available_providers()
            }
        }
        
    except Exception as e:
        logger.error(f"Routing debug error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug endpoint error: {str(e)}")

@router.get("/routing-debug/test")
async def routing_debug_test(
    message: str = "Write a Python function to sort a list"
):
    """
    Quick test endpoint for routing debug
    
    Args:
        message: Test message to analyze
    """
    try:
        request = ChatRequest(
            message=message
        )
        
        return await routing_debug(request)
        
    except Exception as e:
        logger.error(f"Routing debug test error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug test error: {str(e)}")

