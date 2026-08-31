from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import CheckoutSessionRequest, CheckoutSessionResponse
from app.services import StripeService, WebhookService
from app.repositories import TenantRepository

router = APIRouter()

@router.post("/billing/create-checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(
    request: CheckoutSessionRequest,
    db: Session = Depends(get_db)
):
    tenant = TenantRepository.get_by_id(db, request.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with id {request.tenant_id} not found"
        )

    try:
        result = StripeService.create_checkout_session(
            tenant_id=request.tenant_id,
            plan_name=request.plan_name,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )

        return CheckoutSessionResponse(
            checkout_url=result["checkout_url"],
            session_id=result["session_id"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating checkout session: {str(e)}"
        )

@router.get("/stripe/mock-checkout")
def mock_checkout(
    tenant_id: int,
    session_id: str,
    plan: str = "PRO",
    db: Session = Depends(get_db)
):
    result = WebhookService.create_mock_webhook_event(db, tenant_id, "checkout.session.completed")
    return RedirectResponse(url=f"/api/v1/stripe/success?tenant_id={tenant_id}&session_id={session_id}")

@router.get("/stripe/success")
def stripe_success(
    tenant_id: int,
    session_id: str = None
):
    return {
        "status": "success",
        "message": "Payment successful! Your plan has been upgraded.",
        "tenant_id": tenant_id,
        "session_id": session_id
    }

@router.get("/stripe/cancel")
def stripe_cancel(
    tenant_id: int
):
    return {
        "status": "canceled",
        "message": "Payment canceled. You can try again anytime.",
        "tenant_id": tenant_id
    }
