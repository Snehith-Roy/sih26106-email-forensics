"""
Unit tests for Phase 6a — risk_score.py
Owner: Member 4

Tests the scoring engine with hand-crafted input dicts (no external deps).
"""

import pytest
from app.scoring.risk_score import compute_risk_score, WEIGHTS


# ---------------------------------------------------------------------------
# Helper factories — build minimal valid dicts for each input category
# ---------------------------------------------------------------------------

def _base_auth(**overrides):
    return {
        "spf_result": "pass",
        "dkim_result": "pass",
        "dmarc_result": "pass",
        "dkim_independently_verified": True,
        "sender_publishes_spf": True,
        "sender_publishes_dmarc": True,
        "dmarc_policy": "reject",
        "spf_dns_lookup_count": 3,
        **overrides,
    }

def _base_nlp(**overrides):
    return {
        "ml_phishing_probability": 0.0,
        "urgency_score": 0.0,
        "impersonation_score": 0.0,
        "display_name_mismatch": False,
        **overrides,
    }

def _base_origin(**overrides):
    return {
        "origin_ip": "203.0.113.1",
        "origin_host_claimed": "mail.example.com",
        "trust_boundary_hop": 2,
        "unverified_self_reported_hops": [],
        "trace_confidence": "high",
        **overrides,
    }

def _base_intel(**overrides):
    return {
        "abuse_confidence_score": 0,
        "is_tor": False,
        "total_reports": 0,
        "isp": "Comcast",
        "usage_type": "ISP",
        "asn": "AS7922",
        "as_name": "Comcast",
        "country": "US",
        "domain_age_days": 3650,
        "mx_mismatch": False,
        **overrides,
    }


# ---------------------------------------------------------------------------
# Auth signal tests
# ---------------------------------------------------------------------------

class TestAuthSignals:
    def test_all_pass_gives_zero_auth_points(self):
        result = compute_risk_score(_base_auth(), _base_nlp(), _base_origin(), _base_intel())
        assert "auth_fail" not in result["breakdown"]
        assert "auth_missing" not in result["breakdown"]
        assert "weak_dmarc_policy" not in result["breakdown"]
        assert "no_spf_dmarc_published" not in result["breakdown"]

    def test_spf_fail_triggers_auth_fail(self):
        result = compute_risk_score(
            _base_auth(spf_result="fail"), _base_nlp(), _base_origin(), _base_intel()
        )
        assert result["breakdown"]["auth_fail"] == WEIGHTS["auth_fail"]

    def test_dkim_fail_triggers_auth_fail(self):
        result = compute_risk_score(
            _base_auth(dkim_result="fail"), _base_nlp(), _base_origin(), _base_intel()
        )
        assert result["breakdown"]["auth_fail"] == WEIGHTS["auth_fail"]

    def test_dmarc_fail_triggers_auth_fail(self):
        result = compute_risk_score(
            _base_auth(dmarc_result="fail"), _base_nlp(), _base_origin(), _base_intel()
        )
        assert result["breakdown"]["auth_fail"] == WEIGHTS["auth_fail"]

    def test_softfail_is_not_auth_fail(self):
        """softfail is not literally 'fail' so auth_fail should not trigger."""
        result = compute_risk_score(
            _base_auth(spf_result="softfail"), _base_nlp(), _base_origin(), _base_intel()
        )
        assert "auth_fail" not in result["breakdown"]

    def test_auth_missing_when_both_none(self):
        result = compute_risk_score(
            _base_auth(spf_result="none", dkim_result="none", dmarc_result="pass"),
            _base_nlp(), _base_origin(), _base_intel()
        )
        assert result["breakdown"]["auth_missing"] == WEIGHTS["auth_missing"]

    def test_auth_missing_not_triggered_when_only_one_none(self):
        result = compute_risk_score(
            _base_auth(spf_result="none", dkim_result="pass", dmarc_result="pass"),
            _base_nlp(), _base_origin(), _base_intel()
        )
        assert "auth_missing" not in result["breakdown"]

    def test_weak_dmarc_policy(self):
        result = compute_risk_score(
            _base_auth(dmarc_policy="none"), _base_nlp(), _base_origin(), _base_intel()
        )
        assert result["breakdown"]["weak_dmarc_policy"] == WEIGHTS["weak_dmarc_policy"]

    def test_strong_dmarc_policy_no_penalty(self):
        result = compute_risk_score(
            _base_auth(dmarc_policy="reject"), _base_nlp(), _base_origin(), _base_intel()
        )
        assert "weak_dmarc_policy" not in result["breakdown"]

    def test_no_spf_dmarc_published(self):
        result = compute_risk_score(
            _base_auth(sender_publishes_spf=False, sender_publishes_dmarc=False),
            _base_nlp(), _base_origin(), _base_intel()
        )
        assert result["breakdown"]["no_spf_dmarc_published"] == WEIGHTS["no_spf_dmarc_published"]

    def test_publishes_spf_only_no_penalty(self):
        result = compute_risk_score(
            _base_auth(sender_publishes_spf=True, sender_publishes_dmarc=False),
            _base_nlp(), _base_origin(), _base_intel()
        )
        assert "no_spf_dmarc_published" not in result["breakdown"]


