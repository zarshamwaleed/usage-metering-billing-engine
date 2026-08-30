from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Tenant, Plan, Subscription, UsageEvent

router = APIRouter()

@router.get("/db-check")
def check_database(db: Session = Depends(get_db)):
    \"\"\"Check database status - for testing only\"\"\"
    tenants = db.query(Tenant).count()
    plans = db.query(Plan).count()
    subscriptions = db.query(Subscription).count()
    usage_events = db.query(UsageEvent).count()

    # Get plan details
    plan_details = []
    for plan in db.query(Plan).all():
        plan_details.append({
            "name": plan.name,
            "api_call_limit": plan.api_call_limit,
            "ai_token_limit": plan.ai_token_limit
        })

    return {
        "status": "ok",
        "counts": {
            "tenants": tenants,
            "plans": plans,
            "subscriptions": subscriptions,
            "usage_events": usage_events
        },
        "plans": plan_details
    }
