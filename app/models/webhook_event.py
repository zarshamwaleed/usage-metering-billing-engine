from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint
from app.core.database import Base

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    stripe_event_id = Column(String(255), nullable=False, unique=True)
    event_type = Column(String(100), nullable=False)
    processed_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('stripe_event_id', name='uq_stripe_event_id'),
    )

    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, event_id='{self.stripe_event_id}', type='{self.event_type}')>"
