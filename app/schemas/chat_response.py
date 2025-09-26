"""
Pydantic schemas for chat responses
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatResponse(BaseModel):
    """Response schema for chat endpoint"""
    
    model_config = {
        "protected_namespaces": (),
        "json_schema_extra": {
            "example": {
                "response": "def sort_list(lst): return sorted(lst)",
                "model_used": "phi-3-mini",
                "provider": "huggingface",
                "routing_reason": "Simple coding task, optimized for speed",
                "cost": 0.001,
                "response_time": 0.5,
                "analysis": {
                    "domain": "coding",
                    "complexity": "low",
                    "estimated_length": "short"
                },
                "conversation_id": "conv_123",
                "timestamp": 1703001234.567
            }
        }
    }
    
    response: str = Field(
        ...,
        description="The model's response to the user's message"
    )
    
    model_used: str = Field(
        ...,
        description="The model that was used to generate the response"
    )
    
    provider: str = Field(
        ...,
        description="The provider of the model used"
    )
    
    routing_reason: str = Field(
        ...,
        description="Explanation of why this model was selected"
    )
    
    cost: float = Field(
        ...,
        ge=0,
        description="Estimated cost of the request"
    )
    
    response_time: float = Field(
        ...,
        ge=0,
        description="Time taken to generate the response in seconds"
    )
    
    analysis: Optional[Dict[str, Any]] = Field(
        None,
        description="Analysis of the original prompt"
    )
    
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID if provided in request"
    )
    
    timestamp: Optional[float] = Field(
        None,
        description="Timestamp of the response"
    )

class ChatStreamResponse(BaseModel):
    """Response schema for streaming chat endpoint"""
    
    model_config = {"protected_namespaces": ()}
    
    chunk: str = Field(
        ...,
        description="A chunk of the streaming response"
    )
    
    model_used: str = Field(
        ...,
        description="The model being used for the response"
    )
    
    is_final: bool = Field(
        ...,
        description="Whether this is the final chunk"
    )
    
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID if provided in request"
    )
    
    timestamp: Optional[float] = Field(
        None,
        description="Timestamp of the chunk"
    )

class ChatErrorResponse(BaseModel):
    """Error response schema for chat endpoint"""
    
    model_config = {"protected_namespaces": ()}
    
    error: str = Field(
        ...,
        description="Error message"
    )
    
    error_code: str = Field(
        ...,
        description="Error code for programmatic handling"
    )
    
    model_used: Optional[str] = Field(
        None,
        description="Model that was attempted to be used"
    )
    
    fallback_used: Optional[bool] = Field(
        False,
        description="Whether a fallback model was used"
    )
    
    timestamp: Optional[float] = Field(
        None,
        description="Timestamp of the error"
    )
    
