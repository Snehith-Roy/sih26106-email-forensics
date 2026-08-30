"""QA checks for the Phase 9 downloadable forensic report."""

from app.reports.pdf_report import generate_forensic_report


def test_forensic_report_is_a_pdf():
    analysis = {
        "risk_score": {
            "total_score": 82,
            "breakdown": {"authentication": 35, "content": 30, "origin": 17},
        },
        "auth": {
            "spf_result": "fail",
            "dkim_result": "fail",
            "dkim_independently_verified": False,
            "dmarc_result": "fail",
        },
        "origin": {
            "origin_ip": "185.220.101.5",
            "geolocation": {"city": "Berlin", "country": "Germany"},
            "trace_confidence": "high",
            "unverified_self_reported_hops": [{"host": "claimed.bank-corp.com"}],
        },
    }

    report = generate_forensic_report(analysis)

    assert report.startswith(b"%PDF")
    assert len(report) > 1_000
