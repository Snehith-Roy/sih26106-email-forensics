"""
Phase 4 — Rule-based feature boosts (urgency, impersonation, display-name
mismatch). Cheap, explainable, and maps directly to the PS's own language.
Owner: Member 2
"""
import re

URGENCY_PATTERNS = [
    r"\burgent\b", r"\bimmediately\b", r"\bwithin 24 hours\b",
    r"\baccount (suspended|locked|compromised)\b", r"\bverify your account\b",
    r"\bact now\b", r"\bfinal notice\b", r"\bclick here\b",
]
IMPERSONATION_PATTERNS = [
    r"\bsecurity team\b", r"\bIT (support|helpdesk)\b",
    r"\baccounts? (payable|department)\b", r"\bceo\b", r"\bwire transfer\b",
]


def urgency_score(text: str) -> float:
    text = text.lower()
    hits = sum(1 for p in URGENCY_PATTERNS if re.search(p, text))
    return min(hits / 3, 1.0)   # normalize 0-1


def impersonation_score(text: str) -> float:
    text = text.lower()
    hits = sum(1 for p in IMPERSONATION_PATTERNS if re.search(p, text))
    return min(hits / 2, 1.0)


def display_name_domain_mismatch(from_name: str, from_address: str) -> bool:
    """Classic BEC signal: display name claims a known brand/bank but the
    actual sending domain doesn't match it at all."""
    known_brands = ["paypal", "microsoft", "google", "bank", "amazon", "apple"]
    name_lower = from_name.lower()
    domain = from_address.split("@")[-1].lower() if "@" in from_address else ""
    for brand in known_brands:
        if brand in name_lower and brand not in domain:
            return True
    return False
