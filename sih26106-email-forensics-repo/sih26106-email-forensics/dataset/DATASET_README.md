# Dataset — SIH26106 Email Threat Detection

This folder contains a **real, ready-to-use starter dataset** for the NLP/ML
phishing classifier (Phase 4), plus a script to pull the full corpus later.

## `starter_phishing_dataset.csv`

- **6,000 emails, perfectly balanced** — 3,000 phishing/spam (`label=1`),
  3,000 legitimate (`label=0`).
- Built by merging and deduplicating three public research corpora
  (Nazario Phishing Corpus, Nigerian Fraud corpus, SpamAssassin public
  corpus), shuffled, with email bodies truncated to 1,500 characters to
  keep the file lightweight (~7.5 MB) for cloning and quick iteration.
- **Columns:** `sender, receiver, date, subject, body, urls, label, source`
  - `urls` = count of URLs found in the body (already extracted upstream).
  - `source` = which original corpus the row came from (useful for
    stratified splitting / error analysis by source).
- Good for: fast prototyping, unit tests, TF-IDF+XGBoost baseline (Phase 4,
  week 1), CI pipeline smoke tests.
- **Not** enough on its own for a strong final model — it's a starter, not
  the full corpus.

## Getting the full corpus (for final training)

Run:
```bash
chmod +x fetch_full_dataset.sh
./fetch_full_dataset.sh
```
This clones the full ~155 MB source repo into `dataset/full_corpus/`,
giving you 7 CSVs (Nazario, Nigerian_Fraud, SpamAssasin, Enron, CEAS_08,
Ling, PhishingEmailData) with the same `sender/receiver/date/subject/body/
urls/label` schema. Combine and rebalance them the same way
`starter_phishing_dataset.csv` was built (see
`ml/prepare_dataset.py` in the main roadmap) — but keep more rows, and
consider keeping the class ratio closer to real-world (phishing is the
minority class in real inboxes) once you move from prototyping to
final evaluation.

**Do not commit `full_corpus/` to git** — add it to `.gitignore`. It's too
big for a normal repo and everyone can regenerate it locally with the
script. If you want one shared copy for the whole team, upload it once to
Google Drive / Kaggle Datasets and drop the link in your repo's `README.md`
instead.

## Source & license

Mirrored on GitHub at `rokibulroni/Phishing-Email-Dataset`
(CC BY-SA 4.0), which itself aggregates these original public datasets:

| Corpus | Original source | Emails |
|---|---|---|
| Nazario Phishing Corpus | J. Nazario, `monkey.org/~jose/phishing/` | ~1,560 |
| Nigerian Fraud ("419") | Public fraud-email archive | ~3,330 |
| SpamAssassin public corpus | Apache SpamAssassin project | ~6,050 |
| Enron Email Corpus | CMU / FERC investigation release | ~500k (subset used) |
| CEAS 2008 | 2008 Spam Challenge (Conference on Email & Anti-Spam) | ~39k |
| Ling-Spam | Linguist mailing list corpus | ~2,900 |

**Cite the original corpora** (table above) in your SIH report and PPT —
that's standard academic practice and panels notice it. Mentioning "we used
a mirror on GitHub" alone looks weaker than naming Nazario/Enron/CEAS by
name with citations, which also signals you understand the data provenance
(a small but real credibility signal for a forensics-focused problem
statement).

## A known label caveat — mention this in your report

`label=1` in this schema means "phishing OR spam" (not phishing
specifically) for the SpamAssassin/Enron/CEAS-derived rows — the original
corpora conflate the two. For a *phishing/BEC*-focused classifier, expect
some noise (e.g. bulk marketing spam labeled the same as credential-theft
phishing). Two options, both defensible in a demo:
1. **Ship it as-is** and describe the model as "phishing + fraud + social-
   engineering spam" detection — matches the SIH problem statement's
   language about "phishing/spoofed/fraudulent" emails reasonably well.
2. **Time-box a manual/heuristic re-labeling pass** on a few hundred
   borderline SpamAssassin rows if a teammate has spare cycles — good
   "extra credit" for the demo but not required to hit a working v1.
