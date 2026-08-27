# SIH26106 — AI-Powered Email Threat Detection, GeoLocation & Forensic Intelligence Platform
### Full Implementation Roadmap (Phase-wise) — Team of 6

> This document is the single source of truth for building this project from
> scratch. It's meant to live at the root of your GitHub repo as
> `IMPLEMENTATION.md`. Every phase has: what to build, why, real working
> starter code (verified against the actual libraries — versions and
> import names below are confirmed, not guessed), and who on the team owns it.

---

## 0. Project Charter (one paragraph, for your PPT)

An AI-powered email forensic platform that goes beyond phishing detection by
fusing **content-based threat classification** (NLP/ML) with **technical
origin tracing** (SPF/DKIM/DMARC forensics + relay-chain + GeoIP + domain
reputation). It ingests a raw `.eml`, validates sender authenticity,
classifies the content for phishing/BEC/social-engineering patterns, traces
the email's actual path back to its most credible origin IP, geolocates and
reputation-checks that IP, fuses every signal into one explainable 0–100 risk
score, clusters related emails into likely campaigns, and hands the analyst
a dashboard + a downloadable PDF forensic report.

---

## 1. Final Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Email parsing | `mail-parser` (imports as `mailparser`) | Handles raw `.eml`, MIME, headers, Received-chain parsing out of the box |
| Auth verification | `authres`, `dkimpy` (imports as `dkim`), `checkdmarc`, `dnspython` | See Phase 2 — each does a distinct, real job; don't rely on one library for everything |
| NLP/ML (baseline) | `scikit-learn` (TF-IDF) + `xgboost` | Trains in seconds on a laptop, strong baseline, judges can see live retraining in a demo |
| NLP/ML (stretch) | `transformers` (DistilBERT fine-tune) | Only if Phase 4 baseline is done early — see time-box warning in Phase 4 |
| GeoIP | `geoip2` + MaxMind **GeoLite2-City** (free, account required) | City-level geolocation, offline `.mmdb` lookup, no per-request API limit |
| IP reputation | AbuseIPDB API (free: 1,000 checks/day) + IPinfo **Lite** API (free: unlimited, country/ASN only) | Abuse confidence score + hosting/VPN/proxy signal |
| Domain intel | `python-whois`, `dnspython` (MX/A/TXT lookups) | Domain age, registrar, hosting mismatch |
| Correlation | `networkx` | Simple graph clustering — shared IP/domain/reply-to → campaign |
| Backend | `FastAPI` + `uvicorn` + `Pydantic` | Async, auto-generated OpenAPI docs (nice for judges), typed |
| DB | `PostgreSQL` (or SQLite for local dev) via `SQLAlchemy` | Relational fits emails/campaigns/scores well |
| Frontend | `React` + `Vite` + `Tailwind` + `recharts` + `react-leaflet` | Fast to build, gauge chart + relay-path map |
| PDF report | `reportlab` | Full control over forensic report layout |
| Containerization | `Docker` + `docker-compose` | One-command run for judges during evaluation |

**Verified package versions** (checked against PyPI at the time of writing —
pin these in `requirements.txt` so nobody's environment silently breaks):

```
mail-parser==4.6.4
dkimpy==1.1.8
checkdmarc==5.17.5
authres==1.2.0
dnspython==2.6.1
geoip2==5.3.0
python-whois==0.9.6
ipwhois==1.3.0
scikit-learn==1.5.2
xgboost==2.1.1
pandas==2.2.3
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
networkx==3.3
reportlab==4.2.5
requests==2.32.3
python-multipart==0.0.9
```

> ⚠️ **`pyspf` warning (save your team a debugging afternoon):** the classic
> `pyspf` package depends on the legacy `pydns` library, which fails to
> install on modern Python 3 (`ModuleNotFoundError: No module named 'Type'`)
> — it hasn't been updated for Python 3's import system. **Don't put `pyspf`
> in requirements.txt.** See Phase 2 for why you mostly don't need it anyway,
> and what to use instead.

---

## 2. Repository Structure

```
sih26106-email-forensics/
├── IMPLEMENTATION.md              ← this file
├── README.md                      ← project overview, setup, demo GIF
├── docker-compose.yml
├── .gitignore
├── .github/
│   ├── workflows/ci.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
├── dataset/
│   ├── DATASET_README.md
│   ├── starter_phishing_dataset.csv
│   └── fetch_full_dataset.sh
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py                ← FastAPI app entrypoint
│   │   ├── models.py              ← SQLAlchemy + Pydantic schemas
│   │   ├── db.py
│   │   ├── ingestion/
│   │   │   └── parser.py          ← Phase 1
│   │   ├── auth_check/
│   │   │   └── verifier.py        ← Phase 2
│   │   ├── nlp/
│   │   │   ├── prepare_dataset.py ← Phase 3
│   │   │   ├── train_baseline.py  ← Phase 4 (TF-IDF + XGBoost)
│   │   │   ├── train_distilbert.py← Phase 4 stretch
│   │   │   └── classify.py
│   │   ├── origin/
│   │   │   ├── relay_trace.py     ← Phase 5
│   │   │   ├── geoip_lookup.py
│   │   │   └── domain_intel.py
│   │   ├── scoring/
│   │   │   ├── risk_score.py      ← Phase 6
│   │   │   └── correlation.py
│   │   ├── reports/
│   │   │   └── pdf_report.py      ← Phase 9
│   │   └── routes/
│   │       ├── analyze.py
│   │       ├── campaigns.py
│   │       └── reports.py
│   ├── models_store/              ← trained .pkl / .mmdb files (gitignored)
│   └── tests/
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── UploadPanel.jsx
│   │   │   ├── RiskGauge.jsx
│   │   │   ├── RelayMap.jsx
│   │   │   ├── AuthBadges.jsx
│   │   │   └── CampaignGraph.jsx
│   │   └── api/client.js
│   └── vite.config.js
└── docs/
    ├── architecture.png
    └── demo_script.md
```

---

## Phase 0 — Environment & Repo Scaffolding (Day 1)

**Owner:** whole team, 1 kickoff session · **Goal:** everyone can `git clone`
and run something within an hour.

```bash
# 1. Create repo, add all 6 as collaborators, protect `main` branch
git init sih26106-email-forensics && cd sih26106-email-forensics
git branch -M main

# 2. Backend skeleton
mkdir -p backend/app/{ingestion,auth_check,nlp,origin,scoring,reports,routes} backend/tests
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt   # from the pinned list above

# 3. Frontend skeleton
npm create vite@latest frontend -- --template react
cd frontend && npm install tailwindcss recharts react-leaflet leaflet axios
cd ..

# 4. Docker Compose for one-command demo (judges will thank you)
```

`docker-compose.yml`:
```yaml
version: "3.9"
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes:
      - ./backend/models_store:/app/models_store
    environment:
      - DATABASE_URL=postgresql://sih:sih@db:5432/sih
      - MAXMIND_ACCOUNT_ID=${MAXMIND_ACCOUNT_ID}
      - MAXMIND_LICENSE_KEY=${MAXMIND_LICENSE_KEY}
      - ABUSEIPDB_API_KEY=${ABUSEIPDB_API_KEY}
      - IPINFO_TOKEN=${IPINFO_TOKEN}
    depends_on: [db]
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: sih
      POSTGRES_PASSWORD: sih
      POSTGRES_DB: sih
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata:
```

`.gitignore` essentials: `*.pyc`, `__pycache__/`, `.venv/`, `node_modules/`,
`models_store/*.pkl`, `models_store/*.mmdb`, `dataset/full_corpus/`, `.env`.

**External accounts to create NOW** (Day 1, don't block Phase 5 on this
later — free, but signup can take a few minutes each):
1. MaxMind GeoLite2 account → https://www.maxmind.com/en/geolite2/signup
   (free account + license key, needed to download the GeoLite2-City
   `.mmdb` file — no per-request limit since it's a local file, not an API).
2. AbuseIPDB account → https://www.abuseipdb.com/register (free tier:
   1,000 IP checks/day, no credit card).
3. IPinfo account → https://ipinfo.io/signup (free **Lite** tier: unlimited
   requests, but only country + ASN fields — good enough as a *secondary*
   hosting/ASN signal; MaxMind remains your primary city-level geolocator).

