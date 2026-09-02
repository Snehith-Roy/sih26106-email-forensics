"""
SQLAlchemy models for email analysis persistence.

Owner: Member 4
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    from_address = Column(String(255))
    from_name = Column(String(255))
    to_addresses = Column(Text)  # JSON string
    subject = Column(Text)
    sender_domain = Column(String(255))
    total_score = Column(Float)
    origin_ip = Column(String(45))
    origin_host_claimed = Column(String(255))
    trace_confidence = Column(String(20))
    geo_country = Column(String(100))
    geo_city = Column(String(100))
    geo_latitude = Column(Float)
    geo_longitude = Column(Float)
    auth_json = Column(Text)
    nlp_json = Column(Text)
    origin_json = Column(Text)
    intel_json = Column(Text)
    breakdown_json = Column(Text)

    auth_result = relationship("AuthResult", back_populates="analysis", uselist=False)


class AuthResult(Base):
    __tablename__ = "auth_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    spf_result = Column(String(20))
    dkim_result = Column(String(20))
    dmarc_result = Column(String(20))
    dkim_independently_verified = Column(Boolean)
    sender_publishes_spf = Column(Boolean)
    sender_publishes_dmarc = Column(Boolean)
    dmarc_policy = Column(String(20))

    analysis = relationship("Analysis", back_populates="auth_result")
