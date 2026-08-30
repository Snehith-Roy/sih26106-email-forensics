# SIH26106 — Demo Script (3-Minute Walkthrough)

> **For the team:** Rehearse this exact sequence at least twice before demo day.
> Don't improvise — judges reward precision over flash.

---

## Pre-Demo Checklist (2 minutes before)

- [ ] Backend running: `uvicorn app.main:app --reload`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] Browser open to `http://localhost:5173`
- [ ] Test `.eml` files ready in `backend/tests/fixtures/`:
  - `spoofed_bank.eml` (phishing — should score HIGH)
  - `legit_newsletter.eml` (legit — should score LOW)
- [ ] FastAPI docs tab open at `http://localhost:8000/docs`

---

## Minute 1 — Upload & Risk Score

**Say:** *"Our platform ingests a raw `.eml` file and runs a multi-signal forensic analysis in under 2 seconds."*

1. **Drag and drop** `spoofed_bank.eml` onto the dashboard
2. **Point to the risk gauge:** *"The system assigns an explainable 0–100 risk score. This email scores [X]/100 — classified as [HIGH/MEDIUM/LOW] risk."*
3. **Highlight the score breakdown:** *"Every signal contributes points — you can see exactly WHY it scored this way."*

---

## Minute 2 — Authentication & NLP

**Say:** *"We verify sender authenticity using three independent checks."*

4. **Point to auth badges (SPF/DKIM/DMARC):** *"SPF checks if the sending IP was authorized. DKIM re-verifies the cryptographic signature. DMARC checks the domain's policy. All three are parsed from the real `Authentication-Results` header — we don't naively re-run SPF, which is a common mistake."*
5. **Point to NLP analysis:** *"Our ML classifier (TF-IDF + XGBoost, trained on 6,000 emails) gives a phishing probability. Combined with rule-based heuristics — urgency cues, impersonation language, display name mismatches."*

---

## Minute 3 — Origin Trace & Campaign

**Say:** *"We trace the email back to its most credible origin IP."*

6. **Point to the relay map:** *"The map pins the origin IP's geographic location. We walk the Received header chain backward from trusted infrastructure (Gmail, Outlook) to find the first untrusted hop — that's the real sender."*
7. **Point to relay timeline:** *"Each hop is marked as verified (green) or unverified claim (red). Attacker-controlled headers are flagged."*
8. **Point to campaign graph:** *"When multiple emails share an origin IP or domain, they cluster into a campaign — useful for tracking persistent threat actors."*

---

## Closing (15 seconds)

**Say:** *"The full pipeline — parse, authenticate, classify, trace, score — runs in under 2 seconds. PDF reports are downloadable with one click. The entire stack runs in Docker with a single `docker-compose up` command."*

**If judges ask about SPF:** *"We don't re-run SPF because it requires the live connecting IP, which only the receiving MTA had. We parse the `Authentication-Results` header instead — that's the ground truth from the actual mail server."*

**If judges ask about scalability:** *"The scoring weights are tunable and explainable. The correlation engine uses graph clustering to link related emails. The DB persists all analyses for campaign tracking."*

---

## Key Differentiators to Emphasize

1. **Explainable scoring** — not a black box, every signal has a weight
2. **Real DKIM re-verification** — cryptographic check, not just header parsing
3. **Relay chain forensics** — walks backward from trusted infra, flags unverified claims
4. **Campaign clustering** — links related emails via shared IP/domain/reply-to
5. **One-command Docker demo** — judges can run it themselves
