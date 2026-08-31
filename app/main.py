from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import health, database, tenants, plans, subscriptions, usage, quota, cost, usage_summary, stripe, webhooks, background_jobs

app = FastAPI(
    title="Usage Metering & Billing Engine",
    description="SaaS usage metering, quota enforcement, and billing system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.API_PREFIX, tags=["health"])
app.include_router(database.router, prefix=settings.API_PREFIX, tags=["database"])
app.include_router(tenants.router, prefix=settings.API_PREFIX, tags=["tenants"])
app.include_router(plans.router, prefix=settings.API_PREFIX, tags=["plans"])
app.include_router(subscriptions.router, prefix=settings.API_PREFIX, tags=["subscriptions"])
app.include_router(usage.router, prefix=settings.API_PREFIX, tags=["usage"])
app.include_router(quota.router, prefix=settings.API_PREFIX, tags=["quota"])
app.include_router(cost.router, prefix=settings.API_PREFIX, tags=["cost"])
app.include_router(usage_summary.router, prefix=settings.API_PREFIX, tags=["usage_summary"])
app.include_router(stripe.router, prefix=settings.API_PREFIX, tags=["stripe"])
app.include_router(webhooks.router, prefix=settings.API_PREFIX, tags=["webhooks"])
app.include_router(background_jobs.router, prefix=settings.API_PREFIX, tags=["background_jobs"])

@app.get("/")
async def root():
    return {
        "message": "Usage Metering & Billing Engine",
        "version": "1.0.0",
        "docs": "/docs"
    }
