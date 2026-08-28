"""
Phase 5a — Relay-chain origin tracing
Owner: Member 3

Key insight: Received headers closest to trusted infrastructure (your own
mail gateway, or a major provider like Gmail/Outlook) are trustworthy —
the attacker doesn't control that server. Headers further down the chain
CAN be forged by the attacker's own sending script. So: walk backward from
the trusted end, stop at the first hop whose connecting IP is public and
outside anything recognized as trusted infra — that's the most credible
origin IP. Everything before that point is a claim, not a fact.
"""
import re
import ipaddress

# Extend this list with your own org's mail gateway hostnames if deploying
# against a real inbox.
TRUSTED_INFRA_PATTERNS = [
    r"google\.com$", r"googlemail\.com$", r"outlook\.com$",
    r"protection\.outlook\.com$", r"amazonses\.com$", r"mail\.yahoo\.com$",
]

IP_PATTERN = re.compile(r"\[(\d{1,3}(?:\.\d{1,3}){3})\]")


def _extract_ip(field: str) -> str | None:
    m = IP_PATTERN.search(field or "")
    return m.group(1) if m else None


def _is_trusted_host(hostname: str) -> bool:
    return any(re.search(p, hostname or "") for p in TRUSTED_INFRA_PATTERNS)


def _is_public_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return not (addr.is_private or addr.is_loopback or addr.is_link_local)
    except ValueError:
        return False


def trace_origin(received_chain: list) -> dict:
    """received_chain must be ordered oldest(hop=1) -> newest, as produced
    by Phase 1's parser.py. We walk NEWEST -> OLDEST looking for the
    boundary between trusted and untrusted infrastructure."""
    chain_newest_first = list(reversed(received_chain))

    candidate_ip = None
    candidate_host = None
    boundary_hop = None
    unverified_claims = []

    for hop in chain_newest_first:
        by_host = hop.get("by", "")
        from_field = hop.get("from", "")
        ip = _extract_ip(from_field)

        if _is_trusted_host(by_host):
            if ip and _is_public_ip(ip):
                candidate_ip = ip
                candidate_host = from_field.split(" ")[0]
                boundary_hop = hop.get("hop")
                break
            continue
        else:
            if ip:
                unverified_claims.append({"host": from_field, "ip": ip})

    claims_before_boundary = [
        {"host": h.get("from", ""), "ip": _extract_ip(h.get("from", ""))}
        for h in received_chain
        if boundary_hop is None or h.get("hop", 0) < boundary_hop
    ]

    return {
        "origin_ip": candidate_ip,
        "origin_host_claimed": candidate_host,
        "trust_boundary_hop": boundary_hop,
        "unverified_self_reported_hops": claims_before_boundary,
        "trace_confidence": "high" if candidate_ip else "low",
    }
