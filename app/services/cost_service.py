from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from app.core.pricing import get_pricing
from app.repositories import TenantRepository, SubscriptionRepository, PlanRepository
from app.models import UsageEvent
from app.models.usage_event import UsageType
from app.schemas import TokenCostBreakdown, UsageCostResponse
from typing import Dict, Any

class CostService:
    @staticmethod
    def calculate_token_cost(
        input_tokens: int = 0,
        cached_input_tokens: int = 0,
        output_tokens: int = 0,
        reasoning_tokens: int = 0
    ) -> Dict[str, Any]:
        pricing = get_pricing()
        
        input_cost_cents = input_tokens * pricing.input_token_price_cents // 1000
        cached_input_cost_cents = cached_input_tokens * pricing.cached_input_token_price_cents // 1000
        output_cost_cents = output_tokens * pricing.output_token_price_cents // 1000
        reasoning_cost_cents = reasoning_tokens * pricing.output_token_price_cents // 1000
        
        return {
            "input_tokens": input_tokens,
            "input_cost_cents": input_cost_cents,
            "cached_input_tokens": cached_input_tokens,
            "cached_input_cost_cents": cached_input_cost_cents,
            "output_tokens": output_tokens,
            "output_cost_cents": output_cost_cents,
            "reasoning_tokens": reasoning_tokens,
            "reasoning_cost_cents": reasoning_cost_cents,
            "total_tokens": input_tokens + cached_input_tokens + output_tokens + reasoning_tokens,
            "total_cost_cents": input_cost_cents + cached_input_cost_cents + output_cost_cents + reasoning_cost_cents
        }
    
    @staticmethod
    def calculate_api_cost(api_calls: int) -> int:
        pricing = get_pricing()
        return api_calls * pricing.api_call_price_cents
    
    @staticmethod
    def get_tenant_cost(
        db: Session,
        tenant_id: int,
        period_start: datetime = None,
        period_end: datetime = None
    ) -> UsageCostResponse:
        tenant = TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise ValueError(f"Tenant with id {tenant_id} not found")
        
        subscription = SubscriptionRepository.get_by_tenant_with_plan(db, tenant_id)
        if not subscription:
            raise ValueError(f"No subscription found for tenant {tenant_id}")
        
        plan = PlanRepository.get_by_id(db, subscription.plan_id)
        if not plan:
            raise ValueError(f"No plan found for subscription {subscription.id}")
        
        if period_start is None:
            now = datetime.utcnow()
            period_start = datetime(now.year, now.month, 1)
        if period_end is None:
            period_end = datetime.utcnow()
        
        query = db.query(UsageEvent).filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.created_at >= period_start,
            UsageEvent.created_at <= period_end
        )
        
        usage_events = query.all()
        
        api_calls = 0
        token_data = {
            "input_tokens": 0,
            "cached_input_tokens": 0,
            "output_tokens": 0,
            "reasoning_tokens": 0
        }
        
        for event in usage_events:
            usage_type_str = str(event.usage_type)
            if 'API_CALL' in usage_type_str or 'api_call' in usage_type_str:
                api_calls += event.quantity
            elif 'AI_TOKEN' in usage_type_str or 'ai_token' in usage_type_str:
                key = event.idempotency_key
                if '_input' in key:
                    token_data["input_tokens"] += event.quantity
                elif '_cached' in key:
                    token_data["cached_input_tokens"] += event.quantity
                elif '_output' in key:
                    token_data["output_tokens"] += event.quantity
                elif '_reasoning' in key:
                    token_data["reasoning_tokens"] += event.quantity
                else:
                    token_data["input_tokens"] += event.quantity
        
        api_cost_cents = CostService.calculate_api_cost(api_calls)
        token_cost_result = CostService.calculate_token_cost(
            token_data["input_tokens"],
            token_data["cached_input_tokens"],
            token_data["output_tokens"],
            token_data["reasoning_tokens"]
        )
        
        token_breakdown = TokenCostBreakdown(
            input_tokens=token_data["input_tokens"],
            input_cost_cents=token_cost_result["input_cost_cents"],
            cached_input_tokens=token_data["cached_input_tokens"],
            cached_input_cost_cents=token_cost_result["cached_input_cost_cents"],
            output_tokens=token_data["output_tokens"],
            output_cost_cents=token_cost_result["output_cost_cents"],
            reasoning_tokens=token_data["reasoning_tokens"],
            reasoning_cost_cents=token_cost_result["reasoning_cost_cents"]
        )
        
        total_cost_cents = api_cost_cents + token_cost_result["total_cost_cents"]
        
        return UsageCostResponse(
            tenant_id=tenant_id,
            plan_name=plan.name,
            period=f"{period_start.strftime('%Y-%m')}",
            api_calls=api_calls,
            api_cost_cents=api_cost_cents,
            token_breakdown=token_breakdown,
            total_cost_cents=total_cost_cents
        )
