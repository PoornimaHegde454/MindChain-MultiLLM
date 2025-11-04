"""
Chat API endpoints for MultiLLM Router
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging
import time
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponse
from app.core.routing_engine import RoutingEngine
from app.database.database import get_db
from app.database.crud import RequestLogCRUD, ResponseLogCRUD, ModelPerformanceCRUD, CostTrackingCRUD

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiter will be accessed from app.state.limiter

# Initialize routing engine (in production, use dependency injection)
routing_engine = RoutingEngine()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: Request, 
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Main chat endpoint that routes requests to optimal LLM models
    
    Args:
        request: FastAPI request object
        chat_request: Chat request with message
        db: Database session
        
    Returns:
        Chat response with model-generated content and metadata
    """
    request_log_id = None
    try:
        # Route the request to optimal model and generate response
        routing_result = await routing_engine.route_request(
            message=chat_request.message
        )
        
        # Log request to database
        try:
            analysis = routing_result.get("analysis", {})
            request_log = RequestLogCRUD.create(db, {
                "message": chat_request.message,
                "context": None,
                "preferences": None,
                "conversation_id": chat_request.conversation_id,
                "model_selected": routing_result["model"],
                "provider": routing_result["provider"],
                "routing_reason": routing_result["reasoning"],
                "domain": analysis.get("domain"),
                "complexity": analysis.get("complexity"),
                "language": analysis.get("language"),
                "routing_time": routing_result.get("routing_time", 0),
                "response_time": routing_result["response_time"],
                "total_time": routing_result.get("routing_time", 0) + routing_result["response_time"],
                "cost": routing_result["cost"],
                "tokens_prompt": routing_result.get("usage", {}).get("prompt_tokens"),
                "tokens_completion": routing_result.get("usage", {}).get("completion_tokens"),
                "tokens_total": routing_result.get("usage", {}).get("total_tokens"),
                "success": routing_result.get("success", True),
                "error_message": routing_result.get("error")
            })
            request_log_id = request_log.id
            
            # Log response
            ResponseLogCRUD.create(db, {
                "request_id": request_log_id,
                "response_text": routing_result["response"],
                "model_used": routing_result["model"],
                "provider": routing_result["provider"],
                "usage": routing_result.get("usage", {}),
                "response_metadata": {
                    "routing_reason": routing_result["reasoning"],
                    "analysis": analysis
                }
            })
            
            # Update model performance metrics
            ModelPerformanceCRUD.update_metrics(
                db,
                routing_result["model"],
                routing_result["provider"],
                routing_result["response_time"],
                routing_result.get("success", True),
                routing_result["cost"],
                routing_result.get("usage", {}).get("total_tokens", 0)
            )
            
            # Update cost tracking
            CostTrackingCRUD.update_cost(
                db,
                routing_result["model"],
                routing_result["provider"],
                routing_result["cost"],
                routing_result.get("usage", {}).get("total_tokens", 0)
            )
            
        except Exception as db_error:
            logger.warning(f"Database logging error: {str(db_error)}")
            # Continue even if database logging fails
        
        return ChatResponse(
            response=routing_result["response"],
            model_used=routing_result["model"],
            provider=routing_result["provider"],
            routing_reason=routing_result["reasoning"],
            cost=routing_result["cost"],
            response_time=routing_result["response_time"],
            analysis=routing_result["analysis"],
            conversation_id=chat_request.conversation_id,
            timestamp=time.time()
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        
        # Log error to database if we have a request log
        if request_log_id:
            try:
                from app.database.models import RequestLog
                db.query(RequestLog).filter(
                    RequestLog.id == request_log_id
                ).update({"success": False, "error_message": str(e)})
                db.commit()
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint for real-time responses
    
    This endpoint streams the response as it's generated by the LLM.
    """
    from fastapi.responses import StreamingResponse
    import json
    
    async def generate_stream():
        """Generator function for streaming responses"""
        try:
            # Analyze the prompt
            analysis = await routing_engine.prompt_analyzer.analyze(
                request.message
            )
            
            # Select optimal model
            model_decision = await routing_engine.model_selector.select_model(
                analysis
            )
            
            # Get provider
            provider = routing_engine.provider_manager.get_provider_for_model(
                model_decision["model"]
            )
            
            # Send initial metadata
            yield f"data: {json.dumps({
                'type': 'metadata',
                'model': model_decision['model'],
                'provider': provider,
                'reasoning': model_decision['reasoning'],
                'analysis': analysis
            })}\n\n"
            
            # Generate response using provider (if it supports streaming)
            if provider and routing_engine.provider_manager.is_provider_available(provider):
                provider_client = routing_engine.provider_manager.providers[provider]
                
                # Check if provider supports streaming
                if hasattr(provider_client, 'generate_response_stream'):
                    async for chunk in provider_client.generate_response_stream(
                        prompt=request.message,
                        model=model_decision["model"],
                        max_tokens=1000,
                        temperature=0.7
                    ):
                        yield f"data: {json.dumps({
                            'type': 'chunk',
                            'content': chunk,
                            'model': model_decision['model']
                        })}\n\n"
                else:
                    # Fallback: generate response and stream it word by word
                    response_result = await routing_engine.provider_manager.generate_response(
                        prompt=request.message,
                        model=model_decision["model"],
                        provider=provider,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    
                    content = response_result.get("content", "")
                    # Stream word by word
                    words = content.split()
                    for word in words:
                        yield f"data: {json.dumps({
                            'type': 'chunk',
                            'content': word + ' ',
                            'model': model_decision['model']
                        })}\n\n"
                        import asyncio
                        await asyncio.sleep(0.05)  # Small delay for streaming effect
            else:
                # Fallback message
                yield f"data: {json.dumps({
                    'type': 'error',
                    'content': 'Provider not available',
                    'model': model_decision['model']
                })}\n\n"
            
            # Send final message
            yield f"data: {json.dumps({
                'type': 'done',
                'model': model_decision['model']
            })}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"data: {json.dumps({
                'type': 'error',
                'error': str(e)
            })}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/chat/history")
async def get_chat_history(limit: int = 50):
    """
    Get chat history (if implemented)
    """
    # TODO: Implement chat history
    return {"message": "Chat history not implemented yet", "limit": limit}

