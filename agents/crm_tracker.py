# crm_tracker.py
"""
CRM/Tracker — the status layer tying every other agent's output together. Updates
company status (not_contacted -> contacted -> replied -> interviewing -> dead) based
on outreach_log and reply data, flags contacts with no reply after N days for
follow-up, and feeds the Streamlit dashboard with a consolidated view across
companies, contacts, job_openings, and outreach_log. Runs on the Linux laptop;
this is the module the dashboard queries directly rather than hitting raw tables.
"""