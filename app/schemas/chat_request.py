"""
Pydantic schemas for chat requests
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    """Request schema for chat endpoint"""
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Write a Python function to sort a list",
                "conversation_id": "conv_123",
                "stream": False
            }
        }
    }
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The user's message or prompt"
    )
    
    conversation_id: Optional[str] = Field(
        None,
        description="Optional conversation ID for context"
    )
    
    stream: Optional[bool] = Field(
        False,
        description="Whether to stream the response"
    )

class ChatStreamRequest(ChatRequest):
    """Request schema for streaming chat endpoint"""
    
    stream: bool = Field(
        True,
        description="Streaming is enabled for this endpoint"
    )
