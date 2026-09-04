# SIH 2026 — PPT Slide Content
### Ready to copy-paste into your SIH template

---

## SLIDE 1 — TITLE PAGE

**Fill in these fields on the template:**

| Field | Content |
|---|---|
| Problem Statement ID | **26106** |
| Problem Statement Title | **Email Forensics and Phishing Detection** |
| Theme | **Cyber Security** |
| PS Category | **Software** |
| Team ID | *(your team ID from portal)* |
| Team Name | *(your team name)* |

---

## SLIDE 2 — IDEA TITLE (Proposed Solution)

**Title:** AI-Powered Email Threat Detection & Forensic Intelligence Platform

**Proposed Solution (3 bullet points):**

• Drag-and-drop any `.eml` file → get a full forensic analysis in under 5 seconds
  - Authentication checks (SPF/DKIM/DMARC) with cryptographic DKIM re-verification
  - ML-based phishing detection using XGBoost trained on 6,000+ real emails
  - Origin IP tracing through relay chain analysis with GeoIP & abuse reputation lookup
  - All signals fused into one explainable 0–100 risk score

• 6 novel forensic features not found in existing tools:
  - Confidence/Uncertainty scoring — tells you *how sure* the system is
  - Counterfactual analysis — shows *"what would need to change to flip the verdict"*
  - SHAP word contributions — highlights exact words pushing the score up
  - Homoglyph/typosquat detection — catches lookalike domains (e.g., paypaI.com)
  - Adversarial red-team testing — automatically tests if the email defeats the model
  - Writing style (stylometry) analysis — detects mismatched sender identity

• One-command Docker deployment — no setup hassle, instant demo

**How it addresses the problem:**
• Current email security relies on server-side checks (SPF/DKIM/DMARC) — users have no way to verify suspicious emails themselves
• Our tool lets anyone analyze any email offline, with real-time threat intelligence from AbuseIPDB, MaxMind, and IPinfo
• Explains *why* an email is dangerous, not just *that* it is — every score point traces back to a specific signal

**Innovation and uniqueness:**
• Combines content-based ML classification with technical infrastructure forensics in a single tool
• Explainable AI — every decision is transparent and auditable
• Red-team adversarial testing simulates attacker evolution before deployment

---

## SLIDE 3 — TECHNICAL APPROACH

**Technologies used:**

| Layer | Technology |
|---|---|
| Backend API | Python, FastAPI, SQLAlchemy, PostgreSQL |
| ML/NLP Engine | XGBoost, scikit-learn (TF-IDF), spaCy |
| Email Parsing | mail-parser, authres, dkimpy, checkdmarc |
| Threat Intelligence | AbuseIPDB API, IPinfo API, MaxMind GeoLite2 |
| Forensic Features | NetworkX (campaign graphs), SHAP, custom homoglyph engine |
| Frontend | React, Vite, Tailwind CSS, Recharts, Leaflet.js |
| PDF Reports | ReportLab |
| Deployment | Docker, docker-compose |

**Methodology / Workflow (describe this as a flow):**

```
[.eml File Upload]
       ↓
[Email Parsing — headers, body, Received chain]
       ↓
┌──────────────────────────────────────────┐
│  PHASE A: Authentication Verification    │
│  • Parse Authentication-Results header   │
│  • Independent DKIM cryptographic check  │
│  • SPF/DMARC policy hygiene check        │
└──────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────┐
│  PHASE B: Content Analysis               │
│  • XGBoost ML classification (TF-IDF)    │
│  • Urgency & impersonation heuristics    │
│  • 6 Novel forensic features             │
└──────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────┐
│  PHASE C: Origin Tracing                 │
│  • Relay chain walk → trusted boundary   │
│  • GeoIP city-level geolocation          │
│  • AbuseIPDB confidence score            │
│  • Domain age & hosting analysis         │
└──────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────┐
│  SCORING ENGINE                          │
│  All signals → weighted risk score 0-100 │
│  + Confidence flag + Counterfactual      │
└──────────────────────────────────────────┘
       ↓
[Dashboard: Risk Gauge + Map + Auth Badges + PDF Report]
```

