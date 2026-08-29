# Three-Minute Demo Script

## Before presenting

Run `docker compose up --build`, then open the dashboard at `http://localhost:5173` and API docs at `http://localhost:8000/docs`.

## Demo

1. **Introduce the problem (20 seconds).** Explain that phishing investigations need more than a spam label: analysts need content, authentication, and origin evidence together.
2. **Upload a suspicious email (30 seconds).** Upload `backend/tests/fixtures/spoofed_bank.eml` from the dashboard.
3. **Explain the results (60 seconds).** Point out the risk score, SPF/DKIM/DMARC results, suspicious content indicators, and the relay/origin trace. State that unverified relay hops are treated as claims, not facts.
4. **Show the report (30 seconds).** Generate/download the PDF forensic report and show its score breakdown, authentication section, and origin summary.
5. **Show technical readiness (25 seconds).** Open `/docs` and mention the automated GitHub Actions pipeline, backend tests, frontend build check, and Docker one-command deployment.
6. **Close (15 seconds).** Summarize that the platform converts a raw email into explainable evidence an analyst can review and export.

## Backup plan

Keep the two fixture emails open in File Explorer. If external GeoIP or reputation credentials are unavailable, explain that the application degrades gracefully and still demonstrates parsing, authentication evidence, scoring, and PDF export.
