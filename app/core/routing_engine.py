"""
Core routing engine for intelligent LLM model selection
"""

from typing import Dict, List, Optional, Tuple
import time
import logging
from app.core.prompt_analyzer import PromptAnalyzer
from app.core.model_selector import ModelSelector
from app.core.performance_tracker import PerformanceTracker
from app.providers.provider_manager import ProviderManager

logger = logging.getLogger(__name__)

class RoutingEngine:
    """Main routing engine that selects optimal models based on prompt analysis"""
    
    def __init__(self):
        self.prompt_analyzer = PromptAnalyzer()
        self.model_selector = ModelSelector()
        self.performance_tracker = PerformanceTracker()
        self.provider_manager = ProviderManager()
        
    async def route_request(
        self, 
        message: str, 
        context: Optional[str] = None,
        preferences: Optional[Dict] = None
    ) -> Dict:
        """
        Route a request to the optimal LLM model and generate response
        
        Args:
            message: The user's prompt/message
            context: Optional context about the request
            preferences: User preferences (speed, cost, quality)
            
        Returns:
            Dictionary with routing decision, response, and metadata
        """
        start_time = time.time()
        
        try:
            # Analyze the prompt
            analysis = await self.prompt_analyzer.analyze(message, context)
            
            # Select optimal model
            model_decision = await self.model_selector.select_model(
                analysis, preferences or {}
            )
            
            # Get the provider for the selected model
            provider = self.provider_manager.get_provider_for_model(model_decision["model"])
            
            if not provider or not self.provider_manager.is_provider_available(provider):
                logger.warning(f"Provider {provider} not available for model {model_decision['model']}, using fallback")
                return await self._fallback_route(message)
            
            # Generate response using the selected model and provider
            response_result = await self.provider_manager.generate_response(
                prompt=message,
                model=model_decision["model"],
                provider=provider,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Track performance
            routing_time = time.time() - start_time
            await self.performance_tracker.track_routing(
                analysis, model_decision, routing_time
            )
            
            # Track actual response time and cost
            if response_result.get("success", False):
                await self.performance_tracker.track_response_time(
                    model_decision["model"], 
                    response_result.get("response_time", 0)
                )
                
                # Calculate actual cost based on usage
                usage = response_result.get("usage", {})
                actual_cost = self._calculate_actual_cost(model_decision["model"], usage)
                await self.performance_tracker.track_cost(
                    model_decision["model"], 
                    actual_cost
                )
            
            return {
                "response": response_result.get("content", "No response generated"),
                "model": model_decision["model"],
                "provider": provider,
                "reasoning": model_decision["reasoning"],
                "analysis": analysis,
                "routing_time": routing_time,
                "cost": actual_cost if response_result.get("success", False) else model_decision.get("cost_estimate", 0),
                "response_time": response_result.get("response_time", model_decision.get("expected_response_time", 0)),
                "success": response_result.get("success", False),
                "usage": response_result.get("usage", {}),
                "error": response_result.get("error") if not response_result.get("success", False) else None
            }
            
        except Exception as e:
            logger.error(f"Routing error: {str(e)}")
            # Fallback to default model
            return await self._fallback_route(message)
    
    def _calculate_actual_cost(self, model: str, usage: Dict) -> float:
        """Calculate actual cost based on token usage"""
        cost_per_token = {
            "phi-3-mini": 0.0001,
            "llama-3.1-8b": 0.0002,
            "llama-3.1-70b": 0.0008,
            "mixtral-8x7b": 0.0004
        }
        
        total_tokens = usage.get("total_tokens", 0)
        return total_tokens * cost_per_token.get(model, 0.0001)
    
    async def _fallback_route(self, message: str) -> Dict:
        """Fallback routing when analysis fails"""
        try:
            # Try to use Hugging Face as fallback
            if self.provider_manager.is_provider_available("huggingface"):
                response_result = await self.provider_manager.generate_response(
                    prompt=message,
                    model="phi-3-mini",
                    provider="huggingface",
                    max_tokens=500,
                    temperature=0.7
                )
                
                return {
                    "response": response_result.get("content", "Fallback response unavailable"),
                    "model": "phi-3-mini",
                    "provider": "huggingface",
                    "reasoning": "Fallback due to analysis error",
                    "analysis": {"domain": "general", "complexity": "medium"},
                    "routing_time": 0.001,
                    "cost": 0.001,
                    "response_time": response_result.get("response_time", 1.0),
                    "success": response_result.get("success", False),
                    "error": response_result.get("error") if not response_result.get("success", False) else None
                }
        except Exception as e:
            logger.error(f"Fallback route error: {str(e)}")
        
        # Ultimate fallback - return error message
        return {
            "response": "I'm sorry, I'm unable to process your request at the moment. Please try again later.",
            "model": "fallback",
            "provider": "none",
            "reasoning": "Fallback due to system error",
            "analysis": {"domain": "general", "complexity": "medium"},
            "routing_time": 0.001,
            "cost": 0.0,
            "response_time": 0.0,
            "success": False,
            "error": "All providers unavailable"
        }
    
    async def get_available_models(self) -> List[Dict]:
        """Get list of available models and their capabilities"""
        return await self.model_selector.get_available_models()
    
    async def get_routing_stats(self) -> Dict:
        """Get routing performance statistics"""
        return await self.performance_tracker.get_stats()
