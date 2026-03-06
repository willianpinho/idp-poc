"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import chat, documents, processing, review
from src.storage.database import close_pool, get_pool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


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
    description="Intelligent Document Processing POC",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
async def health_check():
    return {"status": "healthy", "service": "praxisiq"}
