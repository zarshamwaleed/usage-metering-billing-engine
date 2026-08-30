from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.subscription import SubscriptionStatus
from app.models.usage_event import UsageType

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

# ===== Usage Schemas =====
class UsageRequest(BaseModel):
    input_tokens: Optional[int] = Field(0, ge=0)
    cached_input_tokens: Optional[int] = Field(0, ge=0)
    output_tokens: Optional[int] = Field(0, ge=0)
    reasoning_tokens: Optional[int] = Field(0, ge=0)
    
    @property
    def total_tokens(self) -> int:
        return (self.input_tokens or 0) + (self.cached_input_tokens or 0) + (self.output_tokens or 0) + (self.reasoning_tokens or 0)

class UsageEventCreate(BaseModel):
    tenant_id: int
    usage_type: UsageType
    quantity: int
    idempotency_key: str

class UsageEventResponse(BaseModel):
    id: int
    tenant_id: int
    usage_type: UsageType
    quantity: int
    idempotency_key: str
    created_at: datetime

    class Config:
        from_attributes = True

class GenerateResponse(BaseModel):
    status: str
    tenant_id: int
    usage_type: str
    quantity: int
    idempotency_key: str
    message: str
    token_breakdown: Optional[dict] = None

# ===== Exports =====
__all__ = [
    "TenantCreate",
    "TenantResponse",
    "TenantWithSubscriptionResponse",
    "PlanResponse",
    "SubscriptionResponse",
    "SubscriptionWithPlanResponse",
    "UsageRequest",
    "UsageEventCreate",
    "UsageEventResponse",
    "GenerateResponse",
    "UsageType",
]
