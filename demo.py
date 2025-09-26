#!/usr/bin/env python3
"""
MultiLLM Router Demo Script
Demonstrates the intelligent routing capabilities of the MultiLLM Router
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_chat_endpoint(message: str, context: str = None, preferences: Dict[str, Any] = None) -> Dict:
    """Test the chat endpoint with a given message"""
    url = f"{BASE_URL}/api/v1/chat"
    payload = {
        "message": message,
        "context": context,
        "preferences": preferences or {}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def print_result(title: str, result: Dict):
    """Print a formatted result"""
    print(f"\n{'='*60}")
    print(f"🧠 {title}")
    print(f"{'='*60}")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"📝 Message: {result.get('message', 'N/A')}")
    print(f"🤖 Model Used: {result.get('model_used', 'N/A')}")
    print(f"🏢 Provider: {result.get('provider', 'N/A')}")
    print(f"💭 Reasoning: {result.get('routing_reason', 'N/A')}")
    print(f"💰 Cost: ${result.get('cost', 0):.4f}")
    print(f"⏱️  Response Time: {result.get('response_time', 0):.2f}s")
    
    analysis = result.get('analysis', {})
    if analysis:
        print(f"📊 Analysis:")
        print(f"   • Domain: {analysis.get('domain', 'N/A')}")
        print(f"   • Complexity: {analysis.get('complexity', 'N/A')}")
        print(f"   • Language: {analysis.get('language', 'N/A')}")
        print(f"   • Word Count: {analysis.get('word_count', 'N/A')}")
    
    print(f"💬 Response: {result.get('response', 'N/A')}")

def test_routing_scenarios():
    """Test various routing scenarios"""
    print("🚀 MultiLLM Router Demo")
    print("=" * 60)
    print("Testing intelligent LLM routing based on prompt analysis...")
    
    # Test scenarios
    scenarios = [
        {
            "title": "Simple Coding Question",
            "message": "Write a Python function to sort a list",
            "context": "coding",
            "preferences": {"speed": "fast", "cost": "low"}
        },
        {
            "title": "Complex Technical Analysis",
            "message": "Analyze the performance implications of using microservices architecture vs monolithic architecture for a high-traffic e-commerce platform",
            "context": "technical",
            "preferences": {"quality": "high"}
        },
        {
            "title": "Creative Writing Request",
            "message": "Write a creative story about a robot learning to paint",
            "preferences": {"quality": "high"}
        },
        {
            "title": "Simple General Question",
            "message": "What is the capital of France?",
            "preferences": {"cost": "low"}
        },
        {
            "title": "Complex Coding Problem",
            "message": "Implement a distributed caching system with Redis and implement cache invalidation strategies, including write-through, write-behind, and time-based expiration",
            "context": "coding",
            "preferences": {"quality": "high"}
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🔍 Test {i}: {scenario['title']}")
        result = test_chat_endpoint(
            scenario["message"],
            scenario.get("context"),
            scenario.get("preferences")
        )
        print_result(scenario["title"], result)
        time.sleep(1)  # Small delay between requests

def test_models_endpoint():
    """Test the models endpoint"""
    print(f"\n{'='*60}")
    print("📋 Available Models")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/models", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"Total Models: {data.get('total_count', 0)}")
        print("\nModel Details:")
        
        for model in data.get('models', []):
            print(f"\n🤖 {model['name']} ({model['provider']})")
            caps = model.get('capabilities', {})
            print(f"   • Domains: {', '.join(caps.get('domains', []))}")
            print(f"   • Complexity: {', '.join(caps.get('complexity', []))}")
            print(f"   • Speed: {caps.get('speed', 'N/A')}")
            print(f"   • Cost: {caps.get('cost', 'N/A')}")
            print(f"   • Quality: {caps.get('quality', 'N/A')}")
            print(f"   • Cost/Token: ${model.get('cost_per_token', 0):.4f}")
            print(f"   • Avg Response Time: {model.get('avg_response_time', 0):.2f}s")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching models: {e}")

def test_health_endpoint():
    """Test the health endpoint"""
    print(f"\n{'='*60}")
    print("🏥 Health Check")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"Status: {data.get('status', 'Unknown')}")
        print(f"Version: {data.get('version', 'Unknown')}")
        print(f"Message: {data.get('message', 'N/A')}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking health: {e}")

def test_metrics_endpoint():
    """Test the metrics endpoint"""
    print(f"\n{'='*60}")
    print("📊 Performance Metrics")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/metrics/summary", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        summary = data.get('summary', {})
        print(f"Total Requests: {summary.get('total_requests', 0)}")
        print(f"Successful Routes: {summary.get('successful_routes', 0)}")
        print(f"Failed Routes: {summary.get('failed_routes', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"Avg Routing Time: {summary.get('avg_routing_time', 0):.3f}s")
        
        model_usage = summary.get('model_usage', {})
        if model_usage:
            print("\nModel Usage:")
            for model, stats in model_usage.items():
                print(f"   • {model}: {stats.get('request_count', 0)} requests ({stats.get('usage_percentage', 0):.1f}%)")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching metrics: {e}")

def main():
    """Main demo function"""
    print("🎯 MultiLLM Router Demo Starting...")
    print("Make sure the server is running on http://localhost:8000")
    print("Start the server with: uvicorn main:app --reload")
    
    # Test health first
    test_health_endpoint()
    
    # Test models
    test_models_endpoint()
    
    # Test routing scenarios
    test_routing_scenarios()
    
    # Test metrics
    test_metrics_endpoint()
    
    print(f"\n{'='*60}")
    print("✅ Demo completed successfully!")
    print("🌐 Visit http://localhost:8000/docs for interactive API documentation")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
