"""
Phase 4 (STRETCH GOAL — time-box to 2 days max)
Owner: Member 2

Only start this once train_baseline.py is trained, evaluated, AND already
wired end-to-end into the live /api/analyze pipeline (Phase 7 working). A
working TF-IDF+XGBoost baseline beats an unfinished transformer every time
in a demo. Requires `transformers`, `datasets`, `torch` — uncomment in
requirements.txt before using.
"""
from transformers import (
    DistilBertTokenizerFast, DistilBertForSequenceClassification,
    Trainer, TrainingArguments
)
from datasets import Dataset
from app.nlp.prepare_dataset import load_dataset


def train():
    df = load_dataset()
    ds = Dataset.from_pandas(df[["text", "label"]]).train_test_split(test_size=0.2)

    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

    def tokenize(batch):
        return tokenizer(batch["text"], padding="max_length", truncation=True, max_length=256)

    ds = ds.map(tokenize, batched=True)

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=2
    )
    args = TrainingArguments(
        output_dir="backend/models_store/distilbert",
        per_device_train_batch_size=16,
        num_train_epochs=2,
        eval_strategy="epoch",
        save_strategy="epoch",
    )
    trainer = Trainer(model=model, args=args,
                       train_dataset=ds["train"], eval_dataset=ds["test"])
    trainer.train()
    trainer.save_model("backend/models_store/distilbert_final")


if __name__ == "__main__":
    train()
