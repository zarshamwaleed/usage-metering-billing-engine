from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import QuotaCheckResponse
from app.services import QuotaService
from app.repositories import TenantRepository

router = APIRouter()

@router.get("/quota/{tenant_id}", response_model=QuotaCheckResponse)
def check_quota(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    """
    Check current quota status for a tenant.
    Returns current usage, limits, and whether the tenant is within limits.
    """
    tenant = TenantRepository.get_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with id {tenant_id} not found"
        )
    
    # Check quota with zero requested usage
    result = QuotaService.check_quota(db, tenant_id, 0, 0)
    
    if result.status_code != 200:
        raise HTTPException(
            status_code=result.status_code,
            detail={
                "error": result.error_code,
                "message": result.message,
                "current_usage": result.current_usage,
                "limits": result.limits
            }
        )
    
    return result

@router.post("/quota/check", response_model=QuotaCheckResponse)
def check_quota_with_request(
    tenant_id: int,
    api_calls_requested: int = 0,
    tokens_requested: int = 0,
    db: Session = Depends(get_db)
):
    """
    Check if a specific usage request would exceed quotas.
    """
    tenant = TenantRepository.get_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with id {tenant_id} not found"
        )
    
    result = QuotaService.check_quota(db, tenant_id, api_calls_requested, tokens_requested)
    
    if result.status_code != 200:
        raise HTTPException(
            status_code=result.status_code,
            detail={
                "error": result.error_code,
                "message": result.message,
                "current_usage": result.current_usage,
                "limits": result.limits
            }
        )
    
    return result
