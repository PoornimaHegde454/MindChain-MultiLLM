"""
Pydantic schemas for model information
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ModelCapabilities(BaseModel):
    """Model capabilities schema"""
    
    domains: List[str] = Field(
        ...,
        description="List of domains this model can handle"
    )
    
    complexity: List[str] = Field(
        ...,
        description="List of complexity levels this model can handle"
    )
    
    speed: str = Field(
        ...,
        description="Speed rating (fast, medium, slow)"
    )
    
    cost: str = Field(
        ...,
        description="Cost rating (very_low, low, medium, high, very_high)"
    )
    
    quality: str = Field(
        ...,
        description="Quality rating (good, very_good, excellent)"
    )

class ModelInfo(BaseModel):
    """Model information schema"""
    
    name: str = Field(
        ...,
        description="Name of the model"
    )
    
    provider: str = Field(
        ...,
        description="Provider of the model"
    )
    
    capabilities: ModelCapabilities = Field(
        ...,
        description="Capabilities of the model"
    )
    
    cost_per_token: float = Field(
        ...,
        ge=0,
        description="Cost per token for this model"
    )
    
    avg_response_time: float = Field(
        ...,
        ge=0,
        description="Average response time in seconds"
    )
    
    max_tokens: Optional[int] = Field(
        None,
        description="Maximum tokens this model can handle"
    )
    
    context_length: Optional[int] = Field(
        None,
        description="Context length this model can handle"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "phi-3-mini",
                "provider": "huggingface",
                "capabilities": {
                    "domains": ["general", "coding"],
                    "complexity": ["low", "medium"],
                    "speed": "fast",
                    "cost": "very_low",
                    "quality": "good"
                },
                "cost_per_token": 0.0001,
                "avg_response_time": 0.5,
                "max_tokens": 2048,
                "context_length": 2048
            }
        }
    }

class ModelListResponse(BaseModel):
    """Response schema for model list endpoint"""
    
    models: List[ModelInfo] = Field(
        ...,
        description="List of available models"
    )
    
    total_count: int = Field(
        ...,
        description="Total number of models available"
    )
    
    message: str = Field(
        ...,
        description="Status message"
    )

class ModelUsageStats(BaseModel):
    """Model usage statistics schema"""
    
    model_name: str = Field(
        ...,
        description="Name of the model"
    )
    
    request_count: int = Field(
        ...,
        ge=0,
        description="Number of requests for this model"
    )
    
    usage_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of total requests for this model"
    )
    
    avg_response_time: Optional[float] = Field(
        None,
        ge=0,
        description="Average response time for this model"
    )
    
    total_cost: Optional[float] = Field(
        None,
        ge=0,
        description="Total cost for this model"
    )

class ModelPerformanceMetrics(BaseModel):
    """Model performance metrics schema"""
    
    model_name: str = Field(
        ...,
        description="Name of the model"
    )
    
    avg_response_time: float = Field(
        ...,
        ge=0,
        description="Average response time"
    )
    
    min_response_time: float = Field(
        ...,
        ge=0,
        description="Minimum response time"
    )
    
    max_response_time: float = Field(
        ...,
        ge=0,
        description="Maximum response time"
    )
    
    request_count: int = Field(
        ...,
        ge=0,
        description="Number of requests"
    )
    
    success_rate: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Success rate percentage"
    )
