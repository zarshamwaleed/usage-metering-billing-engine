import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import Plan, Tenant, Subscription, UsageEvent
from app.models.subscription import SubscriptionStatus

def seed_plans():
    db = SessionLocal()
    try:
        existing = db.query(Plan).count()
        if existing > 0:
            print(f"Plans already exist ({existing} plans). Skipping seed.")
            return

        free_plan = Plan(
            name="FREE",
            api_call_limit=1000,
            ai_token_limit=100000
        )

        pro_plan = Plan(
            name="PRO",
            api_call_limit=10000,
            ai_token_limit=1000000
        )

        db.add_all([free_plan, pro_plan])
        db.commit()
        print("Free and Pro plans seeded successfully!")
        print(f"   - FREE: {free_plan.api_call_limit} API calls, {free_plan.ai_token_limit} AI tokens")
        print(f"   - PRO: {pro_plan.api_call_limit} API calls, {pro_plan.ai_token_limit} AI tokens")

    except Exception as e:
        db.rollback()
        print(f"Error seeding plans: {e}")
    finally:
        db.close()

def seed_demo_tenant():
    db = SessionLocal()
    try:
        demo = db.query(Tenant).filter(Tenant.name == "Demo Tenant").first()
        if demo:
            print("Demo tenant already exists. Skipping.")
            return

        free_plan = db.query(Plan).filter(Plan.name == "FREE").first()
        if not free_plan:
            print("Free plan not found. Run seed_plans first.")
            return

        tenant = Tenant(name="Demo Tenant")
        db.add(tenant)
        db.flush()

        subscription = Subscription(
            tenant_id=tenant.id,
            plan_id=free_plan.id,
            status=SubscriptionStatus.ACTIVE
        )
        db.add(subscription)
        db.commit()
        print(f"Demo tenant created: ID={tenant.id}, Name={tenant.name}")
        print(f"   Subscription: Plan={free_plan.name}, Status={subscription.status}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding demo tenant: {e}")
    finally:
        db.close()

def seed_usage_events():
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.name == "Demo Tenant").first()
        if not tenant:
            print("Demo tenant not found. Run seed_demo_tenant first.")
            return

        count = db.query(UsageEvent).filter(UsageEvent.tenant_id == tenant.id).count()
        if count > 0:
            print(f"Usage events already exist ({count} events). Skipping.")
            return

        sample_events = []
        for i in range(5):
            sample_events.append(
                UsageEvent(
                    tenant_id=tenant.id,
                    usage_type="api_call",
                    quantity=1,
                    idempotency_key=f"seed_key_{i}"
                )
            )

        sample_events.append(
            UsageEvent(
                tenant_id=tenant.id,
                usage_type="ai_token",
                quantity=2500,
                idempotency_key="seed_token_key_1"
            )
        )
        sample_events.append(
            UsageEvent(
                tenant_id=tenant.id,
                usage_type="ai_token",
                quantity=1800,
                idempotency_key="seed_token_key_2"
            )
        )

        db.add_all(sample_events)
        db.commit()
        print(f"Seeded {len(sample_events)} usage events for tenant {tenant.name}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding usage events: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding database...")
    seed_plans()
    seed_demo_tenant()
    seed_usage_events()
    print("Seeding complete!")
