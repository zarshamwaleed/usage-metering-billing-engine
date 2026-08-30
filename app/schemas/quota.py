from pydantic import BaseModel
from typing import Optional

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
