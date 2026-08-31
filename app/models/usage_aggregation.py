from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger, UniqueConstraint
from app.core.database import Base

class UsageAggregation(Base):
    __tablename__ = "usage_aggregations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False)
    period = Column(String(7), nullable=False)  # Format: YYYY-MM
    api_calls = Column(BigInteger, default=0)
    ai_tokens = Column(BigInteger, default=0)
    api_cost_cents = Column(BigInteger, default=0)
    token_cost_cents = Column(BigInteger, default=0)
    total_cost_cents = Column(BigInteger, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('tenant_id', 'period', name='uq_tenant_period'),
    )

    def __repr__(self):
        return f"<UsageAggregation(tenant_id={self.tenant_id}, period='{self.period}', api_calls={self.api_calls}, total_cost={self.total_cost_cents})>"
