"""
Phase 5c — IP reputation + domain intel
Owner: Member 3

Requires ABUSEIPDB_API_KEY and IPINFO_TOKEN env vars (see .env.example
and IMPLEMENTATION.md §13 for free-tier signup links).
"""
import os
from datetime import datetime, timezone

import dns.resolver
import requests
import whois

ABUSEIPDB_KEY = os.environ.get("ABUSEIPDB_API_KEY", "")
IPINFO_TOKEN = os.environ.get("IPINFO_TOKEN", "")


def check_abuseipdb(ip: str) -> dict:
    if not ABUSEIPDB_KEY:
        return {
            "abuse_confidence_score": 0,
            "is_tor": False,
            "total_reports": 0,
            "isp": "Mock ISP",
            "usage_type": "Mock Usage",
        }
        
    try:
        resp = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            params={"ipAddress": ip, "maxAgeInDays": 90},
            headers={"Key": ABUSEIPDB_KEY, "Accept": "application/json"},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
    except Exception as e:
        data = {}
        
    return {
        "abuse_confidence_score": data.get("abuseConfidenceScore"),
        "is_tor": data.get("isTor"),
        "total_reports": data.get("totalReports"),
        "isp": data.get("isp"),
        "usage_type": data.get("usageType"),   # e.g. "Data Center/Web Hosting/Transit"
    }


def check_ipinfo_lite(ip: str) -> dict:
    if not IPINFO_TOKEN:
        return {"asn": "AS0000", "as_name": "Mock AS", "country": "US"}
        
    try:
        # Free "Lite" tier: unlimited requests, country + ASN only.
        resp = requests.get(
            f"https://api.ipinfo.io/lite/{ip}", params={"token": IPINFO_TOKEN}, timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        data = {}
        
    return {"asn": data.get("asn"), "as_name": data.get("as_name"),
            "country": data.get("country")}


def domain_age_days(domain: str) -> int | None:
    try:
        w = whois.whois(domain)
        created = w.creation_date
        if isinstance(created, list):
            created = created[0]
        if created is None:
            return None
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - created).days
    except Exception:
        return None


def mx_hosting_mismatch(domain: str) -> bool:
    """Heuristic: does the domain's MX record point somewhere completely
    unrelated to the domain itself (common in freshly-stood-up phishing
    infra)? Simplified check — good enough for a hackathon MVP."""
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        mx_hosts = [str(r.exchange).rstrip(".") for r in mx_records]
        return not any(domain.split(".")[-2] in h for h in mx_hosts)
    except Exception:
        return False
