import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models import Tenant, Plan, Subscription, UsageEvent
from app.models.subscription import SubscriptionStatus
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        seed_test_data(session)
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def seed_test_data(db):
    free_plan = Plan(name="FREE", api_call_limit=1000, ai_token_limit=100000)
    pro_plan = Plan(name="PRO", api_call_limit=10000, ai_token_limit=1000000)
    db.add_all([free_plan, pro_plan])
    db.commit()

    tenant = Tenant(name="Test Tenant")
    db.add(tenant)
    db.flush()

    subscription = Subscription(
        tenant_id=tenant.id,
        plan_id=free_plan.id,
        status=SubscriptionStatus.ACTIVE
    )
    db.add(subscription)
    db.commit()
