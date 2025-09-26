"""
Base provider class for LLM providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseProvider(ABC):
    """Base class for all LLM providers"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM
        
        Args:
            prompt: The input prompt
            model: The model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with response and metadata
        """
        pass
    
    @abstractmethod
    async def get_available_models(self) -> list:
        """Get list of available models for this provider"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and accessible"""
        pass
    
    def _format_response(
        self, 
        content: str, 
        model: str, 
        usage: Optional[Dict] = None,
        response_time: float = 0.0
    ) -> Dict[str, Any]:
        """Format the response in a consistent way"""
        return {
            "content": content,
            "model": model,
            "provider": self.__class__.__name__.lower().replace("client", ""),
            "usage": usage or {},
            "response_time": response_time,
            "success": True
        }
    
    def _format_error(self, error: str, model: str) -> Dict[str, Any]:
        """Format an error response"""
        return {
            "content": f"Error: {error}",
            "model": model,
            "provider": self.__class__.__name__.lower().replace("client", ""),
            "usage": {},
            "response_time": 0.0,
            "success": False,
            "error": error
        }
