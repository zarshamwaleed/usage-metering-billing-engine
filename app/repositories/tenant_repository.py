from sqlalchemy.orm import Session
from app.models import Tenant, Subscription, Plan
from app.models.subscription import SubscriptionStatus
from typing import Optional

class TenantRepository:
    @staticmethod
    def create(db: Session, name: str) -> Tenant:
        # Create tenant
        tenant = Tenant(name=name)
        db.add(tenant)
        db.flush()
        
        # Get Free plan
        free_plan = db.query(Plan).filter(Plan.name == "FREE").first()
        if not free_plan:
            raise ValueError("Free plan not found. Please seed the database first.")
        
        # Create subscription with Free plan
        subscription = Subscription(
            tenant_id=tenant.id,
            plan_id=free_plan.id,
            status=SubscriptionStatus.ACTIVE
        )
        db.add(subscription)
        db.commit()
        db.refresh(tenant)
        
        return tenant
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int) -> Optional[Tenant]:
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Tenant).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_with_subscription(db: Session, tenant_id: int) -> Optional[Tenant]:
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()
