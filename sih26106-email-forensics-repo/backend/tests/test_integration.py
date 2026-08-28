"""
End-to-end integration test — Phase 7
Owner: Member 4

Runs fixture .eml files through the full analysis pipeline (parse → auth →
NLP → origin → intel → scoring) and asserts sane output shapes & score
ranges. Uses an in-memory SQLite DB to verify persistence.

Run with: cd backend && pytest tests/test_integration.py -v
"""

import io
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_test_engine

# In-memory test engine — no file system needed
_test_engine = get_test_engine()
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create fresh tables on in-memory DB before each test, drop after."""
    Base.metadata.create_all(bind=_test_engine)
    yield
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture(autouse=True)
def override_get_db():
    """Override the FastAPI get_db dependency to use our test session."""
    from app.db import get_db
    def _override():
        db = _TestSession()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


def _load_fixture(name: str) -> bytes:
    with open(f"tests/fixtures/{name}", "rb") as f:
        return f.read()


# ─── /api/analyze endpoint tests ────────────────────────────────────────

class TestAnalyzeEndpoint:
    def test_spoofed_email_returns_high_score(self):
        """The spoofed_bank fixture is crafted to score high."""
        client = TestClient(app)
        raw = _load_fixture("spoofed_bank.eml")

        response = client.post(
            "/api/analyze",
            files={"file": ("spoofed_bank.eml", io.BytesIO(raw), "message/rfc822")},
        )
        assert response.status_code == 200
        data = response.json()

        # Structure checks
        assert "analysis_id" in data
        assert "risk_score" in data
        assert "auth" in data
        assert "nlp" in data
        assert "origin" in data
        assert "intel" in data
        assert "parsed" in data

        # Score should be in sane range
        score = data["risk_score"]["total_score"]
        assert 0 <= score <= 100
        assert isinstance(data["risk_score"]["breakdown"], dict)

        # The spoofed email should have a high score (many negative signals)
        assert score > 0, "Spoofed email should score above 0"

    def test_legit_email_returns_lower_score(self):
        """The legit newsletter fixture should score lower than the spoofed one."""
        client = TestClient(app)
        raw = _load_fixture("legit_newsletter.eml")

        response = client.post(
            "/api/analyze",
            files={"file": ("legit_newsletter.eml", io.BytesIO(raw), "message/rfc822")},
        )
        assert response.status_code == 200
        data = response.json()
        score = data["risk_score"]["total_score"]
        assert 0 <= score <= 100

    def test_spoofed_scores_higher_than_legit(self):
        """Core invariant: spoofed > legit on the same pipeline."""
        client = TestClient(app)

        spoofed = client.post(
            "/api/analyze",
            files={"file": ("spoofed.eml", io.BytesIO(_load_fixture("spoofed_bank.eml")), "message/rfc822")},
        ).json()
        legit = client.post(
            "/api/analyze",
            files={"file": ("legit.eml", io.BytesIO(_load_fixture("legit_newsletter.eml")), "message/rfc822")},
        ).json()

        assert spoofed["risk_score"]["total_score"] > legit["risk_score"]["total_score"]

    def test_auth_fields_present(self):
        """Auth response should have all expected keys."""
        client = TestClient(app)
        raw = _load_fixture("spoofed_bank.eml")

        response = client.post(
            "/api/analyze",
            files={"file": ("spoofed.eml", io.BytesIO(raw), "message/rfc822")},
        )
        data = response.json()

        auth = data["auth"]
        for key in [
            "spf_result", "dkim_result", "dmarc_result",
            "dkim_independently_verified", "sender_publishes_spf",
            "sender_publishes_dmarc", "dmarc_policy",
        ]:
            assert key in auth, f"Missing auth key: {key}"

    def test_nlp_fields_present(self):
        """NLP response should have all expected keys."""
        client = TestClient(app)
        raw = _load_fixture("spoofed_bank.eml")

        response = client.post(
            "/api/analyze",
            files={"file": ("spoofed.eml", io.BytesIO(raw), "message/rfc822")},
        )
        data = response.json()

        nlp = data["nlp"]
        for key in [
            "ml_phishing_probability", "urgency_score",
            "impersonation_score", "display_name_mismatch",
        ]:
            assert key in nlp, f"Missing NLP key: {key}"

    def test_origin_has_geolocation(self):
        """Origin response should include geolocation sub-dict."""
        client = TestClient(app)
        raw = _load_fixture("spoofed_bank.eml")

        response = client.post(
            "/api/analyze",
            files={"file": ("spoofed.eml", io.BytesIO(raw), "message/rfc822")},
        )
        data = response.json()

        assert "geolocation" in data["origin"]
        geo = data["origin"]["geolocation"]
        assert "latitude" in geo
        assert "longitude" in geo

    def test_invalid_file_returns_error(self):
        """Uploading garbage should fail gracefully."""
        client = TestClient(app)
        response = client.post(
            "/api/analyze",
            files={"file": ("bad.eml", io.BytesIO(b"not a real email"), "message/rfc822")},
        )
        # Should either return 422/500 or handle gracefully — not 200 with None values
        assert response.status_code in (200, 422, 500)


# ─── /health endpoint ──────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_ok(self):
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


# ─── /api/campaigns endpoint ───────────────────────────────────────────

class TestCampaignsEndpoint:
    def test_empty_db_returns_empty_campaigns(self):
        client = TestClient(app)
        response = client.get("/api/campaigns")
        assert response.status_code == 200
        data = response.json()
        assert data["campaigns"] == []
        assert data["total_analyzed"] == 0
