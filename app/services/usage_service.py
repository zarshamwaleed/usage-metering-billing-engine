from sqlalchemy.orm import Session
from app.repositories import UsageRepository, TenantRepository
from app.schemas import UsageRequest, GenerateResponse
from app.models.usage_event import UsageType
from app.services.idempotency_service import IdempotencyService

class UsageService:
    @staticmethod
    def generate_usage(db: Session, tenant_id: int, request: UsageRequest, idempotency_key: str) -> GenerateResponse:
        tenant = TenantRepository.get_by_id(db, tenant_id)
        if not tenant:
            raise ValueError(f"Tenant with id {tenant_id} not found")

        if not idempotency_key or len(idempotency_key.strip()) == 0:
            raise ValueError("idempotency_key is required")

        token_data = {
            'input_tokens': request.input_tokens or 0,
            'cached_input_tokens': request.cached_input_tokens or 0,
            'output_tokens': request.output_tokens or 0,
            'reasoning_tokens': request.reasoning_tokens or 0
        }

        if sum(token_data.values()) == 0:
            raise ValueError("No tokens provided. At least one token type must be > 0")

        return IdempotencyService.process_generate_request(
            db, tenant_id, idempotency_key, token_data
        )
