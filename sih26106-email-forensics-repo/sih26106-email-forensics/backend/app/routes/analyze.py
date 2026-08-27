"""
Phase 7 — /api/analyze endpoint
Owner: Member 4 (lead) + Member 1
"""
from fastapi import APIRouter, UploadFile, File

from app.ingestion.parser import parse_eml
from app.auth_check.verifier import run_auth_checks
from app.nlp.classify import classify_email
from app.origin.relay_trace import trace_origin
from app.origin.geoip_lookup import geolocate_ip
from app.origin.domain_intel import (
    check_abuseipdb, check_ipinfo_lite, domain_age_days, mx_hosting_mismatch,
)
from app.scoring.risk_score import compute_risk_score

router = APIRouter()


@router.post("/api/analyze")
async def analyze_email(file: UploadFile = File(...)):
    raw = await file.read()
    parsed = parse_eml(raw)
    sender_domain = parsed.from_address.split("@")[-1]

    auth = run_auth_checks(raw, parsed.raw_authentication_results, sender_domain)
    nlp = classify_email(parsed.subject, parsed.body, parsed.from_name, parsed.from_address)
    origin = trace_origin(parsed.received_chain)

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

    score = compute_risk_score(auth.__dict__, nlp, origin, intel)

    return {
        "parsed": parsed.__dict__,
        "auth": auth.__dict__,
        "nlp": nlp,
        "origin": {**origin, "geolocation": geo},
        "intel": intel,
        "risk_score": score,
    }
