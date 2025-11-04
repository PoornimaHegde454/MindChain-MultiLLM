"""
Pytest configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from app.core.routing_engine import RoutingEngine
from app.providers.provider_manager import ProviderManager
import os

# Set test environment variables
os.environ["DEBUG"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///./test_multillm.db"

@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)

@pytest.fixture
def routing_engine():
    """Create routing engine instance"""
    return RoutingEngine()

@pytest.fixture
def provider_manager():
    """Create provider manager instance"""
    return ProviderManager()

@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing"""
    return {
        "message": "Write a Python function to sort a list",
        "context": "coding",
        "preferences": {
            "speed": "fast",
            "cost": "low"
        }
    }

@pytest.fixture
def sample_analysis():
    """Sample prompt analysis for testing"""
    return {
        "domain": "coding",
        "complexity": "low",
        "language": "en",
        "estimated_length": "short",
        "requires_reasoning": False,
        "requires_creativity": False
    }

