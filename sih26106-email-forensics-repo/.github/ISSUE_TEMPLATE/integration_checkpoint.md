---
name: Mid-point Integration Checkpoint
about: Day 12 (end of Week 2) — plug everyone's real modules together early
title: "[CHECKPOINT] Mid-point integration — Day 12"
labels: demo-critical
---

**Owner:** Member 4 (Backend/Integration Lead)
**Target date:** end of Week 2 (Day 12) — adjust to your actual timeline

## Why this issue exists

Everyone builds solo against agreed data shapes, which is efficient but
means the team never sees the real pieces connected until someone tries
it. This checkpoint makes that attempt happen deliberately, at the
halfway point — not the night before the demo.

## What to do

- [ ] Every member pushes their current branch, even if incomplete
- [ ] Member 4 swaps mock data in `backend/app/routes/analyze.py` for
      real imports:
  - [ ] `app.ingestion.parser` (Member 1)
  - [ ] `app.auth_check.verifier` (Member 1)
  - [ ] `app.nlp.classify` (Member 2)
  - [ ] `app.origin.relay_trace` (Member 3)
  - [ ] `app.origin.geoip_lookup` / `domain_intel` (Member 3)
- [ ] Run `PYTHONPATH=. pytest -v` in `backend/` against real modules
      (not just the fixture-based tests)
- [ ] Run the two fixture `.eml` files in
      `backend/tests/fixtures/` through the real `/api/analyze` endpoint
      end-to-end
- [ ] Note any shape mismatches below (renamed field, unexpected `None`,
      different key name, etc.)

## Mismatches found (fill in during the checkpoint)

| Module | Expected shape | Actual shape | Fix owner |
|---|---|---|---|
| | | | |

## Outcome

- [ ] ✅ Integration works — continue as planned
- [ ] ⚠️ Mismatches found — fixes assigned above, re-check by: _____
