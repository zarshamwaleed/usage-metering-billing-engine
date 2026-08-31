# Usage Metering & Billing Engine

A FastAPI-based service for SaaS usage metering, quota enforcement, and billing with Stripe integration.

## 📋 Overview

Every SaaS product needs to answer three questions:

* How much has this customer used?
* How much should they pay?
* Have they reached their plan limits?

This service answers all three with:

* ✅ Idempotent usage metering
* ✅ Quota enforcement with 429/402 responses
* ✅ AI token pricing (cached tokens cheaper, reasoning = output)
* ✅ Stripe test mode integration (mock mode for Pakistan)
* ✅ Webhook handling with deduplication
* ✅ Background jobs for aggregation

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                        Client / Frontend                         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI Application                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ /generate   │  │ /tenants    │  │ /billing/checkout       │  │
│  │ Usage API   │  │ Tenant API  │  │ Stripe Checkout          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ /quota      │  │ /cost       │  │ /webhooks/stripe        │  │
│  │ Quota API   │  │ Cost API    │  │ Webhook Handler          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ /usage      │  │ /jobs/*     │  │ Background Jobs           │  │
│  │ Usage API   │  │ Job API     │  │ Aggregation & Cleanup     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐  ┌────────────────┐ │
│  │ Tenants │  │ Plans   │  │Subscriptions│  │ Usage Events   │ │
│  └─────────┘  └─────────┘  └─────────────┘  └────────────────┘ │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────────────────────────────┐ │
│  │ Webhook Events  │  │ Usage Aggregations                   │ │
│  └─────────────────┘  └──────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Stripe Test Mode (Mock)                      │
│                      Webhook Simulator                           │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

* Docker Desktop
* Docker Compose
* Python 3.10+ (for local development)

### Run with Docker

```bash
# Clone the repository
git clone https://github.com/zarshamwaleed/usage-metering-billing-engine.git

# Navigate to the project
cd usage-metering-billing-engine

# Start the containers
docker compose up --build -d

# Verify it's running
curl http://localhost:8000/api/v1/health
```

## 🌐 Access the API

* **API:** http://localhost:8000
* **Health Check:** http://localhost:8000/api/v1/health
* **API Documentation:** http://localhost:8000/docs
* **ReDoc:** http://localhost:8000/redoc

## 📊 Plans & Pricing

| Plan     | API Calls / Month | AI Tokens / Month |
| -------- | ----------------: | ----------------: |
| **FREE** |             1,000 |           100,000 |
| **PRO**  |            10,000 |         1,000,000 |

### Token Pricing

Pricing per 1,000 tokens:

| Token Type          | Price | Notes                |
| ------------------- | ----: | -------------------- |
| Input Tokens        | $0.03 | Standard price       |
| Cached Input Tokens | $0.01 | Cheaper cached input |
| Output Tokens       | $0.06 | Standard output      |
| Reasoning Tokens    | $0.06 | Charged as output    |

## 🔧 API Endpoints

### Health & Status

| Method | Endpoint           | Description     |
| ------ | ------------------ | --------------- |
| GET    | `/api/v1/health`   | Health check    |
| GET    | `/api/v1/db-check` | Database status |

### Tenants

| Method | Endpoint               | Description                  |
| ------ | ---------------------- | ---------------------------- |
| POST   | `/api/v1/tenants`      | Create tenant with FREE plan |
| GET    | `/api/v1/tenants`      | List all tenants             |
| GET    | `/api/v1/tenants/{id}` | Get tenant details           |

### Plans & Subscriptions

| Method | Endpoint                            | Description             |
| ------ | ----------------------------------- | ----------------------- |
| GET    | `/api/v1/plans`                     | List all plans          |
| GET    | `/api/v1/plans/{id}`                | Get plan details        |
| GET    | `/api/v1/subscriptions/tenant/{id}` | Get tenant subscription |

### Usage

| Method | Endpoint                    | Description               |
| ------ | --------------------------- | ------------------------- |
| POST   | `/api/v1/generate`          | Record usage (idempotent) |
| GET    | `/api/v1/usage/{tenant_id}` | Usage summary with limits |

### Quota

| Method | Endpoint                    | Description             |
| ------ | --------------------------- | ----------------------- |
| GET    | `/api/v1/quota/{tenant_id}` | Check quota status      |
| POST   | `/api/v1/quota/check`       | Check quota for request |

### Cost

| Method | Endpoint                             | Description             |
| ------ | ------------------------------------ | ----------------------- |
| GET    | `/api/v1/cost/{tenant_id}`           | Get cost breakdown      |
| GET    | `/api/v1/cost/{tenant_id}/breakdown` | Detailed cost breakdown |

### Stripe (Mock Mode)

| Method | Endpoint                                  | Description             |
| ------ | ----------------------------------------- | ----------------------- |
| POST   | `/api/v1/billing/create-checkout-session` | Create checkout session |
| GET    | `/api/v1/stripe/success`                  | Success page            |
| GET    | `/api/v1/stripe/cancel`                   | Cancel page             |

### Webhooks

| Method | Endpoint                         | Description              |
| ------ | -------------------------------- | ------------------------ |
| POST   | `/api/v1/webhooks/stripe`        | Stripe webhook handler   |
| POST   | `/api/v1/webhooks/stripe/mock`   | Mock webhook for testing |
| GET    | `/api/v1/webhooks/stripe/events` | List webhook events      |

### Background Jobs

| Method | Endpoint                         | Description           |
| ------ | -------------------------------- | --------------------- |
| POST   | `/api/v1/jobs/aggregate`         | Run usage aggregation |
| POST   | `/api/v1/jobs/cleanup`           | Run cleanup job       |
| POST   | `/api/v1/jobs/reconcile`         | Run reconciliation    |
| GET    | `/api/v1/jobs/aggregations/{id}` | Get aggregations      |

## 🧪 Testing

### Run all tests

```bash
pytest tests/ -v
```

### Run specific tests

```bash
pytest tests/test_idempotency.py -v
pytest tests/test_quota.py -v
pytest tests/test_pricing.py -v
```

### Run tests with coverage

```bash
pytest --cov=app --cov-report=html tests/
```

## 📁 Project Structure

```text
usage-metering-billing-engine/
├── app/
│   ├── api/                    # API routes
│   │   ├── health.py
│   │   ├── tenants.py
│   │   ├── usage.py
│   │   ├── quota.py
│   │   ├── cost.py
│   │   ├── stripe.py
│   │   └── webhooks.py
│   │
│   ├── core/                   # Configuration
│   │   ├── config.py
│   │   ├── database.py
│   │   └── pricing.py
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── tenant.py
│   │   ├── plan.py
│   │   ├── subscription.py
│   │   ├── usage_event.py
│   │   └── webhook_event.py
│   │
│   ├── repositories/           # Data access layer
│   ├── services/               # Business logic
│   ├── schemas/                # Pydantic schemas
│   └── main.py                 # Application entry point
│
├── tests/                      # Test suite
├── scripts/                    # Utility scripts
├── alembic/                    # Database migrations
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── EVIDENCE.md
├── BUILDLOG.md
├── capstone.yaml
└── .env.example
```

## 🛠️ Tech Stack

* **Language:** Python 3.11
* **Framework:** FastAPI
* **Database:** PostgreSQL 15
* **ORM:** SQLAlchemy 2.0
* **Migrations:** Alembic
* **Payments:** Stripe (Mock Mode)
* **Containerization:** Docker
* **Testing:** Pytest

## 🔐 Key Features

### Idempotent Usage Metering

Usage events are recorded using idempotency keys to prevent duplicate usage charges when the same request is submitted multiple times.

### Quota Enforcement

The service automatically checks tenant usage against their plan limits and can return:

* **429 Too Many Requests** when API usage limits are reached.
* **402 Payment Required** when payment or billing requirements prevent continued usage.

### AI Token Pricing

The billing engine supports different token types:

* Input tokens
* Cached input tokens
* Output tokens
* Reasoning tokens

Cached input tokens are charged at a lower rate, while reasoning tokens are billed using the output-token rate.

### Stripe Integration

Stripe integration runs in test/mock mode, allowing billing flows and webhook handling to be tested without processing real payments.

### Webhook Deduplication

Incoming webhook events are stored and deduplicated to prevent the same Stripe event from being processed multiple times.

### Background Jobs

The application provides jobs for:

* Usage aggregation
* Data cleanup
* Billing reconciliation

## 📄 License

This project is developed for educational and demonstration purposes.
