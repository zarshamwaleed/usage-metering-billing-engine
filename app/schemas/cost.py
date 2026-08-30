from pydantic import BaseModel
from typing import Optional, Dict

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
        return (self.input_tokens + 
                self.cached_input_tokens + 
                self.output_tokens + 
                self.reasoning_tokens)
    
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
