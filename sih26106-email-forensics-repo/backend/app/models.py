"""
SQLAlchemy ORM models + Pydantic response schemas.

Owner: Member 4

- ORM models persist every analysis run so campaigns (Phase 6b) and
  PDF reports (Phase 9) can reference stored results by ID.
- Pydantic schemas match the /api/analyze response shape exactly so
  the frontend (Member 5) has a single source of truth.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.db import Base


# ─── SQLAlchemy ORM ─────────────────────────────────────────────────────

def _uuid():
    return str(uuid.uuid4())


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=_uuid)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    from_address = Column(String, index=True)
    from_name = Column(String, default="")
    to_addresses = Column(Text, default="[]")          # JSON-encoded list
    subject = Column(String, default="")
    sender_domain = Column(String, index=True)

    # Score
    total_score = Column(Integer, default=0)

    # Origin
    origin_ip = Column(String, index=True, nullable=True)
    origin_host_claimed = Column(String, nullable=True)
    trace_confidence = Column(String, default="low")

    # Geolocation
    geo_country = Column(String, nullable=True)
    geo_city = Column(String, nullable=True)
    geo_latitude = Column(Float, nullable=True)
    geo_longitude = Column(Float, nullable=True)

    # Full JSON blobs for rich detail
    auth_json = Column(Text, default="{}")
    nlp_json = Column(Text, default="{}")
    origin_json = Column(Text, default="{}")
    intel_json = Column(Text, default="{}")
    breakdown_json = Column(Text, default="{}")

    # Relationships
    auth_result = relationship("AuthResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")


class AuthResult(Base):
    __tablename__ = "auth_results"

    id = Column(String, primary_key=True, default=_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), unique=True, nullable=False)

    spf_result = Column(String, default="none")
    dkim_result = Column(String, default="none")
    dmarc_result = Column(String, default="none")
    dkim_independently_verified = Column(Boolean, nullable=True)
    sender_publishes_spf = Column(Boolean, default=False)
    sender_publishes_dmarc = Column(Boolean, default=False)
    dmarc_policy = Column(String, nullable=True)

    analysis = relationship("Analysis", back_populates="auth_result")


# ─── Pydantic Schemas (for API responses) ──────────────────────────────

class RiskScoreResponse(BaseModel):
    total_score: int
    breakdown: dict

class AuthResponse(BaseModel):
    spf_result: str = "none"
    dkim_result: str = "none"
    dmarc_result: str = "none"
    dkim_independently_verified: bool | None = None
    sender_publishes_spf: bool = False
    sender_publishes_dmarc: bool = False
    dmarc_policy: str | None = None

class NLPResponse(BaseModel):
    ml_phishing_probability: float = 0.0
    urgency_score: float = 0.0
    impersonation_score: float = 0.0
    display_name_mismatch: bool = False

class GeoLocationResponse(BaseModel):
    country: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    accuracy_radius_km: float | None = None

class AnalyzeResponse(BaseModel):
    analysis_id: str
    risk_score: RiskScoreResponse
    auth: AuthResponse
    nlp: NLPResponse
    origin: dict
    intel: dict
    parsed: dict
