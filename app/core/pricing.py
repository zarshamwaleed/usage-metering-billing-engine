from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class PricingConfig:
    api_call_price_cents: int = 1
    input_token_price_cents: int = 3
    cached_input_token_price_cents: int = 1
    output_token_price_cents: int = 6

PRICING = PricingConfig()

def get_pricing() -> PricingConfig:
    return PRICING
