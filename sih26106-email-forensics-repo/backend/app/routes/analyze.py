"""
Phase 7 — /api/analyze endpoint
Owner: Member 4 (lead) + Member 1

Saves every analysis to the DB so campaigns (Phase 6b) and reports
(Phase 9) can reference results by ID.
"""

import json
import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Analysis, AuthResult
from app.ingestion.parser import parse_eml
from app.auth_check.verifier import run_auth_checks
from app.nlp.classify import classify_email
from app.origin.relay_trace import trace_origin
from app.origin.geoip_lookup import geolocate_ip
from app.origin.domain_intel import (
    check_abuseipdb, check_ipinfo_lite, domain_age_days, mx_hosting_mismatch,
)
from app.scoring.risk_score import compute_risk_score
from app.novelty.confidence import assess_confidence
from app.novelty.counterfactual import generate_counterfactuals
from app.novelty.homoglyph import analyze_domain_for_spoofing
from app.novelty.highlight import get_word_contributions, highlight_text

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/analyze")
async def analyze_email(
    file: UploadFile = File(...),
    db: Optional[Session] = Depends(get_db),
):
    """Analyze a .eml file and persist the results to the database.

    Returns the full analysis payload + an analysis_id that the frontend
    can use for campaign grouping and PDF report generation.
    """
    raw = await file.read()
    parsed = parse_eml(raw)
    sender_domain = parsed.from_address.split("@")[-1]

    # ── Auth verification ───────────────────────────────────────────────
    auth = run_auth_checks(raw, parsed.raw_authentication_results, sender_domain)

    # ── NLP classification ─────────────────────────────────────────────
    nlp = classify_email(parsed.subject, parsed.body, parsed.from_name, parsed.from_address)

    # ── Origin tracing ─────────────────────────────────────────────────
    origin = trace_origin(parsed.received_chain)

    # ── GeoIP + IP reputation + domain intel ───────────────────────────
    geo, abuse, ipinfo = {}, {}, {}
    if origin["origin_ip"]:
        geo = geolocate_ip(origin["origin_ip"])
        abuse = check_abuseipdb(origin["origin_ip"])
        ipinfo = check_ipinfo_lite(origin["origin_ip"])

    intel = {
        **abuse, **ipinfo,
        "domain_age_days": domain_age_days(sender_domain),
        "mx_mismatch": mx_hosting_mismatch(sender_domain),
    }

    # ── Scoring ────────────────────────────────────────────────────────
    score = compute_risk_score(auth.__dict__, nlp, origin, intel)

    # ── Novel Features ─────────────────────────────────────────────────
    # Feature 6: Confidence/Uncertainty Flagging
    confidence = assess_confidence(nlp["ml_phishing_probability"])
    
    # Feature 2: Counterfactual Risk Explanation
    counterfactuals = generate_counterfactuals(auth.__dict__, nlp, origin, intel)
    
    # Feature 5: Homoglyph/Lookalike-Domain Detector
    domain_spoof_check = analyze_domain_for_spoofing(sender_domain)
    
    # Feature 3: Highlighted-Text Explainability (with graceful fallback)
    word_contributions = []
    highlighted_body = parsed.body
    try:
        word_contributions = get_word_contributions(parsed.subject + " " + parsed.body)
        highlighted_body = highlight_text(parsed.body, word_contributions)
    except Exception as e:
        logger.warning(f"SHAP highlighting failed: {e}")

    # ── Persist to DB ──────────────────────────────────────────────────
    analysis_id = None
    if db is not None:
        try:
            analysis = Analysis(
                from_address=parsed.from_address,
                from_name=parsed.from_name,
                to_addresses=json.dumps(parsed.to_addresses),
                subject=parsed.subject,
                sender_domain=sender_domain,
                total_score=score["total_score"],
                origin_ip=origin.get("origin_ip"),
                origin_host_claimed=origin.get("origin_host_claimed"),
                trace_confidence=origin.get("trace_confidence", "low"),
                geo_country=geo.get("country"),
                geo_city=geo.get("city"),
                geo_latitude=geo.get("latitude"),
                geo_longitude=geo.get("longitude"),
                auth_json=json.dumps(auth.__dict__),
                nlp_json=json.dumps(nlp),
                origin_json=json.dumps(origin),
                intel_json=json.dumps(intel),
                breakdown_json=json.dumps(score["breakdown"]),
            )

            auth_result = AuthResult(
                analysis_id=None,  # will be set after flush
                spf_result=auth.spf_result,
                dkim_result=auth.dkim_result,
                dmarc_result=auth.dmarc_result,
                dkim_independently_verified=auth.dkim_independently_verified,
                sender_publishes_spf=auth.sender_publishes_spf,
                sender_publishes_dmarc=auth.sender_publishes_dmarc,
                dmarc_policy=auth.dmarc_policy,
            )
            analysis.auth_result = auth_result

            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            analysis_id = analysis.id
        except Exception as e:
            logger.error(f"Failed to persist analysis: {e}")
            db.rollback()

    return {
        "analysis_id": analysis_id,
        "parsed": parsed.__dict__,
        "auth": auth.__dict__,
        "nlp": nlp,
        "origin": {**origin, "geolocation": geo},
        "intel": intel,
        "risk_score": score,
        # Novel features
        "confidence": confidence,
        "counterfactuals": counterfactuals,
        "domain_spoof_check": domain_spoof_check,
        "word_contributions": word_contributions,
        "highlighted_body": highlighted_body,
    }
