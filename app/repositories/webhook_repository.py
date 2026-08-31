from sqlalchemy.orm import Session
from app.models import WebhookEvent
from typing import Optional

class WebhookRepository:
    @staticmethod
    def create(db: Session, stripe_event_id: str, event_type: str) -> WebhookEvent:
        webhook_event = WebhookEvent(
            stripe_event_id=stripe_event_id,
            event_type=event_type
        )
        db.add(webhook_event)
        db.commit()
        db.refresh(webhook_event)
        return webhook_event
    
    @staticmethod
    def get_by_event_id(db: Session, stripe_event_id: str) -> Optional[WebhookEvent]:
        return db.query(WebhookEvent).filter(
            WebhookEvent.stripe_event_id == stripe_event_id
        ).first()
    
    @staticmethod
    def exists(db: Session, stripe_event_id: str) -> bool:
        return db.query(WebhookEvent).filter(
            WebhookEvent.stripe_event_id == stripe_event_id
        ).first() is not None
