"""
Feature 5 — Homoglyph / Lookalike-Domain Detector.

Detects IDN homograph attacks (Cyrillic 'а' vs Latin 'a') and
typosquatting (paypa1.com, micros0ft.com).

Requires: pip install confusable-homoglyphs rapidfuzz
"""

try:
    from confusable_homoglyphs import confusables
    HAS_HOMOGLYPHS = True
except ImportError:
    HAS_HOMOGLYPHS = False

try:
    from rapidfuzz import distance
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

# Commonly impersonated brands — extend with your org's domain
WATCHED_BRANDS = [
    "paypal.com", "microsoft.com", "google.com", "amazon.com",
    "apple.com", "bank-corp.com", "netflix.com", "facebook.com",
    "instagram.com", "twitter.com", "linkedin.com", "github.com",
]


def check_homoglyph_attack(domain: str) -> dict:
    """
    Check if domain mixes Unicode scripts (homograph spoofing attempt).
    
    Returns:
        dict with keys:
            - is_homoglyph_attack: bool
            - confusable_characters: list of suspicious characters
    """
    if not HAS_HOMOGLYPHS:
        return {"is_homoglyph_attack": False, "confusable_characters": []}
    
    try:
        is_dangerous = confusables.is_dangerous(domain)
        detail = confusables.is_confusable(domain, greedy=True) if is_dangerous else None
        return {
            "is_homoglyph_attack": bool(is_dangerous),
            "confusable_characters": (
                [d["character"] for d in detail] if detail else []
            ),
        }
    except Exception:
        return {"is_homoglyph_attack": False, "confusable_characters": []}


def check_typosquat(domain: str, threshold: int = 2) -> dict:
    """
    Check if domain is close to a watched brand (Levenshtein distance).
    
    Returns:
        dict with keys:
            - is_typosquat_suspected: bool
            - closest_watched_brand: str or None
            - edit_distance: int or None
    """
    if not HAS_RAPIDFUZZ:
        return {"is_typosquat_suspected": False, "closest_watched_brand": None, "edit_distance": None}
    
    domain_clean = domain.lower().split("@")[-1]
    closest = None
    closest_distance = None
    
    for brand in WATCHED_BRANDS:
        d = distance.Levenshtein.distance(domain_clean, brand)
        if closest_distance is None or d < closest_distance:
            closest_distance = d
            closest = brand

    is_suspicious = (
        closest_distance is not None
        and 0 < closest_distance <= threshold
        and domain_clean != closest
    )
    
    return {
        "is_typosquat_suspected": is_suspicious,
        "closest_watched_brand": closest if is_suspicious else None,
        "edit_distance": closest_distance if is_suspicious else None,
    }


def analyze_domain_for_spoofing(domain: str) -> dict:
    """
    Combined analysis: check for homoglyph attacks and typosquatting.
    
    Returns:
        dict with all homoglyph and typosquat fields
    """
    homoglyph_result = check_homoglyph_attack(domain)
    typosquat_result = check_typosquat(domain)
    return {**homoglyph_result, **typosquat_result}
