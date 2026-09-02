"""
Phase 4 — NLP/ML Classifier: baseline (TF-IDF + XGBoost)
Owner: Member 2

Build this FIRST. Always have a working model before attempting the
DistilBERT stretch goal (train_distilbert.py) — see the time-box warning
in IMPLEMENTATION.md Phase 4.
"""
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from xgboost import XGBClassifier
from app.nlp.prepare_dataset import load_dataset


def train():
    df = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42,
        stratify=df["label"]
    )

    vectorizer = TfidfVectorizer(
        max_features=8000, ngram_range=(1, 2), stop_words="english"
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    clf = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1,
        eval_metric="logloss", random_state=42
    )
    clf.fit(X_train_vec, y_train)

    print(classification_report(y_test, clf.predict(X_test_vec)))

    # Save relative to the backend/ directory (3 levels up from this file)
    _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _store = os.path.join(_backend_dir, "models_store")
    os.makedirs(_store, exist_ok=True)
    joblib.dump(vectorizer, os.path.join(_store, "tfidf_vectorizer.pkl"))
    joblib.dump(clf, os.path.join(_store, "xgb_classifier.pkl"))
    print(f"Models saved to {_store}")


if __name__ == "__main__":
    train()
