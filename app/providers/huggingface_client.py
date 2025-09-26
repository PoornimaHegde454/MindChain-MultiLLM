"""
Hugging Face API client implementation
"""

import httpx
import time
import asyncio
from typing import Dict, Any, Optional
from app.providers.base_provider import BaseProvider
from app.config import settings

class HuggingFaceClient(BaseProvider):
    """Hugging Face API client for Phi-3 Mini and other models"""
    
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or settings.HUGGINGFACE_API_KEY
        if not api_key:
            raise ValueError("Hugging Face API key is required")
        
        super().__init__(api_key, "https://api-inference.huggingface.co")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_response(
        self, 
        prompt: str, 
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response using Hugging Face API"""
        start_time = time.time()
        
        try:
            # Map our internal model names to Hugging Face model names
            hf_models = {
                "phi-3-mini": "microsoft/Phi-3-mini-4k-instruct"
            }
            
            hf_model = hf_models.get(model, model)
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": min(max_tokens, 1000),  # HF has limits
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
            
            # Add any additional parameters
            payload["parameters"].update(kwargs)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{hf_model}",
                    headers=self.headers,
                    json=payload
                )
                
                # Handle rate limiting
                if response.status_code == 503:
                    # Model is loading, wait and retry
                    await asyncio.sleep(10)
                    response = await client.post(
                        f"{self.base_url}/models/{hf_model}",
                        headers=self.headers,
                        json=payload
                    )
                
                response.raise_for_status()
                
                data = response.json()
                response_time = time.time() - start_time
                
                # Extract response content
                if isinstance(data, list) and len(data) > 0:
                    content = data[0].get("generated_text", "")
                else:
                    content = str(data)
                
                # Estimate usage (HF doesn't provide detailed usage info)
                usage = {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(content.split()),
                    "total_tokens": len(prompt.split()) + len(content.split())
                }
                
                return self._format_response(
                    content=content,
                    model=model,
                    usage=usage,
                    response_time=response_time
                )
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Hugging Face API HTTP error: {e.response.status_code} - {e.response.text}")
            return self._format_error(f"HTTP {e.response.status_code}: {e.response.text}", model)
            
        except httpx.RequestError as e:
            self.logger.error(f"Hugging Face API request error: {str(e)}")
            return self._format_error(f"Request error: {str(e)}", model)
            
        except Exception as e:
            self.logger.error(f"Hugging Face API unexpected error: {str(e)}")
            return self._format_error(f"Unexpected error: {str(e)}", model)
    
    async def get_available_models(self) -> list:
        """Get list of available Hugging Face models"""
        try:
            # For now, return our configured models
            return [
                {
                    "id": "microsoft/Phi-3-mini-4k-instruct",
                    "name": "phi-3-mini",
                    "provider": "huggingface",
                    "capabilities": {
                        "domains": ["general", "coding"],
                        "complexity": ["low", "medium"],
                        "speed": "fast",
                        "cost": "very_low",
                        "quality": "good"
                    }
                }
            ]
        except Exception as e:
            self.logger.error(f"Error fetching Hugging Face models: {str(e)}")
            return []
    
    async def health_check(self) -> bool:
        """Check if Hugging Face API is accessible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://huggingface.co/api/models",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Hugging Face health check failed: {str(e)}")
            return False
