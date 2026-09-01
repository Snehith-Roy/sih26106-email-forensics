"""
Feature 6 — Confidence / Uncertainty Flagging.

Flags emails where the ML model is uncertain (probability near 0.5)
as "needs human review" instead of giving a false-confident verdict.
"""

UNCERTAINTY_BAND = (0.35, 0.65)  # tune against your validation set


def assess_confidence(ml_phishing_probability: float) -> dict:
    """
    Assess confidence level of the ML prediction.
    
    Returns:
        dict with keys:
            - verdict: "phishing", "legitimate", or "uncertain"
            - confidence_label: "high" or "low"
            - needs_human_review: bool
            - distance_from_boundary: float (how far from 0.5)
    """
    low, high = UNCERTAINTY_BAND
    in_band = low <= ml_phishing_probability <= high

    if ml_phishing_probability >= high:
        verdict, confidence_label = "phishing", "high"
    elif ml_phishing_probability <= low:
        verdict, confidence_label = "legitimate", "high"
    else:
        verdict, confidence_label = "uncertain", "low"

    return {
        "verdict": verdict,
        "confidence_label": confidence_label,
        "needs_human_review": in_band,
        "distance_from_boundary": round(abs(ml_phishing_probability - 0.5), 3),
    }
