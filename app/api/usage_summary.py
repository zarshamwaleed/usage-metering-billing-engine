from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import UsageSummaryResponse
from app.services import UsageSummaryService
from app.repositories import TenantRepository

router = APIRouter()

@router.get("/usage/{tenant_id}", response_model=UsageSummaryResponse)
def get_usage_summary(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    tenant = TenantRepository.get_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with id {tenant_id} not found"
        )

    try:
        summary = UsageSummaryService.get_usage_summary(db, tenant_id)
        return summary
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting usage summary: {str(e)}"
        )
