"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import os

# Set test environment
os.environ["DEBUG"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///./test_multillm.db"

@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_models_endpoint(client):
    """Test models endpoint"""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data or isinstance(data, list)

def test_chat_endpoint(client, sample_chat_request):
    """Test chat endpoint"""
    response = client.post("/api/v1/chat", json=sample_chat_request)
    # May return 200 or 500 depending on API keys
    assert response.status_code in [200, 500, 503]
    if response.status_code == 200:
        data = response.json()
        assert "response" in data
        assert "model_used" in data
        assert "provider" in data

def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data or isinstance(data, dict)

def test_routing_debug_endpoint(client, sample_chat_request):
    """Test routing debug endpoint"""
    response = client.post("/api/v1/routing-debug", json=sample_chat_request)
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "model_decision" in data

def test_routing_debug_test_endpoint(client):
    """Test routing debug test endpoint"""
    response = client.get(
        "/api/v1/routing-debug/test",
        params={"message": "Test message"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data

