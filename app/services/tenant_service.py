from sqlalchemy.orm import Session
from app.repositories import TenantRepository, PlanRepository, SubscriptionRepository
from app.schemas import (
    TenantCreate, 
    TenantResponse, 
    TenantWithSubscriptionResponse, 
    PlanResponse, 
    SubscriptionWithPlanResponse
)
from typing import Optional

class TenantService:
    @staticmethod
    def create_tenant(db: Session, tenant_data: TenantCreate) -> TenantResponse:
        tenant = TenantRepository.create(db, tenant_data.name)
        return TenantResponse.model_validate(tenant)
    
    @staticmethod
    def get_tenant(db: Session, tenant_id: int) -> Optional[TenantResponse]:
        tenant = TenantRepository.get_by_id(db, tenant_id)
        if tenant:
            return TenantResponse.model_validate(tenant)
        return None
    
    @staticmethod
    def get_tenant_with_details(db: Session, tenant_id: int) -> Optional[TenantWithSubscriptionResponse]:
        tenant = TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            return None
        
        subscription = SubscriptionRepository.get_by_tenant_with_plan(db, tenant_id)
        
        response = TenantWithSubscriptionResponse.model_validate(tenant)
        if subscription:
            plan = PlanRepository.get_by_id(db, subscription.plan_id)
            # Use SubscriptionWithPlanResponse instead
            subscription_response = SubscriptionWithPlanResponse.model_validate(subscription)
            if plan:
                subscription_response.plan = PlanResponse.model_validate(plan)
            response.subscription = subscription_response
        
        return response
