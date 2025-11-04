#!/usr/bin/env python3
"""
Test script to verify all modules work correctly
Run this after installing dependencies: pip install -r requirements.txt
"""

import sys
import traceback

def test_module(module_name, import_statement):
    """Test if a module can be imported"""
    try:
        exec(import_statement)
        print(f"✓ {module_name}")
        return True
    except ImportError as e:
        print(f"✗ {module_name}: Missing dependency - {e.name}")
        return False
    except Exception as e:
        print(f"✗ {module_name}: {type(e).__name__} - {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all module tests"""
    print("=" * 60)
    print("Testing MultiLLM Router Modules")
    print("=" * 60)
    print()
    
    results = []
    
    # Test database modules
    print("Database Modules:")
    print("-" * 60)
    results.append(test_module("Database Models", "from app.database.models import RequestLog, ResponseLog, ModelPerformance, CostTracking"))
    results.append(test_module("Database CRUD", "from app.database.crud import RequestLogCRUD, ResponseLogCRUD, ModelPerformanceCRUD, CostTrackingCRUD"))
    results.append(test_module("Database Connection", "from app.database.database import get_db, init_db, SessionLocal"))
    print()
    
    # Test utility modules
    print("Utility Modules:")
    print("-" * 60)
    results.append(test_module("Cache", "from app.utils.cache import Cache, cache"))
    results.append(test_module("Rate Limiter", "from app.utils.rate_limiter import limiter"))
    print()
    
    # Test API modules
    print("API Modules:")
    print("-" * 60)
    results.append(test_module("Chat API", "from app.api import chat"))
    results.append(test_module("Models API", "from app.api import models"))
    results.append(test_module("Health API", "from app.api import health"))
    results.append(test_module("Metrics API", "from app.api import metrics"))
    results.append(test_module("Debug API", "from app.api import debug"))
    print()
    
    # Test core modules
    print("Core Modules:")
    print("-" * 60)
    results.append(test_module("Routing Engine", "from app.core.routing_engine import RoutingEngine"))
    results.append(test_module("Prompt Analyzer", "from app.core.prompt_analyzer import PromptAnalyzer"))
    results.append(test_module("Model Selector", "from app.core.model_selector import ModelSelector"))
    results.append(test_module("Performance Tracker", "from app.core.performance_tracker import PerformanceTracker"))
    print()
    
    # Test provider modules
    print("Provider Modules:")
    print("-" * 60)
    results.append(test_module("Provider Manager", "from app.providers.provider_manager import ProviderManager"))
    results.append(test_module("Base Provider", "from app.providers.base_provider import BaseProvider"))
    results.append(test_module("Groq Client", "from app.providers.groq_client import GroqClient"))
    results.append(test_module("HuggingFace Client", "from app.providers.huggingface_client import HuggingFaceClient"))
    results.append(test_module("GitHub Models Client", "from app.providers.github_models_client import GitHubModelsClient"))
    print()
    
    # Test schema modules
    print("Schema Modules:")
    print("-" * 60)
    results.append(test_module("Chat Request Schema", "from app.schemas.chat_request import ChatRequest"))
    results.append(test_module("Chat Response Schema", "from app.schemas.chat_response import ChatResponse"))
    results.append(test_module("Model Info Schema", "from app.schemas.model_info import ModelInfo"))
    print()
    
    # Test configuration
    print("Configuration:")
    print("-" * 60)
    results.append(test_module("Settings", "from app.config import settings"))
    print()
    
    # Test main application
    print("Main Application:")
    print("-" * 60)
    results.append(test_module("FastAPI App", "from main import app"))
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} modules passed")
    print("=" * 60)
    
    if passed == total:
        print("✅ All modules are working correctly!")
        return 0
    else:
        print(f"⚠️  {total - passed} module(s) failed. Install dependencies: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

