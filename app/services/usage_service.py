from sqlalchemy.orm import Session
from app.repositories import UsageRepository, TenantRepository
from app.schemas import UsageRequest, UsageEventCreate, GenerateResponse
from app.models.usage_event import UsageType
from typing import Optional

class UsageService:
    @staticmethod
    def record_usage(db: Session, tenant_id: int, usage_type: str, quantity: int, idempotency_key: str) -> GenerateResponse:
        existing = UsageRepository.get_by_idempotency_key(db, tenant_id, idempotency_key)
        if existing:
            return GenerateResponse(
                status="duplicate",
                tenant_id=tenant_id,
                usage_type=str(existing.usage_type),
                quantity=existing.quantity,
                idempotency_key=idempotency_key,
                message=f"Duplicate request ignored. Usage already recorded with key: {idempotency_key}",
                token_breakdown=None
            )
        
        usage_data = UsageEventCreate(
            tenant_id=tenant_id,
            usage_type=usage_type,
            quantity=quantity,
            idempotency_key=idempotency_key
        )
        
        usage_event = UsageRepository.create(db, usage_data)
        
        return GenerateResponse(
            status="recorded",
            tenant_id=tenant_id,
            usage_type=str(usage_event.usage_type),
            quantity=usage_event.quantity,
            idempotency_key=idempotency_key,
            message="Usage recorded successfully",
            token_breakdown=None
        )
    
    @staticmethod
    def generate_usage(db: Session, tenant_id: int, request: UsageRequest, idempotency_key: str) -> GenerateResponse:
        tenant = TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise ValueError(f"Tenant with id {tenant_id} not found")
        
        # Check idempotency - look for any event with this prefix
        existing_events = UsageRepository.get_by_idempotency_prefix(db, tenant_id, idempotency_key)
        if existing_events:
            total_tokens = sum([e.quantity for e in existing_events if str(e.usage_type) == "ai_token"])
            
            return GenerateResponse(
                status="duplicate",
                tenant_id=tenant_id,
                usage_type="ai_token",
                quantity=total_tokens,
                idempotency_key=idempotency_key,
                message=f"Duplicate request ignored. Usage already recorded with key: {idempotency_key}",
                token_breakdown=None
            )
        
        # Record the main idempotency key first (to prevent duplicates)
        UsageRepository.create(db, UsageEventCreate(
            tenant_id=tenant_id,
            usage_type=UsageType.API_CALL,
            quantity=0,
            idempotency_key=idempotency_key
        ))
        
        total_tokens = 0
        token_breakdown = {}
        
        if request.input_tokens and request.input_tokens > 0:
            UsageRepository.create(db, UsageEventCreate(
                tenant_id=tenant_id,
                usage_type=UsageType.AI_TOKEN,
                quantity=request.input_tokens,
                idempotency_key=f"{idempotency_key}_input"
            ))
            total_tokens += request.input_tokens
            token_breakdown["input_tokens"] = request.input_tokens
        
        if request.cached_input_tokens and request.cached_input_tokens > 0:
            UsageRepository.create(db, UsageEventCreate(
                tenant_id=tenant_id,
                usage_type=UsageType.AI_TOKEN,
                quantity=request.cached_input_tokens,
                idempotency_key=f"{idempotency_key}_cached"
            ))
            total_tokens += request.cached_input_tokens
            token_breakdown["cached_input_tokens"] = request.cached_input_tokens
        
        if request.output_tokens and request.output_tokens > 0:
            UsageRepository.create(db, UsageEventCreate(
                tenant_id=tenant_id,
                usage_type=UsageType.AI_TOKEN,
                quantity=request.output_tokens,
                idempotency_key=f"{idempotency_key}_output"
            ))
            total_tokens += request.output_tokens
            token_breakdown["output_tokens"] = request.output_tokens
        
        if request.reasoning_tokens and request.reasoning_tokens > 0:
            UsageRepository.create(db, UsageEventCreate(
                tenant_id=tenant_id,
                usage_type=UsageType.AI_TOKEN,
                quantity=request.reasoning_tokens,
                idempotency_key=f"{idempotency_key}_reasoning"
            ))
            total_tokens += request.reasoning_tokens
            token_breakdown["reasoning_tokens"] = request.reasoning_tokens
        
        UsageRepository.create(db, UsageEventCreate(
            tenant_id=tenant_id,
            usage_type=UsageType.API_CALL,
            quantity=1,
            idempotency_key=f"{idempotency_key}_api_call"
        ))
        
        return GenerateResponse(
            status="recorded",
            tenant_id=tenant_id,
            usage_type="ai_token",
            quantity=total_tokens,
            idempotency_key=idempotency_key,
            message=f"Usage recorded successfully. Total tokens: {total_tokens}",
            token_breakdown=token_breakdown
        )
