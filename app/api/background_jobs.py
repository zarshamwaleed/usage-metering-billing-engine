from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import BackgroundJobService
from app.repositories import AggregationRepository
from datetime import datetime

router = APIRouter()

@router.post("/jobs/aggregate")
def run_aggregation_job(db: Session = Depends(get_db)):
    try:
        result = BackgroundJobService.run_usage_aggregation(db)
        return {
            "job": "usage_aggregation",
            "started_at": datetime.utcnow().isoformat(),
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job failed: {str(e)}"
        )

@router.post("/jobs/cleanup")
def run_cleanup_job(
    days_to_keep: int = 30,
    db: Session = Depends(get_db)
):
    try:
        result = BackgroundJobService.run_cleanup_job(db, days_to_keep)
        return {
            "job": "cleanup",
            "started_at": datetime.utcnow().isoformat(),
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job failed: {str(e)}"
        )

@router.post("/jobs/reconcile")
def run_reconciliation_job(db: Session = Depends(get_db)):
    try:
        result = BackgroundJobService.run_stripe_reconciliation(db)
        return {
            "job": "stripe_reconciliation",
            "started_at": datetime.utcnow().isoformat(),
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job failed: {str(e)}"
        )

@router.get("/jobs/aggregations/{tenant_id}")
def get_tenant_aggregations(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    aggregations = AggregationRepository.get_all_by_tenant(db, tenant_id)
    return [
        {
            "period": agg.period,
            "api_calls": agg.api_calls,
            "ai_tokens": agg.ai_tokens,
            "api_cost_cents": agg.api_cost_cents,
            "token_cost_cents": agg.token_cost_cents,
            "total_cost_cents": agg.total_cost_cents,
            "updated_at": agg.updated_at
        }
        for agg in aggregations
    ]
