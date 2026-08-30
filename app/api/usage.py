from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import UsageRequest, GenerateResponse
from app.services import UsageService, QuotaService
from app.repositories import TenantRepository

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
def generate_usage(
    request: UsageRequest,
    tenant_id: int,
    idempotency_key: str = Header(..., description="Unique key to prevent duplicate processing"),
    db: Session = Depends(get_db)
):
    # Check if tenant exists
    tenant = TenantRepository.get_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with id {tenant_id} not found"
        )

    # Validate idempotency key
    if not idempotency_key or len(idempotency_key.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="idempotency_key header is required"
        )

    # Check if there's any usage to record
    if request.total_tokens == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tokens provided. At least one token type must be > 0"
        )

    # ===== QUOTA CHECK =====
    # Check API call quota (1 API call per request)
    quota_check = QuotaService.check_quota(
        db, 
        tenant_id, 
        api_calls_requested=1,
        tokens_requested=request.total_tokens
    )
    
    if not quota_check.allowed:
        # Return appropriate error response
        status_code = quota_check.status_code
        if status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": quota_check.error_code,
                    "message": quota_check.message,
                    "current_usage": quota_check.current_usage,
                    "limits": quota_check.limits
                }
            )
        elif status_code == 402:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": quota_check.error_code,
                    "message": quota_check.message,
                    "current_usage": quota_check.current_usage,
                    "limits": quota_check.limits
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=quota_check.message
            )

    # ===== PROCESS USAGE =====
    try:
        result = UsageService.generate_usage(db, tenant_id, request, idempotency_key)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording usage: {str(e)}"
        )
