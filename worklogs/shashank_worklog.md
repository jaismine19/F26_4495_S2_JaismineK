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
| Oct 15, 2026 | 0.5 | App polish: removed roadmap/phase-date notes from app pages (Crime Map, ML, Statistical, Add Incident) and updated the Security page control statuses to reflect implemented controls; installed scipy and re-verified the Statistical Analysis page |
| Oct 18, 2026 | 1.0 | Database: built the SQLite incident store (app/utils/db.py) with parameterized queries so user text can never become SQL; user-entered records kept in a separate table tagged source='user' (data/prototype.db, gitignored) |
| Oct 18, 2026 | 1.0 | Validation: added hour-of-day check (0-23) to the validation module and wired it into the full-record validation used by the incident form |
| Oct 22, 2026 | 2.0 | Add Incident form: rebuilt the page with the full validated form (crime type, neighbourhood, date, hour, location, notes); on submit the record is validated, saved to the SQLite DB, and written to the audit log; records table below the form (admins see all, others only their own); Overview page section showing user-entered incidents separately from public data |
| Oct 24, 2026 | 1.0 | Testing: extended tests/test_db.py (hour/role storage, per-user record filtering, count, SQL-injection-as-literal-text); merged with Jaismine's parallel Add Incident work into one shared db.py module; full suite now 73 tests passing |
| Oct 25, 2026 | 0.5 | Docs: threat model v0.4, Security page control statuses, README updates |
| Oct 28, 2026 | 1.0 | RBAC demo: made the Analyst vs Data Entry difference visible (Analyst sees all entered records, Data Entry sees only their own) with role info banners and an RBAC matrix on the Security page |
| Oct 28, 2026 | 1.5 | Dependency scan: ran pip-audit - found 41 known vulnerabilities in certifi and pillow; upgraded both to patched versions and pinned minimum versions in requirements.txt; re-scan reports 0 vulnerabilities; wrote docs/security/dependency_scan_report.md |
| Oct 29, 2026 | 1.5 | Security testing: added RBAC permission-matrix tests and password-verification tests to tests/test_security.py; full suite now 81 tests passing; threat model v0.5 and Security page statuses updated |
| Nov 1, 2026 | 1.5 | Session hardening: added session management to app/utils/auth.py - fresh random session id on every login (prevents session fixation), 30-minute sliding expiry, and logout clears the session; wired session checks into the Add Incident and Audit Log pages |
| Nov 1, 2026 | 1.0 | Session testing: wrote 6 session tests (unique id, expiry, refresh, invalid sessions, permissions); full suite now 87 tests passing |
| Nov 4, 2026 | 1.0 | Manual security testing: performed and documented 10 OWASP-style attack cases (SQL injection, XSS, auth bypass, role matrix, brute force, session reuse, secrets) in docs/security/security_testing_log.md; threat model v0.6, Security page, README updates |
| Nov 6, 2026 | 0.5 | Threat model: updated STRIDE spoofing, tampering, and repudiation statuses to "Implemented" now that password hashing, sessions, RBAC, and the append-only audit log are live in the app |
| Nov 7, 2026 | 1.5 | Threat model: updated information-disclosure and elevation-of-privilege statuses (SQL injection, stored XSS, location privacy, role checks, session fixation all marked implemented) |
| Nov 10, 2026 | 0.5 | Threat model: completed the Security Controls Summary table - refreshed statuses, dependency-scan date, and test-count references |
| Nov 13, 2026 | 1.5 | Threat model: added a Security Testing Results section (87 automated tests, 10 manual OWASP cases, pip-audit clean) and finalized the document as v1.0 |
| Nov 13, 2026 | 0.25 | Security page: updated it to reference the final threat model v1.0 |
| Nov 15, 2026 | 2.0 | Dependency scan and final checks: reinstalled pip-audit after the laptop update and re-ran the scan - 0 known vulnerabilities; re-ran the full test suite (87 passing); resolved the threat model section 7 open questions (deployment target local, Add Incident behind login only); updated the dependency scan report and the README progress table |
| Nov 17, 2026 | 1.5 | Re-verified project state for Progress Report 3: re-ran the full pytest suite (95 passing) and pip-audit (0 known vulnerabilities) to confirm the security baseline before adding new work |
| Nov 18, 2026 | 1.5 | Implemented a password-policy helper in app/utils/auth.py (validate_password_policy): minimum length 8, at least one letter and one digit, common/breached-password deny-list, and password-must-not-equal-username; added it as threat-model control #1 |
| Nov 18, 2026 | 1.5 | Wrote 7 tests for the password policy (strong password accepted; too-short/no-digit/no-letter/common/matches-username/empty rejected); full suite now 102 passing |
| Nov 21, 2026 | 1.0 | Fixed test_classification.py missing the sys.path bootstrap, so the documented `pytest Implementation/tests/` command runs from the repo root without PYTHONPATH (was erroring during collection) |
| Nov 21, 2026 | 1.5 | Updated docs to match: threat model v1.1 (password policy, spoofing/control-1 statuses, test count 87 -> 102), README security/test entries, and the Methodology page test count |
