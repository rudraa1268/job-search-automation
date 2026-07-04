import sqlite3
from jobspy import scrape_jobs

DB_PATH = "job_search.db"
CITY = "Bangalore"  # change or make input() later
HOURS_OLD = 24
RESULTS_PER_ROLE = 20

ROLES = [
    "frontend developer fresher",
    "backend developer fresher",
    "fullstack developer fresher",
    "python developer fresher",
    "data analyst fresher",
    "n8n automation",
    "django developer",
    "django developer fresher",
    "react developer fresher",
    "django react developer",
    "mern stack developer fresher",

    # Experience-level variants (you have ~1 yr, not zero)
    "junior software engineer",
    "junior full stack developer",
    "associate software engineer",
    "software engineer 1 year experience",
    "sde-1",

    # Adjacent to what you've actually done (automation, ML exposure from MediGuide)
    "automation engineer",
    "python automation developer",
    "backend developer django",
    "api developer python",

    # Broader nets that still match your profile
    "software developer fresher",
    "web developer fresher",
    "javascript developer fresher",
    "rest api developer",
]

SITES = ['indeed']
def fetch_jobs():
    all_jobs = []
    for role in ROLES:
        for remote in [False, True]:
            label = "remote" if remote else CITY
            print(f"Scraping: {role} ({label})")
            try:
                jobs = scrape_jobs(
                    site_name=SITES,
                    search_term=role,
                    google_search_term=f"{role} jobs {'remote' if remote else 'near ' + CITY} since yesterday",
                    location=CITY if not remote else "India",
                    is_remote=remote,
                    results_wanted=RESULTS_PER_ROLE,
                    hours_old=HOURS_OLD,
                    country_indeed="India",
                )
                all_jobs.append(jobs)
                
            except Exception as e:
                print(f"Failed on {role} ({label}): {e}")
    return all_jobs

def insert_jobs(job_dfs):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    inserted = 0
    for df in job_dfs:
        for _, row in df.iterrows():
            try:
                cur.execute("""
                    INSERT OR IGNORE INTO job_openings
                    (title, apply_url, source_site, city, date_posted)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    row.get("title"),
                    row.get("job_url"),
                    row.get("site"),
                    CITY,
                    str(row.get("date_posted")),
                ))
                if cur.rowcount:
                    inserted += 1
            except Exception as e:
                print(f"Skipped one row: {e}")
    conn.commit()
    conn.close()
    print(f"Inserted {inserted} new job rows.")

if __name__ == "__main__":
    job_dfs = fetch_jobs()
    insert_jobs(job_dfs)