Put all keys in a `.env` file (gitignored), never commit them.

---

## Phase 1 — Email Ingestion & Parsing (Days 2–4)

**Owner:** Member 1 · **Depends on:** nothing · **Blocks:** Phases 2, 5

Parse a raw `.eml` into a structured object: headers, from/to/subject/body,
attachments, and — critically — the **ordered Received-header chain**,
which Phase 5 depends on entirely.

```python
# backend/app/ingestion/parser.py
import mailparser
from dataclasses import dataclass, field

@dataclass
class ParsedEmail:
    from_name: str
    from_address: str
    to_addresses: list
    subject: str
    date: str
    body: str
    raw_authentication_results: str | None
    received_chain: list       # ordered oldest -> newest, see note below
    attachments: list
    raw_headers: dict

def parse_eml(raw_bytes: bytes) -> ParsedEmail:
    mail = mailparser.parse_from_bytes(raw_bytes)

    from_name, from_address = (mail.from_[0] if mail.from_ else ("", ""))
    to_addresses = [addr for _, addr in mail.to] if mail.to else []

    return ParsedEmail(
        from_name=from_name,
        from_address=from_address,
        to_addresses=to_addresses,
        subject=mail.subject or "",
        date=str(mail.date) if mail.date else "",
        body=mail.body or "",
        # NOTE: mailparser strips the "Authentication-Results:" prefix from
        # the value — Phase 2's `authres` parser needs it added back.
        raw_authentication_results=mail.headers.get("Authentication-Results"),
        # mailparser numbers hops chronologically: hop=1 is the OLDEST
        # (earliest/bottommost in the raw file), hop=N is the NEWEST
        # (closest to final delivery). This ordering is exactly what
        # Phase 5's relay-walk algorithm needs.
        received_chain=sorted(mail.received, key=lambda h: h.get("hop", 0)),
        attachments=[a.get("filename") for a in mail.attachments],
        raw_headers=dict(mail.headers),
    )
```

**Test fixture** — commit a few realistic `.eml` samples to
`backend/tests/fixtures/` (a clean legitimate one, a spoofed-domain one, a
lookalike-domain one) so the whole team can develop against the same
ground truth without waiting on real data.

```python
# backend/tests/test_parser.py
from app.ingestion.parser import parse_eml

def test_parses_basic_fields():
    raw = open("tests/fixtures/spoofed_bank.eml", "rb").read()
    result = parse_eml(raw)
    assert result.from_address == "noreply@bank-corp.com"
    assert len(result.received_chain) >= 1
    assert result.received_chain[0]["hop"] == 1
```

---

## Phase 2 — Authentication Verification (Days 3–6)

**Owner:** Member 1 (with Member 5 support) · **Depends on:** Phase 1

### The nuance most teams get wrong — read this before writing code

You **cannot reliably re-run a full SPF check** on a `.eml` after the fact
and expect a trustworthy pass/fail. SPF evaluates *"was the IP that
connected to the mail server authorized to send for this domain, at the
moment it connected"* — and the only party with ground truth on that
connecting IP is the receiving mail server itself, at delivery time. A
`.eml` file doesn't carry that live connection state, and the SPF record
may have changed since. Two things ARE reliable after the fact:

1. **DKIM signature verification is fully re-checkable and deterministic**
   — it's a cryptographic signature over the message content, independent
   of network path. `dkimpy` really re-verifies it.
