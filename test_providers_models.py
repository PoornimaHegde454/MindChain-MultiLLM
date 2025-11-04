#!/usr/bin/env python3
"""
Test script to check which providers and models are working
Tests all configured models and generates a report of working vs non-working models
"""

import asyncio
import sys
import json
import time
from typing import Dict, List, Tuple
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.providers.provider_manager import ProviderManager
from app.core.model_selector import ModelSelector
from app.config import settings

class ProviderModelTester:
    """Test all providers and models"""
    
    def __init__(self):
        self.provider_manager = ProviderManager()
        self.model_selector = ModelSelector()
        self.results = {
            "providers": {},
            "models": {},
            "summary": {
                "total_providers": 0,
                "working_providers": 0,
                "total_models": 0,
                "working_models": 0,
                "failed_models": 0
            }
        }
        self.test_prompt = "Hello, this is a test. Please respond with 'OK'."
    
    async def test_provider_health(self, provider_name: str) -> bool:
        """Test if a provider is healthy"""
        try:
            if not self.provider_manager.is_provider_available(provider_name):
                return False
            
            provider_client = self.provider_manager.providers.get(provider_name)
            if provider_client:
                health = await provider_client.health_check()
                return health
            return False
        except Exception as e:
            print(f"  ❌ Health check error: {str(e)}")
            return False
    
    async def test_model(self, model_name: str, provider_name: str) -> Tuple[bool, Dict]:
        """Test if a model works"""
        result = {
            "model": model_name,
            "provider": provider_name,
            "success": False,
            "response_time": 0.0,
            "error": None,
            "response_preview": None
        }
        
        try:
            start_time = time.time()
            
            # Generate a test response
            response = await self.provider_manager.generate_response(
                prompt=self.test_prompt,
                model=model_name,
                provider=provider_name,
                max_tokens=50,  # Small response for testing
                temperature=0.7
            )
            
            response_time = time.time() - start_time
            result["response_time"] = response_time
            
            if response.get("success", False):
                result["success"] = True
                content = response.get("content", "")
                result["response_preview"] = content[:100] + "..." if len(content) > 100 else content
                result["usage"] = response.get("usage", {})
            else:
                result["success"] = False
                result["error"] = response.get("error", "Unknown error")
                
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
        
        return result["success"], result
    
    async def test_all_providers(self):
        """Test all providers"""
        print("\n" + "=" * 70)
        print("Testing Providers")
        print("=" * 70)
        
        available_providers = self.provider_manager.get_available_providers()
        self.results["summary"]["total_providers"] = len(available_providers)
        
        for provider_name in available_providers:
            print(f"\n📡 Testing provider: {provider_name}")
            print("-" * 70)
            
            is_available = self.provider_manager.is_provider_available(provider_name)
            print(f"  Available: {'✅ Yes' if is_available else '❌ No'}")
            
            if is_available:
                is_healthy = await self.test_provider_health(provider_name)
                print(f"  Health: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
                
                self.results["providers"][provider_name] = {
                    "available": is_available,
                    "healthy": is_healthy
                }
                
                if is_healthy:
                    self.results["summary"]["working_providers"] += 1
            else:
                self.results["providers"][provider_name] = {
                    "available": False,
                    "healthy": False
                }
    
    async def test_all_models(self):
        """Test all configured models"""
        print("\n" + "=" * 70)
        print("Testing Models")
        print("=" * 70)
        
        # Get all models from model selector
        all_models = self.model_selector.models
        self.results["summary"]["total_models"] = len(all_models)
        
        working_models = []
        failed_models = []
        
        for model_name, model_info in all_models.items():
            provider_name = model_info.get("provider")
            
            print(f"\n🤖 Testing model: {model_name}")
            print(f"   Provider: {provider_name}")
            print("-" * 70)
            
            # Check if provider is available
            if not self.provider_manager.is_provider_available(provider_name):
                print(f"  ❌ Provider '{provider_name}' not available")
                result = {
                    "model": model_name,
                    "provider": provider_name,
                    "success": False,
                    "error": f"Provider '{provider_name}' not available",
                    "response_time": 0.0
                }
                self.results["models"][model_name] = result
                failed_models.append(model_name)
                continue
            
            # Test the model
            success, result = await self.test_model(model_name, provider_name)
            self.results["models"][model_name] = result
            
            if success:
                print(f"  ✅ Working")
                print(f"  ⏱️  Response time: {result['response_time']:.2f}s")
                if result.get("response_preview"):
                    print(f"  📝 Response: {result['response_preview']}")
                working_models.append(model_name)
                self.results["summary"]["working_models"] += 1
            else:
                print(f"  ❌ Failed")
                print(f"  💥 Error: {result.get('error', 'Unknown error')}")
                failed_models.append(model_name)
                self.results["summary"]["failed_models"] += 1
            
            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)
        
        return working_models, failed_models
    
    def generate_report(self, working_models: List[str], failed_models: List[str]):
        """Generate a detailed report"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        print(f"\n📊 Providers:")
        print(f"   Total: {self.results['summary']['total_providers']}")
        print(f"   ✅ Working: {self.results['summary']['working_providers']}")
        print(f"   ❌ Failed: {self.results['summary']['total_providers'] - self.results['summary']['working_providers']}")
        
        print(f"\n🤖 Models:")
        print(f"   Total: {self.results['summary']['total_models']}")
        print(f"   ✅ Working: {self.results['summary']['working_models']}")
        print(f"   ❌ Failed: {self.results['summary']['failed_models']}")
        
        print(f"\n✅ Working Models ({len(working_models)}):")
        for model in working_models:
            model_info = self.results["models"][model]
            provider = model_info["provider"]
            response_time = model_info.get("response_time", 0)
            print(f"   • {model} ({provider}) - {response_time:.2f}s")
        
        if failed_models:
            print(f"\n❌ Failed Models ({len(failed_models)}):")
            for model in failed_models:
                model_info = self.results["models"][model]
                provider = model_info["provider"]
                error = model_info.get("error", "Unknown error")
                print(f"   • {model} ({provider}) - Error: {error}")
        
        # Save detailed results to JSON
        output_file = "provider_model_test_results.json"
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {output_file}")
    
    def generate_filtered_model_config(self, working_models: List[str]):
        """Generate a filtered model configuration with only working models"""
        filtered_models = {}
        filtered_routing_rules = {}
        
        # Filter models
        for model_name in working_models:
            if model_name in self.model_selector.models:
                filtered_models[model_name] = self.model_selector.models[model_name]
        
        # Filter routing rules - only keep rules that use working models
        for (domain, complexity), model_name in self.model_selector.routing_rules.items():
            if model_name in working_models:
                filtered_routing_rules[(domain, complexity)] = model_name
            else:
                # Find a working alternative
                # Try to find a working model with similar capabilities
                model_info = self.model_selector.models.get(model_name, {})
                model_domains = model_info.get("capabilities", {}).get("domains", [])
                model_complexity = model_info.get("capabilities", {}).get("complexity", [])
                
                # Find a working alternative
                alternative = None
                for working_model in working_models:
                    working_info = self.model_selector.models.get(working_model, {})
                    working_domains = working_info.get("capabilities", {}).get("domains", [])
                    working_complexity_levels = working_info.get("capabilities", {}).get("complexity", [])
                    
                    if domain in working_domains and complexity in working_complexity_levels:
                        alternative = working_model
                        break
                
                # If no specific alternative, use a general working model
                if not alternative and working_models:
                    # Prefer llama-3.1-8b-instant or similar
                    for preferred in ["llama-3.1-8b-instant", "llama-3.1-8b", "gpt-oss-20b", "phi-3-mini"]:
                        if preferred in working_models:
                            alternative = preferred
                            break
                    if not alternative:
                        alternative = working_models[0]  # Use first working model
                
                if alternative:
                    filtered_routing_rules[(domain, complexity)] = alternative
                    print(f"   ⚠️  Replaced {model_name} with {alternative} for ({domain}, {complexity})")
        
        # Generate Python code snippet
        config_code = f"""# Filtered model configuration - Only working models
