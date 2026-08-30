# Final Project Report — Email Forensics Platform

## Problem addressed

Phishing and business-email-compromise messages can look legitimate while hiding authentication failures, malicious wording, suspicious infrastructure, and forged relay data. This platform brings those signals together in one analyst workflow.

## Solution

The application accepts a raw `.eml` email and produces an explainable forensic analysis. It parses headers and body content, checks SPF/DKIM/DMARC evidence, evaluates phishing and social-engineering indicators, traces the email relay path, and combines results into a risk score. The React dashboard presents the findings, and the report endpoint produces a downloadable PDF.

## Architecture

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React, Vite | Upload workflow and analyst dashboard |
| Backend | FastAPI | Analysis, scoring, reporting APIs |
| Forensics | Python libraries | Parsing, authentication checks, relay/origin tracing |
| Reporting | ReportLab | Downloadable PDF forensic report |
| Deployment | Docker Compose | One-command local deployment |
| Quality | Pytest and GitHub Actions | Automated backend tests and frontend build validation |

## Demonstrated workflow

1. Upload a suspicious `.eml` file.
2. Review authentication results and risk-score breakdown.
3. Inspect the likely origin and relay-trace confidence.
4. Download the generated forensic PDF.
5. Use the dashboard/API documentation for further investigation.

## Limitations and future work

External reputation and GeoIP enrichment depend on configured API/database credentials. GeoIP indicates a likely network region rather than a person's precise location. Future work includes broader fixture coverage, authenticated user roles, persistent case storage, and more trained-model evaluation.
