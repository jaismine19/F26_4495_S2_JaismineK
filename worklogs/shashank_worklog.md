# Work Log - Shashank Chaudhary (300392521)

| Date | Hours | Description of work done |
|---|---|---|
| Sep 18, 2026 | 1.5 | Initial research/project planning |
| Sep 22, 2026 | 2.5 | Cybersecurity research/threat modeling: Identified potential security risks for the crime-data web application, including unauthorized access, SQL injection, XSS, password security, session security, and data exposure |
| Sep 26, 2026 | 2 | GitHub/repository work: Accepted collaborator invitation, cloned the project repository, and set up the local project directory for development |
| Oct 9, 2026 | 1.5 | Project setup: Created folder structure (data/, scripts/, docs/, app/, tests/, worklogs/); added .gitignore; wrote scripts/00_download_data.py for reproducible data acquisition |
| Oct 9, 2026 | 1.5 | Data acquisition: Downloaded VPD crime dataset from GeoDASH open data (all neighbourhoods, all years); wrote scripts/01_inspect_data.py; generated data quality summary (927,794 rows; 34,527 duplicates; missing 2022; 83K zero coordinates) |
| Oct 9, 2026 | 0.75 | Data cleaning: Wrote scripts/02_clean_data.py (dedupe, categorical standardization, zero-coordinate flagging, datetime/day-of-week/season features); cleaned dataset 927,794 to 893,267 rows with documented cleaning log |
| Oct 9, 2026 | 0.75 | Documentation: Wrote docs/research/dataset_documentation.md covering source, schema, quality findings, and privacy notes |
| Oct 9, 2026 | 0.75 | Threat model: Drafted docs/security/threat_model.md v0.1 - assets, threat actors, STRIDE analysis, OWASP Top 10 relevance, planned controls, and security testing plan |
| Oct 9, 2026 | 0.75 | Privacy review: Drafted docs/security/privacy_and_data_protection.md v0.1 - data inventory, privacy principles, credential handling, location-data handling, implementation checklist |
| Oct 11, 2026 | 1.5 | Repo restructure: moved implementation code (app/, scripts/, notebooks/, tests/) under the Implementation/ folder per the progress report template; fixed all path references (README, docstrings, data loader); verified tests and app still run |
| Oct 11, 2026 | 1.5 | Security implementation: extended app/utils/auth.py with append-only audit logging (log_audit/read_audit_log, JSONL) and login attempt limiting (5 failures per 60s lockout) |
| Oct 11, 2026 | 1 | Security testing: wrote tests/test_security.py (6 tests covering audit logging and lockout); full test suite now 20 tests passing; updated threat model to v0.2 with implemented control statuses; committed and pushed |
| Oct 15, 2026 | 1.5 | Input validation module: wrote app/utils/validation.py for the incident-entry form - allow-lists for the 11 crime types and 24 neighbourhoods (taken from the real dataset), date range checks (no future dates, nothing before 2003), length limits, and HTML/script sanitization to prevent stored XSS |
| Oct 15, 2026 | 1.5 | Validation testing: wrote tests/test_validation.py (18 tests covering sanitization, allow-lists, date rules, and full-record validation); ran the whole suite - 38 tests passing |
| Oct 15, 2026 | 0.75 | Threat model v0.3: marked the input validation/XSS control as implemented with the new module; added revision entry; updated work log and pushed |
| Oct 15, 2026 | 1.5 | Audit Log page: built app/pages/9_audit_log.py - administrator-only page showing the append-only audit log; registered it in the app navigation |
| Oct 15, 2026 | 1 | Login hardening: wired audit logging and lockout enforcement into the Add Incident login flow (login_success/login_failure/logout events, 60s lockout after 5 failed attempts); verified app and tests |