# Generated by test_providers_models.py
# Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

WORKING_MODELS = {json.dumps(filtered_models, indent=2)}

WORKING_ROUTING_RULES = {{
"""
        for (domain, complexity), model_name in filtered_routing_rules.items():
            config_code += f'    ("{domain}", "{complexity}"): "{model_name}",\n'
        config_code += "}\n"
        
        output_file = "working_models_config.py"
        with open(output_file, "w") as f:
            f.write(config_code)
        
        print(f"\n📝 Filtered model configuration saved to: {output_file}")
        print(f"   Working models: {len(filtered_models)}")
        print(f"   Routing rules: {len(filtered_routing_rules)}")
        
        return filtered_models, filtered_routing_rules

async def main():
    """Main test function"""
    print("=" * 70)
    print("Provider and Model Tester")
    print("=" * 70)
    print(f"\nTest prompt: '{ProviderModelTester().test_prompt}'")
    print(f"API Keys configured:")
    print(f"  Groq: {'✅' if (settings.GROQ_API_KEY or settings.GROQ_KEY) else '❌'}")
    print(f"  Hugging Face: {'✅' if settings.HUGGINGFACE_API_KEY else '❌'}")
    print(f"  GitHub Models: {'✅' if settings.GITHUB_MODELS_API_KEY else '❌'}")
    
    tester = ProviderModelTester()
    
    # Test providers
    await tester.test_all_providers()
    
    # Test models
    working_models, failed_models = await tester.test_all_models()
    
    # Generate report
    tester.generate_report(working_models, failed_models)
    
    # Generate filtered configuration
    if working_models:
        print("\n" + "=" * 70)
        print("Generating Filtered Configuration")
        print("=" * 70)
        filtered_models, filtered_rules = tester.generate_filtered_model_config(working_models)
        
        print("\n✅ Test completed!")
        print(f"\n💡 To use only working models, update your model_selector.py with the filtered configuration.")
    else:
        print("\n⚠️  No working models found! Check your API keys and provider configurations.")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

