from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import TenantCreate, TenantResponse, TenantWithSubscriptionResponse
from app.services import TenantService
from typing import List

router = APIRouter()

@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(tenant_data: TenantCreate, db: Session = Depends(get_db)):
    try:
        tenant = TenantService.create_tenant(db, tenant_data)
        return tenant
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/tenants/{tenant_id}", response_model=TenantWithSubscriptionResponse)
def get_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = TenantService.get_tenant_with_details(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with id {tenant_id} not found"
        )
    return tenant

@router.get("/tenants", response_model=List[TenantResponse])
def get_all_tenants(db: Session = Depends(get_db)):
    from app.repositories import TenantRepository
    tenants = TenantRepository.get_all(db)
    return [TenantResponse.model_validate(t) for t in tenants]
