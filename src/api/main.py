"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.routes import chat, documents, processing, review
from src.storage.database import close_pool, get_pool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting PraxisIQ API...")
    await get_pool()
    logger.info("Database pool initialized")
    yield
    logger.info("Shutting down PraxisIQ API...")
    await close_pool()


app = FastAPI(
    title="PraxisIQ",
    description="Intelligent Document Processing POC — Portfolio Demo",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://idp-poc.dev.willianpinho.com",
        "http://localhost:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(documents.router)
app.include_router(processing.router)
app.include_router(chat.router)
app.include_router(review.router)


@app.get("/health")
@limiter.exempt
async def health_check(request: Request):
    return {"status": "healthy", "service": "praxisiq"}
