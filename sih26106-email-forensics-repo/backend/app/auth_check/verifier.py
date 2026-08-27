"""
Phase 2 — Authentication Verification (SPF/DKIM/DMARC)
Owner: Member 1

IMPORTANT: read IMPLEMENTATION.md Phase 2 before touching this file.
Short version: you cannot reliably re-run a full per-message SPF check
after the fact (that requires the live connecting IP, which only the
real receiving MTA had). This module instead:
  1. Parses the existing Authentication-Results header (primary signal —
     added by the real receiving server, e.g. Gmail/Outlook).
  2. Independently re-verifies the DKIM signature (real cryptographic
     check, network-path-independent).
  3. Checks the sender domain's published SPF/DMARC policy hygiene
     (does it even publish one, and how strict).
Do NOT add `pyspf` to requirements.txt — its `pydns` dependency is broken
on modern Python 3.
"""
from authres import AuthenticationResultsHeader
import dkim
import checkdmarc
from dataclasses import dataclass


@dataclass
class AuthResult:
    spf_result: str            # pass / fail / softfail / neutral / none / unknown
    dkim_result: str           # pass / fail / none / unknown
    dmarc_result: str          # pass / fail / none / unknown
    dkim_independently_verified: bool | None
    sender_publishes_spf: bool
    sender_publishes_dmarc: bool
    dmarc_policy: str | None   # none / quarantine / reject
    spf_dns_lookup_count: int | None


def parse_authentication_results(raw_header_value: str | None) -> dict:
    if not raw_header_value:
        return {"spf": "none", "dkim": "none", "dmarc": "none"}
    try:
        header = AuthenticationResultsHeader.parse(
            "Authentication-Results: " + raw_header_value
        )
    except Exception:
        return {"spf": "unknown", "dkim": "unknown", "dmarc": "unknown"}

    out = {"spf": "none", "dkim": "none", "dmarc": "none"}
    for r in header.results:
        method = getattr(r, "method", None)
        if method in out:
            out[method] = r.result
    return out


def independently_verify_dkim(raw_eml_bytes: bytes) -> bool | None:
    """Real cryptographic re-check — network-path-independent.
    Returns None if the message has no DKIM signature to check."""
    if b"DKIM-Signature:" not in raw_eml_bytes:
        return None
    try:
        return dkim.verify(raw_eml_bytes)
    except Exception:
        return False


def check_domain_auth_hygiene(sender_domain: str) -> dict:
    """Domain-policy hygiene (does it publish SPF/DMARC, how strict) —
    NOT a per-message pass/fail."""
    spf = checkdmarc.check_spf(sender_domain)
    dmarc = checkdmarc.check_dmarc(sender_domain)
    return {
        "publishes_spf": spf.get("valid", False),
        "spf_dns_lookups": spf.get("dns_lookups"),
        "publishes_dmarc": dmarc.get("valid", False),
        "dmarc_policy": (dmarc.get("tags", {}).get("p", {}).get("value")
                          if dmarc.get("valid") else None),
    }


def run_auth_checks(raw_eml_bytes: bytes, raw_ar_header: str | None,
                     sender_domain: str) -> AuthResult:
    ar = parse_authentication_results(raw_ar_header)
    hygiene = check_domain_auth_hygiene(sender_domain)
    return AuthResult(
        spf_result=ar["spf"],
        dkim_result=ar["dkim"],
        dmarc_result=ar["dmarc"],
        dkim_independently_verified=independently_verify_dkim(raw_eml_bytes),
        sender_publishes_spf=hygiene["publishes_spf"],
        sender_publishes_dmarc=hygiene["publishes_dmarc"],
        dmarc_policy=hygiene["dmarc_policy"],
        spf_dns_lookup_count=hygiene["spf_dns_lookups"],
    )
