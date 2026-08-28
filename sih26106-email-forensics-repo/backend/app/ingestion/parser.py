"""
Phase 1 — Email Ingestion & Parsing
Owner: Member 1
See IMPLEMENTATION.md Phase 1 for full context.
"""
import mailparser
from dataclasses import dataclass


@dataclass
class ParsedEmail:
    from_name: str
    from_address: str
    to_addresses: list
    subject: str
    date: str
    body: str
    raw_authentication_results: str | None
    received_chain: list       # ordered oldest -> newest
    attachments: list
    raw_headers: dict


def parse_eml(raw_bytes: bytes) -> ParsedEmail:
    mail = mailparser.parse_from_bytes(raw_bytes)

    from_name, from_address = (mail.from_[0] if mail.from_ else ("", ""))
    to_addresses = [addr for _, addr in mail.to] if mail.to else []

    return ParsedEmail(
        from_name=from_name,
        from_address=from_address,
        to_addresses=to_addresses,
        subject=mail.subject or "",
        date=str(mail.date) if mail.date else "",
        body=mail.body or "",
        # NOTE: mailparser strips the "Authentication-Results:" prefix from
        # the value — Phase 2's `authres` parser needs it added back.
        raw_authentication_results=mail.headers.get("Authentication-Results"),
        # mailparser numbers hops chronologically: hop=1 is the OLDEST
        # (earliest/bottommost in the raw file), hop=N is the NEWEST
        # (closest to final delivery). This ordering is exactly what
        # Phase 5's relay-walk algorithm needs.
        received_chain=sorted(mail.received, key=lambda h: h.get("hop", 0)),
        attachments=[a.get("filename") for a in mail.attachments],
        raw_headers=dict(mail.headers),
    )
