"""
Phase 9 — /api/reports/generate endpoint
Owner: Member 6
"""
from fastapi import APIRouter
from fastapi.responses import Response

from app.reports.pdf_report import generate_forensic_report

router = APIRouter()


@router.post("/api/reports/generate")
async def generate_report(analysis: dict):
    pdf_bytes = generate_forensic_report(analysis)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=forensic_report.pdf"},
    )
