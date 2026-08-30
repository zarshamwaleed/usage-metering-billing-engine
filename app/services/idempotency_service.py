from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories import UsageRepository
from app.schemas import UsageEventCreate, GenerateResponse
from app.models.usage_event import UsageType
from typing import Dict, Any
import hashlib
import json

class IdempotencyService:
    @staticmethod
    def generate_idempotency_key(tenant_id: int, request_data: Dict[str, Any]) -> str:
        sorted_data = json.dumps(request_data, sort_keys=True)
        hash_input = f"{tenant_id}:{sorted_data}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:32]

    @staticmethod
    def check_and_record(
        db: Session,
        tenant_id: int,
        idempotency_key: str,
        usage_type: str,
        quantity: int
    ) -> Dict[str, Any]:
        existing = UsageRepository.get_by_idempotency_key(db, tenant_id, idempotency_key)

        if existing:
            return {
                'is_duplicate': True,
                'existing_event': existing,
                'new_event': None
            }

        try:
            usage_data = UsageEventCreate(
                tenant_id=tenant_id,
                usage_type=usage_type,
                quantity=quantity,
                idempotency_key=idempotency_key
            )
            new_event = UsageRepository.create(db, usage_data)

            return {
                'is_duplicate': False,
                'existing_event': None,
                'new_event': new_event
            }

        except IntegrityError:
            db.rollback()
            existing = UsageRepository.get_by_idempotency_key(db, tenant_id, idempotency_key)
            return {
                'is_duplicate': True,
                'existing_event': existing,
                'new_event': None
            }

    @staticmethod
    def process_generate_request(
        db: Session,
        tenant_id: int,
        idempotency_key: str,
        token_data: Dict[str, int]
    ) -> GenerateResponse:
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

        total_tokens = 0
        token_breakdown = {}

        token_mappings = {
            'input_tokens': '_input',
            'cached_input_tokens': '_cached',
            'output_tokens': '_output',
            'reasoning_tokens': '_reasoning'
        }

        for token_type, suffix in token_mappings.items():
            quantity = token_data.get(token_type, 0)
            if quantity and quantity > 0:
                sub_key = f"{idempotency_key}{suffix}"
                UsageRepository.create(db, UsageEventCreate(
                    tenant_id=tenant_id,
                    usage_type=UsageType.AI_TOKEN,
                    quantity=quantity,
                    idempotency_key=sub_key
                ))
                total_tokens += quantity
                token_breakdown[token_type] = quantity

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
