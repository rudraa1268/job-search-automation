# contact_enrichment_agent.py
"""
Contact Enrichment Agent — for each company in the companies table, finds real
people (HR/recruiters/hiring managers/employees) via Apollo.io (primary, higher
volume) and Hunter.io (domain search, ~50 credits/month budget). Falls back to
email-pattern guessing with SMTP-level verification when neither API returns results.
Tags each contact as 'email_target' (HR/recruiter/hiring manager — eligible for
automated email outreach) or 'linkedin_only' (regular employee — added to the
manual LinkedIn connect list only, never emailed in bulk). Runs on the Linux laptop.
Writes to the contacts table, deduped per (company_id, email).
"""