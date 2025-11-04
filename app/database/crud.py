"""
CRUD operations for database models
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from app.database.models import RequestLog, ResponseLog, ModelPerformance, CostTracking

class RequestLogCRUD:
    """CRUD operations for request logs"""
    
    @staticmethod
    def create(db: Session, request_data: Dict[str, Any]) -> RequestLog:
        """Create a new request log entry"""
        log = RequestLog(**request_data)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_by_id(db: Session, log_id: int) -> Optional[RequestLog]:
        """Get request log by ID"""
        return db.query(RequestLog).filter(RequestLog.id == log_id).first()
    
    @staticmethod
    def get_by_conversation(
        db: Session, 
        conversation_id: str, 
        limit: int = 50
    ) -> List[RequestLog]:
        """Get request logs by conversation ID"""
        return db.query(RequestLog)\
            .filter(RequestLog.conversation_id == conversation_id)\
            .order_by(RequestLog.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_recent(db: Session, limit: int = 100) -> List[RequestLog]:
        """Get recent request logs"""
        return db.query(RequestLog)\
            .order_by(RequestLog.created_at.desc())\
            .limit(limit)\
            .all()


class ResponseLogCRUD:
    """CRUD operations for response logs"""
    
    @staticmethod
    def create(db: Session, response_data: Dict[str, Any]) -> ResponseLog:
        """Create a new response log entry"""
        log = ResponseLog(**response_data)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_by_request_id(db: Session, request_id: int) -> Optional[ResponseLog]:
        """Get response log by request ID"""
        return db.query(ResponseLog)\
            .filter(ResponseLog.request_id == request_id)\
            .first()


class ModelPerformanceCRUD:
    """CRUD operations for model performance metrics"""
    
    @staticmethod
    def get_or_create(db: Session, model_name: str, provider: str) -> ModelPerformance:
        """Get or create model performance entry"""
        perf = db.query(ModelPerformance)\
            .filter(
                ModelPerformance.model_name == model_name,
                ModelPerformance.provider == provider
            )\
            .first()
        
        if not perf:
            perf = ModelPerformance(
                model_name=model_name,
                provider=provider
            )
            db.add(perf)
            db.commit()
            db.refresh(perf)
        
        return perf
    
    @staticmethod
    def update_metrics(
        db: Session,
        model_name: str,
        provider: str,
        response_time: float,
        success: bool,
        cost: float = 0.0,
        tokens: int = 0
    ):
        """Update model performance metrics"""
        perf = ModelPerformanceCRUD.get_or_create(db, model_name, provider)
        
        perf.total_requests += 1
        if success:
            perf.successful_requests += 1
        else:
            perf.failed_requests += 1
        
        # Update average response time
        if perf.total_requests > 0:
            perf.avg_response_time = (
                (perf.avg_response_time * (perf.total_requests - 1) + response_time) 
                / perf.total_requests
            )
        
        # Update min/max
        if perf.min_response_time is None or response_time < perf.min_response_time:
            perf.min_response_time = response_time
        if perf.max_response_time is None or response_time > perf.max_response_time:
            perf.max_response_time = response_time
        
        # Update cost and tokens
        perf.total_cost += cost
        perf.total_tokens += tokens
        
        perf.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(perf)
    
    @staticmethod
    def get_all(db: Session) -> List[ModelPerformance]:
        """Get all model performance entries"""
        return db.query(ModelPerformance).all()
    
    @staticmethod
    def get_by_model(db: Session, model_name: str) -> Optional[ModelPerformance]:
        """Get performance for a specific model"""
        return db.query(ModelPerformance)\
            .filter(ModelPerformance.model_name == model_name)\
            .first()


class CostTrackingCRUD:
    """CRUD operations for cost tracking"""
    
    @staticmethod
    def get_or_create(
        db: Session,
        date: date,
        model_name: str,
        provider: str
    ) -> CostTracking:
        """Get or create cost tracking entry for a date"""
        tracking = db.query(CostTracking)\
            .filter(
                CostTracking.date == date,
                CostTracking.model_name == model_name,
                CostTracking.provider == provider
            )\
            .first()
        
        if not tracking:
            tracking = CostTracking(
                date=date,
                model_name=model_name,
                provider=provider
            )
            db.add(tracking)
            db.commit()
            db.refresh(tracking)
        
        return tracking
    
    @staticmethod
    def update_cost(
        db: Session,
        model_name: str,
        provider: str,
        cost: float,
        tokens: int = 0
    ):
        """Update cost tracking for today"""
        today = date.today()
        tracking = CostTrackingCRUD.get_or_create(db, today, model_name, provider)
        
        tracking.total_cost += cost
        tracking.request_count += 1
        tracking.token_count += tokens
        tracking.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(tracking)
    
    @staticmethod
    def get_daily_costs(db: Session, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily cost breakdown for the last N days"""
        from datetime import timedelta
        start_date = date.today() - timedelta(days=days)
        
        results = db.query(
            CostTracking.date,
            func.sum(CostTracking.total_cost).label('total_cost'),
            func.sum(CostTracking.request_count).label('request_count'),
            func.sum(CostTracking.token_count).label('token_count')
        )\
        .filter(CostTracking.date >= start_date)\
        .group_by(CostTracking.date)\
        .order_by(CostTracking.date.desc())\
        .all()
        
        return [
            {
                "date": r.date.isoformat(),
                "total_cost": float(r.total_cost),
                "request_count": r.request_count,
                "token_count": r.token_count
            }
            for r in results
        ]

