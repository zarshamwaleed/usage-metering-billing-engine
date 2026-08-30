from sqlalchemy.orm import Session
from app.models import Subscription, Plan
from typing import Optional

class SubscriptionRepository:
    @staticmethod
    def get_by_tenant_id(db: Session, tenant_id: int) -> Optional[Subscription]:
        return db.query(Subscription).filter(Subscription.tenant_id == tenant_id).first()
    
    @staticmethod
    def get_by_tenant_with_plan(db: Session, tenant_id: int) -> Optional[Subscription]:
        return db.query(Subscription).filter(Subscription.tenant_id == tenant_id).first()
    
    @staticmethod
    def get_active_subscription(db: Session, tenant_id: int) -> Optional[Subscription]:
        return db.query(Subscription).filter(
            Subscription.tenant_id == tenant_id,
            Subscription.status == "active"
        ).first()
