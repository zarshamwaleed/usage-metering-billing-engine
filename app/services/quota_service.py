from sqlalchemy.orm import Session
from app.repositories import TenantRepository, SubscriptionRepository, PlanRepository, UsageRepository
from app.schemas import QuotaCheckResponse
from datetime import datetime
from typing import Dict, Any

class QuotaService:
    @staticmethod
    def get_current_usage(db: Session, tenant_id: int) -> Dict[str, Any]:
        # Get current month's start
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        # Get all usage events for this tenant in current month
        from app.models import UsageEvent
        from app.models.usage_event import UsageType
        
        usage_events = db.query(UsageEvent).filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.created_at >= month_start
        ).all()
        
        # Aggregate by usage type
        api_calls = 0
        ai_tokens = 0
        
        for event in usage_events:
            # Check the usage type (could be stored as string or enum)
            usage_type_str = str(event.usage_type)
            if 'API_CALL' in usage_type_str or 'api_call' in usage_type_str:
                api_calls += event.quantity
            elif 'AI_TOKEN' in usage_type_str or 'ai_token' in usage_type_str:
                ai_tokens += event.quantity
        
        return {
            "api_calls": api_calls,
            "ai_tokens": ai_tokens
        }
    
    @staticmethod
    def check_quota(
        db: Session, 
        tenant_id: int, 
        api_calls_requested: int = 0, 
        tokens_requested: int = 0
    ) -> QuotaCheckResponse:
        # Get tenant
        tenant = TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            return QuotaCheckResponse(
                allowed=False,
                status_code=404,
                message=f"Tenant with id {tenant_id} not found",
                error_code="tenant_not_found",
                current_usage={},
                limits={}
            )
        
        # Get subscription
        subscription = SubscriptionRepository.get_by_tenant_with_plan(db, tenant_id)
        if not subscription:
            return QuotaCheckResponse(
                allowed=False,
                status_code=402,
                message="No active subscription found. Please subscribe to a plan.",
                error_code="no_subscription",
                current_usage={},
                limits={}
            )
        
        # Get plan
        plan = PlanRepository.get_by_id(db, subscription.plan_id)
        if not plan:
            return QuotaCheckResponse(
                allowed=False,
                status_code=402,
                message="Plan not found. Please contact support.",
                error_code="plan_not_found",
                current_usage={},
                limits={}
            )
        
        # Get current usage
        current_usage = QuotaService.get_current_usage(db, tenant_id)
        current_api_calls = current_usage["api_calls"]
        current_tokens = current_usage["ai_tokens"]
        
        # Check API calls quota
        api_limit = plan.api_call_limit
        new_api_total = current_api_calls + api_calls_requested
        api_allowed = new_api_total <= api_limit
        
        # Check AI tokens quota
        token_limit = plan.ai_token_limit
        new_token_total = current_tokens + tokens_requested
        token_allowed = new_token_total <= token_limit
        
        # Determine if allowed
        is_allowed = api_allowed and token_allowed
        
        # Build response
        if is_allowed:
            return QuotaCheckResponse(
                allowed=True,
                status_code=200,
                message="Quota check passed. Request allowed.",
                error_code=None,
                current_usage={
                    "api_calls": current_api_calls,
                    "ai_tokens": current_tokens
                },
                limits={
                    "api_calls": api_limit,
                    "ai_tokens": token_limit
                }
            )
        else:
            # Determine which quota was exceeded
            error_code = None
            message = None
            
            if not api_allowed and not token_allowed:
                error_code = "both_quotas_exceeded"
                message = f"API call quota ({api_limit}) and AI token quota ({token_limit}) exceeded. Current usage: {current_api_calls} API calls, {current_tokens} tokens."
            elif not api_allowed:
                error_code = "api_call_quota_exceeded"
                message = f"Monthly API call limit of {api_limit} exceeded. Current usage: {current_api_calls} API calls."
            else:
                error_code = "ai_token_quota_exceeded"
                message = f"Monthly AI token limit of {token_limit} exceeded. Current usage: {current_tokens} tokens."
            
            status_code = 429
            
            return QuotaCheckResponse(
                allowed=False,
                status_code=status_code,
                message=message,
                error_code=error_code,
                current_usage={
                    "api_calls": current_api_calls,
                    "ai_tokens": current_tokens
                },
                limits={
                    "api_calls": api_limit,
                    "ai_tokens": token_limit
                }
            )
