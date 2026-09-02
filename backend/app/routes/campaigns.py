"""
Phase 6b/7 — /api/campaigns endpoint
Owner: Member 4

Queries persisted analyses from the DB and builds a campaign correlation
graph via scoring/correlation.py.
"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Analysis
from app.scoring.correlation import build_campaign_graph, get_campaigns

router = APIRouter()


@router.get("/api/campaigns")
async def list_campaigns(db: Optional[Session] = Depends(get_db)):
    if db is None:
        return {"campaigns": [], "total_analyzed": 0}

    rows = db.query(Analysis).all()
    analyzed_emails = [
        {
            "email_id": str(r.id),
            "origin_ip": r.origin_ip,
            "sender_domain": r.sender_domain,
            "reply_to": r.from_address,
        }
        for r in rows
    ]
    graph = build_campaign_graph(analyzed_emails)
    campaigns = get_campaigns(graph)
    return {"campaigns": campaigns, "total_analyzed": len(analyzed_emails)}
