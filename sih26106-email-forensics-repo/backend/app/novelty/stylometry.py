"""
Feature 1 — Stylometric author linking.

Extends the existing campaign-correlation graph (scoring/correlation.py)
with a new edge type based on WRITING STYLE rather than infrastructure.

Two emails from completely different servers can still be linked as
"probably the same author" if they share the same writing habits.
"""

import re
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Function words — the strongest, most attacker-hard-to-fake signal
# Function words are subconscious and rarely varied deliberately
FUNCTION_WORDS = [
    "the", "of", "and", "to", "in", "a", "is", "that", "it", "for",
    "on", "with", "as", "was", "at", "by", "this", "be", "or", "an",
    "will", "your", "please", "we", "you", "our", "if", "not",
]

GREETING_PATTERNS = [r"^dear\s+\w+", r"^hi\s+\w*", r"^hello\s*"]
SIGNOFF_PATTERNS = [
    r"regards,?\s*$", r"best,?\s*$", r"sincerely,?\s*$",
    r"thank you,?\s*$", r"thanks,?\s*$",
]


def extract_stylometric_vector(body: str) -> np.ndarray:
    """
    Extract a fixed-length numeric vector describing writing style,
    independent of topic/content.
    
    Features:
        - Average sentence length (words)
        - Average word length (characters)
        - Type-token ratio (vocabulary richness)
        - Punctuation frequency per 100 words
        - Capitalization ratio
        - Average paragraph length
        - Has greeting pattern
        - Has sign-off pattern
        - Function word frequencies (27 features)
    """
    text = body.strip()
    if not text:
        return np.zeros(8 + len(FUNCTION_WORDS))

    sentences = re.split(r"[.!?]+\s+", text)
    sentences = [s for s in sentences if s.strip()]
    words = re.findall(r"[a-zA-Z']+", text.lower())
    all_words = re.findall(r"[a-zA-Z']+", text)  # keep case for caps check
    paragraphs = [p for p in text.split("\n\n") if p.strip()]

    if not words:
        return np.zeros(8 + len(FUNCTION_WORDS))

    avg_sentence_len = np.mean([len(re.findall(r"[a-zA-Z']+", s)) for s in sentences]) if sentences else 0
    avg_word_len = np.mean([len(w) for w in words])
    type_token_ratio = len(set(words)) / len(words)
    punct_counts = {p: text.count(p) for p in ["!", "?", "...", "-"]}
    punct_freq = sum(punct_counts.values()) / max(len(words), 1) * 100
    caps_ratio = sum(1 for w in all_words if w.isupper() and len(w) > 1) / max(len(all_words), 1)
    avg_para_len = np.mean([len(p.split()) for p in paragraphs]) if paragraphs else len(words)

    has_greeting = any(re.search(p, text.lower()) for p in GREETING_PATTERNS)
    has_signoff = any(re.search(p, text.lower()) for p in SIGNOFF_PATTERNS)

    base_features = [
        avg_sentence_len, avg_word_len, type_token_ratio, punct_freq,
        caps_ratio, avg_para_len, float(has_greeting), float(has_signoff),
    ]

    word_count = len(words)
    fw_freqs = [words.count(fw) / word_count for fw in FUNCTION_WORDS]

    return np.array(base_features + fw_freqs)


def stylometric_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Cosine similarity between two stylometric vectors.
    
    Returns:
        float: 1.0 = identical writing style, 0.0 = completely different
    """
    norm_a, norm_b = np.linalg.norm(vec_a), np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def link_by_style(analyzed_emails: list[dict], threshold: float = 0.85) -> list[tuple]:
    """
    Link emails by writing style similarity.
    
    Args:
        analyzed_emails: list of dicts with 'email_id' and 'body'
        threshold: cosine similarity threshold (default 0.85)
    
    Returns:
        list of (email_id_a, email_id_b, similarity) tuples above threshold
        — feed these as extra edges into correlation.py's build_campaign_graph()
    """
    vectors = {
        e["email_id"]: extract_stylometric_vector(e["body"])
        for e in analyzed_emails
    }
    ids = list(vectors.keys())
    links = []
    
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            sim = stylometric_similarity(vectors[ids[i]], vectors[ids[j]])
            if sim >= threshold:
                links.append((ids[i], ids[j], round(sim, 3)))
    
    return links
