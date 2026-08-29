# QA and DevOps Test Report

**Owner:** Member 6 — QA/DevOps/Reporting  
**Project:** SIH26106 Email Forensics Platform

## Automated checks

| Check | Command | Expected result |
|---|---|---|
| Backend unit tests | `cd backend && PYTHONPATH=. python -m pytest -v` | All tests pass |
| PDF report generation | Included in the backend test suite | A valid PDF byte stream is produced |
| Frontend production build | `cd frontend && npm ci && npm run build` | Vite completes without errors |
| CI pipeline | GitHub Actions on push/PR | Backend tests and frontend build both pass |

## Docker acceptance check

Run the following from the repository root:

```bash
docker compose up --build
```

Open `http://localhost:5173` for the dashboard and `http://localhost:8000/docs` for API documentation. The frontend mapping is `5173:80` because its production container uses nginx on port 80.

## Manual demo checks

| Scenario | Expected outcome |
|---|---|
| Upload `backend/tests/fixtures/spoofed_bank.eml` | Analysis finishes and shows a high-risk result |
| Upload `backend/tests/fixtures/legit_newsletter.eml` | Analysis finishes and returns lower risk than the spoofed email |
| Generate forensic report | Browser downloads a readable PDF report |
| View API docs | `/docs` loads and the health endpoint returns `{"status":"ok"}` |

## Test environment note

Run the commands above on a computer with Python 3.11, Node.js 20, and Docker Desktop installed. GitHub Actions performs the automated checks on every push and pull request.
