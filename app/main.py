from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import health

app = FastAPI(
    title="Usage Metering & Billing Engine",
    description="SaaS usage metering, quota enforcement, and billing system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.API_PREFIX, tags=["health"])

@app.get("/")
async def root():
    return {
        "message": "Usage Metering & Billing Engine",
        "version": "1.0.0",
        "docs": "/docs"
    }
