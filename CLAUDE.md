# Job Search Automation — Project Context

## What this is
Multi-agent automation system to reduce manual job-search grunt work: 
finding companies, finding contacts, sending outreach, tracking status. 
Built across 2 old laptops (Linux + Windows) + n8n orchestration.

## Architecture decisions (locked in)
- n8n (self-hosted, free Community Edition) = orchestration layer on Linux laptop
- SQLite, not Postgres — data volume is small (hundreds of rows), and 4GB RAM laptops can't spare it
- Claude API (Haiku 4.5) = brain, used sparingly (edge-case resume matching only, NOT per-email drafting)
- Email outreach = templated mail-merge (2-3 rotating templates), not LLM-generated per email — cheaper, faster, avoids spam-pattern detection
- Email sends: capped 20-40/day, only in two windows — 9:30-11:00 AM and 1:00-2:30 PM IST, weekdays only
- LinkedIn: NOT automated (ban risk too high) — agent finds people + drafts note, human clicks send
- Dashboard: Streamlit (not Django) — reusing architecture pattern from BjornMelin/ai-job-scraper on GitHub

## Agents (5) + Dashboard
1. Job Opening Agent — GitHub JobSpy library (Naukri/Indeed/Google Jobs) — runs on Linux
2. Company Discovery Agent — custom (DPIIT/NASSCOM/GitHub org/STPI scraping) — runs on Windows (browser-heavy)
3. Contact Enrichment Agent — Apollo + Hunter API calls (pyhunter wrapper for Hunter half) — runs on Linux
4. Email Outreach Agent — templated mail-merge — runs on Linux
5. CRM/Tracker — status tracking (not contacted → contacted → replied → interviewing → dead) — runs on Linux
6. Dashboard (Streamlit) — views all of the above, phone-accessible via Tailscale — runs on Linux

## Laptops
- Linux (4GB RAM, 500GB HDD): n8n, SQLite, agents 1/3/4/5, dashboard — always-on server role
- Windows (4GB RAM, 128GB SSD+500GB HDD): agent 2 (browser automation) — secondary worker

## Status
- [ ] Not started yet — repo just initialized

## Log (newest first)
- [DATE] Repo initialized, CLAUDE.md created
## Status
- DONE: Repo initialized, schema created
- DONE: Agent 1 (Job Opening Agent) — Indeed only (Naukri/Glassdoor/ZipRecruiter blocked by bot detection)
- TODO: Agent 2 (Company Discovery)
- TODO: Agent 3 (Contact Enrichment) — blocked on Agent 2
- TODO: Agent 4 (Email Outreach)
- TODO: Agent 5 (CRM/Tracker)
- TODO: Dashboard

## Log (newest first)
- [2026-07-04] Job Opening Agent complete. Sites: Indeed only (Naukri=406 recaptcha, Glassdoor=broken API, ZipRecruiter=403 bot-block even with delays). 259+ jobs inserted for Bangalore + remote, 22 role variants, 24hr freshness.
- [2026-07-03] Repo initialized, schema.sql created and verified (6 tables), venv set up (Python 3.14, numpy/pandas/jobspy version overrides needed for 3.14 compatibility).
