# SIH26106 — AI-Powered Email Threat Detection, GeoLocation & Forensic Intelligence Platform

An AI-powered email forensic platform that combines phishing/BEC content
classification (NLP/ML) with technical origin tracing (SPF/DKIM/DMARC
forensics, relay-chain analysis, GeoIP, domain reputation) into one
explainable risk score and analyst dashboard.

**Full build plan:** see [`IMPLEMENTATION.md`](./IMPLEMENTATION.md) — every
phase, owner, and starter code lives there. Read it before opening your
first PR.

## Team

| Member | Role | Owns |
|---|---|---|
| _(name)_ | Ingestion & Auth Lead | Phase 1, 2 |
| _(name)_ | ML/NLP Lead | Phase 3, 4 |
| _(name)_ | Forensics/OSINT Lead | Phase 5 |
| _(name)_ | Backend/Integration Lead | Phase 6, 7 |
| _(name)_ | Frontend Lead | Phase 8 |
| _(name)_ | QA/DevOps/Reporting Lead | Phase 9, 10 |

_(Fill in names above once the repo is up — first PR.)_

## Quickstart

```bash
git clone <this-repo-url>
cd sih26106-email-forensics

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Or, once Docker files are added (Phase 0 in `IMPLEMENTATION.md`):
```bash
docker-compose up
```

## Dataset

A ready-to-use starter dataset is already in `dataset/` — see
[`dataset/DATASET_README.md`](./dataset/DATASET_README.md).

## Contributing

- Branch off `dev`, not `main`: `feat/phase<N>-<short-desc>`
- Follow Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`)
- Fill out the PR template — every PR needs at least 1 approval before
  merging into `dev`
- See `IMPLEMENTATION.md` §12 for the full workflow
