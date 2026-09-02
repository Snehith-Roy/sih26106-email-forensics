"""
FastAPI app entrypoint.
Owner: Member 4

Run locally with:  uvicorn app.main:app --reload
Swagger docs at:    http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine, Base
from app.routes import analyze, campaigns, reports

app = FastAPI(title="SIH26106 Email Forensics API")


@app.on_event("startup")
def _create_tables():
    Base.metadata.create_all(bind=engine)

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
