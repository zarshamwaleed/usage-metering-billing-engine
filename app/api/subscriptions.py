from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import SubscriptionResponse, SubscriptionWithPlanResponse
from app.services import SubscriptionService

router = APIRouter()

@router.get("/subscriptions/tenant/{tenant_id}", response_model=SubscriptionWithPlanResponse)
def get_tenant_subscription(tenant_id: int, db: Session = Depends(get_db)):
    subscription = SubscriptionService.get_subscription_with_plan(db, tenant_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No subscription found for tenant {tenant_id}"
        )
    return subscription
