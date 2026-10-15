# Threat Model - Vancouver Urban Safety Intelligence Platform

**Owner:** Shashank Chaudhary (Cybersecurity workstream)
**Status:** Draft v0.3 - October 15, 2026
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
| Attacker impersonates another user | Medium | Hashed passwords (e.g., bcrypt/argon2), session validation on every request | Planned |
| Attacker guesses/reuses credentials | Medium | Password policy: minimum length, breach-password check where feasible | Planned |

### 4.2 Tampering

| Threat | Risk | Mitigation | Status |
|---|---|---|---|
| User modifies another user's incident records | Medium | Role-based access control (RBAC); ownership checks on update/delete | Planned |
| User alters audit logs | Medium | Append-only audit table; no update/delete permissions on logs | Planned |
| Injection of fake incident data | Low-Medium | All user-entered records tagged with `source='user'` and kept separate from public data | Planned |

### 4.3 Repudiation

| Threat | Risk | Mitigation | Status |
|---|---|---|---|
| User denies submitting a record | Low | Audit logs with user_id, action, timestamp on every write | Planned |

### 4.4 Information Disclosure

| Threat | Risk | Mitigation | Status |
|---|---|---|---|
| SQL injection leaks database contents | High | Parameterized queries only; test with injection payloads | Planned |
| Passwords stored in plain text | High | Secure password hashing (bcrypt/argon2), never store plaintext | Planned |
| Error messages reveal internals | Low | Generic error pages; log details server-side only | Planned |
| Sensitive data in logs | Medium | Redact credentials/tokens from logs | Planned |
| Over-precise location display | Low-Medium | Aggregate/generalize coordinates on public maps (privacy) | Planned |

### 4.5 Denial of Service

| Threat | Risk | Mitigation | Status |
|---|---|---|---|
| Resource exhaustion via repeated requests | Low | Rate limiting where feasible; demo app runs on a small instance | Under review |

### 4.6 Elevation of Privilege

| Threat | Risk | Mitigation | Status |
|---|---|---|---|
| Role confusion (user acts as admin) | High | Server-side role checks on every privileged page/action; roles assigned only by admin | Planned |
| Session fixation/hijacking | Medium | Secure session configuration; regenerate session on login | Planned |

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

| # | Control | Priority | Status (Oct 11) |
|---|---|---|---|
| 1 | Password hashing | Critical | Implemented - PBKDF2-HMAC-SHA256, 200k iterations, per-user salt (`app/utils/auth.py`); bcrypt/argon2 upgrade before any non-demo use |
| 2 | RBAC: Administrator, Analyst, Data Entry | Critical | Implemented - roles + permission sets enforced on Add Incident page |
| 3 | Parameterized SQL queries | Critical | Planned (with database phase) |
| 4 | Input validation/encoding (XSS prevention) | High | Implemented (module) - allow-lists for crime type/neighbourhood, date range checks, HTML/script sanitization (`app/utils/validation.py`, 18 tests); awaiting form integration |
| 5 | Audit logging for user actions | High | Implemented (prototype) - append-only JSONL audit log (`log_audit`/`read_audit_log`); DB-backed audit table planned |
| 6 | Session security (regenerate on login, secure config) | High | Partial - Streamlit session state; hardening planned |
| 7 | Login attempt limiting | High | Implemented (prototype) - 5 failures per 60s lockout (`record_failed_attempt`/`is_locked_out`) |
| 8 | Data minimization & coordinate generalization | Medium | Documented in privacy review; map implementation later |
| 9 | Dependency scanning (pip-audit) | Medium | Planned (testing phase) |
| 10 | Secrets management (no keys in repo) | High | In place - `.gitignore`, no credentials committed |
| 11 | Functional + security test checklist | Medium | In progress - 6 security unit tests added (`tests/test_security.py`) |

## 6. Security Testing Plan (for later phases)

- Manual testing with OWASP-style test cases (SQLi, XSS, auth bypass).
- Automated dependency scan: `pip-audit`.
- Session/role matrix test: every page x every role.
- Review of audit logs after test submissions.

## 7. Open Questions / Decisions Needed

- Final database choice (SQLite for prototype vs PostgreSQL) - affects controls.
- Deployment target (Streamlit Community Cloud vs local) - affects HTTPS/session config.
- Whether the Add Incident page is behind login only, or also IP-restricted for demos.

## 8. Revision History

| Date | Version | Author | Change |
|---|---|---|---|
| Oct 9, 2026 | 0.1 | Shashank Chaudhary | Initial draft from proposal threat matrix |
| Oct 11, 2026 | 0.2 | Shashank Chaudhary | Control statuses updated for implemented auth/RBAC/audit/login-limiting; added login-attempt-limiting control; reflected prototype audit log design |
| Oct 15, 2026 | 0.3 | Shashank Chaudhary | Input validation module added (allow-lists, date checks, XSS sanitization) with 18 tests; control status updated |