2. **The `Authentication-Results:` header is the ground truth for what
   the *actual* receiving mail server (Gmail, Outlook, your org's gateway)
   concluded about SPF/DKIM/DMARC at the moment of delivery** — because
   *they* had the real connecting IP. This is your **primary signal**.

So Phase 2 has three tiers, in priority order:

| Tier | What | Library | Reliability |
|---|---|---|---|
| 1 (primary) | Parse existing `Authentication-Results` header | `authres` | High — added by the real receiving MTA |
| 2 (independent re-check) | Re-verify the DKIM signature yourself | `dkimpy` | High — cryptographic, network-independent |
| 3 (policy hygiene) | Does the sender domain even *publish* a valid SPF/DMARC record, and how strict is it? | `checkdmarc` | Medium — a missing/weak policy is itself a red flag, even without a per-message check |

```python
# backend/app/auth_check/verifier.py
from authres import AuthenticationResultsHeader
import dkim
import checkdmarc
from dataclasses import dataclass

@dataclass
class AuthResult:
    spf_result: str            # pass / fail / softfail / neutral / none / unknown
    dkim_result: str           # pass / fail / none / unknown
    dmarc_result: str          # pass / fail / none / unknown
    dkim_independently_verified: bool | None   # our own re-check, not just the header's claim
    sender_publishes_spf: bool
    sender_publishes_dmarc: bool
    dmarc_policy: str | None   # none / quarantine / reject
    spf_dns_lookup_count: int | None  # >10 = broken SPF record (RFC limit)

def parse_authentication_results(raw_header_value: str | None) -> dict:
    if not raw_header_value:
        return {"spf": "none", "dkim": "none", "dmarc": "none"}
    try:
        header = AuthenticationResultsHeader.parse(
            "Authentication-Results: " + raw_header_value
        )
    except Exception:
        return {"spf": "unknown", "dkim": "unknown", "dmarc": "unknown"}

    out = {"spf": "none", "dkim": "none", "dmarc": "none"}
    for r in header.results:
        method = getattr(r, "method", None)
        if method in out:
            out[method] = r.result
    return out

def independently_verify_dkim(raw_eml_bytes: bytes) -> bool | None:
    """Real cryptographic re-check — network-path-independent.
    Returns None if the message has no DKIM signature to check."""
    if b"DKIM-Signature:" not in raw_eml_bytes:
        return None
    try:
        return dkim.verify(raw_eml_bytes)
    except Exception:
        return False

def check_domain_auth_hygiene(sender_domain: str) -> dict:
    """Does the domain even publish SPF/DMARC, and how strict?
    This is domain-policy hygiene, NOT a per-message pass/fail."""
    spf = checkdmarc.check_spf(sender_domain)
    dmarc = checkdmarc.check_dmarc(sender_domain)
    return {
        "publishes_spf": spf.get("valid", False),
        "spf_dns_lookups": spf.get("dns_lookups"),
        "publishes_dmarc": dmarc.get("valid", False),
        "dmarc_policy": (dmarc.get("tags", {}).get("p", {}).get("value")
                          if dmarc.get("valid") else None),
    }

def run_auth_checks(raw_eml_bytes: bytes, raw_ar_header: str | None,
                     sender_domain: str) -> AuthResult:
    ar = parse_authentication_results(raw_ar_header)
    hygiene = check_domain_auth_hygiene(sender_domain)
    return AuthResult(
        spf_result=ar["spf"],
        dkim_result=ar["dkim"],
        dmarc_result=ar["dmarc"],
        dkim_independently_verified=independently_verify_dkim(raw_eml_bytes),
        sender_publishes_spf=hygiene["publishes_spf"],
        sender_publishes_dmarc=hygiene["publishes_dmarc"],
        dmarc_policy=hygiene["dmarc_policy"],
        spf_dns_lookup_count=hygiene["spf_dns_lookups"],
    )
```

**Demo tip:** put this exact reasoning (why you don't naively re-run SPF)
as a slide bullet or a code comment the judges can see — technical panels
specifically probe "did you actually understand what SPF checking means"
and this is the single most common shortcut teams take that doesn't hold
up under questioning.

---

## Phase 3 — Dataset Preparation (Days 2–5, parallel with Phase 1–2)

**Owner:** Member 2 · Already scaffolded for you — see `dataset/` folder
in this repo.

- `dataset/starter_phishing_dataset.csv` — **6,000 real emails, balanced
  3,000 phishing / 3,000 legitimate**, merged from the Nazario Phishing
  Corpus, the Nigerian Fraud corpus, and the SpamAssassin public corpus
  (columns: `sender, receiver, date, subject, body, urls, label, source`).
  Good enough to build and unit-test the whole pipeline immediately.
- `dataset/fetch_full_dataset.sh` — pulls the full ~155 MB corpus
  (adds Enron, CEAS 2008, Ling-Spam) for final model training before the
  demo. Read `dataset/DATASET_README.md` for the label caveat (the source
  corpora label "phishing OR spam" as one class — worth a line in your
  report).

```python
# backend/app/nlp/prepare_dataset.py
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
```

---

## Phase 4 — NLP/ML Classification Engine (Days 5–12)

**Owner:** Member 2 (with Member 3 support on feature engineering) ·
**Depends on:** Phase 3

### Step 1 — Baseline (build this FIRST, always have a working model)

```python
# backend/app/nlp/train_baseline.py
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

    joblib.dump(vectorizer, "backend/models_store/tfidf_vectorizer.pkl")
    joblib.dump(clf, "backend/models_store/xgb_classifier.pkl")

if __name__ == "__main__":
    train()
```

### Step 2 — Rule-based feature boosts (these win demo points — cheap,
explainable, and directly map to the PS's own language: "urgency cues,
impersonation language, social-engineering patterns")

```python
# backend/app/nlp/heuristics.py
import re

URGENCY_PATTERNS = [
    r"\burgent\b", r"\bimmediately\b", r"\bwithin 24 hours\b",
    r"\baccount (suspended|locked|compromised)\b", r"\bverify your account\b",
    r"\bact now\b", r"\bfinal notice\b", r"\bclick here\b",
]
IMPERSONATION_PATTERNS = [
    r"\bsecurity team\b", r"\bIT (support|helpdesk)\b",
    r"\baccounts? (payable|department)\b", r"\bceo\b", r"\bwire transfer\b",
]

def urgency_score(text: str) -> float:
    text = text.lower()
    hits = sum(1 for p in URGENCY_PATTERNS if re.search(p, text))
    return min(hits / 3, 1.0)   # normalize 0-1

def impersonation_score(text: str) -> float:
    text = text.lower()
    hits = sum(1 for p in IMPERSONATION_PATTERNS if re.search(p, text))
    return min(hits / 2, 1.0)

def display_name_domain_mismatch(from_name: str, from_address: str) -> bool:
    """Classic BEC signal: display name claims a known brand/bank but the
    actual sending domain doesn't match it at all."""
    known_brands = ["paypal", "microsoft", "google", "bank", "amazon", "apple"]
    name_lower = from_name.lower()
    domain = from_address.split("@")[-1].lower() if "@" in from_address else ""
    for brand in known_brands:
        if brand in name_lower and brand not in domain:
            return True
    return False
```

### Step 3 (stretch, time-boxed) — DistilBERT fine-tune

> ⏱️ **Time-box this to a maximum of 2 days.** Only start this once the
> XGBoost baseline is trained, evaluated, and already wired into the
> backend end-to-end (Phase 7 working). A working baseline beats an
> unfinished transformer every time in a demo. If GPU access is limited,
> skip this and spend the time on Phase 8 (frontend polish) or Phase 10
> (testing) instead — judges reward a polished, working v1 over an
> ambitious but broken v2.

```python
# backend/app/nlp/train_distilbert.py  (stretch goal — see warning above)
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
```

### Inference wrapper (what the backend actually calls)

```python
# backend/app/nlp/classify.py
import joblib
from app.nlp.prepare_dataset import clean_body
from app.nlp.heuristics import urgency_score, impersonation_score, display_name_domain_mismatch

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
```

---

## Phase 5 — Origin Tracing: Relay Chain, GeoIP, Domain Intel (Days 5–12)

**Owner:** Member 3 · **Depends on:** Phase 1

### 5a. Walking the Received chain to find the real origin

This is the technical heart of the "forensic" half of the project — get
this right and it's your strongest differentiator from generic phishing
classifiers.

**Key insight:** `Received:` headers are prepended by every server the
message passes through. The headers closest to *your own trusted
infrastructure* (your mail gateway, or a major provider like Gmail/Outlook)
are trustworthy, because the attacker doesn't control that server. Headers
further down the chain (added earlier, further from you) **can be forged
by the attacker's own sending script** — so "walk from the trusted end
backward, stop at the first hop whose connecting IP is public and outside
anything you recognize as trusted infrastructure — that's your most
credible origin IP." Everything chronologically before that point is a
*claim*, not a fact, and should be labeled as such in the UI/report.

```python
# backend/app/origin/relay_trace.py
import re
import ipaddress

# Hostnames/domains you consider "trusted infra" (extend for your own org's
# mail gateway hostnames if deploying for a real inbox).
TRUSTED_INFRA_PATTERNS = [
    r"google\.com$", r"googlemail\.com$", r"outlook\.com$",
    r"protection\.outlook\.com$", r"amazonses\.com$", r"mail\.yahoo\.com$",
]

IP_PATTERN = re.compile(r"\[(\d{1,3}(?:\.\d{1,3}){3})\]")

def _extract_ip(field: str) -> str | None:
    m = IP_PATTERN.search(field or "")
    return m.group(1) if m else None

def _is_trusted_host(hostname: str) -> bool:
    return any(re.search(p, hostname or "") for p in TRUSTED_INFRA_PATTERNS)

def _is_public_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return not (addr.is_private or addr.is_loopback or addr.is_link_local)
    except ValueError:
        return False

def trace_origin(received_chain: list) -> dict:
    """received_chain must be ordered oldest(hop=1) -> newest, as produced
    by Phase 1's parser.py. We walk NEWEST -> OLDEST looking for the
    boundary between trusted and untrusted infrastructure."""
    chain_newest_first = list(reversed(received_chain))

    candidate_ip = None
    candidate_host = None
    boundary_hop = None
    unverified_claims = []

    for hop in chain_newest_first:
        by_host = hop.get("by", "")
        from_field = hop.get("from", "")
        ip = _extract_ip(from_field)

        if _is_trusted_host(by_host):
            # This hop was recorded by infrastructure we trust — its
            # record of who connected TO it is credible.
            if ip and _is_public_ip(ip):
                candidate_ip = ip
                candidate_host = from_field.split(" ")[0]
                boundary_hop = hop.get("hop")
                break
            # trusted infra handing off internally (e.g. Google's own
            # internal routing) — keep walking backward
            continue
        else:
            # Not (yet) inside trusted infra — keep walking, but note this
            # hop's self-reported origin as an unverified claim in case we
            # never reach a trusted boundary.
            if ip:
                unverified_claims.append({"host": from_field, "ip": ip})

    # everything chronologically before the boundary hop is attacker-
    # controllable and must be flagged as such
    claims_before_boundary = [
        {"host": h.get("from", ""), "ip": _extract_ip(h.get("from", ""))}
        for h in received_chain
        if boundary_hop is None or h.get("hop", 0) < boundary_hop
    ]

    return {
        "origin_ip": candidate_ip,
        "origin_host_claimed": candidate_host,
        "trust_boundary_hop": boundary_hop,
        "unverified_self_reported_hops": claims_before_boundary,
        "trace_confidence": "high" if candidate_ip else "low",
    }
```

### 5b. GeoIP lookup (MaxMind GeoLite2-City, offline `.mmdb`)

```python
# backend/app/origin/geoip_lookup.py
import geoip2.database

_reader = geoip2.database.Reader("backend/models_store/GeoLite2-City.mmdb")

def geolocate_ip(ip: str) -> dict:
    try:
        r = _reader.city(ip)
        return {
            "country": r.country.name,
            "city": r.city.name,
            "latitude": r.location.latitude,
            "longitude": r.location.longitude,
            "accuracy_radius_km": r.location.accuracy_radius,
        }
    except Exception:
        return {"country": None, "city": None, "latitude": None,
                "longitude": None, "accuracy_radius_km": None}
```

Download the database once (needs the free MaxMind license key from
Phase 0):
```bash
curl -sL "https://download.maxmind.com/geoip/databases/GeoLite2-City/download?suffix=tar.gz" \
  -u "ACCOUNT_ID:LICENSE_KEY" -o GeoLite2-City.tar.gz
tar -xzf GeoLite2-City.tar.gz --strip-components=1 --wildcards '*/GeoLite2-City.mmdb'
mv GeoLite2-City.mmdb backend/models_store/
```
Re-download monthly (MaxMind refreshes the free database regularly) — put
this in a `Makefile` target, not something anyone has to remember by hand.

### 5c. IP reputation + domain intel

```python
# backend/app/origin/domain_intel.py
import requests
import whois
import dns.resolver
from datetime import datetime, timezone
import os

ABUSEIPDB_KEY = os.environ["ABUSEIPDB_API_KEY"]
IPINFO_TOKEN = os.environ["IPINFO_TOKEN"]

def check_abuseipdb(ip: str) -> dict:
    resp = requests.get(
        "https://api.abuseipdb.com/api/v2/check",
        params={"ipAddress": ip, "maxAgeInDays": 90},
        headers={"Key": ABUSEIPDB_KEY, "Accept": "application/json"},
        timeout=5,
    )
    data = resp.json().get("data", {})
    return {
        "abuse_confidence_score": data.get("abuseConfidenceScore"),
        "is_tor": data.get("isTor"),
        "total_reports": data.get("totalReports"),
        "isp": data.get("isp"),
        "usage_type": data.get("usageType"),   # e.g. "Data Center/Web Hosting/Transit"
    }

def check_ipinfo_lite(ip: str) -> dict:
    # Free "Lite" tier: unlimited requests, country + ASN only.
    resp = requests.get(
        f"https://api.ipinfo.io/lite/{ip}", params={"token": IPINFO_TOKEN}, timeout=5
    )
    data = resp.json()
    return {"asn": data.get("asn"), "as_name": data.get("as_name"),
            "country": data.get("country")}

def domain_age_days(domain: str) -> int | None:
    try:
        w = whois.whois(domain)
        created = w.creation_date
        if isinstance(created, list):
            created = created[0]
        if created is None:
            return None
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - created).days
    except Exception:
        return None

def mx_hosting_mismatch(domain: str) -> bool:
    """Heuristic: does the domain's MX record point somewhere completely
    unrelated to the domain itself (common in freshly-stood-up phishing
    infra)? Simplified check — good enough for a hackathon MVP."""
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        mx_hosts = [str(r.exchange).rstrip(".") for r in mx_records]
        return not any(domain.split(".")[-2] in h for h in mx_hosts)
    except Exception:
        return False
```

---

## Phase 6 — Scoring & Correlation Engine (Days 10–14)

**Owner:** Member 4 · **Depends on:** Phases 2, 4, 5

### 6a. Weighted, explainable risk score

Keep every weight in one dict so it's tunable and — critically for a
judge Q&A — **explainable**: you should be able to show *why* a given
email scored 82/100, not just the number.

```python
# backend/app/scoring/risk_score.py

WEIGHTS = {
    "auth_fail": 20,             # SPF or DKIM or DMARC = fail
    "auth_missing": 8,           # no Authentication-Results at all
    "weak_dmarc_policy": 6,      # domain publishes DMARC but p=none
    "no_spf_dmarc_published": 6, # domain publishes neither
    "ml_phishing_probability": 30,   # scaled 0-1 -> 0-30
    "urgency_language": 6,
    "impersonation_language": 6,
    "display_name_mismatch": 8,
    "newly_registered_domain": 8,    # domain age < 90 days
    "abuse_confidence": 10,          # scaled 0-100 -> 0-10
    "hosting_type_flag": 6,          # datacenter/VPN/proxy rather than residential/ISP
    "mx_mismatch": 6,
}
# NOTE: max possible sum > 100 by design (signals overlap in real attacks);
# final score is capped at 100.

def compute_risk_score(auth: dict, nlp: dict, origin: dict, intel: dict) -> dict:
    breakdown = {}

    if "fail" in (auth["spf_result"], auth["dkim_result"], auth["dmarc_result"]):
        breakdown["auth_fail"] = WEIGHTS["auth_fail"]
    if auth["spf_result"] == auth["dkim_result"] == "none":
        breakdown["auth_missing"] = WEIGHTS["auth_missing"]
    if auth["dmarc_policy"] == "none":
        breakdown["weak_dmarc_policy"] = WEIGHTS["weak_dmarc_policy"]
    if not auth["sender_publishes_spf"] and not auth["sender_publishes_dmarc"]:
        breakdown["no_spf_dmarc_published"] = WEIGHTS["no_spf_dmarc_published"]

    breakdown["ml_phishing_probability"] = round(
        nlp["ml_phishing_probability"] * WEIGHTS["ml_phishing_probability"], 1
    )
    if nlp["urgency_score"] > 0.3:
        breakdown["urgency_language"] = WEIGHTS["urgency_language"]
    if nlp["impersonation_score"] > 0.3:
        breakdown["impersonation_language"] = WEIGHTS["impersonation_language"]
    if nlp["display_name_mismatch"]:
        breakdown["display_name_mismatch"] = WEIGHTS["display_name_mismatch"]

    if intel.get("domain_age_days") is not None and intel["domain_age_days"] < 90:
        breakdown["newly_registered_domain"] = WEIGHTS["newly_registered_domain"]
    if intel.get("abuse_confidence_score"):
        breakdown["abuse_confidence"] = round(
            intel["abuse_confidence_score"] / 100 * WEIGHTS["abuse_confidence"], 1
        )
    if intel.get("usage_type") and "hosting" in intel["usage_type"].lower():
        breakdown["hosting_type_flag"] = WEIGHTS["hosting_type_flag"]
    if intel.get("mx_mismatch"):
        breakdown["mx_mismatch"] = WEIGHTS["mx_mismatch"]

    total = min(sum(breakdown.values()), 100)
    return {"total_score": round(total), "breakdown": breakdown}
```

### 6b. Campaign correlation (shared IP / domain / reply-to → graph clustering)

```python
# backend/app/scoring/correlation.py
import networkx as nx

def build_campaign_graph(analyzed_emails: list[dict]) -> nx.Graph:
    """analyzed_emails: list of dicts each with keys
    'email_id', 'origin_ip', 'sender_domain', 'reply_to'."""
    G = nx.Graph()
    for e in analyzed_emails:
        G.add_node(e["email_id"], **e)

    by_ip, by_domain, by_reply_to = {}, {}, {}
    for e in analyzed_emails:
        by_ip.setdefault(e.get("origin_ip"), []).append(e["email_id"])
        by_domain.setdefault(e.get("sender_domain"), []).append(e["email_id"])
        by_reply_to.setdefault(e.get("reply_to"), []).append(e["email_id"])

    for grouping in (by_ip, by_domain, by_reply_to):
        for key, ids in grouping.items():
            if key and len(ids) > 1:
                for i in range(len(ids) - 1):
                    G.add_edge(ids[i], ids[i + 1], shared=key)
    return G

def get_campaigns(G: nx.Graph) -> list[list[str]]:
    """Each connected component with >1 email = a likely campaign."""
    return [list(c) for c in nx.connected_components(G) if len(c) > 1]
```

---

## Phase 7 — Backend API Integration (Days 12–16)

**Owner:** Member 4 (lead) + Member 1 · **Depends on:** everything above

```python
# backend/app/routes/analyze.py
from fastapi import APIRouter, UploadFile, File
from app.ingestion.parser import parse_eml
from app.auth_check.verifier import run_auth_checks
from app.nlp.classify import classify_email
from app.origin.relay_trace import trace_origin
from app.origin.geoip_lookup import geolocate_ip
from app.origin.domain_intel import (
    check_abuseipdb, check_ipinfo_lite, domain_age_days, mx_hosting_mismatch,
)
from app.scoring.risk_score import compute_risk_score

router = APIRouter()

@router.post("/api/analyze")
async def analyze_email(file: UploadFile = File(...)):
    raw = await file.read()
    parsed = parse_eml(raw)
    sender_domain = parsed.from_address.split("@")[-1]

    auth = run_auth_checks(raw, parsed.raw_authentication_results, sender_domain)
    nlp = classify_email(parsed.subject, parsed.body, parsed.from_name, parsed.from_address)
    origin = trace_origin(parsed.received_chain)

    geo, abuse, ipinfo = {}, {}, {}
    if origin["origin_ip"]:
        geo = geolocate_ip(origin["origin_ip"])
        abuse = check_abuseipdb(origin["origin_ip"])
        ipinfo = check_ipinfo_lite(origin["origin_ip"])

    intel = {
        **abuse, **ipinfo,
        "domain_age_days": domain_age_days(sender_domain),
        "mx_mismatch": mx_hosting_mismatch(sender_domain),
    }

    score = compute_risk_score(auth.__dict__, nlp, origin, intel)

    return {
        "parsed": parsed.__dict__,
        "auth": auth.__dict__,
        "nlp": nlp,
        "origin": {**origin, "geolocation": geo},
        "intel": intel,
        "risk_score": score,
    }
```

Wire it up:
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import analyze, campaigns, reports

app = FastAPI(title="SIH26106 Email Forensics API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(analyze.router)
app.include_router(campaigns.router)
app.include_router(reports.router)
```

`/docs` (FastAPI's auto-generated Swagger UI) is a genuinely good thing to
have open during the judge demo — it doubles as live API documentation.

---

## Phase 8 — Frontend React Dashboard (Days 12–18)

**Owner:** Member 5 · **Depends on:** Phase 7 API contract (agree on the
JSON shape above EARLY — Day 10 — so frontend isn't blocked)

Core screens: (1) upload panel, (2) risk score gauge + auth badges,
(3) relay path map, (4) campaign graph view.

```jsx
// frontend/src/components/RiskGauge.jsx
import { RadialBarChart, RadialBar, PolarAngleAxis } from "recharts";

export default function RiskGauge({ score }) {
  const color = score >= 70 ? "#dc2626" : score >= 40 ? "#f59e0b" : "#16a34a";
  const data = [{ name: "risk", value: score, fill: color }];
  return (
    <RadialBarChart width={220} height={220} innerRadius={70} outerRadius={100}
      data={data} startAngle={90} endAngle={-270}>
      <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
      <RadialBar dataKey="value" cornerRadius={10} background clockWise />
      <text x={110} y={110} textAnchor="middle" fontSize={32} fontWeight="bold" fill={color}>
        {score}
      </text>
    </RadialBarChart>
  );
}
```

```jsx
// frontend/src/components/RelayMap.jsx
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function RelayMap({ geolocation, originIp }) {
  if (!geolocation?.latitude) return <p className="text-gray-500">No origin IP resolved.</p>;
  const pos = [geolocation.latitude, geolocation.longitude];
  return (
    <MapContainer center={pos} zoom={4} style={{ height: 320, width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <Marker position={pos}>
        <Popup>
          Origin IP: {originIp}<br />
          {geolocation.city}, {geolocation.country}
        </Popup>
      </Marker>
    </MapContainer>
  );
}
```

```jsx
// frontend/src/components/UploadPanel.jsx
import { useState } from "react";
import axios from "axios";

export default function UploadPanel({ onResult }) {
  const [loading, setLoading] = useState(false);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    const form = new FormData();
    form.append("file", file);
    const res = await axios.post("/api/analyze", form);
    onResult(res.data);
    setLoading(false);
  }

  return (
    <div className="p-4 border-2 border-dashed rounded-xl text-center">
      <input type="file" accept=".eml" onChange={handleUpload} />
      {loading && <p className="text-sm text-gray-500 mt-2">Analyzing…</p>}
    </div>
  );
}
```

`AuthBadges.jsx` and `CampaignGraph.jsx` follow the same pattern — small,
focused components consuming the JSON from `/api/analyze`. Keep the API
contract as the shared interface: agree on it in a doc/Slack thread on
Day 10 so backend and frontend can build in parallel without blocking
each other.

---

## Phase 9 — PDF Forensic Report Generation (Days 16–19)

**Owner:** Member 6 · **Depends on:** Phase 7

```python
# backend/app/reports/pdf_report.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO

def generate_forensic_report(analysis: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Email Forensic Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    score = analysis["risk_score"]["total_score"]
    elements.append(Paragraph(f"<b>Risk Score:</b> {score}/100", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("Score Breakdown", styles["Heading3"]))
    rows = [["Signal", "Points"]] + [
        [k, str(v)] for k, v in analysis["risk_score"]["breakdown"].items()
    ]
    t = Table(rows, colWidths=[300, 100])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Authentication Results", styles["Heading3"]))
    auth = analysis["auth"]
    elements.append(Paragraph(
        f"SPF: {auth['spf_result']} | DKIM: {auth['dkim_result']} "
        f"(independently re-verified: {auth['dkim_independently_verified']}) | "
        f"DMARC: {auth['dmarc_result']}", styles["Normal"]
    ))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Origin Trace", styles["Heading3"]))
    origin = analysis["origin"]
    geo = origin.get("geolocation", {})
    elements.append(Paragraph(
        f"Origin IP: {origin.get('origin_ip')} "
        f"({geo.get('city')}, {geo.get('country')}) — "
        f"trace confidence: {origin.get('trace_confidence')}", styles["Normal"]
    ))
    if origin.get("unverified_self_reported_hops"):
        elements.append(Paragraph(
            "⚠ The following relay hops were self-reported by the sending "
            "path and could not be independently verified:", styles["Normal"]
        ))
        for hop in origin["unverified_self_reported_hops"]:
            elements.append(Paragraph(f"— {hop['host']}", styles["Normal"]))

    doc.build(elements)
    return buf.getvalue()
```

```python
# backend/app/routes/reports.py
from fastapi import APIRouter
from fastapi.responses import Response
from app.reports.pdf_report import generate_forensic_report

router = APIRouter()

@router.post("/api/reports/generate")
async def generate_report(analysis: dict):
    pdf_bytes = generate_forensic_report(analysis)
    return Response(content=pdf_bytes, media_type="application/pdf",
                     headers={"Content-Disposition": "attachment; filename=forensic_report.pdf"})
```

---

## Phase 10 — Testing, Integration, Deployment, Demo Prep (Days 18–24)

**Owner:** Member 6 (lead) + whole team

1. **Unit tests** per module (`backend/tests/`) — parser, auth checker,
   scoring formula (test with hand-crafted input dicts, not just live
   emails), relay tracer (use the fixture `.eml` files from Phase 1).
2. **Integration test** — one script that runs a fixture `.eml` through
   the entire `/api/analyze` pipeline end-to-end and asserts a sane score
   range.
3. **CI** — GitHub Actions running `pytest` on every PR (see workflow
   below).
4. **Load a "campaign" demo set** — analyze 5–6 fixture emails that
   deliberately share an origin IP or reply-to address, so the campaign
   clustering view has something to show live.
5. **`docker-compose up`** should be the ONLY command needed to run the
   full stack for judges — test this on a clean machine (or at least a
   fresh clone) before the demo, not just on dev laptops with leftover
   local state.
6. **Demo script** (`docs/demo_script.md`) — a scripted 3-minute walk-
   through: upload a spoofed email → show auth fail badges → show NLP
   score → show relay map pinning a foreign IP → show final risk score →
   download PDF → show a campaign cluster of 3 related emails. Rehearse
   this exact sequence, don't improvise live.

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest -v
  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: cd frontend && npm install && npm run build
```

---

## 11. Team Task Allocation — 6 Members

| # | Role | Owns (phases) | Primary files |
|---|---|---|---|
| **1** | Ingestion & Auth Lead | Phase 1, Phase 2 | `ingestion/parser.py`, `auth_check/verifier.py` |
| **2** | ML/NLP Lead | Phase 3, Phase 4 | `nlp/*` |
| **3** | Forensics/OSINT Lead | Phase 5 | `origin/*` |
| **4** | Backend/Integration Lead | Phase 6, Phase 7 | `scoring/*`, `routes/*`, `main.py` |
| **5** | Frontend Lead | Phase 8 | `frontend/src/*` |
| **6** | QA/DevOps/Reporting Lead | Phase 9, Phase 10 | `reports/*`, CI, Docker, demo prep |

Everyone touches Phase 0 together on Day 1. From Day 10 onward, Member 4
(Backend/Integration) is the connective tissue — they should sync daily
with Members 1, 2, 3 (whose modules feed into `/api/analyze`) and with
Member 5 (who consumes its output).

**Suggested weekly rhythm** (compress/stretch to your actual SIH
timeline — this assumes roughly 4 weeks):

| Week | Focus |
|---|---|
| 1 | Phase 0 (all) → Phases 1, 2, 3 in parallel |
| 2 | Phases 4, 5 in parallel; Member 4 starts scaffolding Phase 7 against mocked module outputs |
| 3 | Phase 6, real Phase 7 integration, Phase 8 (frontend) starts against the real API |
| 4 | Phase 9, Phase 10, buffer days for integration bugs, rehearse the demo script at least twice |

---

## 12. GitHub Collaboration Workflow

**Branching:** `main` (protected, only merges via PR) →
`dev` (integration branch) → feature branches `feat/<phase>-<short-desc>`
(e.g. `feat/phase2-dkim-verify`).

```
main  ← protected, only PRs from dev, requires 1 approval
 └── dev  ← daily integration
      ├── feat/phase1-eml-parser
      ├── feat/phase2-auth-verifier
      ├── feat/phase4-baseline-classifier
      ├── feat/phase5-relay-trace
      ├── feat/phase7-analyze-endpoint
      └── feat/phase8-dashboard-ui
```

**Commit convention** (Conventional Commits — makes the repo history
readable for judges skimming it):
```
feat(auth): add authres-based Authentication-Results parsing
fix(scoring): cap total risk score at 100
test(parser): add fixtures for lookalike-domain email
docs(readme): add setup instructions
```

**PR template** (`.github/PULL_REQUEST_TEMPLATE.md`):
```markdown
## What
<!-- one-line summary -->

## Phase / Module
<!-- e.g. Phase 5 — origin/relay_trace.py -->

## Testing done
- [ ] Unit tests added/updated
- [ ] Ran against fixture .eml files
- [ ] No secrets/API keys committed

## Screenshots (if frontend)
```

**Issue labels:** `phase-1` … `phase-10`, `bug`, `blocked`, `good-first-
issue` (for the two lighter days each member will have), `demo-critical`
(reserve this for the handful of things that MUST work for the live demo
— triage these first if time runs short).

**Project board columns:** `Backlog` → `In Progress` → `Review` →
`Done`. Run a 10-minute daily standup (async in Slack/Discord is fine) —
just answer: what I did yesterday, what I'm doing today, what's blocking
me. This alone prevents the classic hackathon failure mode of two people
duplicating work on the same module.

---

## 13. External Services & Signup Checklist

| Service | Free tier | Signup | Used in |
|---|---|---|---|
| MaxMind GeoLite2 | Free account + license key, no per-request limit (local `.mmdb` file, refresh monthly) | maxmind.com/en/geolite2/signup | Phase 5 |
| AbuseIPDB | 1,000 IP checks/day, no credit card | abuseipdb.com/register | Phase 5 |
| IPinfo | "Lite" tier: unlimited requests, country+ASN fields only (full city-level data needs a paid Core plan — use MaxMind for that instead) | ipinfo.io/signup | Phase 5 |

Do all three signups on Day 1 (Phase 0) — nothing in Phase 5 should be
blocked waiting on an account approval in week 2.

---

## 14. Risk Register — Known Pitfalls (read before you hit them)

- **Don't put `pyspf` in requirements.txt.** Its `pydns` dependency is
  broken on modern Python 3. Phase 2's tiered approach (Authentication-
  Results parsing + independent DKIM re-check + domain policy hygiene)
  avoids needing it at all, and is also the more defensible design
  when a judge asks "how does per-message SPF actually work."
- **DistilBERT is a stretch goal, not the baseline.** Time-box it to 2
  days max, and only after the XGBoost baseline is fully wired into the
  live pipeline. An unfinished transformer model demos worse than a
  working TF-IDF+XGBoost one.
- **Agree on the `/api/analyze` JSON contract by Day 10**, even before
  every module is fully done — mock the shape with dummy data so
  frontend (Member 5) isn't blocked waiting on backend integration.
- **The `SpamAssassin`/`Enron`/`CEAS`-derived labels mean "phishing OR
  spam"**, not phishing specifically — mention this limitation
  proactively in your report; judges respect teams that name their own
  dataset's limitations rather than overclaiming.
- **GeoIP accuracy has real limits** — MaxMind's own docs are explicit
  that geolocation is often nearest-population-center, not exact. Don't
  overclaim precision in the demo; frame it as "likely origin region /
  hosting provider," which is also what real investigators actually rely
  on.
- **Re-download the GeoLite2 database monthly** — MaxMind updates it
  regularly and stale data silently degrades accuracy without erroring.
- **Test `docker-compose up` on a clean checkout before the demo**, not
  just on dev machines that already have caches/venvs/env vars set up
  from earlier debugging.

---

## 15. Mapping Back to What SIH Judges Actually Score

- **Technical depth beyond a generic classifier:** the SPF/DKIM/DMARC
  nuance in Phase 2 and the trust-boundary relay-walk in Phase 5 are your
  strongest talking points if a technical judge probes "how is this
  different from a spam filter."
- **Working, demoable end-to-end system:** phase ordering above is
  deliberately sequenced so you have a complete (if rough) pipeline
  working by end of week 2, with weeks 3–4 for polish — not a set of
  disconnected modules finished separately at the last minute.
- **Explainability:** the weighted, itemized risk-score breakdown (Phase
  6a) — being able to say "this scored 82 because of X, Y, Z" — matters
  more to most panels than a marginally higher raw model accuracy number.
- **Real dataset provenance, honestly described:** cite Nazario/Enron/
  CEAS by name (see `dataset/DATASET_README.md`) and name the known label
  caveat rather than hiding it.
