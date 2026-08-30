from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import PlanResponse
from app.services import PlanService
from typing import List

router = APIRouter()

@router.get("/plans", response_model=List[PlanResponse])
def get_all_plans(db: Session = Depends(get_db)):
    return PlanService.get_all_plans(db)

@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = PlanService.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with id {plan_id} not found"
        )
    return plan
