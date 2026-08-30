from pydantic import BaseModel
from typing import Optional

class CheckoutSessionRequest(BaseModel):
    tenant_id: int
    plan_name: str = "PRO"
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str

class WebhookEvent(BaseModel):
    id: str
    type: str
    data: dict
