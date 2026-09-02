"""
Phase 3 — Dataset Preparation
Owner: Member 2
"""
import os
import re
try:
    import pandas as pd
    DataFrameType = pd.DataFrame
except ImportError:
    pd = None
    DataFrameType = "Any"


def clean_body(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)              # strip HTML tags
    text = re.sub(r"http\S+", " URLTOKEN ", text)      # normalize URLs
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_dataset(path=None) -> DataFrameType:
    if path is None:
        # Resolve relative to the backend/ directory (3 levels up from this file)
        _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(os.path.dirname(_backend_dir), "dataset", "starter_phishing_dataset.csv")
    df = pd.read_csv(path)
    df = df.dropna(subset=["body", "label"])
    df["clean_body"] = df["body"].apply(clean_body)
    df["text"] = df["subject"].fillna("") + " " + df["clean_body"]
    return df[["text", "label", "source"]]


if __name__ == "__main__":
    df = load_dataset()
    print(df["label"].value_counts())
    df.to_csv("backend/models_store/prepared_dataset.csv", index=False)
