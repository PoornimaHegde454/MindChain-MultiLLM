"""
Models API endpoints for MultiLLM Router
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
import logging
from app.core.routing_engine import RoutingEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize routing engine
routing_engine = RoutingEngine()

@router.get("/models")
async def get_available_models():
    """
    Get list of available models and their capabilities
    
    Returns:
        List of available models with their characteristics
    """
    try:
        # Get models from model selector (includes all configured models)
        models = await routing_engine.model_selector.get_available_models()
        
        # Also get models from providers to check availability
        provider_models = await routing_engine.provider_manager.get_available_models()
        provider_model_ids = {m.get("id") or m.get("name") for m in provider_models}
        
        # Enhance model info with availability status
        for model in models:
            model_id = model["name"]
            # Check if model is available from provider
            model["available"] = model_id in provider_model_ids or any(
                model_id in (pm.get("id") or pm.get("name", "")) for pm in provider_models
            )
        
        return {
            "models": models,
            "total_count": len(models),
            "message": "Available models retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving models: {str(e)}")

@router.get("/models/{model_name}")
async def get_model_details(model_name: str):
    """
    Get detailed information about a specific model
    
    Args:
        model_name: Name of the model to get details for
        
    Returns:
        Detailed model information
    """
    try:
        models = await routing_engine.provider_manager.get_available_models()
        
        # Find the requested model
        model_info = None
        for model in models:
            if model["name"] == model_name:
                model_info = model
                break
        
        if not model_info:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
        return {
            "model": model_info,
            "message": f"Details for model '{model_name}' retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving model details: {str(e)}")

@router.get("/models/capabilities")
async def get_model_capabilities():
    """
    Get model capabilities matrix
    
    Returns:
        Matrix of models and their capabilities
    """
    try:
        models = await routing_engine.provider_manager.get_available_models()
        
        capabilities_matrix = {}
        for model in models:
            capabilities_matrix[model["name"]] = {
                "domains": model["capabilities"]["domains"],
                "complexity_levels": model["capabilities"]["complexity"],
                "speed": model["capabilities"]["speed"],
                "cost": model["capabilities"]["cost"],
                "quality": model["capabilities"]["quality"]
            }
        
        return {
            "capabilities_matrix": capabilities_matrix,
            "message": "Model capabilities matrix retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving capabilities: {str(e)}")

@router.get("/models/performance")
async def get_model_performance():
    """
    Get performance statistics for all models
    
    Returns:
        Performance statistics for each model
    """
    try:
        stats = await routing_engine.get_routing_stats()
        return {
            "performance_stats": stats,
            "message": "Model performance statistics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting performance stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving performance stats: {str(e)}")
