import stripe
from sqlalchemy.orm import Session
from app.core.stripe_config import STRIPE_PRICE_ID_PRO
from app.core.config import settings
from app.repositories import TenantRepository, SubscriptionRepository
from app.models.subscription import SubscriptionStatus
from typing import Dict, Any
import os
import uuid
import json

class StripeService:
    @staticmethod
    def create_checkout_session(
        tenant_id: int,
        plan_name: str = "PRO",
        success_url: str = None,
        cancel_url: str = None
    ) -> Dict[str, Any]:
        if plan_name.upper() != "PRO":
            raise ValueError("Only PRO plan is supported for checkout")

        if not success_url:
            success_url = f"{settings.APP_URL}/api/v1/stripe/success?tenant_id={tenant_id}"
        if not cancel_url:
            cancel_url = f"{settings.APP_URL}/api/v1/stripe/cancel?tenant_id={tenant_id}"

        # Mock mode (for countries where Stripe is not available)
        if os.getenv("STRIPE_MOCK_MODE", "false").lower() == "true":
            # Generate a mock session ID
            mock_session_id = f"cs_test_mock_{uuid.uuid4().hex[:16]}"
            mock_checkout_url = (
                f"{settings.APP_URL}/api/v1/stripe/mock-checkout"
                f"?tenant_id={tenant_id}"
                f"&session_id={mock_session_id}"
                f"&plan=PRO"
            )
            return {
                "checkout_url": mock_checkout_url,
                "session_id": mock_session_id,
                "is_mock": True
            }

        # Real Stripe call
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": STRIPE_PRICE_ID_PRO,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(tenant_id),
                metadata={
                    "tenant_id": str(tenant_id),
                    "plan": plan_name
                }
            )

            return {
                "checkout_url": session.url,
                "session_id": session.id,
                "is_mock": False
            }

        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")

    @staticmethod
    def handle_webhook_event(
        db: Session,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        event_type = event_data.get("type")
        event_object = event_data.get("data", {}).get("object", {})

        if event_type == "checkout.session.completed":
            return StripeService.handle_checkout_completed(db, event_object)
        elif event_type == "customer.subscription.updated":
            return StripeService.handle_subscription_updated(db, event_object)
        elif event_type == "customer.subscription.deleted":
            return StripeService.handle_subscription_deleted(db, event_object)
        else:
            return {"status": "ignored", "message": f"Event {event_type} not handled"}

    @staticmethod
    def handle_checkout_completed(db: Session, event_object: Dict[str, Any]) -> Dict[str, Any]:
        tenant_id = event_object.get("client_reference_id")
        if not tenant_id:
            # Check if it's a mock event
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

            from app.repositories import PlanRepository
            pro_plan = PlanRepository.get_by_name(db, "PRO")
            if pro_plan:
                subscription.plan_id = pro_plan.id

            db.commit()
            db.refresh(subscription)

            return {
                "status": "success",
                "message": f"Tenant {tenant_id} upgraded to PRO",
                "subscription_id": subscription_id,
                "mock": True
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
            return {"status": "success", "message": f"Subscription {subscription_id} updated to {status}"}
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
            return {"status": "success", "message": f"Subscription {subscription_id} canceled"}
        else:
            return {"status": "ignored", "message": f"Subscription {subscription_id} not found"}

    @staticmethod
    def process_mock_checkout(
        db: Session,
        tenant_id: int,
        session_id: str,
        plan: str = "PRO"
    ) -> Dict[str, Any]:
        # Simulate a successful checkout
        event_data = {
            "type": "checkout.session.completed",
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
        return StripeService.handle_webhook_event(db, event_data)
