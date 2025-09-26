"""
Model selection logic for choosing optimal LLM based on analysis
"""

from typing import Dict, List, Optional
import logging
from app.core.enums import Domain, Complexity

logger = logging.getLogger(__name__)

class ModelSelector:
    """Selects optimal models based on prompt analysis and preferences"""
    
    def __init__(self):
        # Model capabilities and characteristics
        self.models = {
            "phi-3-mini": {
                "provider": "huggingface",
                "capabilities": {
                    "domains": ["general", "coding"],
                    "complexity": ["low", "medium"],
                    "speed": "fast",
                    "cost": "very_low",
                    "quality": "good"
                },
                "cost_per_token": 0.0001,
                "avg_response_time": 0.5
            },
            "llama-3.1-8b": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["general", "creative", "coding"],
                    "complexity": ["low", "medium", "high"],
                    "speed": "fast",
                    "cost": "low",
                    "quality": "very_good"
                },
                "cost_per_token": 0.0002,
                "avg_response_time": 0.8
            },
            "llama-3.1-8b-instant": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["general", "creative", "coding"],
                    "complexity": ["low", "medium", "high"],
                    "speed": "fast",
                    "cost": "low",
                    "quality": "very_good"
                },
                "cost_per_token": 0.0002,
                "avg_response_time": 0.8
            },
            "llama-3.1-70b": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["general", "creative", "coding", "technical"],
                    "complexity": ["low", "medium", "high"],
                    "speed": "medium",
                    "cost": "high",
                    "quality": "excellent"
                },
                "cost_per_token": 0.0008,
                "avg_response_time": 2.0
            },
            "llama-3.1-70b-versatile": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["general", "creative", "coding", "technical"],
                    "complexity": ["low", "medium", "high"],
                    "speed": "medium",
                    "cost": "high",
                    "quality": "excellent"
                },
                "cost_per_token": 0.0008,
                "avg_response_time": 2.0
            },
            "mixtral-8x7b": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["coding", "technical", "general"],
                    "complexity": ["medium", "high"],
                    "speed": "fast",
                    "cost": "medium",
                    "quality": "very_good"
                },
                "cost_per_token": 0.0004,
                "avg_response_time": 1.2
            },
            "mixtral-8x7b-32768": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["coding", "technical", "general"],
                    "complexity": ["medium", "high"],
                    "speed": "fast",
                    "cost": "medium",
                    "quality": "very_good"
                },
                "cost_per_token": 0.0004,
                "avg_response_time": 1.2
            }
        }
        
        # Routing rules based on domain and complexity
        self.routing_rules = {
            ("coding", "low"): "llama-3.1-8b-instant",  # Use available model
            ("coding", "medium"): "llama-3.1-8b-instant",
            ("coding", "high"): "llama-3.1-8b-instant",
            ("creative", "low"): "llama-3.1-8b-instant",
            ("creative", "medium"): "llama-3.1-8b-instant",
            ("creative", "high"): "llama-3.1-8b-instant",
            ("technical", "low"): "llama-3.1-8b-instant",
            ("technical", "medium"): "llama-3.1-8b-instant",
            ("technical", "high"): "llama-3.1-8b-instant",
            ("general", "low"): "llama-3.1-8b-instant",
            ("general", "medium"): "llama-3.1-8b-instant",
            ("general", "high"): "llama-3.1-8b-instant"
        }
    
    async def select_model(
        self, 
        analysis: Dict, 
        preferences: Dict
    ) -> Dict:
        """
        Select the optimal model based on analysis and preferences
        
        Args:
            analysis: Prompt analysis results
            preferences: User preferences (speed, cost, quality)
            
        Returns:
            Dictionary with model selection and reasoning
        """
        try:
            domain = analysis.get("domain", "general")
            complexity = analysis.get("complexity", "medium")
            speed_priority = analysis.get("speed_priority", "balanced")
            
            # Get base model from routing rules
            base_model = self.routing_rules.get((domain, complexity), "llama-3.1-8b")
            
            # Apply preference adjustments
            selected_model = self._apply_preferences(
                base_model, analysis, preferences
            )
            
            # Get model details
            model_info = self.models[selected_model]
            
            # Calculate cost estimate
            estimated_tokens = self._estimate_tokens(analysis)
            cost_estimate = estimated_tokens * model_info["cost_per_token"]
            
            return {
                "model": selected_model,
                "provider": model_info["provider"],
                "reasoning": self._generate_reasoning(
                    domain, complexity, speed_priority, selected_model
                ),
                "cost_estimate": cost_estimate,
                "expected_response_time": model_info["avg_response_time"],
                "capabilities": model_info["capabilities"]
            }
            
        except Exception as e:
            logger.error(f"Model selection error: {str(e)}")
            return self._fallback_selection()
    
    def _apply_preferences(
        self, 
        base_model: str, 
        analysis: Dict, 
        preferences: Dict
    ) -> str:
        """Apply user preferences to model selection"""
        speed_pref = preferences.get("speed", "balanced")
        cost_pref = preferences.get("cost", "balanced")
        quality_pref = preferences.get("quality", "balanced")
        
        # Speed priority adjustments
        if speed_pref == "fast":
            # Prefer faster models
            if base_model == "llama-3.1-70b":
                return "llama-3.1-8b"
            elif base_model == "mixtral-8x7b":
                return "phi-3-mini"
        
        # Cost priority adjustments
        if cost_pref == "low":
            # Prefer cheaper models
            if base_model in ["llama-3.1-70b", "mixtral-8x7b"]:
                return "phi-3-mini"
            elif base_model == "llama-3.1-8b":
                return "phi-3-mini"
        
        # Quality priority adjustments
        if quality_pref == "high":
            # Prefer higher quality models
            if base_model == "phi-3-mini":
                return "llama-3.1-8b"
            elif base_model == "llama-3.1-8b":
                return "llama-3.1-70b"
        
        return base_model
    
    def _estimate_tokens(self, analysis: Dict) -> int:
        """Estimate token count for cost calculation"""
        word_count = analysis.get("word_count", 0)
        estimated_length = analysis.get("estimated_length", "medium")
        
        # Rough token estimation (1 token ≈ 0.75 words)
        base_tokens = int(word_count * 1.33)
        
        # Adjust based on estimated response length
        length_multipliers = {
            "short": 0.5,
            "medium": 1.0,
            "long": 2.0
        }
        
        multiplier = length_multipliers.get(estimated_length, 1.0)
        return int(base_tokens * multiplier)
    
    def _generate_reasoning(
        self, 
        domain: str, 
        complexity: str, 
        speed_priority: str, 
        model: str
    ) -> str:
        """Generate human-readable reasoning for model selection"""
        model_descriptions = {
            "phi-3-mini": "Phi-3 Mini (fast, cost-effective for simple tasks)",
            "llama-3.1-8b": "Llama 3.1 8B (balanced performance and speed)",
            "llama-3.1-70b": "Llama 3.1 70B (high-quality reasoning and analysis)",
            "mixtral-8x7b": "Mixtral 8x7B (excellent for coding and technical tasks)"
        }
        
        reasoning_parts = [
            f"Domain: {domain}",
            f"Complexity: {complexity}",
            f"Speed priority: {speed_priority}",
            f"Selected: {model_descriptions.get(model, model)}"
        ]
        
        return " | ".join(reasoning_parts)
    
    def _fallback_selection(self) -> Dict:
        """Fallback model selection when errors occur"""
        return {
            "model": "phi-3-mini",
            "provider": "huggingface",
            "reasoning": "Fallback selection due to error",
            "cost_estimate": 0.001,
            "expected_response_time": 0.5,
            "capabilities": {"domains": ["general"], "complexity": ["low", "medium"]}
        }
    
    async def get_available_models(self) -> List[Dict]:
        """Get list of available models and their capabilities"""
        return [
            {
                "name": name,
                "provider": info["provider"],
                "capabilities": info["capabilities"],
                "cost_per_token": info["cost_per_token"],
                "avg_response_time": info["avg_response_time"]
            }
            for name, info in self.models.items()
        ]
