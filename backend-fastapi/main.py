"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import accounts, calculator

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="CatobiGato API — AI-native learning platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(accounts.router, prefix=settings.api_prefix)
app.include_router(calculator.router, prefix=settings.api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "catobigato-fastapi"}


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
    }