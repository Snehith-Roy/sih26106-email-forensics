"""
Feature 3 — Highlighted-text explainability via SHAP.

Uses SHAP (SHapley Additive exPlanations) to show which exact words
in the email body pushed the ML score up.

Requires: pip install shap
Uses the SAME trained model/vectorizer as nlp/classify.py — no retraining needed.
"""

import re
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Try to load SHAP and the model — gracefully degrade if not available
try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
    logger.warning("shap not installed — word contributions will be empty")

try:
    import joblib
    _backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _vectorizer_path = os.path.join(_backend_dir, "models_store", "tfidf_vectorizer.pkl")
    _model_path = os.path.join(_backend_dir, "models_store", "xgb_classifier.pkl")
    
    if os.path.exists(_vectorizer_path) and os.path.exists(_model_path):
        _vectorizer = joblib.load(_vectorizer_path)
        _model = joblib.load(_model_path)
        if HAS_SHAP:
            _explainer = shap.TreeExplainer(_model)
        _feature_names = _vectorizer.get_feature_names_out()
        HAS_MODEL = True
    else:
        HAS_MODEL = False
        logger.warning("Model files not found — word contributions will be empty")
except Exception as e:
    HAS_MODEL = False
    logger.warning(f"Failed to load model: {e} — word contributions will be empty")


def get_word_contributions(text: str, top_n: int = 15) -> list[dict]:
    """
    Get the top_n words/bigrams that most increased (or decreased)
    the phishing score for this specific email.
    
    Returns list of dicts with:
        - term: the word/bigram
        - contribution: float (positive = more phishing, negative = less)
    """
    if not HAS_SHAP or not HAS_MODEL:
        return []

    try:
        X = _vectorizer.transform([text])
        raw_shap = _explainer.shap_values(X)

        # Handle both shap API shapes across versions
        if isinstance(raw_shap, list):
            shap_row = raw_shap[1][0]  # class 1 = phishing
        else:
            arr = np.array(raw_shap)
            shap_row = arr[0] if arr.ndim == 2 else arr[0, :, 1]

        nonzero_idx = X.nonzero()[1]
        contributions = [
            {"term": _feature_names[i], "contribution": float(shap_row[i])}
            for i in nonzero_idx
        ]
        contributions.sort(key=lambda c: abs(c["contribution"]), reverse=True)
        return contributions[:top_n]
    except Exception as e:
        logger.error(f"SHAP computation failed: {e}")
        return []


def highlight_text(original_body: str, contributions: list[dict]) -> str:
    """
    Wrap contributing words in <mark> spans with intensity classes.
    
    Returns HTML-safe string with highlighted terms:
        - hl-red high: strong phishing indicator
        - hl-red low: mild phishing indicator
        - hl-green high: strong legitimate indicator
        - hl-green low: mild legitimate indicator
    """
    if not contributions:
        return original_body

    html = original_body
    # Sort by term length descending so bigger matches wrap correctly
    # even when one term is a substring of another
    for c in sorted(contributions, key=lambda x: len(x["term"]), reverse=True):
        term = c["term"]
        intensity = "high" if abs(c["contribution"]) > 0.5 else "low"
        color_class = "hl-red" if c["contribution"] > 0 else "hl-green"
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        html = pattern.sub(
            lambda m: f'<mark class="{color_class} {intensity}">{m.group(0)}</mark>',
            html,
        )
    return html
