"""
Performance tracking and analytics for routing decisions
"""

from typing import Dict, List, Optional
import time
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class PerformanceTracker:
    """Tracks performance metrics for routing decisions and model usage"""
    
    def __init__(self):
        # In-memory storage for metrics (in production, use a database)
        self.routing_stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "avg_routing_time": 0.0,
            "model_usage": defaultdict(int),
            "domain_distribution": defaultdict(int),
            "complexity_distribution": defaultdict(int),
            "recent_requests": deque(maxlen=1000)  # Keep last 1000 requests
        }
        
        self.response_times = deque(maxlen=1000)
        self.cost_tracking = deque(maxlen=1000)
    
    async def track_routing(
        self, 
        analysis: Dict, 
        model_decision: Dict, 
        routing_time: float
    ):
        """Track a routing decision and its performance"""
        try:
            # Update basic stats
            self.routing_stats["total_requests"] += 1
            self.routing_stats["successful_routes"] += 1
            
            # Update routing time
            self._update_avg_routing_time(routing_time)
            
            # Track model usage
            model = model_decision.get("model", "unknown")
            self.routing_stats["model_usage"][model] += 1
            
            # Track domain and complexity distribution
            domain = analysis.get("domain", "unknown")
            complexity = analysis.get("complexity", "unknown")
            self.routing_stats["domain_distribution"][domain] += 1
            self.routing_stats["complexity_distribution"][complexity] += 1
            
            # Store recent request details
            request_data = {
                "timestamp": time.time(),
                "domain": domain,
                "complexity": complexity,
                "model": model,
                "routing_time": routing_time,
                "cost_estimate": model_decision.get("cost_estimate", 0)
            }
            self.routing_stats["recent_requests"].append(request_data)
            
        except Exception as e:
            logger.error(f"Performance tracking error: {str(e)}")
            self.routing_stats["failed_routes"] += 1
    
    async def track_response_time(self, model: str, response_time: float):
        """Track actual response time for a model"""
        try:
            self.response_times.append({
                "model": model,
                "response_time": response_time,
                "timestamp": time.time()
            })
        except Exception as e:
            logger.error(f"Response time tracking error: {str(e)}")
    
    async def track_cost(self, model: str, actual_cost: float):
        """Track actual cost for a model"""
        try:
            self.cost_tracking.append({
                "model": model,
                "cost": actual_cost,
                "timestamp": time.time()
            })
        except Exception as e:
            logger.error(f"Cost tracking error: {str(e)}")
    
    def _update_avg_routing_time(self, new_time: float):
        """Update average routing time using exponential moving average"""
        current_avg = self.routing_stats["avg_routing_time"]
        total_requests = self.routing_stats["total_requests"]
        
        if total_requests == 1:
            self.routing_stats["avg_routing_time"] = new_time
        else:
            # Exponential moving average with alpha = 0.1
            alpha = 0.1
            self.routing_stats["avg_routing_time"] = (
                alpha * new_time + (1 - alpha) * current_avg
            )
    
    async def get_stats(self) -> Dict:
        """Get comprehensive performance statistics"""
        try:
            # Calculate model performance metrics
            model_performance = self._calculate_model_performance()
            
            # Calculate recent performance (last 100 requests)
            recent_performance = self._calculate_recent_performance()
            
            # Calculate cost efficiency
            cost_efficiency = self._calculate_cost_efficiency()
            
            return {
                "routing_stats": dict(self.routing_stats),
                "model_performance": model_performance,
                "recent_performance": recent_performance,
                "cost_efficiency": cost_efficiency,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Stats calculation error: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_model_performance(self) -> Dict:
        """Calculate performance metrics for each model"""
        model_perf = {}
        
        # Get response times by model
        model_response_times = defaultdict(list)
        for entry in self.response_times:
            model_response_times[entry["model"]].append(entry["response_time"])
        
        # Calculate metrics for each model
        for model, times in model_response_times.items():
            if times:
                model_perf[model] = {
                    "avg_response_time": sum(times) / len(times),
                    "min_response_time": min(times),
                    "max_response_time": max(times),
                    "request_count": len(times)
                }
        
        return model_perf
    
    def _calculate_recent_performance(self) -> Dict:
        """Calculate performance metrics for recent requests"""
        recent_requests = list(self.routing_stats["recent_requests"])
        
        if not recent_requests:
            return {"message": "No recent requests"}
        
        recent_times = [req["routing_time"] for req in recent_requests]
        
        return {
            "avg_routing_time": sum(recent_times) / len(recent_times),
            "min_routing_time": min(recent_times),
            "max_routing_time": max(recent_times),
            "request_count": len(recent_requests)
        }
    
    def _calculate_cost_efficiency(self) -> Dict:
        """Calculate cost efficiency metrics"""
        if not self.cost_tracking:
            return {"message": "No cost data available"}
        
        total_cost = sum(entry["cost"] for entry in self.cost_tracking)
        avg_cost = total_cost / len(self.cost_tracking)
        
        # Cost by model
        model_costs = defaultdict(list)
        for entry in self.cost_tracking:
            model_costs[entry["model"]].append(entry["cost"])
        
        cost_by_model = {}
        for model, costs in model_costs.items():
            cost_by_model[model] = {
                "avg_cost": sum(costs) / len(costs),
                "total_cost": sum(costs),
                "request_count": len(costs)
            }
        
        return {
            "total_cost": total_cost,
            "avg_cost_per_request": avg_cost,
            "cost_by_model": cost_by_model
        }
    
    async def get_model_usage_stats(self) -> Dict:
        """Get detailed model usage statistics"""
        total_requests = self.routing_stats["total_requests"]
        if total_requests == 0:
            return {"message": "No requests processed yet"}
        
        usage_stats = {}
        for model, count in self.routing_stats["model_usage"].items():
            usage_stats[model] = {
                "request_count": count,
                "usage_percentage": (count / total_requests) * 100
            }
        
        return usage_stats
    
    async def reset_stats(self):
        """Reset all performance statistics"""
        self.routing_stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "avg_routing_time": 0.0,
            "model_usage": defaultdict(int),
            "domain_distribution": defaultdict(int),
            "complexity_distribution": defaultdict(int),
            "recent_requests": deque(maxlen=1000)
        }
        self.response_times.clear()
        self.cost_tracking.clear()
        logger.info("Performance statistics reset")
