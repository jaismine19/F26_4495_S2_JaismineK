# Threat Model - Vancouver Urban Safety Intelligence Platform

**Owner:** Shashank Chaudhary (Cybersecurity workstream)
**Status:** Final v1.0 - November 4, 2026
**Scope:** Streamlit web application, authentication system, database, and
prototype incident-entry feature described in the project proposal.

> This is a living document. It will be updated as the application design is
> implemented and security testing is performed.

## 1. Assets

| Asset | Sensitivity | Description |
|---|---|---|
| User accounts (username, password hash, role) | High | Credential data for authorized users |
| User-entered incident records | Medium | Prototype entries submitted by authorized users |
| Public VPD crime dataset | Low | Public data; integrity matters for analysis |
| Audit logs | Medium | Records of user actions; must be tamper-evident |
| Application code & configuration | High | Secrets, queries, dependencies |
| Availability of the dashboard | Medium | Research prototype used for demos/evaluation |

## 2. System Components & Trust Boundaries

```
[Browser/User] --HTTPS--> [Streamlit App] --queries--> [Database (SQLite/PostgreSQL)]
                              |                              |
                              +---> [Python analytics/ML code]
                              +---> [Static VPD dataset (read-only)]
```

Trust boundaries:
1. **User <-> App:** All input crossing this boundary is untrusted.
2. **App <-> Database:** Only parameterized queries may cross.
3. **App <-> Public dataset:** Read-only access; never modified by users.

## 3. Threat Actors

| Actor | Motivation | Access level |
|---|---|---|
| Anonymous web visitor | Curiosity, disruption | None (limited to public pages) |
| Malicious authenticated user | Escalate privileges, inject bad data | Low-privilege role |
| External attacker | Data theft, defacement, DoS | Remote, unauthenticated |
| Accidental misuse | Human error | Authenticated user |

## 4. Threat Analysis (STRIDE-style)

### 4.1 Spoofing

| Threat | Risk | Mitigation | Status |
|---|---|---|---|
| Attacker impersonates another user | Medium | Hashed passwords (PBKDF2) and a fresh random session id on every login | Implemented |
| Attacker guesses/reuses credentials | Medium | Login lockout (5 tries / 60s); password policy (min length, breach check) not yet enforced on demo accounts | Partially implemented |

### 4.2 Tampering

| Threat | Risk | Mitigation | Status |
|---|---|---|---|
| User modifies another user's incident records | Medium | Role-based access control (RBAC); users can only view their own records; no update/delete endpoint exposed | Implemented |
| User alters audit logs | Medium | Append-only JSONL audit log; no update/delete operations on logs | Implemented |
| Injection of fake incident data | Low-Medium | All user-entered records tagged with `source='user'` and kept separate from public data | Implemented |

### 4.3 Repudiation

| Threat | Risk | Mitigation | Status |
|---|---|---|---|
| User denies submitting a record | Low | Audit log records user_id, action, and timestamp on every write | Implemented |

### 4.4 Information Disclosure

| Threat | Risk | Mitigation | Status |
|---|---|---|---|
| SQL injection leaks database contents | High | Parameterized queries only; injection payloads tested (`tests/test_db.py`) | Implemented |
| Passwords stored in plain text | High | PBKDF2-HMAC-SHA256 hashing with per-user salt; plaintext never stored | Implemented |
| Error messages reveal internals | Low | Generic error handling; detailed errors kept server-side only | Partially implemented |
| Sensitive data in logs | Medium | Audit log stores username/action only; no passwords or tokens are written | Implemented |
| Over-precise location display | Low-Medium | Neighbourhood-level aggregation on the public map (privacy-safe) | Implemented |

### 4.5 Denial of Service

| Threat | Risk | Mitigation | Status |
|---|---|---|---|
| Resource exhaustion via repeated requests | Low | Rate limiting where feasible; demo app runs on a small instance | Under review |

### 4.6 Elevation of Privilege

| Threat | Risk | Mitigation | Status |
|---|---|---|---|
| Role confusion (user acts as admin) | High | Server-side permission checks on every privileged page/action (`has_permission`) | Implemented |
| Session fixation/hijacking | Medium | Fresh random session id on every login; 30-minute expiry; logout clears session | Implemented |

### 4.7 Cross-cutting Application Threats (OWASP Top 10 relevance)

| OWASP Category | Relevance | Planned Control |
|---|---|---|
| A01 Broken Access Control | Direct (RBAC app) | Role checks, ownership checks |
| A02 Cryptographic Failures | Direct | Strong hashing, HTTPS, no secrets in repo |
| A03 Injection | Direct (SQL input) | Parameterized queries, input validation |
| A04 Insecure Design | Direct | Threat model (this document), design review |
| A05 Security Misconfiguration | Direct | Secure defaults, secrets management |
| A06 Vulnerable Components | Direct | Dependency scanning (pip-audit) |
| A07 Identification & Auth Failures | Direct | Login, sessions, hashing |
| A08 Software/Data Integrity | Partial | Supply-chain review of dependencies |
| A09 Logging & Monitoring Failures | Partial | Audit logs for user actions |
| A10 SSRF | Low | No server-side URL fetching planned |

