"""
Database models for MultiLLM Router
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class RequestLog(Base):
    """Log table for all API requests"""
    __tablename__ = "request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    preferences = Column(JSON, nullable=True)
    conversation_id = Column(String(255), nullable=True, index=True)
    
    # Routing decision
    model_selected = Column(String(100), nullable=False)
    provider = Column(String(100), nullable=False)
    routing_reason = Column(Text, nullable=True)
    
    # Analysis
    domain = Column(String(50), nullable=True)
    complexity = Column(String(50), nullable=True)
    language = Column(String(50), nullable=True)
    
    # Performance
    routing_time = Column(Float, nullable=True)
    response_time = Column(Float, nullable=True)
    total_time = Column(Float, nullable=True)
    
    # Cost and usage
    cost = Column(Float, default=0.0)
    tokens_prompt = Column(Integer, nullable=True)
    tokens_completion = Column(Integer, nullable=True)
    tokens_total = Column(Integer, nullable=True)
    
    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ResponseLog(Base):
    """Log table for model responses"""
    __tablename__ = "response_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, nullable=False, index=True)  # Reference to request_logs.id
    response_text = Column(Text, nullable=False)
    
    # Model information
    model_used = Column(String(100), nullable=False)
    provider = Column(String(100), nullable=False)
    
    # Metadata
    usage = Column(JSON, nullable=True)
    response_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelPerformance(Base):
    """Performance metrics for each model"""
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    
    # Metrics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    
    # Performance
    avg_response_time = Column(Float, default=0.0)
    avg_routing_time = Column(Float, default=0.0)
    min_response_time = Column(Float, nullable=True)
    max_response_time = Column(Float, nullable=True)
    
    # Cost
    total_cost = Column(Float, default=0.0)
    total_tokens = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CostTracking(Base):
    """Cost tracking per day/model"""
    __tablename__ = "cost_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    
    # Cost metrics
    total_cost = Column(Float, default=0.0)
    request_count = Column(Integer, default=0)
    token_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