**For the flow chart image:** Draw the above as a vertical flowchart with colored boxes (red = auth, blue = ML, green = origin, orange = scoring). Add the dashboard screenshot at the bottom.

---

## SLIDE 4 — FEASIBILITY AND VIABILITY

**Analysis of feasibility:**

• ML model trains in under 60 seconds on a laptop — no GPU required
• All APIs have free tiers sufficient for demo and early deployment:
  - AbuseIPDB: 1,000 checks/day (free)
  - IPinfo Lite: unlimited requests (free)
  - MaxMind GeoLite2: offline `.mmdb` file, no API limits
• Publicly available training datasets (Nazario, SpamAssassin, Enron) — no data acquisition barrier
• Docker one-command deployment eliminates environment issues

**Potential challenges and risks:**

• API rate limits under heavy demo load
• Model accuracy on novel/zero-day phishing patterns
• `.eml` file format variations across email clients
• GeoIP accuracy (city-level, not exact address)

**Strategies for overcoming these challenges:**

• API responses are cached locally — repeat lookups are instant
• Model retraining pipeline built in — new samples can be added continuously
• mail-parser handles all standard `.eml` MIME variations; edge cases handled with fallbacks
• GeoIP accuracy radius displayed transparently — users know the precision limit

---

## SLIDE 5 — IMPACT AND BENEFITS

**Potential impact on target audience:**

• **Individual users:** Verify suspicious emails themselves — no IT dependency
• **Organizations:** Automated triage reduces security team workload by filtering obvious phishing
• **Incident responders:** Forensic PDF reports provide ready-to-share evidence
• **Banks & financial institutions:** Real-time BEC (Business Email Compromise) detection

**Benefits:**

| Benefit | Description |
|---|---|
| **Social** | Protects citizens from financial fraud — India loses ₹1,200+ crore annually to email phishing |
| **Economic** | Reduces incident response time from hours to seconds; cuts security tool costs |
| **Scalability** | Open-source core — any organization can deploy without licensing fees |
| **Awareness** | Explainable AI teaches users *why* emails are dangerous, building long-term security awareness |
| **Research** | Novel forensic features (counterfactual, SHAP, red-team) advance the state of email security research |

---

## SLIDE 6 — RESEARCH AND REFERENCES

**Research and references:**

1. **Dataset:** Nazario Phishing Corpus — https://monkey.org/~jose/phishing/
2. **SpamAssassin Public Corpus:** https://spamassassin.apache.org/old/publiccorpus/
3. **XGBoost:** Chen & Guestrin, "XGBoost: A Scalable Tree Boosting System" (KDD 2016)
4. **TF-IDF:** Salton & Buckley, "The Term-Weighting Approach to IR" (1988)
5. **SPF/DKIM/DMARC Standards:** RFC 7208 (SPF), RFC 6376 (DKIM), RFC 7489 (DMARC)
6. **GeoLite2 Database:** MaxMind — https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
7. **AbuseIPDB:** https://www.abuseipdb.com/
8. **Explainable AI (SHAP):** Lundberg & Lee, "A Unified Approach to Interpreting Model Predictions" (NeurIPS 2017)
9. **Email Authentication Best Practices:** Google Postmaster Tools documentation
10. **FastAPI Documentation:** https://fastapi.tiangolo.com/

---

## QUICK REFERENCE — Key Metrics for Q&A

**Model performance:**
- Accuracy: 97.5% on balanced test set
- Ham (legitimate) detection: 95.0%
- Spam/phishing detection: 100.0%
- ML probability range: ham avg 0.05, spam avg 0.94

**System specs:**
- Analysis time: ~4 seconds per email
- ML model: XGBoost (300 trees, depth 6)
- Training data: 6,000+ real emails
- API calls: ~3 per analysis (AbuseIPDB, IPinfo, GeoIP local)

**Scoring breakdown:**
- ML probability: 40% weight
- Authentication failure: 18% weight
- AbuseIPDB score: 10% weight
- Urgency/impersonation language: 12% weight
- Display name mismatch: 8% weight
- Domain age/infrastructure: 12% weight
