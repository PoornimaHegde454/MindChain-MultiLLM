"""
Provider manager for handling multiple LLM providers
"""

from typing import Dict, Any, Optional, List
import logging
from app.providers.groq_client import GroqClient
from app.providers.huggingface_client import HuggingFaceClient
from app.config import settings

logger = logging.getLogger(__name__)

class ProviderManager:
    """Manages all LLM providers and their interactions"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers"""
        try:
            # Initialize Groq client
            groq_key = settings.GROQ_API_KEY or settings.GROQ_KEY
            if groq_key:
                self.providers["groq"] = GroqClient(groq_key)
                logger.info("Groq provider initialized")
            else:
                logger.warning("Groq API key not found, skipping Groq provider")
            
            # Initialize Hugging Face client
            if settings.HUGGINGFACE_API_KEY:
                self.providers["huggingface"] = HuggingFaceClient()
                logger.info("Hugging Face provider initialized")
            else:
                logger.warning("Hugging Face API key not found, skipping Hugging Face provider")
            
        except Exception as e:
            logger.error(f"Error initializing providers: {str(e)}")
    
    async def generate_response(
        self, 
        prompt: str, 
        model: str,
        provider: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response using the specified provider and model"""
        try:
            if provider not in self.providers:
                return {
                    "content": f"Provider '{provider}' not available",
                    "model": model,
                    "provider": provider,
                    "success": False,
                    "error": f"Provider '{provider}' not found"
                }
            
            provider_client = self.providers[provider]
            return await provider_client.generate_response(prompt, model, **kwargs)
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "content": f"Error generating response: {str(e)}",
                "model": model,
                "provider": provider,
                "success": False,
                "error": str(e)
            }
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get all available models from all providers"""
        all_models = []
        
        for provider_name, provider_client in self.providers.items():
            try:
                models = await provider_client.get_available_models()
                for model in models:
                    model["provider"] = provider_name
                all_models.extend(models)
            except Exception as e:
                logger.error(f"Error getting models from {provider_name}: {str(e)}")
        
        return all_models
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health_status = {}
        
        for provider_name, provider_client in self.providers.items():
            try:
                health_status[provider_name] = await provider_client.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {provider_name}: {str(e)}")
                health_status[provider_name] = False
        
        return health_status
    
    def get_provider_for_model(self, model: str) -> Optional[str]:
        """Get the provider name for a given model"""
        model_provider_map = {
            "phi-3-mini": "huggingface",
            "llama-3.1-8b": "groq",
            "llama-3.1-70b": "groq",
            "mixtral-8x7b": "groq",
            # Handle actual API model names
            "llama-3.1-8b-instant": "groq",
            "llama-3.1-70b-versatile": "groq",
            "mixtral-8x7b-32768": "groq"
        }
        
        return model_provider_map.get(model)
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available"""
        return provider in self.providers
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
