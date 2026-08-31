from sqlalchemy.orm import Session
from app.repositories import WebhookRepository, SubscriptionRepository, PlanRepository
from app.models.subscription import SubscriptionStatus
from typing import Dict, Any
import uuid
import json

class WebhookService:
    @staticmethod
    def verify_signature(payload: bytes, signature: str) -> bool:
        # Mock mode - always return True
        return True
    
    @staticmethod
    def process_webhook_event(db: Session, payload: bytes, signature: str) -> Dict[str, Any]:
        # Verify signature
        if not WebhookService.verify_signature(payload, signature):
            return {"status": "error", "message": "Invalid signature", "code": 400}
        
        try:
            event_data = json.loads(payload)
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON payload", "code": 400}
        
        event_id = event_data.get("id")
        event_type = event_data.get("type")
        
        if not event_id or not event_type:
            return {"status": "error", "message": "Missing event id or type", "code": 400}
        
        # Check idempotency - prevent duplicate processing
        if WebhookRepository.exists(db, event_id):
            return {
                "status": "duplicate",
                "message": f"Event {event_id} already processed",
                "code": 200
            }
        
        # Process the event
        result = WebhookService.handle_webhook_event(db, event_data)
        
        if result.get("status") == "success":
            WebhookRepository.create(db, event_id, event_type)
            result["event_id"] = event_id
        
        return result
    
    @staticmethod
    def handle_webhook_event(db: Session, event_data: Dict[str, Any]) -> Dict[str, Any]:
        event_type = event_data.get("type")
        event_object = event_data.get("data", {}).get("object", {})

        if event_type == "checkout.session.completed":
            return WebhookService.handle_checkout_completed(db, event_object)
        elif event_type == "customer.subscription.updated":
            return WebhookService.handle_subscription_updated(db, event_object)
        elif event_type == "customer.subscription.deleted":
            return WebhookService.handle_subscription_deleted(db, event_object)
        else:
            return {"status": "ignored", "message": f"Event {event_type} not handled"}

    @staticmethod
    def handle_checkout_completed(db: Session, event_object: Dict[str, Any]) -> Dict[str, Any]:
        tenant_id = event_object.get("client_reference_id")
        if not tenant_id:
            if event_object.get("mock", False):
                tenant_id = event_object.get("tenant_id")
            
        if not tenant_id:
            return {"status": "error", "message": "No tenant_id in event"}

        tenant_id = int(tenant_id)
        subscription_id = event_object.get("subscription") or f"mock_sub_{uuid.uuid4().hex[:8]}"
        customer_id = event_object.get("customer") or f"mock_cus_{uuid.uuid4().hex[:8]}"

        subscription = SubscriptionRepository.get_by_tenant_id(db, tenant_id)
        if subscription:
            subscription.stripe_subscription_id = subscription_id
            subscription.stripe_customer_id = customer_id
            subscription.status = SubscriptionStatus.ACTIVE

            pro_plan = PlanRepository.get_by_name(db, "PRO")
            if pro_plan:
                subscription.plan_id = pro_plan.id

            db.commit()
            db.refresh(subscription)

            return {
                "status": "success",
                "message": f"Tenant {tenant_id} upgraded to PRO",
                "subscription_id": subscription_id,
                "mock": True,
                "details": {
                    "tenant_id": tenant_id,
                    "plan": "PRO",
                    "subscription_id": subscription_id
                }
            }
        else:
            return {"status": "error", "message": f"Subscription not found for tenant {tenant_id}"}

    @staticmethod
    def handle_subscription_updated(db: Session, event_object: Dict[str, Any]) -> Dict[str, Any]:
        subscription_id = event_object.get("id")
        status = event_object.get("status")

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_id
        ).first()

        if subscription:
            subscription.status = status
            db.commit()
            return {
                "status": "success",
                "message": f"Subscription {subscription_id} updated to {status}"
            }
        else:
            return {"status": "ignored", "message": f"Subscription {subscription_id} not found"}

    @staticmethod
    def handle_subscription_deleted(db: Session, event_object: Dict[str, Any]) -> Dict[str, Any]:
        subscription_id = event_object.get("id")

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_id
        ).first()

        if subscription:
            subscription.status = SubscriptionStatus.CANCELED
            db.commit()
            return {
                "status": "success",
                "message": f"Subscription {subscription_id} canceled"
            }
        else:
            return {"status": "ignored", "message": f"Subscription {subscription_id} not found"}

    @staticmethod
    def create_mock_webhook_event(
        db: Session,
        tenant_id: int,
        event_type: str = "checkout.session.completed"
    ) -> Dict[str, Any]:
        event_id = f"evt_mock_{uuid.uuid4().hex[:16]}"
        
        event_data = {
            "id": event_id,
            "type": event_type,
            "data": {
                "object": {
                    "client_reference_id": str(tenant_id),
                    "subscription": f"mock_sub_{uuid.uuid4().hex[:8]}",
                    "customer": f"mock_cus_{uuid.uuid4().hex[:8]}",
                    "mock": True,
                    "tenant_id": str(tenant_id)
                }
            }
        }
        
        return WebhookService.process_webhook_event(
            db,
            json.dumps(event_data).encode(),
            "mock_signature"
        )
