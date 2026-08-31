# Evidence of Requirements - Usage Metering & Billing Engine

This document provides proof that all requirements for the FlyRank Capstone project have been met. Each requirement is listed with evidence including test outputs, API responses, and database queries.

## 📋 Requirements Checklist

| Requirement            | Status | Evidence                           |
| ---------------------- | ------ | ---------------------------------- |
| Idempotent Metering    | ✅      | Test passes                        |
| Quota Enforcement      | ✅      | 429/402 responses                  |
| Token Pricing          | ✅      | Cached cheaper, reasoning = output |
| Money as Integer Cents | ✅      | No floats                          |
| Stripe Checkout        | ✅      | FREE → PRO upgrade                 |
| Webhook Signature      | ✅      | Invalid → 400                      |
| Webhook Deduplication  | ✅      | Unique constraint                  |
| Background Job         | ✅      | `/jobs/aggregate`                  |
| Tests                  | ✅      | 11/11 passing                      |

---

## 1. Idempotent Metering

**Requirement:** A billable action creates exactly one usage event, even under retries.

### Evidence: Test Output

```text
tests/test_idempotency.py::test_idempotency_same_request_twice PASSED

First Request with idempotency-key "test-idempotent-001":
→ Status: 200
→ Response: {"status": "recorded", "quantity": 150, ...}

Second Request with same idempotency-key "test-idempotent-001":
→ Status: 200
→ Response: {"status": "duplicate", "quantity": 150, ...}

Database Query:
SELECT COUNT(*) FROM usage_events
WHERE idempotency_key = 'test-idempotent-001';

→ 1 row (Only ONE usage event created)
```

### Code Evidence

* `app/models/usage_event.py`: UniqueConstraint on `(tenant_id, idempotency_key)`
* `app/services/idempotency_service.py`: Idempotency check logic

**✅ VERIFIED**

---

## 2. Quota Enforcement

**Requirement:** Usage is checked against plan limits; over-limit requests are rejected with 429/402.

### Evidence: API Response

```text
Before:
GET /api/v1/quota/1

→ {
    "current_usage": {
        "api_calls": 864
    },
    "limits": {
        "api_calls": 1000
    }
}

Request at boundary (1000th call):

POST /api/v1/generate?tenant_id=1
with 1 API call

→ Status: 200 OK

Request after boundary (1001st call):

POST /api/v1/generate?tenant_id=1
with 1 API call

→ Status: 429 Too Many Requests

→ Response:
{
    "detail": {
        "error": "api_call_quota_exceeded",
        "message": "Monthly API call limit of 1000 exceeded. Current usage: 1000 API calls.",
        "current_usage": {
            "api_calls": 1000,
            "ai_tokens": 11247
        },
        "limits": {
            "api_calls": 1000,
            "ai_tokens": 100000
        }
    }
}
```

### Code Evidence

* `app/services/quota_service.py`: `check_quota()` method
* `app/api/usage.py`: Quota check before recording usage

**✅ VERIFIED**

---

## 3. Cost Calculation - AI Token Pricing

**Requirement:** Token pricing handles cached input tokens as cheaper and reasoning tokens as output.

### Evidence: Cost Calculation

Pricing configuration in cents per 1,000 tokens:

```text
- Input Tokens: 3 cents ($0.03)
- Cached Input Tokens: 1 cent ($0.01) ← CHEAPER!
- Output Tokens: 6 cents ($0.06)
- Reasoning Tokens: 6 cents ($0.06) ← Charged as OUTPUT
```

### Test Request

```text
POST /api/v1/generate

Tokens:
{
    "input_tokens": 1000,
    "cached_input_tokens": 500,
    "output_tokens": 200,
    "reasoning_tokens": 100
}
```

### Response

```text
{
    "status": "recorded",
    "quantity": 1800,
    "token_breakdown": {
        "input_tokens": 1000,
        "cached_input_tokens": 500,
        "output_tokens": 200,
        "reasoning_tokens": 100
    }
}
```

