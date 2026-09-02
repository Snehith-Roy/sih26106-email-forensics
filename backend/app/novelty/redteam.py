"""
Feature 4 — Adversarial self-red-teaming.

Tests whether the classifier can be trivially evaded, and reports a
robustness score per perturbation type.

Run this as a standalone report generator, not on every live request —
it's for your demo/report, not production latency.
"""

import re
import logging
from app.nlp.heuristics import URGENCY_PATTERNS
from app.nlp.classify import classify_email

logger = logging.getLogger(__name__)

ZERO_WIDTH = "\u200b"

# Homoglyph map — Latin -> lookalike substitutions
HOMOGLYPH_MAP = {
    "a": "а",  # Cyrillic а
    "e": "е",  # Cyrillic е
    "o": "о",  # Cyrillic о
    "c": "с",  # Cyrillic с
    "p": "р",  # Cyrillic р
    "i": "і",  # Ukrainian і
}

# Synonym substitutions — replace flagged urgency words with less-common synonyms
SYNONYM_MAP = {
    "urgent": "pressing",
    "immediately": "right away",
    "verify": "confirm",
    "suspended": "disabled",
    "click": "tap",
    "account": "profile",
    "act now": "respond promptly",
    "final notice": "last reminder",
}


def perturb_zero_width(text: str) -> str:
    """Insert zero-width spaces inside urgency trigger words."""
    for pattern in URGENCY_PATTERNS:
        word = pattern.strip(r"\b")
        if word.isalpha() and word in text.lower():
            mid = len(word) // 2
            injected = word[:mid] + ZERO_WIDTH + word[mid:]
            text = re.sub(re.escape(word), injected, text, flags=re.IGNORECASE)
    return text


def perturb_homoglyph(text: str) -> str:
    """Swap 1-2 Latin letters for lookalikes inside trigger words only."""
    words = text.split()
    out = []
    for w in words:
        lw = w.lower()
        if any(t in lw for t in ["urgent", "verify", "suspend", "account"]):
            chars = list(w)
            replaced = 0
            for i, ch in enumerate(chars):
                if ch.lower() in HOMOGLYPH_MAP and replaced < 2:
                    chars[i] = HOMOGLYPH_MAP[ch.lower()]
                    replaced += 1
            w = "".join(chars)
        out.append(w)
    return " ".join(out)


def perturb_synonym(text: str) -> str:
    """Replace urgency words with synonyms the model wasn't trained on."""
    for original, synonym in SYNONYM_MAP.items():
        text = re.sub(re.escape(original), synonym, text, flags=re.IGNORECASE)
    return text


def perturb_html_comment(text: str) -> str:
    """Split words with invisible HTML comments (only meaningful for raw HTML)."""
    for pattern in URGENCY_PATTERNS:
        word = pattern.strip(r"\b")
        if word.isalpha() and word in text.lower():
            mid = len(word) // 2
            injected = word[:mid] + "<!-- -->" + word[mid:]
            text = re.sub(re.escape(word), injected, text, flags=re.IGNORECASE)
    return text


PERTURBATIONS = {
    "zero_width_injection": perturb_zero_width,
    "homoglyph_substitution": perturb_homoglyph,
    "synonym_substitution": perturb_synonym,
    "html_comment_injection": perturb_html_comment,
}


def run_robustness_report(
    known_phishing_emails: list[dict],
    detection_threshold: float = 0.5,
) -> dict:
    """
    Run adversarial robustness report on known phishing emails.
    
    Args:
        known_phishing_emails: list of dicts with 'subject', 'body',
            'from_name', 'from_address'
        detection_threshold: ML probability threshold for "detected"
    
    Returns:
        dict with per-perturbation robustness stats
    """
    if not known_phishing_emails:
        return {"error": "No emails provided for robustness testing"}

    results = {}
    for name, perturb_fn in PERTURBATIONS.items():
        still_caught = 0
        details = []
        
        for email in known_phishing_emails:
            perturbed_body = perturb_fn(email["body"])
            try:
                outcome = classify_email(
                    email["subject"], perturbed_body,
                    email["from_name"], email["from_address"],
                )
                detected = outcome["ml_phishing_probability"] >= detection_threshold
                if detected:
                    still_caught += 1
                details.append({
                    "subject": email["subject"][:50],
                    "original_prob": None,  # would need original classification
                    "perturbed_prob": outcome["ml_phishing_probability"],
                    "detected": detected,
                })
            except Exception as e:
                logger.error(f"Classification failed for {name}: {e}")
                details.append({
                    "subject": email["subject"][:50],
                    "error": str(e),
                })

        total = len(known_phishing_emails)
        results[name] = {
            "still_caught": still_caught,
            "total": total,
            "robustness_pct": round(still_caught / total * 100, 1) if total > 0 else 0,
            "details": details,
        }

    return results
