"""
Phase 6b/7 — /api/campaigns endpoint
Owner: Member 4

Now queries the real DB instead of _FAKE_STORE.
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
    """Return all detected campaigns from persisted analysis results."""
    if db is None:
        return {"campaigns": [], "total_analyzed": 0, "message": "No database connected"}

    rows = db.query(Analysis).all()

    emails = [
        {
            "email_id": row.id,
            "origin_ip": row.origin_ip,
            "sender_domain": row.sender_domain,
            "reply_to": None,  # could extract from intel_json if needed
        }
        for row in rows
    ]

    graph = build_campaign_graph(emails)
    campaigns = get_campaigns(graph)
    return {"campaigns": campaigns, "total_analyzed": len(emails)}
