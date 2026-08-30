from sqlalchemy.orm import Session
from app.models import Plan
from typing import List, Optional

class PlanRepository:
    @staticmethod
    def get_all(db: Session) -> List[Plan]:
        return db.query(Plan).all()
    
    @staticmethod
    def get_by_id(db: Session, plan_id: int) -> Optional[Plan]:
        return db.query(Plan).filter(Plan.id == plan_id).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Plan]:
        return db.query(Plan).filter(Plan.name == name).first()
