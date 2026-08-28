"""
FastAPI app entrypoint.
Owner: Member 4

Run locally with:  uvicorn app.main:app --reload
Swagger docs at:    http://localhost:8000/docs
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routes import analyze, campaigns, reports

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup."""
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Database ready.")
    yield


app = FastAPI(
    title="SIH26106 Email Forensics API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(campaigns.router)
app.include_router(reports.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
