"""
Feature 2 — Counterfactual Risk Explanation.

Answers: "what single change would most reduce this email's risk score?"
Reuses the existing compute_risk_score() function unchanged — just
calls it multiple times with one signal flipped each time.
"""

import logging
from app.scoring.risk_score import compute_risk_score

logger = logging.getLogger(__name__)


def generate_counterfactuals(auth: dict, nlp: dict, origin: dict, intel: dict) -> list[dict]:
    """
    Generate counterfactual explanations — "what if" scenarios.
    
    Returns a ranked list of scenarios sorted by biggest score reduction first.
    Each entry shows what change would reduce the score and by how much.
    """
    try:
        baseline = compute_risk_score(auth, nlp, origin, intel)
        baseline_score = baseline["total_score"]
    except Exception as e:
        logger.error(f"Failed to compute baseline score: {e}")
        return []

    scenarios = []

    # Scenario 1: SPF/DKIM/DMARC all pass instead of failing
    if any(r in ("fail", "softfail") for r in [auth.get("spf_result"), auth.get("dkim_result"), auth.get("dmarc_result")]):
        modified_auth = {**auth, "spf_result": "pass", "dkim_result": "pass", "dmarc_result": "pass"}
        try:
            new_score = compute_risk_score(modified_auth, nlp, origin, intel)["total_score"]
            scenarios.append({
                "change": "If SPF, DKIM, and DMARC had all passed",
                "new_score": new_score,
                "delta": new_score - baseline_score,
            })
        except Exception:
            pass

    # Scenario 2: ML content score was benign (0.05 instead of actual)
    if nlp.get("ml_phishing_probability", 0) > 0.3:
        modified_nlp = {**nlp, "ml_phishing_probability": 0.05}
        try:
            new_score = compute_risk_score(auth, modified_nlp, origin, intel)["total_score"]
            scenarios.append({
                "change": "If the email content had not matched phishing language patterns",
                "new_score": new_score,
                "delta": new_score - baseline_score,
            })
        except Exception:
            pass

    # Scenario 3: domain was NOT newly registered
    domain_age = intel.get("domain_age_days")
    if domain_age is not None and domain_age < 90:
        modified_intel = {**intel, "domain_age_days": 3650}
        try:
            new_score = compute_risk_score(auth, nlp, origin, modified_intel)["total_score"]
            scenarios.append({
                "change": "If the sending domain were an established domain (10+ years old)",
                "new_score": new_score,
                "delta": new_score - baseline_score,
            })
        except Exception:
            pass

    # Scenario 4: origin IP had a clean reputation
    abuse_score = intel.get("abuse_confidence_score", 0)
    if abuse_score and abuse_score > 0:
        modified_intel = {**intel, "abuse_confidence_score": 0}
        try:
            new_score = compute_risk_score(auth, nlp, origin, modified_intel)["total_score"]
            scenarios.append({
                "change": "If the origin IP had no abuse reports",
                "new_score": new_score,
                "delta": new_score - baseline_score,
            })
        except Exception:
            pass

    # Scenario 5: no display-name/domain mismatch
    if nlp.get("display_name_mismatch"):
        modified_nlp = {**nlp, "display_name_mismatch": False}
        try:
            new_score = compute_risk_score(auth, modified_nlp, origin, intel)["total_score"]
            scenarios.append({
                "change": "If the sender's display name matched the actual sending domain",
                "new_score": new_score,
                "delta": new_score - baseline_score,
            })
        except Exception:
            pass

    # Sort by delta (most negative = biggest risk driver first)
    scenarios.sort(key=lambda s: s["delta"])
    
    # Add baseline for reference
    return {
        "baseline_score": baseline_score,
        "scenarios": scenarios,
    }