### Cost Calculation

```text
Input:
1000 × 3 / 1000 = 3 cents

Cached Input:
500 × 1 / 1000 = 0 cents (0.5 rounded down)

Output:
200 × 6 / 1000 = 1 cent

Reasoning:
100 × 6 / 1000 = 0 cents (0.6 rounded down)

Total:
4 cents
```

### Money Handling

All costs are stored as **INTEGER cents** — NO FLOATS are used.

### Code Evidence

* `app/core/pricing.py`: Pricing configuration
* `app/services/cost_service.py`: `calculate_token_cost()`

**✅ VERIFIED**

---

## 4. Stripe Checkout (Mock Mode)

**Requirement:** Subscription checkout works end-to-end in Stripe test/mock mode.

### Evidence: Checkout Flow

#### Step 1: Tenant on FREE Plan

```text
GET /api/v1/tenants/1

→ Plan: FREE (ID: 1)
```

#### Step 2: Create Checkout Session

```text
POST /api/v1/billing/create-checkout-session

→ Response:
{
    "checkout_url": "http://localhost:8000/api/v1/stripe/mock-checkout?tenant_id=1&session_id=cs_test_mock_...",
    "session_id": "cs_test_mock_..."
}
```

#### Step 3: Open Mock Checkout

```text
Mock Checkout URL opened in browser

→ Automatically processes mock payment
```

#### Step 4: Webhook Processed

```text
POST /api/v1/webhooks/stripe/mock?tenant_id=1

→ Status: success
→ Message: "Tenant 1 upgraded to PRO"
```

#### Step 5: Verify Upgrade

```text
GET /api/v1/tenants/1

→ Plan: PRO (ID: 2)
→ Status: active
→ Stripe Subscription ID: mock_sub_xxxxxxxx
```

### Code Evidence

* `app/services/stripe_service.py`: `create_checkout_session()`
* `app/services/webhook_service.py`: `handle_checkout_completed()`
* `app/api/stripe.py`: Checkout endpoints
* `app/api/webhooks.py`: Webhook handler

**✅ VERIFIED**

---

## 5. Webhook Security - Signature Verification

**Requirement:** Webhooks verify signatures; forged webhooks return 400.

### Evidence: Test Output

```text
tests/test_webhooks.py::test_forged_webhook_rejected PASSED

Request with invalid signature:

POST /api/v1/webhooks/stripe

Headers:
{
    "stripe-signature": "invalid_signature"
}

Payload:
{
    "id": "evt_test_123",
    "type": "checkout.session.completed",
    ...
}

→ Status: 400 Bad Request
→ No database changes
```

### Code Evidence

* `app/services/webhook_service.py`: `verify_signature()`
* `app/api/webhooks.py`: `stripe_webhook()` endpoint

**✅ VERIFIED**

---

## 6. Webhook Idempotency - Duplicate Prevention

**Requirement:** The same webhook event is processed only once.

### Evidence: Test Output

```text
tests/test_webhooks.py::test_duplicate_webhook_ignored PASSED

First Webhook:

Event ID:
"evt_duplicate_test_001"

→ Processed successfully
→ Recorded in webhook_events table

Second Webhook (same event ID):

→ Status: "duplicate"
→ Message: "Event evt_duplicate_test_001 already processed"
→ No second update to subscription

Database Query:

SELECT COUNT(*) FROM webhook_events
WHERE stripe_event_id = 'evt_duplicate_test_001';

→ 1 row (Only ONE webhook event recorded)
```

### Code Evidence

* `app/models/webhook_event.py`: UniqueConstraint on `stripe_event_id`
* `app/repositories/webhook_repository.py`: `exists()` check
* `app/services/webhook_service.py`: `process_webhook_event()`

**✅ VERIFIED**

---

## 7. Background Job - Off-Request-Path Processing

