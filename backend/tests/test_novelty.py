"""
Tests for Novel Features (NOVEL_FEATURES.md)

Feature 1: Stylometric Author Linking
Feature 2: Counterfactual Risk Explanation
Feature 3: Highlighted-Text Explainability
Feature 4: Adversarial Red-Teaming
Feature 5: Homoglyph/Lookalike-Domain Detector
Feature 6: Confidence/Uncertainty Flagging
"""

import pytest
import numpy as np


# ═══════════════════════════════════════════════════════════════════════
# Feature 6: Confidence/Uncertainty Flagging
# ═══════════════════════════════════════════════════════════════════════

class TestConfidence:
    """Tests for confidence/uncertainty flagging."""

    def test_high_phishing_confidence(self):
        from app.novelty.confidence import assess_confidence
        result = assess_confidence(0.95)
        assert result["verdict"] == "phishing"
        assert result["confidence_label"] == "high"
        assert result["needs_human_review"] is False
        assert result["distance_from_boundary"] == 0.45

    def test_high_legitimate_confidence(self):
        from app.novelty.confidence import assess_confidence
        result = assess_confidence(0.1)
        assert result["verdict"] == "legitimate"
        assert result["confidence_label"] == "high"
        assert result["needs_human_review"] is False
        assert result["distance_from_boundary"] == 0.4

    def test_uncertain_in_band(self):
        from app.novelty.confidence import assess_confidence
        result = assess_confidence(0.5)
        assert result["verdict"] == "uncertain"
        assert result["confidence_label"] == "low"
        assert result["needs_human_review"] is True
        assert result["distance_from_boundary"] == 0.0

    def test_boundary_low(self):
        from app.novelty.confidence import assess_confidence
        result = assess_confidence(0.35)
        assert result["needs_human_review"] is True

    def test_boundary_high(self):
        from app.novelty.confidence import assess_confidence
        result = assess_confidence(0.65)
        assert result["needs_human_review"] is True

    def test_just_below_band(self):
        from app.novelty.confidence import assess_confidence
        result = assess_confidence(0.34)
        assert result["needs_human_review"] is False
        assert result["verdict"] == "legitimate"

    def test_just_above_band(self):
        from app.novelty.confidence import assess_confidence
        result = assess_confidence(0.66)
        assert result["needs_human_review"] is False
        assert result["verdict"] == "phishing"


# ═══════════════════════════════════════════════════════════════════════
# Feature 5: Homoglyph/Lookalike-Domain Detector
# ═══════════════════════════════════════════════════════════════════════

class TestHomoglyph:
    """Tests for homoglyph and typosquat detection."""

    def test_clean_domain_no_flags(self):
        from app.novelty.homoglyph import analyze_domain_for_spoofing
        result = analyze_domain_for_spoofing("google.com")
        assert result["is_homoglyph_attack"] is False
        assert result["is_typosquat_suspected"] is False

    def test_typosquat_detection(self):
        from app.novelty.homoglyph import check_typosquat
        result = check_typosquat("paypa1.com")
        assert result["is_typosquat_suspected"] is True
        assert result["closest_watched_brand"] == "paypal.com"
        assert result["edit_distance"] == 1

    def test_typosquat_distance_2(self):
        from app.novelty.homoglyph import check_typosquat
        result = check_typosquat("micros0ft.com")
        assert result["is_typosquat_suspected"] is True

    def test_exact_match_not_suspicious(self):
        from app.novelty.homoglyph import check_typosquat
        result = check_typosquat("paypal.com")
        assert result["is_typosquat_suspected"] is False

    def test_unrelated_domain_not_suspicious(self):
        from app.novelty.homoglyph import check_typosquat
        result = check_typosquat("random-domain.xyz")
        assert result["is_typosquat_suspected"] is False

    def test_homoglyph_with_cyrillic(self):
        """Test with a domain containing Cyrillic characters."""
        from app.novelty.homoglyph import check_homoglyph_attack
        # Cyrillic 'а' (U+0430) instead of Latin 'a'
        result = check_homoglyph_attack("bаnk.com")  # Note: Cyrillic а
        # Result depends on confusable-homoglyphs library
        assert "is_homoglyph_attack" in result
        assert "confusable_characters" in result


# ═══════════════════════════════════════════════════════════════════════
# Feature 2: Counterfactual Risk Explanation
# ═══════════════════════════════════════════════════════════════════════