# ---------------------------------------------------------------------------
# NLP signal tests
# ---------------------------------------------------------------------------

class TestNLPSignals:
    def test_high_ml_probability_adds_proportional_score(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(ml_phishing_probability=1.0), _base_origin(), _base_intel()
        )
        assert result["breakdown"]["ml_phishing_probability"] == 30.0

    def test_zero_ml_probability(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(ml_phishing_probability=0.0), _base_origin(), _base_intel()
        )
        assert result["breakdown"]["ml_phishing_probability"] == 0.0

    def test_urgency_triggers_above_threshold(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(urgency_score=0.5), _base_origin(), _base_intel()
        )
        assert result["breakdown"]["urgency_language"] == WEIGHTS["urgency_language"]

    def test_urgency_below_threshold_no_penalty(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(urgency_score=0.3), _base_origin(), _base_intel()
        )
        assert "urgency_language" not in result["breakdown"]

    def test_impersonation_triggers_above_threshold(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(impersonation_score=0.6), _base_origin(), _base_intel()
        )
        assert result["breakdown"]["impersonation_language"] == WEIGHTS["impersonation_language"]

    def test_display_name_mismatch(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(display_name_mismatch=True), _base_origin(), _base_intel()
        )
        assert result["breakdown"]["display_name_mismatch"] == WEIGHTS["display_name_mismatch"]

    def test_no_display_name_mismatch(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(display_name_mismatch=False), _base_origin(), _base_intel()
        )
        assert "display_name_mismatch" not in result["breakdown"]


# ---------------------------------------------------------------------------
# Intel signal tests
# ---------------------------------------------------------------------------

class TestIntelSignals:
    def test_newly_registered_domain(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(), _base_origin(),
            _base_intel(domain_age_days=30)
        )
        assert result["breakdown"]["newly_registered_domain"] == WEIGHTS["newly_registered_domain"]

    def test_old_domain_no_penalty(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(), _base_origin(),
            _base_intel(domain_age_days=365)
        )
        assert "newly_registered_domain" not in result["breakdown"]

    def test_none_domain_age_no_penalty(self):
        """domain_age_days=None (whois lookup failed) should not crash."""
        result = compute_risk_score(
            _base_auth(), _base_nlp(), _base_origin(),
            _base_intel(domain_age_days=None)
        )
        assert "newly_registered_domain" not in result["breakdown"]

    def test_abuse_confidence_proportional(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(), _base_origin(),
            _base_intel(abuse_confidence_score=50)
        )
        assert result["breakdown"]["abuse_confidence"] == 5.0  # 50/100 * 10

    def test_zero_abuse_no_penalty(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(), _base_origin(),
            _base_intel(abuse_confidence_score=0)
        )
        assert "abuse_confidence" not in result["breakdown"]

    def test_hosting_type_flag(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(), _base_origin(),
            _base_intel(usage_type="Data Center/Web Hosting/Transit")
        )
        assert result["breakdown"]["hosting_type_flag"] == WEIGHTS["hosting_type_flag"]

    def test_isp_usage_no_flag(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(), _base_origin(),
            _base_intel(usage_type="ISP")
        )
        assert "hosting_type_flag" not in result["breakdown"]

    def test_mx_mismatch(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(), _base_origin(),
            _base_intel(mx_mismatch=True)
        )
        assert result["breakdown"]["mx_mismatch"] == WEIGHTS["mx_mismatch"]


# ---------------------------------------------------------------------------
# Score capping & total
# ---------------------------------------------------------------------------

class TestScoreCapping:
    def test_score_capped_at_100(self):
        """When every signal fires, total should be min(sum, 100)."""
        result = compute_risk_score(
            _base_auth(
                spf_result="fail", dkim_result="fail", dmarc_result="fail",
                dmarc_policy="none", sender_publishes_spf=False,
                sender_publishes_dmarc=False
            ),
            _base_nlp(
                ml_phishing_probability=1.0, urgency_score=1.0,
                impersonation_score=1.0, display_name_mismatch=True
            ),
            _base_origin(),
            _base_intel(
                domain_age_days=1, abuse_confidence_score=100,
                usage_type="Data Center/Web Hosting/Transit", mx_mismatch=True
            ),
        )
        assert result["total_score"] == 100

    def test_minimal_email_gives_low_score(self):
        """A clean, legitimate email with all-pass auth should score low."""
        result = compute_risk_score(
            _base_auth(), _base_nlp(), _base_origin(), _base_intel()
        )
        # Only ml_phishing_probability at 0.0 contributes 0
        assert result["total_score"] == 0

    def test_result_structure(self):
        result = compute_risk_score(
            _base_auth(), _base_nlp(), _base_origin(), _base_intel()
        )
        assert "total_score" in result
        assert "breakdown" in result
        assert isinstance(result["breakdown"], dict)
        assert isinstance(result["total_score"], int)

    def test_weights_sum_exceeds_100(self):
        """Verify the design intent: raw weights sum > 100 so capping matters."""
        assert sum(WEIGHTS.values()) > 100
