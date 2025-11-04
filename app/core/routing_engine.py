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
        message: str
    ) -> Dict:
        """
        Route a request to the optimal LLM model and generate response
        
        Args:
            message: The user's prompt/message
            
        Returns:
            Dictionary with routing decision, response, and metadata
        """
        start_time = time.time()
        
        try:
            # Analyze the prompt
            analysis = await self.prompt_analyzer.analyze(message)
            
            # Select optimal model
            model_decision = await self.model_selector.select_model(analysis)
            
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
            
            # If primary model fails, try fallback models
            if not response_result.get("success", False):
                original_model = model_decision["model"]
                logger.warning(f"Primary model {original_model} failed, trying fallback models")
                response_result = await self._try_fallback_models(message, original_model)
                if response_result.get("success", False):
                    # Update model decision with fallback model
                    fallback_model = response_result.get("model", original_model)
                    model_decision["model"] = fallback_model
                    model_decision["reasoning"] = f"Fallback: {fallback_model} (original: {original_model})"
                    provider = response_result.get("provider", provider)
            
            # Track performance
            routing_time = time.time() - start_time
            await self.performance_tracker.track_routing(
                analysis, model_decision, routing_time
            )
            
            # Initialize cost estimate
            actual_cost = model_decision.get("cost_estimate", 0)
            
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
                "cost": actual_cost,
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
        # Get cost from model selector if available
        if model in self.model_selector.models:
            cost_per_token = self.model_selector.models[model]["cost_per_token"]
        else:
            # Fallback costs (only working models)
            cost_per_token = {
                "llama-3.1-8b": 0.0002,
                "llama-3.1-8b-instant": 0.0002,
                "llama-3.3-70b-versatile": 0.00069,
                "meta-llama/llama-guard-4-12b": 0.0002,
                "llama-guard-4-12b": 0.0002,
                "openai/gpt-oss-120b": 0.000375,
                "gpt-oss-120b": 0.000375,
                "openai/gpt-oss-20b": 0.0001875,
                "gpt-oss-20b": 0.0001875,
            }.get(model, 0.0002)  # Default to a reasonable cost
        
        total_tokens = usage.get("total_tokens", 0)
        return total_tokens * cost_per_token
    
    async def _try_fallback_models(self, message: str, original_model: str) -> Dict:
        """Try multiple fallback models in sequence"""
        # List of reliable general models to try in order (only working models)
        fallback_models = [
            ("llama-3.1-8b-instant", "groq"),  # Most reliable general model
            ("llama-3.1-8b", "groq"),  # Alternative Groq model
            ("gpt-oss-20b", "groq"),  # Fast OpenAI OSS model
            ("openai/gpt-oss-20b", "groq"),  # Alternative GPT OSS 20B
            ("llama-3.3-70b-versatile", "groq"),  # Higher quality fallback
            ("gpt-oss-120b", "groq"),  # Large model fallback
            ("openai/gpt-oss-120b", "groq"),  # Alternative GPT OSS 120B
        ]
        
        for model_name, provider_name in fallback_models:
            # Skip if it's the same as original model
            if model_name == original_model:
                continue
                
            # Skip if provider not available
            if not self.provider_manager.is_provider_available(provider_name):
                continue
            
            try:
                logger.info(f"Trying fallback model: {model_name} from {provider_name}")
                response_result = await self.provider_manager.generate_response(
                    prompt=message,
                    model=model_name,
                    provider=provider_name,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                if response_result.get("success", False):
                    response_result["model"] = model_name
                    response_result["provider"] = provider_name
                    logger.info(f"Fallback model {model_name} succeeded")
                    return response_result
                else:
                    logger.warning(f"Fallback model {model_name} failed: {response_result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.warning(f"Error trying fallback model {model_name}: {str(e)}")
                continue
        
        # All fallbacks failed
        return {
            "success": False,
            "content": "Unable to generate response with available models",
            "error": "All fallback models failed",
            "model": "fallback",
            "provider": "none"
        }
    
    async def _fallback_route(self, message: str) -> Dict:
        """Fallback routing when analysis fails - tries multiple general models"""
        try:
            # Try to analyze the prompt first
            try:
                analysis = await self.prompt_analyzer.analyze(message)
            except Exception:
                analysis = {"domain": "general", "complexity": "medium"}
            
            # Try fallback models
            fallback_result = await self._try_fallback_models(message, "")
            
            if fallback_result.get("success", False):
                return {
                    "response": fallback_result.get("content", "Fallback response unavailable"),
                    "model": fallback_result.get("model", "unknown"),
                    "provider": fallback_result.get("provider", "unknown"),
                    "reasoning": f"Fallback model used due to routing error",
                    "analysis": analysis,
                    "routing_time": 0.001,
                    "cost": 0.001,
                    "response_time": fallback_result.get("response_time", 1.0),
                    "success": True,
                    "usage": fallback_result.get("usage", {}),
                    "error": None
                }
            else:
                # Ultimate fallback - return error message
                return {
                    "response": "I'm sorry, I'm unable to process your request at the moment. Please try again later.",
                    "model": "fallback",
                    "provider": "none",
                    "reasoning": "Fallback due to system error - all models unavailable",
                    "analysis": analysis,
                    "routing_time": 0.001,
                    "cost": 0.0,
                    "response_time": 0.0,
                    "success": False,
                    "error": "All providers and models unavailable"
                }
        except Exception as e:
            logger.error(f"Fallback route error: {str(e)}")
            # Last resort error message
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
                "error": f"System error: {str(e)}"
            }
    
    async def get_available_models(self) -> List[Dict]:
        """Get list of available models and their capabilities"""
        return await self.model_selector.get_available_models()
    
    async def get_routing_stats(self) -> Dict:
        """Get routing performance statistics"""
        return await self.performance_tracker.get_stats()
