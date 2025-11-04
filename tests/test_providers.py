"""
Tests for LLM providers
"""

import pytest
from app.providers.provider_manager import ProviderManager

@pytest.mark.asyncio
async def test_provider_manager_initialization():
    """Test provider manager initialization"""
    manager = ProviderManager()
    assert hasattr(manager, "providers")
    assert isinstance(manager.providers, dict)

@pytest.mark.asyncio
async def test_get_available_models(provider_manager):
    """Test getting available models from providers"""
    models = await provider_manager.get_available_models()
    assert isinstance(models, list)

@pytest.mark.asyncio
async def test_health_check(provider_manager):
    """Test provider health check"""
    health = await provider_manager.health_check()
    assert isinstance(health, dict)

def test_get_provider_for_model(provider_manager):
    """Test getting provider for a model"""
    provider = provider_manager.get_provider_for_model("phi-3-mini")
    assert provider in ["huggingface", None]

def test_is_provider_available(provider_manager):
    """Test checking if provider is available"""
    # May return True or False depending on API keys
    result = provider_manager.is_provider_available("groq")
    assert isinstance(result, bool)

def test_get_available_providers(provider_manager):
    """Test getting list of available providers"""
    providers = provider_manager.get_available_providers()
    assert isinstance(providers, list)

