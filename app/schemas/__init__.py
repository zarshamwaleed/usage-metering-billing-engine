from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.subscription import SubscriptionStatus

# ===== Tenant Schemas =====
class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class TenantResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

# ===== Plan Schemas =====
class PlanResponse(BaseModel):
    id: int
    name: str
    api_call_limit: int
    ai_token_limit: int
    created_at: datetime

    class Config:
        from_attributes = True

# ===== Subscription Schemas =====
class SubscriptionResponse(BaseModel):
    id: int
    tenant_id: int
    plan_id: int
    status: SubscriptionStatus
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SubscriptionWithPlanResponse(SubscriptionResponse):
    plan: Optional[PlanResponse] = None

class TenantWithSubscriptionResponse(TenantResponse):
    subscription: Optional[SubscriptionWithPlanResponse] = None

# ===== Exports =====
__all__ = [
    "TenantCreate",
    "TenantResponse",
    "TenantWithSubscriptionResponse",
    "PlanResponse",
    "SubscriptionResponse",
    "SubscriptionWithPlanResponse",
]
