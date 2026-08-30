from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import UsageRequest, GenerateResponse
from app.services import UsageService
from app.repositories import TenantRepository

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
def generate_usage(
    request: UsageRequest,
    tenant_id: int,
    idempotency_key: str = Header(..., description="Unique key to prevent duplicate processing"),
    db: Session = Depends(get_db)
):
    """
    Generate usage for a tenant.
    
    This endpoint simulates a billable AI generation request.
    It records token usage and an API call.
    
    - **tenant_id**: The tenant making the request
    - **idempotency_key**: Unique key to prevent duplicate processing (required)
    - **request**: Token breakdown (input, cached_input, output, reasoning)
    """
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
