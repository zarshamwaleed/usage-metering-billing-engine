from sqlalchemy.orm import Session
from app.repositories import SubscriptionRepository, PlanRepository
from app.schemas import SubscriptionResponse, SubscriptionWithPlanResponse, PlanResponse
from typing import Optional

class SubscriptionService:
    @staticmethod
    def get_subscription_by_tenant(db: Session, tenant_id: int) -> Optional[SubscriptionResponse]:
        subscription = SubscriptionRepository.get_by_tenant_id(db, tenant_id)
        if subscription:
            return SubscriptionResponse.model_validate(subscription)
        return None
    
    @staticmethod
    def get_subscription_with_plan(db: Session, tenant_id: int) -> Optional[SubscriptionWithPlanResponse]:
        subscription = SubscriptionRepository.get_by_tenant_with_plan(db, tenant_id)
        if not subscription:
            return None
        
        plan = PlanRepository.get_by_id(db, subscription.plan_id)
        response = SubscriptionWithPlanResponse.model_validate(subscription)
        if plan:
            response.plan = PlanResponse.model_validate(plan)
        
        return response
