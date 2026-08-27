"""
Phase 3 — Dataset Preparation
Owner: Member 2
"""
import pandas as pd
import re


def clean_body(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)              # strip HTML tags
    text = re.sub(r"http\S+", " URLTOKEN ", text)      # normalize URLs
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_dataset(path="dataset/starter_phishing_dataset.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.dropna(subset=["body", "label"])
    df["clean_body"] = df["body"].apply(clean_body)
    df["text"] = df["subject"].fillna("") + " " + df["clean_body"]
    return df[["text", "label", "source"]]


if __name__ == "__main__":
    df = load_dataset()
    print(df["label"].value_counts())
    df.to_csv("backend/models_store/prepared_dataset.csv", index=False)
