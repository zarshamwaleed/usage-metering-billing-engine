from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Enum, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class UsageType(str, enum.Enum):
    API_CALL = "api_call"
    AI_TOKEN = "ai_token"

class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    usage_type = Column(Enum(UsageType), nullable=False)
    quantity = Column(BigInteger, nullable=False)
    idempotency_key = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="usage_events")

    # Unique constraint to prevent duplicate events at database level
    __table_args__ = (
        UniqueConstraint('tenant_id', 'idempotency_key', name='uq_tenant_idempotency'),
    )

    def __repr__(self):
        return f"<UsageEvent(id={self.id}, tenant_id={self.tenant_id}, type='{self.usage_type}', qty={self.quantity}, key='{self.idempotency_key}')>"
