from pydantic import BaseModel
from typing import Optional

class UsageMetric(BaseModel):
    used: int
    limit: int
    percentage: Optional[float] = None

class CostSummary(BaseModel):
    amount: int  # in cents
    currency: str = "USD"
    
    @property
    def amount_dollars(self) -> float:
        return self.amount / 100

class UsageSummaryResponse(BaseModel):
    tenant_id: int
    plan: str
    api_calls: UsageMetric
    ai_tokens: UsageMetric
    cost: CostSummary
    period: str  # e.g., "2026-08"
    token_breakdown: Optional[dict] = None
