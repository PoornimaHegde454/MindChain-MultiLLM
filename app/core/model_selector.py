"""
Model selection logic for choosing optimal LLM based on analysis
"""

from typing import Dict, List, Optional
import logging
import json
import os
from collections import defaultdict
from app.core.enums import Domain, Complexity

logger = logging.getLogger(__name__)

class ModelSelector:
    """Selects optimal models based on prompt analysis and preferences"""
    
    def __init__(self):
        # Load working models from test results
        self.working_models = self._load_working_models()
        
        # Model capabilities and characteristics (only working models)
        self.models = self._build_models_dict()
        
        # Track model usage for diversity
        self.model_usage_count = defaultdict(int)
        self.domain_complexity_last_model = {}  # Track last model used for each domain/complexity combo
        
        # Routing rules based on domain and complexity
        # Strategy:
        # - Low complexity: Fast, cost-effective models (gpt-oss-20b, llama-3.1-8b-instant)
        # - Medium complexity: Balanced models (llama-3.1-8b, gpt-oss-20b)
        # - High complexity: High-quality models (llama-3.3-70b, gpt-oss-120b)
        # - Coding tasks: Prefer llama models or gpt-oss models
        # - Technical tasks: Prefer larger models for better reasoning
        # - Creative tasks: Prefer versatile models with good language capabilities
        self.routing_rules = {
            ("coding", "low"): ["gpt-oss-20b", "llama-3.1-8b-instant", "llama-3.1-8b"],
            ("coding", "medium"): ["llama-3.1-8b", "gpt-oss-20b", "llama-3.1-8b-instant"],
            ("coding", "high"): ["llama-3.3-70b-versatile", "gpt-oss-120b", "openai/gpt-oss-120b"],
            ("creative", "low"): ["llama-3.1-8b-instant", "llama-3.1-8b", "gpt-oss-20b"],
            ("creative", "medium"): ["llama-3.1-8b", "llama-3.1-8b-instant", "gpt-oss-20b"],
            ("creative", "high"): ["llama-3.3-70b-versatile", "gpt-oss-120b", "openai/gpt-oss-120b"],
            ("technical", "low"): ["gpt-oss-20b", "llama-3.1-8b", "llama-3.1-8b-instant"],
            ("technical", "medium"): ["llama-3.3-70b-versatile", "gpt-oss-20b", "llama-3.1-8b"],
            ("technical", "high"): ["gpt-oss-120b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"],
            ("general", "low"): ["llama-3.1-8b-instant", "gpt-oss-20b", "llama-3.1-8b"],
            ("general", "medium"): ["llama-3.1-8b", "llama-3.1-8b-instant", "gpt-oss-20b"],
            ("general", "high"): ["llama-3.3-70b-versatile", "gpt-oss-120b", "openai/gpt-oss-120b"],
            ("security", "low"): ["llama-guard-4-12b", "meta-llama/llama-guard-4-12b"],
            ("security", "medium"): ["llama-guard-4-12b", "meta-llama/llama-guard-4-12b"],
            ("security", "high"): ["llama-guard-4-12b", "meta-llama/llama-guard-4-12b"],
            ("safety", "low"): ["llama-guard-4-12b", "meta-llama/llama-guard-4-12b"],
            ("safety", "medium"): ["llama-guard-4-12b", "meta-llama/llama-guard-4-12b"],
            ("safety", "high"): ["llama-guard-4-12b", "meta-llama/llama-guard-4-12b"],
            ("content-moderation", "low"): ["llama-guard-4-12b", "meta-llama/llama-guard-4-12b"],
            ("content-moderation", "medium"): ["llama-guard-4-12b", "meta-llama/llama-guard-4-12b"],
            ("content-moderation", "high"): ["llama-guard-4-12b", "meta-llama/llama-guard-4-12b"],
        }
    
    def _load_working_models(self) -> Dict:
        """Load working models from provider_model_test_results.json"""
        try:
            # Get the project root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            json_path = os.path.join(project_root, "provider_model_test_results.json")
            
            if not os.path.exists(json_path):
                logger.warning(f"Test results file not found at {json_path}, using default working models")
                return self._get_default_working_models()
            
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Extract working models (success: true)
            working_models = {}
            for model_name, model_data in data.get("models", {}).items():
                if model_data.get("success", False):
                    working_models[model_name] = {
                        "provider": model_data.get("provider"),
                        "response_time": model_data.get("response_time", 1.0),
                        "usage": model_data.get("usage", {})
                    }
            
            logger.info(f"Loaded {len(working_models)} working models from test results")
            return working_models
            
        except Exception as e:
            logger.error(f"Error loading working models: {str(e)}, using defaults")
            return self._get_default_working_models()
    
    def _get_default_working_models(self) -> Dict:
        """Default working models if JSON file is not available"""
        return {
            "llama-3.1-8b": {"provider": "groq", "response_time": 0.15},
            "llama-3.1-8b-instant": {"provider": "groq", "response_time": 0.16},
            "llama-3.3-70b-versatile": {"provider": "groq", "response_time": 0.15},
            "gpt-oss-20b": {"provider": "groq", "response_time": 0.18},
            "openai/gpt-oss-20b": {"provider": "groq", "response_time": 0.19},
            "gpt-oss-120b": {"provider": "groq", "response_time": 0.24},
            "openai/gpt-oss-120b": {"provider": "groq", "response_time": 0.27},
            "llama-guard-4-12b": {"provider": "groq", "response_time": 0.38},
            "meta-llama/llama-guard-4-12b": {"provider": "groq", "response_time": 0.37},
        }
    
    def _build_models_dict(self) -> Dict:
        """Build models dictionary with only working models"""
        # Base model configurations
        base_models = {
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
                "avg_response_time": 0.8,
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
                "avg_response_time": 0.8,
            },
            "llama-3.3-70b-versatile": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["general", "creative", "coding", "technical"],
                    "complexity": ["low", "medium", "high"],
                    "speed": "medium",
                    "cost": "high",
                    "quality": "excellent"
                },
                "cost_per_token": 0.00069,
                "avg_response_time": 1.8,
            },
            "meta-llama/llama-guard-4-12b": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["security", "safety", "content-moderation"],
                    "complexity": ["low", "medium", "high"],
                    "speed": "very_fast",
                    "cost": "medium",
                    "quality": "very_good",
                    "max_completion_tokens": 1024
                },
                "cost_per_token": 0.0002,
                "avg_response_time": 0.4,
            },
            "llama-guard-4-12b": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["security", "safety", "content-moderation"],
                    "complexity": ["low", "medium", "high"],
                    "speed": "very_fast",
                    "cost": "medium",
                    "quality": "very_good",
                    "max_completion_tokens": 1024
                },
                "cost_per_token": 0.0002,
                "avg_response_time": 0.4,
            },
            "openai/gpt-oss-120b": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["general", "creative", "coding", "technical"],
                    "complexity": ["medium", "high"],
                    "speed": "medium",
                    "cost": "medium",
                    "quality": "excellent"
                },
                "cost_per_token": 0.000375,
                "avg_response_time": 1.5,
            },
            "gpt-oss-120b": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["general", "creative", "coding", "technical"],
                    "complexity": ["medium", "high"],
                    "speed": "medium",
                    "cost": "medium",
                    "quality": "excellent"
                },
                "cost_per_token": 0.000375,
                "avg_response_time": 1.5,
            },
            "openai/gpt-oss-20b": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["general", "creative", "coding", "technical"],
                    "complexity": ["low", "medium", "high"],
                    "speed": "fast",
                    "cost": "low",
                    "quality": "very_good"
                },
                "cost_per_token": 0.0001875,
                "avg_response_time": 0.7,
            },
            "gpt-oss-20b": {
                "provider": "groq",
                "capabilities": {
                    "domains": ["general", "creative", "coding", "technical"],
                    "complexity": ["low", "medium", "high"],
                    "speed": "fast",
                    "cost": "low",
                    "quality": "very_good"
                },
                "cost_per_token": 0.0001875,
                "avg_response_time": 0.7,
            },
        }
        
        # Filter to only include working models and update response times from test results
        filtered_models = {}
        for model_name, model_config in base_models.items():
            if model_name in self.working_models:
                # Update response time from test results if available
                if "response_time" in self.working_models[model_name]:
                    model_config["avg_response_time"] = self.working_models[model_name]["response_time"]
                filtered_models[model_name] = model_config
        
        logger.info(f"Built models dictionary with {len(filtered_models)} working models")
        return filtered_models
    
    def _select_with_diversity(self, candidate_models: List[str], domain: str, complexity: str) -> str:
        """
        Select a model from candidates with diversity logic to avoid always choosing the same model
        """
        # Filter candidates to only working models
        valid_candidates = [m for m in candidate_models if m in self.models]
        
        if not valid_candidates:
            logger.warning("No valid candidates, using fallback")
            return self._get_fallback_model()
        
        # Get the key for tracking last model used
        key = f"{domain}_{complexity}"
        last_model = self.domain_complexity_last_model.get(key)
        
        # If we have multiple candidates and the last one was used, try a different one
        if len(valid_candidates) > 1 and last_model in valid_candidates:
            # Remove last used model from candidates
            other_candidates = [m for m in valid_candidates if m != last_model]
            if other_candidates:
                # Select based on usage count (prefer less used models)
                selected = min(other_candidates, key=lambda m: self.model_usage_count[m])
            else:
                selected = last_model
        else:
            # Select based on usage count (prefer less used models)
            selected = min(valid_candidates, key=lambda m: self.model_usage_count[m])
        
        # Update tracking
        self.model_usage_count[selected] += 1
        self.domain_complexity_last_model[key] = selected
        
        return selected
    
    def _get_fallback_model(self) -> str:
        """Get a reliable fallback model"""
        fallback_options = ["llama-3.1-8b-instant", "llama-3.1-8b", "gpt-oss-20b"]
        for model in fallback_options:
            if model in self.models:
                return model
        # Last resort: return first available model
        if self.models:
            return list(self.models.keys())[0]
        return "llama-3.1-8b-instant"
    
    async def select_model(
        self, 
        analysis: Dict
    ) -> Dict:
        """
        Select the optimal model based on analysis with diversity
        
        Args:
            analysis: Prompt analysis results
            
        Returns:
            Dictionary with model selection and reasoning
        """
        try:
            domain = analysis.get("domain", "general")
            complexity = analysis.get("complexity", "medium")
            speed_priority = analysis.get("speed_priority", "balanced")
            
            # Get candidate models from routing rules
            candidate_models = self.routing_rules.get(
                (domain, complexity), 
                ["llama-3.1-8b-instant", "llama-3.1-8b", "gpt-oss-20b"]
            )
            
            # Select model with diversity
            selected_model = self._select_with_diversity(candidate_models, domain, complexity)
            
            # Adjust model based on speed priority
            if speed_priority == "speed":
                selected_model = self._adjust_for_speed(selected_model, domain, complexity)
            elif speed_priority == "quality":
                selected_model = self._adjust_for_quality(selected_model, domain, complexity)
            
            # Ensure selected model is valid
            if selected_model not in self.models:
                logger.warning(f"Selected model {selected_model} not in working models, using fallback")
                selected_model = self._get_fallback_model()
            
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
    
    def _adjust_for_speed(self, base_model: str, domain: str, complexity: str) -> str:
        """Adjust model selection for speed priority"""
        # Speed adjustments: prefer faster models
        speed_optimized = {
            "llama-3.3-70b-versatile": "llama-3.1-8b-instant",
            "gpt-oss-120b": "gpt-oss-20b",
            "openai/gpt-oss-120b": "openai/gpt-oss-20b",
            "llama-3.1-8b": "llama-3.1-8b-instant"
        }
        
        if base_model in speed_optimized:
            faster_model = speed_optimized[base_model]
            if faster_model in self.models:
                return faster_model
        
        # For very low complexity, prefer fastest models
        if complexity == "low" and domain == "general":
            fast_models = ["llama-3.1-8b-instant", "gpt-oss-20b", "llama-3.1-8b"]
            for model in fast_models:
                if model in self.models:
                    return model
        
        return base_model
    
    def _adjust_for_quality(self, base_model: str, domain: str, complexity: str) -> str:
        """Adjust model selection for quality priority"""
        # Quality adjustments: prefer higher quality models
        if base_model == "gpt-oss-20b":
            quality_models = ["llama-3.1-8b", "llama-3.3-70b-versatile"] if complexity in ["medium", "high"] else ["llama-3.1-8b"]
            for model in quality_models:
                if model in self.models:
                    return model
        elif base_model == "llama-3.1-8b-instant":
            quality_models = ["llama-3.1-8b"] if complexity == "low" else ["llama-3.1-8b", "llama-3.3-70b-versatile"]
            for model in quality_models:
                if model in self.models:
                    return model
        elif base_model == "llama-3.1-8b":
            if complexity in ["medium", "high"]:
                quality_models = ["llama-3.3-70b-versatile", "gpt-oss-120b", "openai/gpt-oss-120b"]
                for model in quality_models:
                    if model in self.models:
                        return model
        
        # For high complexity, prefer largest models
        if complexity == "high":
            if domain == "coding":
                quality_models = ["llama-3.3-70b-versatile", "gpt-oss-120b", "openai/gpt-oss-120b"]
                for model in quality_models:
                    if model in self.models:
                        return model
            elif domain == "technical":
                quality_models = ["gpt-oss-120b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]
                for model in quality_models:
                    if model in self.models:
                        return model
            else:
                quality_models = ["llama-3.3-70b-versatile", "gpt-oss-120b", "openai/gpt-oss-120b"]
                for model in quality_models:
                    if model in self.models:
                        return model
        
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
            "llama-3.1-8b": "Llama 3.1 8B (balanced performance and speed)",
            "llama-3.1-8b-instant": "Llama 3.1 8B Instant (fast, balanced performance)",
            "llama-3.3-70b-versatile": "Llama 3.3 70B Versatile (latest, high-quality)",
            "llama-guard-4-12b": "Llama Guard 4 12B (content safety and moderation)",
            "meta-llama/llama-guard-4-12b": "Llama Guard 4 12B (content safety and moderation)",
            "gpt-oss-120b": "GPT OSS 120B (large, high-quality OpenAI open-source model)",
            "openai/gpt-oss-120b": "GPT OSS 120B (large, high-quality OpenAI open-source model)",
            "gpt-oss-20b": "GPT OSS 20B (fast, efficient OpenAI open-source model)",
            "openai/gpt-oss-20b": "GPT OSS 20B (fast, efficient OpenAI open-source model)",
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
        fallback_model = self._get_fallback_model()
        model_info = self.models.get(fallback_model, {
            "provider": "groq",
            "cost_per_token": 0.0002,
            "avg_response_time": 0.8,
            "capabilities": {"domains": ["general"], "complexity": ["low", "medium"]}
        })
        
        return {
            "model": fallback_model,
            "provider": model_info.get("provider", "groq"),
            "reasoning": "Fallback selection due to error",
            "cost_estimate": 0.001,
            "expected_response_time": model_info.get("avg_response_time", 0.8),
            "capabilities": model_info.get("capabilities", {})
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
