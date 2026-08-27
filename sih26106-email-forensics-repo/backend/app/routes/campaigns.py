"""
Phase 6b/7 — /api/campaigns endpoint
Owner: Member 4

TODO (Member 4): once analyzed emails are persisted (SQLAlchemy models in
app/models.py + app/db.py), replace `_FAKE_STORE` below with a real query,
build the graph via app.scoring.correlation.build_campaign_graph, and
return get_campaigns(G). Left as an in-memory placeholder so the frontend
(Member 5) can build against a real response shape from day 1.
"""
from fastapi import APIRouter
from app.scoring.correlation import build_campaign_graph, get_campaigns

router = APIRouter()

# Placeholder in-memory store — swap for a real DB query.
_FAKE_STORE: list[dict] = []


@router.get("/api/campaigns")
async def list_campaigns():
    graph = build_campaign_graph(_FAKE_STORE)
    campaigns = get_campaigns(graph)
    return {"campaigns": campaigns, "total_analyzed": len(_FAKE_STORE)}
