"""
GitHub Models API client implementation (optional provider)
"""

import httpx
import time
from typing import Dict, Any, Optional
from app.providers.base_provider import BaseProvider
from app.config import settings

class GitHubModelsClient(BaseProvider):
    """GitHub Models API client (if available)"""
    
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or settings.GITHUB_MODELS_API_KEY
        if not api_key:
            raise ValueError("GitHub Models API key is required")
        
        # GitHub Models API endpoint (placeholder - update with actual endpoint)
        super().__init__(api_key, "https://api.github.com/models")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def generate_response(
        self, 
        prompt: str, 
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response using GitHub Models API"""
        start_time = time.time()
        
        try:
            # Note: This is a placeholder implementation
            # Update with actual GitHub Models API endpoint when available
            
            payload = {
                "prompt": prompt,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                response_time = time.time() - start_time
                
                # Extract response content
                content = data.get("response", data.get("text", ""))
                
                # Extract usage information
                usage = data.get("usage", {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(content.split()),
                    "total_tokens": len(prompt.split()) + len(content.split())
                })
                
                return self._format_response(
                    content=content,
                    model=model,
                    usage=usage,
                    response_time=response_time
                )
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"GitHub Models API HTTP error: {e.response.status_code} - {e.response.text}")
            return self._format_error(f"HTTP {e.response.status_code}: {e.response.text}", model)
            
        except httpx.RequestError as e:
            self.logger.error(f"GitHub Models API request error: {str(e)}")
            return self._format_error(f"Request error: {str(e)}", model)
            
        except Exception as e:
            self.logger.error(f"GitHub Models API unexpected error: {str(e)}")
            return self._format_error(f"Unexpected error: {str(e)}", model)
    
    async def get_available_models(self) -> list:
        """Get list of available GitHub Models"""
        try:
            # Placeholder - update with actual API call when available
            return [
                {
                    "id": "github-model-1",
                    "name": "github-model-1",
                    "provider": "github",
                    "capabilities": {
                        "domains": ["general", "coding"],
                        "complexity": ["low", "medium"],
                        "speed": "medium",
                        "cost": "low",
                        "quality": "good"
                    }
                }
            ]
        except Exception as e:
            self.logger.error(f"Error fetching GitHub Models: {str(e)}")
            return []
    
    async def health_check(self) -> bool:
        """Check if GitHub Models API is accessible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception as e:
            self.logger.error(f"GitHub Models health check failed: {str(e)}")
            return False

