# Build Log - AI Usage Report

## Project Overview

| Field             | Value                                                          |
| ----------------- | -------------------------------------------------------------- |
| **Project**       | Usage Metering & Billing Engine                                |
| **Student**       | Zarsham Waleed                                                 |
| **Date**          | August 2026                                                    |
| **Repository**    | https://github.com/zarshamwaleed/usage-metering-billing-engine |
| **Duration**      | ~40 hours                                                      |
| **AI Tools Used** | Claude (Anthropic)                                             |

---

## 1. Where AI Helped

### 1.1 Code Generation

| Module             | AI Contribution                                   | Generated |
| ------------------ | ------------------------------------------------- | --------- |
| Project Foundation | Dockerfile, docker-compose.yml, FastAPI setup     | ✅         |
| Database Models    | SQLAlchemy models, Alembic migrations             | ✅         |
| API Endpoints      | CRUD operations for tenants, plans, subscriptions | ✅         |
| Usage Metering     | Idempotency key handling, usage recording         | ✅         |
| Quota Enforcement  | Quota checking logic, 429/402 responses           | ✅         |
| Cost Calculation   | Token pricing, integer cents handling             | ✅         |
| Stripe Integration | Checkout sessions, webhook handling               | ✅         |
| Background Jobs    | Aggregation jobs, reconciliation                  | ✅         |
| Testing            | Pytest configuration, test cases                  | ✅         |
| Documentation      | README, EVIDENCE, BUILDLOG                        | ✅         |

### 1.2 Debugging Help

AI assistance was used to help:

* Fix syntax errors in multiple files
* Resolve import issues such as `RedirectResponse` and schemas
* Fix Pytest BOM encoding issues
* Resolve database connection issues
* Fix Pydantic schema property access

### 1.3 Architecture Guidance

AI provided guidance on:

* Repository pattern for data access
* Service layer for business logic
* Dependency injection for database sessions
* Idempotency key design
* Webhook deduplication strategy

---

## 2. Where AI Was Wrong

### 2.1 Syntax Errors

```text
❌ Issue:
Docstring syntax errors caused an "unexpected character after line continuation" error.

✅ Fix:
Removed problematic docstrings and used simple comments.

📁 Files:
- app/api/cost.py
- app/services/cost_service.py
- app/core/pricing.py
```

### 2.2 Import Errors

```text
❌ Issue:
"cannot import name 'RedirectResponse' from 'fastapi'"

✅ Fix:
Changed the import to:

from fastapi.responses import RedirectResponse

📁 File:
app/api/stripe.py
```

### 2.3 Schema Property Access

```text
❌ Issue:
"'TokenCostBreakdown' object has no attribute 'total_tokens'"

✅ Fix:
Calculated total_tokens manually in the service layer.

📁 File:
app/services/usage_summary_service.py
```

### 2.4 Pytest Configuration

```text
❌ Issue:
"pytest.ini: unexpected line: '\ufeff[pytest]'"

The issue was caused by a BOM (Byte Order Mark) character.

✅ Fix:
Recreated pytest.ini using ASCII/UTF-8 encoding without BOM.

📁 File:
pytest.ini
```

### 2.5 Stripe Availability

```text
❌ Issue:
Stripe was not available for the required payment workflow in Pakistan.

✅ Fix:
Implemented a complete mock mode with webhook simulation.

📁 File:
app/services/stripe_service.py
```

---

## 3. What I Changed Myself

### 3.1 Architecture Decisions

* Chose **FastAPI** over Flask for better performance and API development
* Used the **repository pattern** for clean data access
* Implemented a **service layer** for business logic
* Used **SQLAlchemy** ORM with **Alembic** migrations

### 3.2 Pricing Configuration

| Token Type          | Price (per 1000) | Notes             |
| ------------------- | ---------------- | ----------------- |
| Input Tokens        | $0.03            | Standard          |
| Cached Input Tokens | $0.01            | Cheaper           |
| Output Tokens       | $0.06            | Standard          |
| Reasoning Tokens    | $0.06            | Charged as output |

### 3.3 Stripe Mock Implementation

* Created complete **mock mode** for the project
* Simulated **webhook events**
* Maintained the complete **checkout flow**
* Implemented FREE → PRO subscription upgrade flow

### 3.4 Plan Limits

| Plan | API Calls    | AI Tokens       |
| ---- | ------------ | --------------- |
| FREE | 1,000/month  | 100,000/month   |
| PRO  | 10,000/month | 1,000,000/month |

### 3.5 Testing Strategy

* Wrote **11 tests** covering the major features
* Added **idempotency tests**
* Added **quota boundary tests**
* Added **token pricing tests**
* Added **webhook security tests**
* Added **webhook deduplication tests**
* Added an **integration workflow test**

---

## 4. Lessons Learned

### 4.1 Technical Lessons

1. **Always use proper UTF-8/ASCII encoding** for configuration and source files.
2. **Test early and often** to catch issues before they become difficult to debug.
3. **Mock external services** when they are unavailable or unsuitable for local development.
4. **Keep money as integers** and never use floating-point values for currency.
5. **Idempotency is critical** for billing systems; database-level unique constraints provide an important safety layer.

### 4.2 Architecture Lessons

1. The **Repository + Service + API** pattern makes testing and maintenance easier.
2. **Dependency injection** improves maintainability and testability.
3. **Docker Compose** simplifies local development and deployment.
4. **Alembic migrations** help keep the database schema synchronized with application models.

### 4.3 Development Lessons

1. **Read error messages carefully** because they often identify the source of the problem.
2. **Use AI as a tool, not a replacement** for understanding the code.
3. **Review generated code** and verify that it actually works.
4. **Document as you go** because it saves time at the end of the project.

---

## 5. Time Breakdown

| Activity               | Hours         |
| ---------------------- | ------------- |
| Project Setup & Docker | 4             |
| Database & Models      | 4             |
| API Development        | 6             |
| Stripe Integration     | 4             |
| Background Jobs        | 3             |
| Testing                | 4             |
| Documentation          | 3             |
| Debugging              | 6             |
| **Total**              | **~34 hours** |

---

## 6. Tools Used

| Tool               | Purpose                                  |
| ------------------ | ---------------------------------------- |
| Claude (Anthropic) | Code generation, debugging, and guidance |
| VS Code            | Code editor                              |
| Docker Desktop     | Containerization                         |
| Git/GitHub         | Version control                          |
| PostgreSQL         | Database                                 |
| Pytest             | Testing                                  |
| FastAPI            | Backend API framework                    |
| SQLAlchemy         | ORM                                      |
| Alembic            | Database migrations                      |

---

## 7. Honesty Statement

I used AI assistance for:

1. **Code generation** — approximately 60% of the code
2. **Debugging** — helped identify and fix errors
3. **Architecture guidance** — suggested patterns and best practices
4. **Documentation** — assisted with project documentation

I reviewed the generated code, fixed errors, tested the implementation, and verified that the required functionality works correctly. I understand the architecture and can explain the implementation and major code components of the project.

**Signed:** Zarsham Waleed
**Date:** August 31, 2026
