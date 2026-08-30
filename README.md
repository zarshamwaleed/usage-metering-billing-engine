# Usage Metering & Billing Engine

A FastAPI-based service for SaaS usage metering, quota enforcement, and billing with Stripe integration.

## Quick Start

### Prerequisites

* Docker Desktop
* Docker Compose

### Run the Application

```bash
docker compose up --build
```

### Access the API

* **API:** http://localhost:8000
* **Health Check:** http://localhost:8000/api/v1/health
* **API Documentation:** http://localhost:8000/docs

## Architecture

Coming soon

## Project Structure

```text
app/
├── api/          # API routes
├── core/         # Core configuration
├── models/       # SQLAlchemy models
├── services/     # Business logic
├── schemas/      # Pydantic schemas
├── utils/        # Utilities
└── repositories/ # Database operations
```

## Tech Stack

* Python 3.11
* FastAPI
* PostgreSQL 15
* Docker
* Stripe
* SQLAlchemy
* Alembic
* Pytest
