# email_outreach_agent.py
"""
Email Outreach Agent — sends templated referral/outreach emails to 'email_target'
contacts only. Fills one of 5 rotating templates (email_templates table) with
company name, person name, and job role, attaches the matching resume variant,
and sends via SMTP. Enforces the daily cap (target: 50/day, ramping up as contact
supply allows) and only sends within the two approved windows (9:30-11:00 AM and
1:00-2:30 PM IST, weekdays). Checks outreach_log before sending to guarantee no
contact is ever emailed twice. Runs on the Linux laptop, triggered by n8n.
"""