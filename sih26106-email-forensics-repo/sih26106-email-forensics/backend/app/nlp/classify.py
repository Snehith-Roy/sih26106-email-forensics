"""
Phase 4 — Inference wrapper. This is what the backend API actually calls.
Owner: Member 2

Requires backend/models_store/tfidf_vectorizer.pkl and xgb_classifier.pkl
to exist — run `python -m app.nlp.train_baseline` first.
"""
import joblib
from app.nlp.prepare_dataset import clean_body
from app.nlp.heuristics import (
    urgency_score, impersonation_score, display_name_domain_mismatch,
)

_vectorizer = joblib.load("backend/models_store/tfidf_vectorizer.pkl")
_model = joblib.load("backend/models_store/xgb_classifier.pkl")


def classify_email(subject: str, body: str, from_name: str, from_address: str) -> dict:
    text = subject + " " + clean_body(body)
    proba = float(_model.predict_proba(_vectorizer.transform([text]))[0][1])
    return {
        "ml_phishing_probability": proba,
        "urgency_score": urgency_score(text),
        "impersonation_score": impersonation_score(text),
        "display_name_mismatch": display_name_domain_mismatch(from_name, from_address),
    }
