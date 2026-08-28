#!/usr/bin/env bash
# ==============================================================================
# fetch_full_dataset.sh
# Downloads the FULL combined phishing/legitimate email dataset (~155 MB, 7 CSVs)
# for SIH26106 - AI-Powered Email Threat Detection Platform.
#
# The starter_phishing_dataset.csv in this folder (6,000 rows, balanced,
# ~7.5 MB) is already extracted from this same source and is enough to build
# and sanity-test the pipeline (Phase 3-4). Run THIS script only when you're
# ready to train the final model on the full corpus for better accuracy
# (Phase 4, final training pass before demo).
#
# Source: rokibulroni/Phishing-Email-Dataset (GitHub), licensed CC BY-SA 4.0.
# It aggregates 7 well-known public phishing/spam research corpora into one
# consistent schema: sender, receiver, date, subject, body, urls, label
# (label: 1 = phishing/spam, 0 = legitimate).
#   - Nazario Phishing Corpus      (~1,560 phishing emails)
#   - Nigerian Fraud / "419" corpus (~3,330 phishing emails)
#   - SpamAssassin public corpus    (~7,860 mixed emails)
#   - Enron email corpus            (~45 MB, mostly legitimate)
#   - CEAS 2008 Spam Challenge      (~68 MB, mixed)
#   - Ling-Spam corpus              (~9 MB, mixed)
#   - Combined PhishingEmailData.csv (small extra sample)
#
# Cite these original sources in your SIH report/PPT, not just the mirror repo.
# ==============================================================================

set -e

REPO_URL="https://github.com/rokibulroni/Phishing-Email-Dataset.git"
DEST_DIR="$(dirname "$0")/full_corpus"

echo ">> Cloning full dataset repo (this pulls ~155 MB, may take a few minutes)..."
git clone --depth 1 "$REPO_URL" "$DEST_DIR"

echo ""
echo ">> Files downloaded:"
ls -lh "$DEST_DIR"/*.csv

echo ""
echo ">> Done. Point your training script's --data-dir at: $DEST_DIR"
echo ">> Recommended: keep full_corpus/ out of git (add to .gitignore) — it's"
echo "   too large for a normal repo. Each teammate runs this script locally,"
echo "   or you host it once on Google Drive / Kaggle and share a link."
