"""
Phase 4 — Inference wrapper. This is what the backend API actually calls.
Owner: Member 2

Requires backend/models_store/tfidf_vectorizer.pkl and xgb_classifier.pkl
to exist — run `python -m app.nlp.train_baseline` first.
"""
import os
import joblib
from app.nlp.prepare_dataset import clean_body
from app.nlp.heuristics import (
    urgency_score, impersonation_score, display_name_domain_mismatch,
)

import logging

_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_store = os.path.join(_backend_dir, "models_store")

try:
    _vectorizer = joblib.load(os.path.join(_store, "tfidf_vectorizer.pkl"))
    _model = joblib.load(os.path.join(_store, "xgb_classifier.pkl"))
    _ml_ready = True
    logging.info(f"ML models loaded successfully from {_store}")
except Exception as e:
    _ml_ready = False
    logging.error(f"CRITICAL: Failed to load ML models from {_store}: {e}")
    logging.error("ML predictions will NOT be available. Train models first:")
    logging.error("  python -m app.nlp.train_baseline")
    _vectorizer = None
    _model = None

def classify_email(subject: str, body: str, from_name: str, from_address: str) -> dict:
    text = subject + " " + clean_body(body)
    
    if _ml_ready and _model and _vectorizer:
        proba = float(_model.predict_proba(_vectorizer.transform([text]))[0][1])
    else:
        raise RuntimeError(
            "ML model not loaded. Cannot make predictions. "
            "Run 'python -m app.nlp.train_baseline' to train the model, "
            "or use Docker: docker-compose up --build"
        )

    return {
        "ml_phishing_probability": proba,
        "urgency_score": urgency_score(text),
        "impersonation_score": impersonation_score(text),
        "display_name_mismatch": display_name_domain_mismatch(from_name, from_address),
    }
