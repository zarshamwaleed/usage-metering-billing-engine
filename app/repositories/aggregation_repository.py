from sqlalchemy.orm import Session
from app.models import UsageAggregation
from typing import Optional, List
from datetime import datetime

class AggregationRepository:
    @staticmethod
    def get_by_tenant_period(db: Session, tenant_id: int, period: str) -> Optional[UsageAggregation]:
        return db.query(UsageAggregation).filter(
            UsageAggregation.tenant_id == tenant_id,
            UsageAggregation.period == period
        ).first()
    
    @staticmethod
    def create_or_update(db: Session, tenant_id: int, period: str, data: dict) -> UsageAggregation:
        agg = AggregationRepository.get_by_tenant_period(db, tenant_id, period)
        
        if agg:
            # Update existing
            agg.api_calls = data.get("api_calls", agg.api_calls)
            agg.ai_tokens = data.get("ai_tokens", agg.ai_tokens)
            agg.api_cost_cents = data.get("api_cost_cents", agg.api_cost_cents)
            agg.token_cost_cents = data.get("token_cost_cents", agg.token_cost_cents)
            agg.total_cost_cents = data.get("total_cost_cents", agg.total_cost_cents)
            db.commit()
            db.refresh(agg)
        else:
            # Create new
            agg = UsageAggregation(
                tenant_id=tenant_id,
                period=period,
                api_calls=data.get("api_calls", 0),
                ai_tokens=data.get("ai_tokens", 0),
                api_cost_cents=data.get("api_cost_cents", 0),
                token_cost_cents=data.get("token_cost_cents", 0),
                total_cost_cents=data.get("total_cost_cents", 0)
            )
            db.add(agg)
            db.commit()
            db.refresh(agg)
        
        return agg
    
    @staticmethod
    def get_all_by_tenant(db: Session, tenant_id: int) -> List[UsageAggregation]:
        return db.query(UsageAggregation).filter(
            UsageAggregation.tenant_id == tenant_id
        ).order_by(UsageAggregation.period.desc()).all()
    
    @staticmethod
    def get_all_tenants(db: Session) -> List[int]:
        from app.models import Tenant
        return [t.id for t in db.query(Tenant).all()]
