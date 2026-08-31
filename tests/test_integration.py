import pytest
from fastapi.testclient import TestClient

def test_complete_workflow(client: TestClient):
    # 1. Check initial tenant status
    response = client.get("/api/v1/tenants/1")
    assert response.status_code == 200
    tenant = response.json()
    assert tenant["subscription"]["plan_id"] == 1  # FREE plan
    
    # 2. Generate some usage
    for i in range(5):
        response = client.post(
            "/api/v1/generate?tenant_id=1",
            json={"input_tokens": 100},
            headers={"idempotency-key": f"integration-test-{i}"}
        )
        assert response.status_code == 200
    
    # 3. Check usage summary
    response = client.get("/api/v1/usage/1")
    assert response.status_code == 200
    usage = response.json()
    assert usage["api_calls"]["used"] > 0
    assert usage["ai_tokens"]["used"] > 0
    
    # 4. Check cost
    response = client.get("/api/v1/cost/1")
    assert response.status_code == 200
    cost = response.json()
    assert cost["total_cost_cents"] > 0
    
    # 5. Create checkout session (mock)
    response = client.post(
        "/api/v1/billing/create-checkout-session",
        json={"tenant_id": 1, "plan_name": "PRO"}
    )
    assert response.status_code == 200
    checkout = response.json()
    assert "checkout_url" in checkout
    assert "session_id" in checkout
    
    # 6. Simulate webhook (upgrade to PRO)
    response = client.post(
        "/api/v1/webhooks/stripe/mock?tenant_id=1"
    )
    assert response.status_code == 200
    webhook = response.json()
    assert webhook["status"] == "success"
    
    # 7. Verify upgrade
    response = client.get("/api/v1/tenants/1")
    assert response.status_code == 200
    tenant = response.json()
    assert tenant["subscription"]["plan_id"] == 2  # PRO plan
    assert tenant["subscription"]["status"] == "active"
    
    # 8. Check updated limits
    response = client.get("/api/v1/usage/1")
    assert response.status_code == 200
    usage = response.json()
    assert usage["api_calls"]["limit"] == 10000  # PRO limit
    assert usage["ai_tokens"]["limit"] == 1000000  # PRO limit
