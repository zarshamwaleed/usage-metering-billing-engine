from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import UsageCostResponse
from app.services import CostService
from app.repositories import TenantRepository
from datetime import datetime

router = APIRouter()

@router.get("/cost/{tenant_id}", response_model=UsageCostResponse)
def get_tenant_cost(
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
        cost = CostService.get_tenant_cost(db, tenant_id)
        return cost
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating cost: {str(e)}"
        )

@router.get("/cost/{tenant_id}/breakdown")
def get_cost_breakdown(
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
        cost = CostService.get_tenant_cost(db, tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "plan": cost.plan_name,
            "period": cost.period,
            "api_calls": {
                "count": cost.api_calls,
                "cost_cents": cost.api_cost_cents,
                "cost_dollars": cost.api_cost_dollars
            },
            "tokens": {
                "input": {
                    "tokens": cost.token_breakdown.input_tokens,
                    "cost_cents": cost.token_breakdown.input_cost_cents,
                    "cost_dollars": cost.token_breakdown.input_cost_cents / 100
                },
                "cached_input": {
                    "tokens": cost.token_breakdown.cached_input_tokens,
                    "cost_cents": cost.token_breakdown.cached_input_cost_cents,
                    "cost_dollars": cost.token_breakdown.cached_input_cost_cents / 100
                },
                "output": {
                    "tokens": cost.token_breakdown.output_tokens,
                    "cost_cents": cost.token_breakdown.output_cost_cents,
                    "cost_dollars": cost.token_breakdown.output_cost_cents / 100
                },
                "reasoning": {
                    "tokens": cost.token_breakdown.reasoning_tokens,
                    "cost_cents": cost.token_breakdown.reasoning_cost_cents,
                    "cost_dollars": cost.token_breakdown.reasoning_cost_cents / 100
                }
            },
            "total": {
                "cost_cents": cost.total_cost_cents,
                "cost_dollars": cost.total_cost_dollars
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating cost: {str(e)}"
        )
