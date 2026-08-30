from sqlalchemy.orm import Session
from app.models import UsageEvent
from app.schemas import UsageEventCreate
from typing import Optional, List
from datetime import datetime

class UsageRepository:
    @staticmethod
    def create(db: Session, usage_data: UsageEventCreate) -> UsageEvent:
        usage_event = UsageEvent(
            tenant_id=usage_data.tenant_id,
            usage_type=usage_data.usage_type,
            quantity=usage_data.quantity,
            idempotency_key=usage_data.idempotency_key
        )
        db.add(usage_event)
        db.commit()
        db.refresh(usage_event)
        return usage_event
    
    @staticmethod
    def get_by_idempotency_key(db: Session, tenant_id: int, idempotency_key: str) -> Optional[UsageEvent]:
        return db.query(UsageEvent).filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.idempotency_key == idempotency_key
        ).first()
    
    @staticmethod
    def get_by_idempotency_prefix(db: Session, tenant_id: int, idempotency_key: str) -> List[UsageEvent]:
        return db.query(UsageEvent).filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.idempotency_key.startswith(idempotency_key)
        ).all()
    
    @staticmethod
    def get_tenant_usage(db: Session, tenant_id: int, usage_type: Optional[str] = None) -> List[UsageEvent]:
        query = db.query(UsageEvent).filter(UsageEvent.tenant_id == tenant_id)
        if usage_type:
            query = query.filter(UsageEvent.usage_type == usage_type)
        return query.all()
    
    @staticmethod
    def get_monthly_usage(db: Session, tenant_id: int) -> dict:
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        usage = db.query(UsageEvent).filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.created_at >= month_start
        ).all()
        
        result = {}
        for event in usage:
            key = str(event.usage_type)
            if key not in result:
                result[key] = 0
            result[key] += event.quantity
        
        return result
    
    @staticmethod
    def get_total_usage_for_type(db: Session, tenant_id: int, usage_type: str, period_start: datetime = None) -> int:
        query = db.query(UsageEvent).filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.usage_type == usage_type
        )
        
        if period_start:
            query = query.filter(UsageEvent.created_at >= period_start)
        
        return sum([event.quantity for event in query.all()])