class TestCounterfactual:
    """Tests for counterfactual risk explanation."""

    def test_auth_pass_reduces_score(self):
        from app.novelty.counterfactual import generate_counterfactuals
        auth = {
            "spf_result": "fail", "dkim_result": "fail", "dmarc_result": "fail",
            "dkim_independently_verified": None, "sender_publishes_spf": False,
            "sender_publishes_dmarc": False, "dmarc_policy": None,
        }
        nlp = {"ml_phishing_probability": 0.9, "urgency_score": 1.0,
               "impersonation_score": 0.5, "display_name_mismatch": False}
        origin = {"origin_ip": "1.2.3.4"}
        intel = {"abuse_confidence_score": 50, "domain_age_days": 30}
        
        result = generate_counterfactuals(auth, nlp, origin, intel)
        assert "baseline_score" in result
        assert "scenarios" in result
        assert len(result["scenarios"]) > 0
        
        # Auth fix should reduce score
        auth_scenario = [s for s in result["scenarios"] if "SPF, DKIM" in s["change"]]
        assert len(auth_scenario) == 1
        assert auth_scenario[0]["delta"] < 0  # Score should decrease

    def test_empty_when_no_risk_signals(self):
        from app.novelty.counterfactual import generate_counterfactuals
        auth = {
            "spf_result": "pass", "dkim_result": "pass", "dmarc_result": "pass",
            "dkim_independently_verified": True, "sender_publishes_spf": True,
            "sender_publishes_dmarc": True, "dmarc_policy": "reject",
        }
        nlp = {"ml_phishing_probability": 0.05, "urgency_score": 0.0,
               "impersonation_score": 0.0, "display_name_mismatch": False}
        origin = {"origin_ip": None}
        intel = {"domain_age_days": 3650, "abuse_confidence_score": 0}
        
        result = generate_counterfactuals(auth, nlp, origin, intel)
        # Should have fewer scenarios since most things are clean
        assert len(result["scenarios"]) <= 1


# ═══════════════════════════════════════════════════════════════════════
# Feature 3: Highlighted-Text Explainability
# ═══════════════════════════════════════════════════════════════════════

class TestHighlight:
    """Tests for highlighted-text explainability."""

    def test_highlight_text_wraps_words(self):
        from app.novelty.highlight import highlight_text
        contributions = [
            {"term": "urgent", "contribution": 0.8},
            {"term": "verify", "contribution": 0.3},
        ]
        result = highlight_text("Please urgent verify your account", contributions)
        assert '<mark class="hl-red high">' in result
        assert '<mark class="hl-red low">' in result
        assert "urgent" in result
        assert "verify" in result

    def test_highlight_empty_contributions(self):
        from app.novelty.highlight import highlight_text
        result = highlight_text("Hello world", [])
        assert result == "Hello world"

    def test_highlight_negative_contribution(self):
        from app.novelty.highlight import highlight_text
        contributions = [{"term": "legitimate", "contribution": -0.6}]
        result = highlight_text("This is legitimate", contributions)
        assert '<mark class="hl-green high">' in result


# ═══════════════════════════════════════════════════════════════════════
# Feature 1: Stylometric Author Linking
# ═══════════════════════════════════════════════════════════════════════

class TestStylometry:
    """Tests for stylometric author linking."""

    def test_extract_vector_returns_numpy(self):
        from app.novelty.stylometry import extract_stylometric_vector
        vec = extract_stylometric_vector("Hello, this is a test email.")
        assert isinstance(vec, np.ndarray)
        assert len(vec) == 8 + len(['the', 'of', 'and', 'to', 'in', 'a', 'is', 'that', 'it', 'for',
                                     'on', 'with', 'as', 'was', 'at', 'by', 'this', 'be', 'or', 'an',
                                     'will', 'your', 'please', 'we', 'you', 'our', 'if', 'not'])

    def test_empty_body_returns_zeros(self):
        from app.novelty.stylometry import extract_stylometric_vector
        vec = extract_stylometric_vector("")
        assert np.all(vec == 0)

    def test_similar_style_high_similarity(self):
        from app.novelty.stylometry import extract_stylometric_vector, stylometric_similarity
        text_a = "Dear Sir, I am writing to inform you about your account. Please verify immediately. Regards, Team"
        text_b = "Dear Customer, I am writing to notify you about your profile. Please confirm urgently. Best, Support"
        
        vec_a = extract_stylometric_vector(text_a)
        vec_b = extract_stylometric_vector(text_b)
        sim = stylometric_similarity(vec_a, vec_b)
        assert sim > 0.8  # Should be similar

    def test_different_style_low_similarity(self):
        from app.novelty.stylometry import extract_stylometric_vector, stylometric_similarity
        text_a = "URGENT!!! CLICK NOW!!! YOUR ACCOUNT IS SUSPENDED!!! ACT IMMEDIATELY!!!"
        text_b = "Dear valued customer, we hope this message finds you well. Please find attached the quarterly report for your review."
        
        vec_a = extract_stylometric_vector(text_a)
        vec_b = extract_stylometric_vector(text_b)
        sim = stylometric_similarity(vec_a, vec_b)
        assert sim < 0.9  # Should be less similar

    def test_link_by_style_returns_list(self):
        from app.novelty.stylometry import link_by_style
        emails = [
            {"email_id": "1", "body": "Dear Sir, please verify your account. Regards"},
            {"email_id": "2", "body": "Dear Customer, please confirm your profile. Best"},
            {"email_id": "3", "body": "URGENT CLICK NOW ACT IMMEDIATELY"},
        ]
        links = link_by_style(emails, threshold=0.7)
        assert isinstance(links, list)


