# company_discovery_agent.py
"""
Company Discovery Agent — builds the master company list, including small companies
that hire via referral and never post openings publicly. Pulls from DPIIT startup
registry, NASSCOM member directory, GitHub organization search, STPI tenant
listings, and Cutshort's company directory, filtered by target city. Fills
name/city/source automatically; tech_stack is filled only when a real signal
exists (GitHub repos, website, LinkedIn About) and left blank otherwise rather
than guessed.
 
Runs on the Windows laptop since most sources require rendering JS-heavy pages
via Playwright. Does NOT write to SQLite directly. Instead, POSTs discovered
companies as a JSON array to an n8n webhook running on the Linux laptop, which
is the single writer to companies.db. This keeps one source of truth instead of
two independently-created SQLite files going out of sync across machines.
 
Target cities: Raipur, Gurgaon, Bangalore (see .env TARGET_CITIES).
Target roles (used only to filter GitHub org search by tech relevance, not for
job matching — that's the Job Opening Agent's job):
    frontend developer fresher, backend developer fresher, fullstack developer
    fresher, python developer fresher, django developer, react developer
    fresher, mern stack developer fresher, n8n automation, junior software
    engineer, sde-1, automation engineer.
"""
 

import os
import json
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
 
load_dotenv()
 
WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")  # e.g. http://192.168.1.50:5678/webhook/company-discovery
TARGET_CITIES = [c.strip() for c in os.getenv("TARGET_CITIES", "Raipur,Gurgaon,Bangalore").split(",")]
 
# Tech keywords used only to decide which GitHub orgs are relevant, not for job matching
TECH_SIGNALS = [
    "django", "react", "python", "mern", "n8n", "flask", "fastapi",
    "postgresql", "javascript", "typescript"
]
 
 
def scrape_dpiit(city: str) -> list[dict]:
    """
    Pulls startups registered under DPIIT for a given city.
    TODO: implement with Playwright against the DPIIT startup registry search page.
    Returns list of dicts: {name, city, source, website, tech_stack}
    """
    companies = []
    # with sync_playwright() as p:
    #     browser = p.chromium.launch()
    #     page = browser.new_page()
    #     page.goto("https://www.startupindia.gov.in/...")
    #     ... scrape rows filtered by city ...
    #     browser.close()
    return companies
 
 
def scrape_nasscom(city: str) -> list[dict]:
    """
    Pulls NASSCOM member directory entries for a given city.
    TODO: implement with Playwright.
    """
    companies = []
    return companies
 
 
def scrape_github_orgs(city: str) -> list[dict]:
    """
    Uses GitHub's org/user search API to find organizations located in `city`
    whose public repos match TECH_SIGNALS. This is the one source where
    tech_stack can be filled with real confidence, since it's read straight
    from repo languages/topics.
    """
    companies = []
    token = os.getenv("GITHUB_TOKEN")  # optional, raises rate limit if set
    headers = {"Authorization": f"token {token}"} if token else {}
 
    query = f"location:{city} type:org"
    resp = requests.get(
        "https://api.github.com/search/users",
        params={"q": query, "per_page": 30},
        headers=headers,
        timeout=15,
    )
    if resp.status_code != 200:
        return companies
 
    for org in resp.json().get("items", []):
        org_login = org["login"]
        repos_resp = requests.get(
            f"https://api.github.com/orgs/{org_login}/repos",
            headers=headers,
            timeout=15,
        )
        if repos_resp.status_code != 200:
            continue
 
        langs = {r.get("language") for r in repos_resp.json() if r.get("language")}
        matched = [t for t in TECH_SIGNALS if any(t.lower() in (l or "").lower() for l in langs)]
        if not matched:
            continue  # skip orgs with no relevant tech signal
 
        companies.append({
            "name": org.get("name") or org_login,
            "city": city,
            "source": "github_org",
            "website": org.get("blog") or f"https://github.com/{org_login}",
            "tech_stack": ",".join(matched),
        })
 
    return companies
 
 
def scrape_stpi(city: str) -> list[dict]:
    """
    Pulls STPI (Software Technology Parks of India) tenant listings for a city.
    TODO: implement with Playwright — STPI publishes tenant lists per park/city.
    """
    companies = []
    return companies
 
 
def scrape_cutshort(city: str) -> list[dict]:
    """
    Pulls company entries from Cutshort's company directory for a city.
    India-specific, startup/fresher-heavy — good complement to DPIIT/NASSCOM
    which skew larger and more metro-heavy.
    TODO: implement with Playwright.
    """
    companies = []
    return companies
 
 
def dedupe(companies: list[dict]) -> list[dict]:
    """
    Local dedup before sending over the wire, on (name.lower().strip(), city).
    Final authority on dedup is still the DB's UNIQUE(name, city) constraint —
    this just avoids sending obvious duplicates in the same run.
    """
    seen = set()
    unique = []
    for c in companies:
        key = (c["name"].strip().lower(), c["city"].strip().lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)
    return unique
 
 
def send_to_n8n(companies: list[dict]) -> None:
    if not WEBHOOK_URL:
        raise RuntimeError("N8N_WEBHOOK_URL not set in .env")
    if not companies:
        print("No companies found this run — nothing to send.")
        return
 
    resp = requests.post(WEBHOOK_URL, json=companies, timeout=30)
    resp.raise_for_status()
    print(f"Sent {len(companies)} companies to n8n webhook. Status: {resp.status_code}")
 
 
def main():
    all_companies = []
    for city in TARGET_CITIES:
        all_companies += scrape_dpiit(city)
        all_companies += scrape_nasscom(city)
        all_companies += scrape_github_orgs(city)
        all_companies += scrape_stpi(city)
        all_companies += scrape_cutshort(city)
 
    unique_companies = dedupe(all_companies)
    print(f"Discovered {len(unique_companies)} unique companies across {TARGET_CITIES}.")
    send_to_n8n(unique_companies)
 
 
if __name__ == "__main__":
    main()