from sqlalchemy.orm import Session
from datetime import datetime
from app.repositories import TenantRepository, SubscriptionRepository, PlanRepository
from app.services import CostService
from app.schemas import UsageMetric, CostSummary, UsageSummaryResponse

class UsageSummaryService:
    @staticmethod
    def get_current_usage(db: Session, tenant_id: int):
        from app.models import UsageEvent
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)

        usage_events = db.query(UsageEvent).filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.created_at >= month_start
        ).all()

        api_calls = 0
        ai_tokens = 0

        for event in usage_events:
            usage_type_str = str(event.usage_type)
            if 'API_CALL' in usage_type_str or 'api_call' in usage_type_str:
                api_calls += event.quantity
            elif 'AI_TOKEN' in usage_type_str or 'ai_token' in usage_type_str:
                ai_tokens += event.quantity

        return {"api_calls": api_calls, "ai_tokens": ai_tokens}

    @staticmethod
    def get_usage_summary(db: Session, tenant_id: int) -> UsageSummaryResponse:
        tenant = TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise ValueError(f"Tenant with id {tenant_id} not found")

        subscription = SubscriptionRepository.get_by_tenant_with_plan(db, tenant_id)
        if not subscription:
            raise ValueError(f"No subscription found for tenant {tenant_id}")

        plan = PlanRepository.get_by_id(db, subscription.plan_id)
        if not plan:
            raise ValueError(f"No plan found for subscription {subscription.id}")

        current_usage = UsageSummaryService.get_current_usage(db, tenant_id)
        api_calls_used = current_usage["api_calls"]
        tokens_used = current_usage["ai_tokens"]

        api_call_limit = plan.api_call_limit
        token_limit = plan.ai_token_limit

        api_percentage = (api_calls_used / api_call_limit * 100) if api_call_limit > 0 else 0
        token_percentage = (tokens_used / token_limit * 100) if token_limit > 0 else 0

        cost_response = CostService.get_tenant_cost(db, tenant_id)

        # Calculate total_tokens manually from the breakdown
        breakdown = cost_response.token_breakdown
        total_tokens = (
            breakdown.input_tokens +
            breakdown.cached_input_tokens +
            breakdown.output_tokens +
            breakdown.reasoning_tokens
        )

        token_breakdown = {
            "input_tokens": breakdown.input_tokens,
            "cached_input_tokens": breakdown.cached_input_tokens,
            "output_tokens": breakdown.output_tokens,
            "reasoning_tokens": breakdown.reasoning_tokens,
            "total_tokens": total_tokens
        }

        return UsageSummaryResponse(
            tenant_id=tenant_id,
            plan=plan.name,
            api_calls=UsageMetric(
                used=api_calls_used,
                limit=api_call_limit,
                percentage=round(api_percentage, 2)
            ),
            ai_tokens=UsageMetric(
                used=tokens_used,
                limit=token_limit,
                percentage=round(token_percentage, 2)
            ),
            cost=CostSummary(
                amount=cost_response.total_cost_cents,
                currency="USD"
            ),
            period=cost_response.period,
            token_breakdown=token_breakdown
        )
