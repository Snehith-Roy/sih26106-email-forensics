"""
Unit tests for Phase 3 & 4 — NLP modules
Owner: Member 2 / verified by Member 4

Tests heuristics, dataset preparation, and classification inference.
"""

import pytest


# ---------------------------------------------------------------------------
# Heuristics tests
# ---------------------------------------------------------------------------

class TestUrgencyScore:
    def test_empty_text_returns_zero(self):
        from app.nlp.heuristics import urgency_score
        assert urgency_score("") == 0.0

    def test_no_urgency_patterns(self):
        from app.nlp.heuristics import urgency_score
        assert urgency_score("Hello, how are you today?") == 0.0

    def test_single_urgency_pattern(self):
        from app.nlp.heuristics import urgency_score
        score = urgency_score("Your account is suspended, act now")
        assert score > 0.0

    def test_multiple_urgency_patterns_max_at_1(self):
        from app.nlp.heuristics import urgency_score
        text = "URGENT! Your account is suspended. Act now immediately click here final notice verify your account"
        score = urgency_score(text)
        assert score == 1.0

    def test_case_insensitive(self):
        from app.nlp.heuristics import urgency_score
        assert urgency_score("URGENT") > 0.0
        assert urgency_score("urgent") > 0.0


class TestImpersonationScore:
    def test_empty_text_returns_zero(self):
        from app.nlp.heuristics import impersonation_score
        assert impersonation_score("") == 0.0

    def test_no_impersonation_patterns(self):
        from app.nlp.heuristics import impersonation_score
        assert impersonation_score("Please review the attached document") == 0.0

    def test_single_impersonation_pattern(self):
        from app.nlp.heuristics import impersonation_score
        score = impersonation_score("This is from the IT helpdesk")
        assert score > 0.0

    def test_multiple_patterns_max_at_1(self):
        from app.nlp.heuristics import impersonation_score
        text = "From: CEO, IT support, accounts payable, wire transfer"
        score = impersonation_score(text)
        assert score == 1.0


class TestDisplayNameDomainMismatch:
    def test_match_when_brand_in_domain(self):
        from app.nlp.heuristics import display_name_domain_mismatch
        assert display_name_domain_mismatch("PayPal Security", "security@paypal.com") is False

    def test_mismatch_when_brand_not_in_domain(self):
        from app.nlp.heuristics import display_name_domain_mismatch
        assert display_name_domain_mismatch("PayPal Security", "security@evil-scam.com") is True

    def test_no_brand_in_name(self):
        from app.nlp.heuristics import display_name_domain_mismatch
        assert display_name_domain_mismatch("John Doe", "john@random.com") is False

    def test_empty_name(self):
        from app.nlp.heuristics import display_name_domain_mismatch
        assert display_name_domain_mismatch("", "x@y.com") is False

    def test_case_insensitive(self):
        from app.nlp.heuristics import display_name_domain_mismatch
        assert display_name_domain_mismatch("MICROSOFT Support", "hacker@evil.com") is True


# ---------------------------------------------------------------------------
# Dataset preparation tests
# ---------------------------------------------------------------------------

class TestPrepareDataset:
    def test_clean_body_strips_html(self):
        from app.nlp.prepare_dataset import clean_body
        result = clean_body("<p>Hello <b>world</b></p>")
        assert "<p>" not in result
        assert "<b>" not in result
        assert "Hello" in result
        assert "world" in result

    def test_clean_body_normalizes_urls(self):
        from app.nlp.prepare_dataset import clean_body
        result = clean_body("Visit http://evil.com/steal now")
        assert "URLTOKEN" in result
        assert "http" not in result

    def test_clean_body_collapses_whitespace(self):
        from app.nlp.prepare_dataset import clean_body
        result = clean_body("  too   many    spaces  ")
        assert result == "too many spaces"

    def test_clean_body_empty_string(self):
        from app.nlp.prepare_dataset import clean_body
        assert clean_body("") == ""


# ---------------------------------------------------------------------------
# Classification inference tests
# ---------------------------------------------------------------------------

class TestClassifyEmail:
    def test_returns_all_expected_keys(self):
        from app.nlp.classify import classify_email
        result = classify_email("Test Subject", "Test body", "John", "john@test.com")
        assert "ml_phishing_probability" in result
        assert "urgency_score" in result
        assert "impersonation_score" in result
        assert "display_name_mismatch" in result

    def test_probability_in_valid_range(self):
        from app.nlp.classify import classify_email
        result = classify_email("Test Subject", "Test body", "John", "john@test.com")
        prob = result["ml_phishing_probability"]
        assert 0.0 <= prob <= 1.0

    def test_urgency_score_in_valid_range(self):
        from app.nlp.classify import classify_email
        result = classify_email("URGENT! Act now!", "Your account is suspended", "IT Support", "scam@evil.com")
        assert 0.0 <= result["urgency_score"] <= 1.0

    def test_real_model_files_exist(self):
        """After training, .pkl files should exist in models_store/."""
        import os
        _backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assert os.path.exists(os.path.join(_backend_dir, "models_store", "tfidf_vectorizer.pkl")), \
            "tfidf_vectorizer.pkl not found — run train_baseline.py first"
        assert os.path.exists(os.path.join(_backend_dir, "models_store", "xgb_classifier.pkl")), \
            "xgb_classifier.pkl not found — run train_baseline.py first"

    def test_classifier_loads_model_on_fresh_import(self):
        """Fresh import of classify module should load real models if available,
        or gracefully fall back to mock if XGBoost DLL is unavailable."""
        import importlib
        import app.nlp.classify as mod
        importlib.reload(mod)
        if mod._model is not None:
            assert mod._vectorizer is not None, "Vectorizer should load alongside model"
        else:
            # XGBoost DLL not available (e.g. missing OpenMP runtime on Windows)
            # The mock fallback should still work
            result = mod.classify_email("test", "body", "name", "a@b.com")
            assert result["ml_phishing_probability"] == 0.85
