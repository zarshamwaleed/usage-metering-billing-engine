from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger
from sqlalchemy.orm import relationship
from app.core.database import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    api_call_limit = Column(BigInteger, nullable=False)
    ai_token_limit = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")

    def __repr__(self):
        return f"<Plan(id={self.id}, name='{self.name}', api_limit={self.api_call_limit}, token_limit={self.ai_token_limit})>"
