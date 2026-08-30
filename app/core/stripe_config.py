import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

STRIPE_PRICE_ID_PRO = settings.STRIPE_PRICE_ID_PRO
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET

def get_stripe_price_id(plan_name: str) -> str:
    if plan_name.upper() == "PRO":
        return STRIPE_PRICE_ID_PRO
    return None
