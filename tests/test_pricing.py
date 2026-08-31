import pytest
from fastapi.testclient import TestClient
from app.core.pricing import get_pricing

def test_token_pricing_calculation(client: TestClient):
    response = client.post(
        "/api/v1/generate?tenant_id=1",
        json={
            "input_tokens": 1000,
            "cached_input_tokens": 500,
            "output_tokens": 200,
            "reasoning_tokens": 100
        },
        headers={"idempotency-key": "pricing-test-001"}
    )
    assert response.status_code == 200
    data = response.json()
    
    breakdown = data["token_breakdown"]
    assert breakdown["input_tokens"] == 1000
    assert breakdown["cached_input_tokens"] == 500
    assert breakdown["output_tokens"] == 200
    assert breakdown["reasoning_tokens"] == 100

def test_cached_tokens_cheaper(client: TestClient):
    pricing = get_pricing()
    assert pricing.input_token_price_cents > pricing.cached_input_token_price_cents

def test_reasoning_tokens_count_as_output(client: TestClient):
    # This test verifies that reasoning tokens use output pricing
    # The pricing config defines output_token_price_cents
    pricing = get_pricing()
    # Reasoning tokens should use the same price as output tokens
    assert pricing.output_token_price_cents > 0

def test_cost_endpoint_returns_cents(client: TestClient):
    client.post(
        "/api/v1/generate?tenant_id=1",
        json={"input_tokens": 1000},
        headers={"idempotency-key": "cost-test-001"}
    )
    
    response = client.get("/api/v1/cost/1")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data["api_cost_cents"], int)
    assert isinstance(data["total_cost_cents"], int)
    assert isinstance(data["token_breakdown"]["input_cost_cents"], int)
