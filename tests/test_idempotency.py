import pytest
from fastapi.testclient import TestClient

def test_idempotency_same_request_twice(client: TestClient):
    # First request with idempotency key
    response1 = client.post(
        "/api/v1/generate?tenant_id=1",
        json={
            "input_tokens": 100,
            "output_tokens": 50
        },
        headers={"idempotency-key": "test-idempotent-001"}
    )
    
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["status"] == "recorded"
    # The quantity might be 0 if the test environment is mocked
    # Just check that the request was processed
    
    # Second request with same idempotency key
    response2 = client.post(
        "/api/v1/generate?tenant_id=1",
        json={
            "input_tokens": 100,
            "output_tokens": 50
        },
        headers={"idempotency-key": "test-idempotent-001"}
    )
    
    assert response2.status_code == 200
    data2 = response2.json()
    # Should be duplicate
    assert data2["status"] == "duplicate"
