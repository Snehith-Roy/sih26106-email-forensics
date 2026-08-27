from app.ingestion.parser import parse_eml
from app.origin.relay_trace import trace_origin


def _load_fixture(name: str) -> bytes:
    with open(f"tests/fixtures/{name}", "rb") as f:
        return f.read()


def test_parses_basic_fields():
    raw = _load_fixture("spoofed_bank.eml")
    result = parse_eml(raw)
    assert result.from_address == "noreply@bank-corp.com"
    assert "victim@example.com" in result.to_addresses
    assert len(result.received_chain) == 3
    assert result.received_chain[0]["hop"] == 1


def test_relay_trace_finds_untrusted_origin():
    raw = _load_fixture("spoofed_bank.eml")
    parsed = parse_eml(raw)
    origin = trace_origin(parsed.received_chain)
    # mx.google.com is trusted infra; it recorded the connecting IP as
    # 185.220.101.5 — that's the credible origin, NOT the bank-corp.com
    # internal relay claimed further down the (forgeable) chain.
    assert origin["origin_ip"] == "185.220.101.5"
    assert origin["trace_confidence"] == "high"
    assert len(origin["unverified_self_reported_hops"]) == 1


def test_legit_email_parses_cleanly():
    raw = _load_fixture("legit_newsletter.eml")
    result = parse_eml(raw)
    assert result.from_address == "newsletter@newsco.com"
    assert "spf=pass" in result.raw_authentication_results
