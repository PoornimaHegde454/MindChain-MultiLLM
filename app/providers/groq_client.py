"""
Groq API client implementation
"""

import httpx
import time
from typing import Dict, Any, Optional
from app.providers.base_provider import BaseProvider
from app.config import settings

class GroqClient(BaseProvider):
    """Groq API client for Llama and Mixtral models"""
    
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("Groq API key is required")
        
        super().__init__(api_key, "https://api.groq.com/openai/v1")
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
        """Generate a response using Groq API"""
        start_time = time.time()
        
        try:
            # Map our internal model names to Groq model names
            groq_models = {
                "llama-3.1-8b": "llama-3.1-8b-instant",
                "llama-3.1-8b-instant": "llama-3.1-8b-instant",
                "llama-3.1-70b": "llama-3.1-70b-versatile",
                "llama-3.1-70b-versatile": "llama-3.1-70b-versatile",
                "llama-3.3-70b-versatile": "llama-3.3-70b-versatile",
                "llama-guard-4-12b": "meta-llama/llama-guard-4-12b",
                "meta-llama/llama-guard-4-12b": "meta-llama/llama-guard-4-12b",
                "gpt-oss-120b": "openai/gpt-oss-120b",
                "openai/gpt-oss-120b": "openai/gpt-oss-120b",
                "gpt-oss-20b": "openai/gpt-oss-20b",
                "openai/gpt-oss-20b": "openai/gpt-oss-20b",
                "whisper-large-v3": "whisper-large-v3",
                "whisper-large-v3-turbo": "whisper-large-v3-turbo",
                "mixtral-8x7b": "mixtral-8x7b-32768"
            }
            
            groq_model = groq_models.get(model, model)
            
            payload = {
                "model": groq_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            # Add any additional parameters
            payload.update(kwargs)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                response_time = time.time() - start_time
                
                # Extract response content
                content = data["choices"][0]["message"]["content"]
                
                # Extract usage information
                usage = data.get("usage", {})
                
                return self._format_response(
                    content=content,
                    model=model,
                    usage=usage,
                    response_time=response_time
                )
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Groq API HTTP error: {e.response.status_code} - {e.response.text}")
            return self._format_error(f"HTTP {e.response.status_code}: {e.response.text}", model)
            
        except httpx.RequestError as e:
            self.logger.error(f"Groq API request error: {str(e)}")
            return self._format_error(f"Request error: {str(e)}", model)
            
        except Exception as e:
            self.logger.error(f"Groq API unexpected error: {str(e)}")
            return self._format_error(f"Unexpected error: {str(e)}", model)
    
    async def get_available_models(self) -> list:
        """Get list of available Groq models"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                response.raise_for_status()
                
                data = response.json()
                models = []
                
                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    # Include all Groq models: llama, mixtral, gpt-oss, whisper, llama-guard
                    if any(x in model_id for x in ["llama", "mixtral", "gpt-oss", "whisper"]):
                        models.append({
                            "id": model_id,
                            "name": model_id,
                            "provider": "groq",
                            "capabilities": self._get_model_capabilities(model_id)
                        })
                
                return models
                
        except Exception as e:
            self.logger.error(f"Error fetching Groq models: {str(e)}")
            return []
    
    def _get_model_capabilities(self, model_id: str) -> Dict[str, Any]:
        """Get capabilities for a specific model"""
        if "llama-3.1-8b" in model_id:
            return {
                "domains": ["general", "creative", "coding"],
                "complexity": ["low", "medium", "high"],
                "speed": "fast",
                "cost": "low",
                "quality": "very_good"
            }
        elif "llama-3.3-70b" in model_id:
            return {
                "domains": ["general", "creative", "coding", "technical"],
                "complexity": ["low", "medium", "high"],
                "speed": "medium",
                "cost": "high",
                "quality": "excellent"
            }
        elif "llama-3.1-70b" in model_id:
            return {
                "domains": ["general", "creative", "coding", "technical"],
                "complexity": ["low", "medium", "high"],
                "speed": "medium",
                "cost": "high",
                "quality": "excellent"
            }
        elif "llama-guard" in model_id or "guard-4" in model_id:
            return {
                "domains": ["security", "safety", "content-moderation"],
                "complexity": ["low", "medium", "high"],
                "speed": "very_fast",
                "cost": "medium",
                "quality": "very_good",
                "max_completion_tokens": 1024
            }
        elif "gpt-oss-120b" in model_id:
            return {
                "domains": ["general", "creative", "coding", "technical"],
                "complexity": ["medium", "high"],
                "speed": "medium",
                "cost": "medium",
                "quality": "excellent"
            }
        elif "gpt-oss-20b" in model_id:
            return {
                "domains": ["general", "creative", "coding", "technical"],
                "complexity": ["low", "medium", "high"],
                "speed": "fast",
                "cost": "low",
                "quality": "very_good"
            }
        elif "whisper" in model_id:
            return {
                "domains": ["audio", "transcription", "speech-to-text"],
                "complexity": ["low", "medium", "high"],
                "speed": "medium",
                "cost": "low",
                "quality": "excellent",
                "type": "audio_transcription"
            }
        elif "mixtral" in model_id:
            return {
                "domains": ["coding", "technical", "general"],
                "complexity": ["medium", "high"],
                "speed": "fast",
                "cost": "medium",
                "quality": "very_good"
            }
        else:
            return {
                "domains": ["general"],
                "complexity": ["low", "medium"],
                "speed": "fast",
                "cost": "medium",
                "quality": "good"
            }
    
    async def health_check(self) -> bool:
        """Check if Groq API is accessible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Groq health check failed: {str(e)}")
            return False
