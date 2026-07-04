# company_discovery_agent.py
"""
Company Discovery Agent — builds the master company list, including small companies
that hire via referral and never post openings publicly. Pulls from DPIIT startup
registry, NASSCOM member directory, GitHub organization search, and STPI tenant
listings, filtered by target city. Fills name/city/source automatically; tech_stack
is filled only when a real signal exists (GitHub repos, website, LinkedIn About) and
left blank otherwise rather than guessed. Runs on the Windows laptop since most
sources require rendering JS-heavy pages via Playwright. Writes/updates rows in the
companies table, deduped on (name, city).
"""