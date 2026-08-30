import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import Tenant, Plan, Subscription, UsageEvent

def check_database():
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).count()
        plans = db.query(Plan).count()
        subscriptions = db.query(Subscription).count()
        usage_events = db.query(UsageEvent).count()

        print("Database Status:")
        print(f"   - Tenants: {tenants}")
        print(f"   - Plans: {plans}")
        print(f"   - Subscriptions: {subscriptions}")
        print(f"   - Usage Events: {usage_events}")

        if plans > 0:
            print("\nPlans:")
            for plan in db.query(Plan).all():
                print(f"   - {plan.name}: {plan.api_call_limit} API calls, {plan.ai_token_limit} AI tokens")

        if tenants > 0:
            print("\nTenants:")
            for tenant in db.query(Tenant).all():
                sub = db.query(Subscription).filter(Subscription.tenant_id == tenant.id).first()
                if sub:
                    plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
                    plan_name = plan.name if plan else "No plan"
                    print(f"   - ID={tenant.id}, Name={tenant.name}, Plan={plan_name}")

        if usage_events > 0:
            print("\nRecent Usage Events:")
            recent = db.query(UsageEvent).order_by(UsageEvent.created_at.desc()).limit(5).all()
            for event in recent:
                print(f"   - {event.usage_type}: {event.quantity} (key: {event.idempotency_key})")

    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
