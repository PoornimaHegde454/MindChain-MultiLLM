"""
Tests for routing engine and model selection
"""

import pytest
from app.core.routing_engine import RoutingEngine
from app.core.prompt_analyzer import PromptAnalyzer
from app.core.model_selector import ModelSelector

@pytest.mark.asyncio
async def test_prompt_analyzer(routing_engine):
    """Test prompt analysis"""
    analyzer = routing_engine.prompt_analyzer
    
    # Test coding prompt
    analysis = await analyzer.analyze("Write a Python function to sort a list")
    assert "domain" in analysis
    assert analysis["domain"] in ["coding", "general", "technical"]
    
    # Test creative prompt
    analysis = await analyzer.analyze("Write a short story about a robot")
    assert "domain" in analysis
    
    # Test technical prompt
    analysis = await analyzer.analyze("Explain quantum computing in detail")
    assert "domain" in analysis

@pytest.mark.asyncio
async def test_model_selector(routing_engine, sample_analysis):
    """Test model selection logic"""
    selector = routing_engine.model_selector
    
    # Test with coding + low complexity
    decision = await selector.select_model(sample_analysis, {})
    assert "model" in decision
    assert "reasoning" in decision
    
    # Test with preferences
    decision = await selector.select_model(
        sample_analysis,
        {"speed": "fast", "cost": "low"}
    )
    assert "model" in decision

@pytest.mark.asyncio
async def test_routing_engine_basic(routing_engine):
    """Test basic routing functionality"""
    result = await routing_engine.route_request(
        message="Hello, how are you?",
        context=None,
        preferences=None
    )
    
    assert "response" in result
    assert "model" in result
    assert "provider" in result
    assert "cost" in result
    assert "response_time" in result

@pytest.mark.asyncio
async def test_routing_engine_with_preferences(routing_engine):
    """Test routing with user preferences"""
    result = await routing_engine.route_request(
        message="Write a Python function",
        context="coding",
        preferences={"speed": "fast", "quality": "high"}
    )
    
    assert "response" in result
    assert "model" in result

@pytest.mark.asyncio
async def test_get_available_models(routing_engine):
    """Test getting available models"""
    models = await routing_engine.get_available_models()
    assert isinstance(models, list)
    assert len(models) > 0

@pytest.mark.asyncio
async def test_get_routing_stats(routing_engine):
    """Test getting routing statistics"""
    stats = await routing_engine.get_routing_stats()
    assert isinstance(stats, dict)

