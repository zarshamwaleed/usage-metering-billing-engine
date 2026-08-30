from sqlalchemy.orm import Session
from app.repositories import PlanRepository
from app.schemas import PlanResponse
from typing import List, Optional

class PlanService:
    @staticmethod
    def get_all_plans(db: Session) -> List[PlanResponse]:
        plans = PlanRepository.get_all(db)
        return [PlanResponse.model_validate(plan) for plan in plans]
    
    @staticmethod
    def get_plan(db: Session, plan_id: int) -> Optional[PlanResponse]:
        plan = PlanRepository.get_by_id(db, plan_id)
        if plan:
            return PlanResponse.model_validate(plan)
        return None
