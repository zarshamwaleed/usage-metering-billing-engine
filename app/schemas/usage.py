from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.usage_event import UsageType

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
