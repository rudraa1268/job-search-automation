"""
Contact Enrichment Agent
Run ONCE A MONTH. Manually enter up to 14 companies below before running.
Apollo-only: pulls 6 contacts/company (founder, senior dev, backend dev,
frontend dev, HR/recruiter — Apollo's own title match decides the split
within the search results).
Writes to contacts table. Idempotent via INSERT OR IGNORE + UNIQUE(company_id, email).
"""
 
import os
import sqlite3
import requests
import time
import sys
 
# ---------------- CONFIG ----------------
DB_PATH = "job_search.db"  # adjust to your actual sqlite file path
 
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY")
 
APOLLO_BUDGET = 90  # matches your account's actual free-tier balance
 
APOLLO_TITLES = [
    "founder",
    "senior software engineer", "senior developer",
    "backend developer", "frontend developer",
    "hr", "human resources", "recruiter", "talent acquisition"
]
 
# ---- MANUALLY ENTER COMPANIES HERE (max 14) ----
COMPANIES = [
    {"name": "Example Corp", "domain": "example.com"},
    # add up to 14 total
]
 
APOLLO_PER_COMPANY = 6
 
 
# ---------------- DB HELPERS ----------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
 
 
def get_or_create_company(conn, name, domain):
    cur = conn.execute(
        "SELECT id FROM companies WHERE name = ?", (name,)
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        """INSERT INTO companies (name, city, source, website)
           VALUES (?, 'Unknown', 'manual', ?)""",
        (name, f"https://{domain}")
    )
    conn.commit()
    return cur.lastrowid
 
 
def existing_contact_count(conn, company_id):
    cur = conn.execute(
        "SELECT COUNT(*) FROM contacts WHERE company_id = ?", (company_id,)
    )
    return cur.fetchone()[0]
 
 
def insert_contact(conn, company_id, name, role, email, source, tier):
    if not email:
        return False
    conn.execute(
        """INSERT OR IGNORE INTO contacts
           (company_id, name, role, email, enrichment_source, verified, contact_tier)
           VALUES (?, ?, ?, ?, ?, 0, ?)""",
        (company_id, name, role, email, source, tier)
    )
    conn.commit()
    return True
 
 
# ---------------- APOLLO ----------------
def apollo_search_people(domain, limit):
    """People API Search - does not consume credits."""
    url = "https://api.apollo.io/api/v1/mixed_people/search"
    headers = {"Content-Type": "application/json", "x-api-key": APOLLO_API_KEY}
    payload = {
        "q_organization_domains": domain,
        "person_titles": APOLLO_TITLES,
        "page": 1,
        "per_page": limit
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json().get("people", [])[:limit]
 
 
def apollo_enrich_person(person_id):
    """People Enrichment - consumes 1 credit if email found."""
    url = "https://api.apollo.io/api/v1/people/match"
    headers = {"Content-Type": "application/json", "x-api-key": APOLLO_API_KEY}
    params = {
        "id": person_id,
        "reveal_personal_emails": "true"
    }
    resp = requests.post(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json().get("person", {})
    return data.get("email"), data.get("name"), data.get("title")
 
 
def run_apollo_for_company(conn, company_id, domain, limit):
    found = 0
    try:
        candidates = apollo_search_people(domain, limit)
    except requests.RequestException as e:
        print(f"  [Apollo] search failed for {domain}: {e}")
        return found
 
    for person in candidates:
        person_id = person.get("id")
        if not person_id:
            continue
        try:
            email, name, title = apollo_enrich_person(person_id)
        except requests.RequestException as e:
            print(f"  [Apollo] enrich failed for {person_id}: {e}")
            continue
        if email:
            inserted = insert_contact(
                conn, company_id, name, title, email, "apollo", "email_target"
            )
            if inserted:
                found += 1
                print(f"  [Apollo] {name} ({title}) -> {email}")
        time.sleep(1)  # stay well under rate limits
    return found
 
 
# ---------------- MAIN ----------------
def main():
    if not APOLLO_API_KEY:
        sys.exit("Missing APOLLO_API_KEY environment variable.")
 
    n = len(COMPANIES)
    apollo_needed = n * APOLLO_PER_COMPANY
 
    print(f"Companies: {n}")
    print(f"Apollo budget check: {apollo_needed}/{APOLLO_BUDGET}")
 
    if apollo_needed > APOLLO_BUDGET:
        sys.exit("Budget exceeded. Reduce company count before running.")
 
    conn = get_conn()
    total_apollo = 0
 
    for company in COMPANIES:
        name, domain = company["name"], company["domain"]
        company_id = get_or_create_company(conn, name, domain)
 
        if existing_contact_count(conn, company_id) >= APOLLO_PER_COMPANY:
            print(f"Skipping {name} — already fully enriched.")
            continue
 
        print(f"\nEnriching {name} ({domain})...")
        total_apollo += run_apollo_for_company(conn, company_id, domain, APOLLO_PER_COMPANY)
 
    conn.close()
    print(f"\nDone. Apollo contacts added: {total_apollo}.")
 
 
if __name__ == "__main__":
    main()
 