## 5. Security Controls Summary

| # | Control | Priority | Status (Nov 4) |
|---|---|---|---|
| 1 | Password hashing | Critical | Implemented - PBKDF2-HMAC-SHA256, 200k iterations, per-user salt (`app/utils/auth.py`); bcrypt/argon2 upgrade before any non-demo use |
| 2 | RBAC: Administrator, Analyst, Data Entry | Critical | Implemented - roles + permission sets enforced on Add Incident page |
| 3 | Parameterized SQL queries | Critical | Implemented - all incident-store queries use parameterized statements (`app/utils/db.py`); SQL-injection tests included |
| 4 | Input validation/encoding (XSS prevention) | High | Implemented - allow-lists for crime type/neighbourhood, date range checks, hour-of-day check, HTML/script sanitization (`app/utils/validation.py`, 18 tests); integrated into the Add Incident form |
| 5 | Audit logging for user actions | High | Implemented (prototype) - append-only JSONL audit log (`log_audit`/`read_audit_log`); DB-backed audit table planned |
| 6 | Session security (regenerate on login, secure config) | High | Implemented (prototype) - fresh random session id per login, 30-minute sliding expiry, logout clears session (`auth.py` create_session/is_session_valid/refresh_session); full HTTPS/session config still needed for real deployment |
| 7 | Login attempt limiting | High | Implemented (prototype) - 5 failures per 60s lockout (`record_failed_attempt`/`is_locked_out`) |
| 8 | Data minimization & coordinate generalization | Medium | Partially implemented - user-entered incidents stored in a separate SQLite DB (`data/prototype.db`) with block-level locations only; map generalization later |
| 9 | Dependency scanning (pip-audit) | Medium | Implemented - ran pip-audit (Oct 29): found 41 vulnerabilities in certifi + pillow, upgraded to patched versions, re-scan clean (see `docs/security/dependency_scan_report.md`) |
| 10 | Secrets management (no keys in repo) | High | In place - `.gitignore`, no credentials committed |
| 11 | Functional + security test checklist | Medium | Implemented - 87 tests total (20 security tests in `tests/test_security.py` and `tests/test_db.py`: audit log, lockout, RBAC matrix, password verification, sessions, injection) |

## 6. Security Testing Results

Testing was performed in two ways: automated tests (pytest) and manual
OWASP-style attack tests.

- **Automated:** 87 tests passing, including 20 security tests covering the
  audit log, login lockout, RBAC matrix, password verification, session
  handling, and SQL-injection safety.
- **Manual:** 10 OWASP-style attack cases tested and all passed, documented in
  `docs/security/security_testing_log.md` (SQL injection, stored XSS, login
  bypass, access control, record visibility, brute force, session reuse,
  allow-list/date validation, and secrets-in-repo).
- **Dependency scan:** `pip-audit` run; 41 vulnerabilities found in certifi
  and pillow, fixed by upgrading, re-scan clean
  (`docs/security/dependency_scan_report.md`).

Remaining before final submission: re-run the automated suite and `pip-audit`,
and review the audit log after the final demo.

## 7. Decisions

- **Database choice:** SQLite for the prototype (`data/prototype.db`, parameterized queries); PostgreSQL only if a production deployment is planned.
- **Deployment target:** Local only for this research prototype (run via `streamlit run Implementation/app/Home.py`). HTTPS/secure-session config is therefore handled by the development server defaults; a production deployment on Streamlit Community Cloud or a managed host would require enabling HTTPS and `secure` cookies before any real use.
- **Add Incident access:** Behind login only (RBAC + session checks). No IP restriction for demos, since the prototype is not exposed publicly.

## 8. Revision History

| Date | Version | Author | Change |
|---|---|---|---|
| Oct 9, 2026 | 0.1 | Shashank Chaudhary | Initial draft from proposal threat matrix |
| Oct 11, 2026 | 0.2 | Shashank Chaudhary | Control statuses updated for implemented auth/RBAC/audit/login-limiting; added login-attempt-limiting control; reflected prototype audit log design |
| Oct 15, 2026 | 0.3 | Shashank Chaudhary | Input validation module added (allow-lists, date checks, XSS sanitization) with 18 tests; control status updated |
| Oct 26, 2026 | 0.4 | Shashank Chaudhary | Database & Add Incident phase started: SQLite incident store with parameterized queries, form integration with validation and audit logging, user records kept separate from public data; controls 3, 4, 8 updated |
| Oct 29, 2026 | 0.5 | Shashank Chaudhary | Security testing phase started: pip-audit scan (41 vulns in certifi/pillow fixed, now clean) with report; RBAC matrix + password verification tests added; controls 9, 11 updated |
| Nov 4, 2026 | 0.6 | Shashank Chaudhary | Session hardening implemented (fresh session id per login, 30-min sliding expiry, logout clears session) with 6 tests; manual OWASP-style testing log added (10 cases, all passed); controls 6, 11 updated |
| Nov 4, 2026 | 1.0 | Shashank Chaudhary | Finalized: STRIDE statuses updated to reflect implemented mitigations, controls table completed, Security Testing Results section added (87 tests + manual testing + pip-audit) |
