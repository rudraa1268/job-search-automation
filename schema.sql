-- ============================================
-- job_search_automation database schema
-- ============================================

PRAGMA foreign_keys = ON;

-- ---------- COMPANIES ----------
CREATE TABLE companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    source TEXT NOT NULL CHECK (source IN 
        ('dpiit','nasscom','github_org','stpi','jobspy','manual')),
    website TEXT,
    tech_stack TEXT,                         -- nullable, comma-separated
    has_open_posting BOOLEAN DEFAULT 0,
    source TEXT NOT NULL CHECK (source IN 
    ('dpiit','nasscom','github_org','stpi','cutshort','jobspy','manual')),
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(name, city)                       -- prevents duplicate entries
);

-- ---------- CONTACTS ----------
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    name TEXT,
    role TEXT,
    email TEXT,
    linkedin_url TEXT,
    enrichment_source TEXT CHECK (enrichment_source IN
        ('apollo','hunter','pattern_guess','manual')),
    verified BOOLEAN DEFAULT 0,
    contact_tier TEXT NOT NULL CHECK (contact_tier IN
        ('email_target','linkedin_only')),  -- HR/recruiter/manager vs regular employee
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(company_id, email)                -- no duplicate contact per company
);

-- ---------- RESUMES ----------
CREATE TABLE resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_name TEXT NOT NULL UNIQUE CHECK (variant_name IN
        ('backend','fullstack','frontend')),
    file_path TEXT NOT NULL,
    keywords TEXT NOT NULL                   -- comma-separated, used for matching
);

-- ---------- JOB OPENINGS ----------
CREATE TABLE job_openings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    title TEXT NOT NULL,
    apply_url TEXT NOT NULL UNIQUE,
    source_site TEXT NOT NULL CHECK (source_site IN
        ('naukri','indeed','google_jobs','glassdoor','zip_recruiter','manual')),
    city TEXT,
    resume_id INTEGER,
    application_status TEXT NOT NULL DEFAULT 'not_applied' CHECK (application_status IN
        ('not_applied','applied','manual_pending')),
    date_posted TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE SET NULL
);

-- ---------- EMAIL TEMPLATES ----------
CREATE TABLE email_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT NOT NULL UNIQUE,      -- 'referral_v1', 'referral_v2', 'referral_v3'
    subject_line TEXT NOT NULL,
    body TEXT NOT NULL,                      -- contains {company_name}, {person_name}, {job_role}
    active BOOLEAN DEFAULT 1
);

-- ---------- OUTREACH LOG ----------
CREATE TABLE outreach_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    resume_id INTEGER,
    template_id INTEGER,
    sent_at TEXT,
    reply_status TEXT NOT NULL DEFAULT 'no_reply' CHECK (reply_status IN
        ('no_reply','replied','bounced')),
    follow_up_due TEXT,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE SET NULL,
    FOREIGN KEY (template_id) REFERENCES email_templates(id) ON DELETE SET NULL,
    UNIQUE(contact_id)                       -- hard block: never email same contact twice
);

-- ---------- INDEXES ----------
CREATE INDEX idx_contacts_company ON contacts(company_id);
CREATE INDEX idx_contacts_tier ON contacts(contact_tier);
CREATE INDEX idx_companies_status ON companies(status);
CREATE INDEX idx_companies_city ON companies(city);
CREATE INDEX idx_job_openings_company ON job_openings(company_id);
CREATE INDEX idx_job_openings_status ON job_openings(application_status);
CREATE INDEX idx_outreach_company ON outreach_log(company_id);
CREATE INDEX idx_outreach_followup ON outreach_log(follow_up_due);

-- ---------- AUTO-UPDATE updated_at ON companies ----------
CREATE TRIGGER trg_companies_updated_at
AFTER UPDATE ON companies
BEGIN
    UPDATE companies SET updated_at = datetime('now') WHERE id = NEW.id;
END;