**Requirement:** At least one background job exists for bulk/slow work with retry support.

### Evidence: API Response

```text
POST /api/v1/jobs/aggregate

→ Response:
{
    "job": "usage_aggregation",
    "started_at": "2026-08-31T00:04:15.656297",
    "result": {
        "status": "success",
        "tenants_processed": 3,
        "errors": [],
        "total_time_ms": 12.34
    }
}
```

### Database Query

```sql
SELECT *
FROM usage_aggregations
WHERE tenant_id = 1;
```

Result:

```text
→ period: "2026-08"
→ api_calls: 864
→ ai_tokens: 11247
→ api_cost_cents: 864
→ token_cost_cents: 30
→ total_cost_cents: 894
```

### Code Evidence

* `app/services/background_job_service.py`: `run_usage_aggregation()`
* `app/api/background_jobs.py`: `/jobs/aggregate` endpoint
* `app/models/usage_aggregation.py`: Aggregation table

**✅ VERIFIED**

---

## 8. Test Coverage

**Requirement:** Tests prove that the system works correctly.

### Evidence: Test Results

```text
========================================= test session starts ==========================================

collected 11 items

tests/test_idempotency.py::test_idempotency_same_request_twice PASSED [  9%]
tests/test_integration.py::test_complete_workflow PASSED [ 18%]
tests/test_pricing.py::test_token_pricing_calculation PASSED [ 27%]
tests/test_pricing.py::test_cached_tokens_cheaper PASSED [ 36%]
tests/test_pricing.py::test_reasoning_tokens_count_as_output PASSED [ 45%]
tests/test_pricing.py::test_cost_endpoint_returns_cents PASSED [ 54%]
tests/test_quota.py::test_quota_boundary PASSED [ 63%]
tests/test_quota.py::test_quota_without_idempotency_key PASSED [ 72%]
tests/test_quota.py::test_quota_no_tokens PASSED [ 81%]
tests/test_webhooks.py::test_forged_webhook_rejected PASSED [ 90%]
tests/test_webhooks.py::test_duplicate_webhook_ignored PASSED [100%]

========================================== 11 passed, 5 warnings ==========================================
```

### Test Files

* `tests/test_idempotency.py`: Idempotency test
* `tests/test_integration.py`: Complete workflow test
* `tests/test_pricing.py`: Token pricing tests
* `tests/test_quota.py`: Quota enforcement tests
* `tests/test_webhooks.py`: Webhook tests

**✅ VERIFIED**

---

## 📊 Summary

| Requirement            | Status   | Test Result                           |
| ---------------------- | -------- | ------------------------------------- |
| Idempotent Metering    | ✅ PASSED | `test_idempotency_same_request_twice` |
| Quota Enforcement      | ✅ PASSED | `test_quota_boundary`                 |
| Token Pricing          | ✅ PASSED | Pricing tests                         |
| Money as Integer Cents | ✅ PASSED | `test_cost_endpoint_returns_cents`    |
| Stripe Checkout        | ✅ PASSED | `test_complete_workflow`              |
| Webhook Signature      | ✅ PASSED | `test_forged_webhook_rejected`        |
| Webhook Deduplication  | ✅ PASSED | `test_duplicate_webhook_ignored`      |
| Background Job         | ✅ PASSED | Manual test                           |
| Overall Tests          | ✅ PASSED | 11/11 tests passing                   |

---

## 🔗 Repository

**GitHub:** https://github.com/zarshamwaleed/usage-metering-billing-engine

---

## 📝 Notes

* Stripe is in **mock mode** because Stripe is not available in Pakistan.
* All money values are stored as **integer cents** with no floating-point values.
* The system is fully containerized using **Docker Compose**.
* All **11 tests pass**, proving the implemented requirements work correctly.

---

# ✅ ALL REQUIREMENTS HAVE BEEN MET AND VERIFIED.
