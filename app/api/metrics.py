"""
Metrics API endpoints for MultiLLM Router
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from app.core.routing_engine import RoutingEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize routing engine
routing_engine = RoutingEngine()

@router.get("/metrics")
async def get_metrics():
    """
    Get comprehensive performance metrics
    
    Returns:
        Detailed performance metrics and statistics
    """
    try:
        stats = await routing_engine.get_routing_stats()
        return {
            "metrics": stats,
            "message": "Metrics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")

@router.get("/metrics/summary")
async def get_metrics_summary():
    """
    Get summary of key performance metrics
    
    Returns:
        Summary of key metrics
    """
    try:
        stats = await routing_engine.get_routing_stats()
        
        # Extract key metrics
        summary = {
            "total_requests": stats.get("routing_stats", {}).get("total_requests", 0),
            "successful_routes": stats.get("routing_stats", {}).get("successful_routes", 0),
            "failed_routes": stats.get("routing_stats", {}).get("failed_routes", 0),
            "avg_routing_time": stats.get("routing_stats", {}).get("avg_routing_time", 0),
            "model_usage": stats.get("routing_stats", {}).get("model_usage", {}),
            "domain_distribution": stats.get("routing_stats", {}).get("domain_distribution", {}),
            "complexity_distribution": stats.get("routing_stats", {}).get("complexity_distribution", {})
        }
        
        # Calculate success rate
        total = summary["total_requests"]
        if total > 0:
            summary["success_rate"] = (summary["successful_routes"] / total) * 100
        else:
            summary["success_rate"] = 0
        
        return {
            "summary": summary,
            "message": "Metrics summary retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics summary: {str(e)}")

@router.get("/metrics/model-usage")
async def get_model_usage_metrics():
    """
    Get detailed model usage metrics
    
    Returns:
        Model usage statistics and trends
    """
    try:
        stats = await routing_engine.get_routing_stats()
        model_usage = stats.get("routing_stats", {}).get("model_usage", {})
        total_requests = stats.get("routing_stats", {}).get("total_requests", 0)
        
        if total_requests == 0:
            return {
                "model_usage": {},
                "message": "No requests processed yet"
            }
        
        # Calculate usage percentages
        usage_with_percentages = {}
        for model, count in model_usage.items():
            usage_with_percentages[model] = {
                "request_count": count,
                "usage_percentage": (count / total_requests) * 100
            }
        
        return {
            "model_usage": usage_with_percentages,
            "total_requests": total_requests,
            "message": "Model usage metrics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting model usage metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving model usage metrics: {str(e)}")

@router.get("/metrics/performance")
async def get_performance_metrics():
    """
    Get performance metrics for models and routing
    
    Returns:
        Performance metrics including response times and costs
    """
    try:
        stats = await routing_engine.get_routing_stats()
        
        performance_metrics = {
            "routing_performance": {
                "avg_routing_time": stats.get("routing_stats", {}).get("avg_routing_time", 0),
                "total_requests": stats.get("routing_stats", {}).get("total_requests", 0)
            },
            "model_performance": stats.get("model_performance", {}),
            "recent_performance": stats.get("recent_performance", {}),
            "cost_efficiency": stats.get("cost_efficiency", {})
        }
        
        return {
            "performance_metrics": performance_metrics,
            "message": "Performance metrics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving performance metrics: {str(e)}")

@router.get("/metrics/domain-distribution")
async def get_domain_distribution():
    """
    Get domain distribution metrics
    
    Returns:
        Distribution of requests across different domains
    """
    try:
        stats = await routing_engine.get_routing_stats()
        domain_dist = stats.get("routing_stats", {}).get("domain_distribution", {})
        total_requests = stats.get("routing_stats", {}).get("total_requests", 0)
        
        if total_requests == 0:
            return {
                "domain_distribution": {},
                "message": "No requests processed yet"
            }
        
        # Calculate percentages
        domain_with_percentages = {}
        for domain, count in domain_dist.items():
            domain_with_percentages[domain] = {
                "request_count": count,
                "percentage": (count / total_requests) * 100
            }
        
        return {
            "domain_distribution": domain_with_percentages,
            "total_requests": total_requests,
            "message": "Domain distribution metrics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting domain distribution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving domain distribution: {str(e)}")

@router.post("/metrics/reset")
async def reset_metrics():
    """
    Reset all performance metrics
    
    Returns:
        Confirmation of metrics reset
    """
    try:
        await routing_engine.performance_tracker.reset_stats()
        return {
            "message": "All metrics have been reset successfully",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error resetting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting metrics: {str(e)}")
