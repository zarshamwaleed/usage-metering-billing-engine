from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import WebhookService
from app.repositories import TenantRepository

router = APIRouter()

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    
    db = next(get_db())
    try:
        result = WebhookService.process_webhook_event(db, payload, signature)
        status_code = result.get("code", 200)
        result_status = result.get("status", "success")
        message = result.get("message", "Webhook processed")
        
        if status_code != 200:
            return Response(
                content=f'{{"status":"{result_status}","message":"{message}"}}',
                status_code=status_code,
                media_type="application/json"
            )
        
        return {
            "status": result_status,
            "message": message,
            "event_id": result.get("event_id"),
            "details": result.get("details", {})
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

@router.post("/webhooks/stripe/mock")
def mock_webhook(
    tenant_id: int,
    event_type: str = "checkout.session.completed",
    db: Session = Depends(get_db)
):
    tenant = TenantRepository.get_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with id {tenant_id} not found"
        )
    
    result = WebhookService.create_mock_webhook_event(db, tenant_id, event_type)
    return result

@router.get("/webhooks/stripe/events")
def list_webhook_events(db: Session = Depends(get_db)):
    from app.models import WebhookEvent
    events = db.query(WebhookEvent).order_by(WebhookEvent.processed_at.desc()).limit(20).all()
    return [
        {
            "id": event.id,
            "stripe_event_id": event.stripe_event_id,
            "event_type": event.event_type,
            "processed_at": event.processed_at
        }
        for event in events
    ]
