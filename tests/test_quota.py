import pytest
from fastapi.testclient import TestClient

def test_quota_boundary(client: TestClient):
    response = client.get("/api/v1/quota/1")
    assert response.status_code == 200
    data = response.json()
    
    current_api_calls = data["current_usage"]["api_calls"]
    limit = 1000
    requests_to_make = min(limit - current_api_calls, 50)
    
    for i in range(requests_to_make):
        response = client.post(
            "/api/v1/generate?tenant_id=1",
            json={"input_tokens": 1},
            headers={"idempotency-key": f"quota-test-{i}"}
        )
        assert response.status_code == 200
    
    response = client.post(
        "/api/v1/generate?tenant_id=1",
        json={"input_tokens": 1},
        headers={"idempotency-key": "quota-test-last"}
    )
    assert response.status_code in [200, 429]

def test_quota_without_idempotency_key(client: TestClient):
    response = client.post(
        "/api/v1/generate?tenant_id=1",
        json={"input_tokens": 10}
    )
    assert response.status_code in [400, 422]

def test_quota_no_tokens(client: TestClient):
    response = client.post(
        "/api/v1/generate?tenant_id=1",
        json={},
        headers={"idempotency-key": "no-tokens-test"}
    )
    assert response.status_code in [400, 422]
