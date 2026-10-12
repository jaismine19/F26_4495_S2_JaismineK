# Work Log - Shashank Chaudhary (300392521)

| Date | Hours | Description of work done |
|---|---|---|
| Sep 18, 2026 | 1.5 | Initial research/project planning |
| Sep 22, 2026 | 2.5 | Cybersecurity research/threat modeling: Identified potential security risks for the crime-data web application, including unauthorized access, SQL injection, XSS, password security, session security, and data exposure |
| Sep 26, 2026 | 2 | GitHub/repository work: Accepted collaborator invitation, cloned the project repository, and set up the local project directory for development |
| Oct 9, 2026 | 0.5 | Project setup: Created folder structure (data/, scripts/, docs/, app/, tests/, worklogs/); added .gitignore; wrote scripts/00_download_data.py for reproducible data acquisition |
| Oct 9, 2026 | 0.5 | Data acquisition: Downloaded VPD crime dataset from GeoDASH open data (all neighbourhoods, all years); wrote scripts/01_inspect_data.py; generated data quality summary (927,794 rows; 34,527 duplicates; missing 2022; 83K zero coordinates) |
| Oct 9, 2026 | 0.25 | Documentation: Wrote docs/research/dataset_documentation.md covering source, schema, quality findings, and privacy notes |
| Oct 9, 2026 | 0.5 | Threat model: Drafted docs/security/threat_model.md v0.1 - assets, threat actors, STRIDE analysis, OWASP Top 10 relevance, planned controls, and security testing plan |
| Oct 9, 2026 | 0.25 | Data cleaning: Wrote scripts/02_clean_data.py (dedupe, categorical standardization, zero-coordinate flagging, date/day-of-week/season features); cleaned dataset 927,794 to 893,267 rows with documented cleaning log |
| Oct 9, 2026 | 0.25 | Privacy review: Drafted docs/security/privacy_and_data_protection.md v0.1 - data inventory, privacy principles, credential handling, location-data handling, implementation checklist |
| Oct 9, 2026 | 0.25 | Repository maintenance: Updated README progress table and work log; committed and pushed all work to GitHub |
| Oct 11, 2026 | 0.5 | Repo restructure: moved implementation code (app/, scripts/, notebooks/, tests/) under the Implementation/ folder per the progress report template; fixed all path references (README, docstrings, data loader); verified tests still pass |
| Oct 11, 2026 | 1 | Security implementation: extended app/utils/auth.py with append-only audit logging (log_audit/read_audit_log, JSONL) and login attempt limiting (5 failures per 60s lockout); wrote tests/test_security.py (6 tests); full suite now 20 tests passing |
| Oct 11, 2026 | 0.75 | Threat model v0.2: updated control statuses (PBKDF2 hashing, RBAC, audit log, login limiting now implemented); added revision entry; verified app serves after restructure |
| Oct 11, 2026 | 0.25 | Verification and repo maintenance: ran full test suite and app smoke test after folder move; updated .gitignore for audit log file; committed and pushed |
