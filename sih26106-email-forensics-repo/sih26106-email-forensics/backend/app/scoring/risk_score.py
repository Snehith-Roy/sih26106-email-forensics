"""
Phase 6a — Weighted, explainable risk score
Owner: Member 4

Every weight lives in one dict so it's tunable and explainable in a judge
Q&A — you should be able to say why a given email scored 82/100, not just
report the number.
"""

WEIGHTS = {
    "auth_fail": 20,             # SPF or DKIM or DMARC = fail
    "auth_missing": 8,           # no Authentication-Results at all
    "weak_dmarc_policy": 6,      # domain publishes DMARC but p=none
    "no_spf_dmarc_published": 6, # domain publishes neither
    "ml_phishing_probability": 30,   # scaled 0-1 -> 0-30
    "urgency_language": 6,
    "impersonation_language": 6,
    "display_name_mismatch": 8,
    "newly_registered_domain": 8,    # domain age < 90 days
    "abuse_confidence": 10,          # scaled 0-100 -> 0-10
    "hosting_type_flag": 6,          # datacenter/VPN/proxy rather than residential/ISP
    "mx_mismatch": 6,
}
# NOTE: max possible sum > 100 by design (signals overlap in real attacks);
# final score is capped at 100.


def compute_risk_score(auth: dict, nlp: dict, origin: dict, intel: dict) -> dict:
    breakdown = {}

    if "fail" in (auth["spf_result"], auth["dkim_result"], auth["dmarc_result"]):
        breakdown["auth_fail"] = WEIGHTS["auth_fail"]
    if auth["spf_result"] == auth["dkim_result"] == "none":
        breakdown["auth_missing"] = WEIGHTS["auth_missing"]
    if auth["dmarc_policy"] == "none":
        breakdown["weak_dmarc_policy"] = WEIGHTS["weak_dmarc_policy"]
    if not auth["sender_publishes_spf"] and not auth["sender_publishes_dmarc"]:
        breakdown["no_spf_dmarc_published"] = WEIGHTS["no_spf_dmarc_published"]

    breakdown["ml_phishing_probability"] = round(
        nlp["ml_phishing_probability"] * WEIGHTS["ml_phishing_probability"], 1
    )
    if nlp["urgency_score"] > 0.3:
        breakdown["urgency_language"] = WEIGHTS["urgency_language"]
    if nlp["impersonation_score"] > 0.3:
        breakdown["impersonation_language"] = WEIGHTS["impersonation_language"]
    if nlp["display_name_mismatch"]:
        breakdown["display_name_mismatch"] = WEIGHTS["display_name_mismatch"]

    if intel.get("domain_age_days") is not None and intel["domain_age_days"] < 90:
        breakdown["newly_registered_domain"] = WEIGHTS["newly_registered_domain"]
    if intel.get("abuse_confidence_score"):
        breakdown["abuse_confidence"] = round(
            intel["abuse_confidence_score"] / 100 * WEIGHTS["abuse_confidence"], 1
        )
    if intel.get("usage_type") and "hosting" in intel["usage_type"].lower():
        breakdown["hosting_type_flag"] = WEIGHTS["hosting_type_flag"]
    if intel.get("mx_mismatch"):
        breakdown["mx_mismatch"] = WEIGHTS["mx_mismatch"]

    total = min(sum(breakdown.values()), 100)
    return {"total_score": round(total), "breakdown": breakdown}
