# Manual Security Testing Log

**Date:** November 4, 2026
**Tester:** Shashank Chaudhary (300392521)
**Scope:** Vancouver Urban Safety Intelligence Platform prototype (Streamlit app)
**Method:** Manual OWASP-style attack tests performed in the browser and with
automated tests. Each case below lists the OWASP Top 10 (2021) category, what
we tried, and the result.

## Results summary

| # | Test | OWASP category | Result |
|---|---|---|---|
| 1 | SQL injection through incident fields | A03 Injection | Passed - stored as plain text |
| 2 | Stored XSS through location/notes | A03 Injection | Passed - markup removed |
| 3 | Login bypass with wrong/empty password | A07 Identification & Auth | Passed - rejected |
| 4 | Access Audit Log as non-admin | A01 Broken Access Control | Passed - blocked |
| 5 | View other users' records as Data Entry | A01 Broken Access Control | Passed - hidden |
| 6 | Brute-force login (many wrong attempts) | A07 Identification & Auth | Passed - locked out 60s |
| 7 | Session reuse / expired session | A07 Identification & Auth | Passed - expired sessions dropped |
| 8 | Unknown crime type / neighbourhood | A03 Injection | Passed - rejected by allow-list |
| 9 | Future or pre-2003 date | A03 / A01 | Passed - rejected |
| 10 | Secrets in the repository | A05 Security Misconfiguration | Passed - no keys committed |

## Details

### 1. SQL injection (A03)
Tried entering `'; DROP TABLE incidents; --` and similar payloads into the
location and notes fields. The records were stored as ordinary text because
every database query uses parameterized statements (`app/utils/db.py`). The
table remained intact and accepted new records afterwards (covered by
`tests/test_db.py`).

### 2. Stored XSS (A03)
Entered `<script>alert(1)</script>` and `javascript:...` into the location and
notes fields. The sanitizer (`app/utils/validation.py`) strips HTML tags and
script markers before the record is saved, so the payload never renders.

### 3. Login bypass (A07)
Tried empty passwords, wrong passwords, and unknown usernames. All were
rejected. Passwords are hashed with PBKDF2 and checked in constant time.

### 4. Audit Log access control (A01)
Logged in as `analyst` and `entry` and tried to open the Audit Log page. The
page shows "Only Administrators can view the audit log" and stops, because
the check uses the `view_audit` permission.

### 5. Record visibility by role (A01)
Logged in as `entry` and confirmed the records table shows only records they
entered. The `analyst` and `admin` roles see all records. This is enforced by
filtering on `created_by` in the query.

### 6. Brute-force login (A07)
Submitted wrong passwords five times in a row. After the fifth failure the
account was locked for 60 seconds (`auth.py`), blocking further attempts.

### 7. Session handling (A07)
After adding sessions (Nov 4), logging in issues a fresh random session id,
expired sessions are detected and dropped with a "session has expired"
message, and logout clears the session. This guards against session fixation
and stale sessions.

### 8-9. Allow-list and date validation (A03/A01)
Crime type and neighbourhood are limited to the exact values from the real
dataset. Dates must be from 2003 onward and not in the future. Invalid
values are rejected with a clear message.

### 10. Secrets in the repository (A05)
Confirmed no API keys or credentials are committed: demo passwords are for
classroom use only and are clearly marked, and the database and data files
are gitignored.

## Conclusion

All manual tests passed. Remaining planned work: re-run the full automated
suite and the pip-audit dependency scan before the final submission, and
review the audit log after the final demo.