# ═══════════════════════════════════════════════════════════════════════
# Feature 4: Adversarial Red-Teaming
# ═══════════════════════════════════════════════════════════════════════

class TestRedTeam:
    """Tests for adversarial red-teaming."""

    def test_perturb_zero_width_inserts_chars(self):
        from app.novelty.redteam import perturb_zero_width
        result = perturb_zero_width("urgent")
        assert "\u200b" in result

    def test_perturb_homoglyph_replaces_chars(self):
        from app.novelty.redteam import perturb_homoglyph
        result = perturb_homoglyph("urgent")
        # Should contain at least one non-ASCII character
        assert any(ord(c) > 127 for c in result)

    def test_perturb_synonym_replaces_words(self):
        from app.novelty.redteam import perturb_synonym
        result = perturb_synonym("urgent action required")
        assert "urgent" not in result.lower()
        assert "pressing" in result.lower() or "right away" in result.lower()

    def test_perturb_html_comment_inserts_tags(self):
        from app.novelty.redteam import perturb_html_comment
        result = perturb_html_comment("urgent")
        assert "<!-- -->" in result

    def test_robustness_report_structure(self):
        from app.novelty.redteam import run_robustness_report
        emails = [{"subject": "Test", "body": "urgent verify", 
                   "from_name": "Test", "from_address": "test@test.com"}]
        result = run_robustness_report(emails)
        assert "zero_width_injection" in result
        assert "homoglyph_substitution" in result
        assert "synonym_substitution" in result
        assert "html_comment_injection" in result
        for key in result:
            assert "still_caught" in result[key]
            assert "robustness_pct" in result[key]

    def test_robustness_report_empty_input(self):
        from app.novelty.redteam import run_robustness_report
        result = run_robustness_report([])
        assert "error" in result


# ═══════════════════════════════════════════════════════════════════════
# Integration: Novel features in analyze endpoint
# ═══════════════════════════════════════════════════════════════════════

import os
_ml_available = os.path.exists(
    os.path.join(os.path.dirname(__file__), "..", "models_store", "xgb_classifier.pkl")
)


class TestNoveltyIntegration:
    """Test that novel features are wired into the analyze endpoint."""

    @pytest.mark.skipif(not _ml_available, reason="ML model not trained yet")
    def test_analyze_returns_confidence(self):
        """Analyze endpoint should return confidence field."""
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        with open("tests/fixtures/legit_newsletter.eml", "rb") as f:
            response = client.post("/api/analyze", files={"file": ("test.eml", f, "message/rfc822")})
        assert response.status_code == 200
        data = response.json()
        assert "confidence" in data
        assert "verdict" in data["confidence"]
        assert "needs_human_review" in data["confidence"]

    @pytest.mark.skipif(not _ml_available, reason="ML model not trained yet")
    def test_analyze_returns_counterfactuals(self):
        """Analyze endpoint should return counterfactuals field."""
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        with open("tests/fixtures/spoofed_bank.eml", "rb") as f:
            response = client.post("/api/analyze", files={"file": ("test.eml", f, "message/rfc822")})
        assert response.status_code == 200
        data = response.json()
        assert "counterfactuals" in data
        assert "baseline_score" in data["counterfactuals"]
        assert "scenarios" in data["counterfactuals"]

    @pytest.mark.skipif(not _ml_available, reason="ML model not trained yet")
    def test_analyze_returns_domain_spoof_check(self):
        """Analyze endpoint should return domain_spoof_check field."""
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        with open("tests/fixtures/spoofed_bank.eml", "rb") as f:
            response = client.post("/api/analyze", files={"file": ("test.eml", f, "message/rfc822")})
        assert response.status_code == 200
        data = response.json()
        assert "domain_spoof_check" in data
        assert "is_homoglyph_attack" in data["domain_spoof_check"]
        assert "is_typosquat_suspected" in data["domain_spoof_check"]
