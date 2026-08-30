from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.subscription import SubscriptionStatus
from app.models.usage_event import UsageType
from app.schemas.cost import TokenCostBreakdown, UsageCostResponse

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

# ===== Quota Schemas =====
class QuotaCheckRequest(BaseModel):
    tenant_id: int
    api_calls_requested: int = 0
    tokens_requested: int = 0

class QuotaResponse(BaseModel):
    tenant_id: int
    plan_name: str
    api_calls: dict
    ai_tokens: dict
    is_allowed: bool
    message: Optional[str] = None
    error_code: Optional[str] = None

class QuotaCheckResponse(BaseModel):
    allowed: bool
    status_code: int
    message: str
    error_code: Optional[str] = None
    current_usage: dict
    limits: dict

# ===== Cost Schemas =====
class TokenCostBreakdown(BaseModel):
    input_tokens: int = 0
    input_cost_cents: int = 0
    cached_input_tokens: int = 0
    cached_input_cost_cents: int = 0
    output_tokens: int = 0
    output_cost_cents: int = 0
    reasoning_tokens: int = 0
    reasoning_cost_cents: int = 0
    
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.cached_input_tokens + self.output_tokens + self.reasoning_tokens
    
    @property
    def total_cost_cents(self) -> int:
        return (self.input_cost_cents + 
                self.cached_input_cost_cents + 
                self.output_cost_cents + 
                self.reasoning_cost_cents)

class UsageCostResponse(BaseModel):
    tenant_id: int
    plan_name: str
    period: str
    api_calls: int
    api_cost_cents: int
    token_breakdown: TokenCostBreakdown
    total_cost_cents: int
    
    @property
    def total_cost_dollars(self) -> float:
        return self.total_cost_cents / 100
    
    @property
    def api_cost_dollars(self) -> float:
        return self.api_cost_cents / 100
    
    @property
    def token_cost_dollars(self) -> float:
        return self.token_breakdown.total_cost_cents / 100

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
    "QuotaCheckRequest",
    "QuotaResponse",
    "QuotaCheckResponse",
    "TokenCostBreakdown",
    "UsageCostResponse",
]
