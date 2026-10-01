# Privacy Review & Data Protection Requirements

**Owner:** Shashank Chaudhary (Cybersecurity workstream)
**Status:** Draft v0.1 - September 30, 2026
**Related:** `docs/security/threat_model.md`

## 1. Data Inventory

| Data | Source | Sensitivity | Stored Where |
|---|---|---|---|
| Public VPD crime records | VPD GeoDASH open data | Public (already anonymized) | Read-only dataset (DB/CSV) |
| User accounts (username, password hash, role) | Created by admin | Personal data | Database |
| User-entered incident records (prototype) | Authorized users | Low-Medium (fictional/prototype) | Database, tagged `source='user'` |
| Audit logs | Application | Internal | Database (append-only) |

## 2. Privacy Analysis of the Public Dataset

The VPD dataset is public and designed to protect privacy:

- **Location anonymization:** Incidents are reported at hundred-block level
  (e.g., `10XX ALBERNI ST`), never exact addresses.
- **Category aggregation:** Violent incidents are aggregated under
  "Offence Against a Person" to reduce identifiability.
- **No personal identifiers:** The dataset contains no names, ages, genders,
  or other demographic fields.

**Our obligations when presenting this data:**

1. Do not attempt to re-identify individuals from incident records.
2. Aggregate or generalize exact coordinates (X/Y) on public maps where
   appropriate (e.g., neighbourhood-level counts, density surfaces).
3. Clearly label the data as *reported* incidents, not all crime (VPD
   documentation itself notes late reporting and reclassification).
4. Keep user-entered prototype records visually and logically separate from
   public historical data.

## 3. Data Protection Principles Applied

| Principle | How we implement it |
|---|---|
| **Data minimization** | Collect only username, password hash, and role; no PII (names, emails, phones) needed for the prototype |
| **Purpose limitation** | Incident-entry feature exists only to demonstrate secure data collection; not official reporting |
| **Storage limitation** | User-entered records carry timestamps and audit info; prototype data can be purged |
| **Integrity & confidentiality** | Parameterized SQL, hashed passwords, RBAC (see threat model) |
| **Transparency** | Methodology/Limitations page explains data sources and prototype scope |

## 4. User-Entered (Prototype) Incident Data

- The "Add Incident" form will collect: crime type, date/time, neighbourhood,
  optional location, and notes.
- We will **not** collect: victim names, addresses of individuals, contact
  details, or any real incident information. Demo entries will be fictional
  and clearly marked.
- Records are stored with `created_by` and `created_at` so they can be
  attributed and audited.

## 5. Passwords & Credentials

- Passwords hashed with a strong adaptive algorithm (bcrypt or argon2);
  never stored or logged in plain text.
- Demo credentials used in class presentations will be changed afterward and
  will never be committed to the repository.
- No API keys, secrets, or database URLs in the GitHub repo (enforced via
  `.gitignore` and review).

## 6. Location Data Handling

- Maps may show: neighbourhood polygons, aggregated counts, and generalized
  points/density surfaces—not raw precise coordinates of individual
  incidents.
- If heatmaps are used, kernel density will smooth values so individual
  incidents are not visually recoverable.

## 7. Compliance Context (Educational Prototype)

- The project is an academic prototype and does not provide services to the
  public; no production data is collected.
- We align practices with general privacy principles and OWASP guidance, and
  note where full compliance frameworks (e.g., BC FIPPA/PIPEDA) would apply
  in a production deployment.

## 8. Requirements Checklist for Implementation

- [ ] RBAC enforced on every page (public vs Analyst vs Data Entry vs Admin)
- [ ] Password hashing (bcrypt/argon2) with per-user salts
- [ ] Parameterized queries everywhere user input touches SQL
- [ ] Input validation on Add Incident form (lengths, allowed values, date ranges)
- [ ] Output encoding to prevent stored XSS from incident fields
- [ ] Audit log entries for login success/failure and record changes
- [ ] No secrets or real data committed to GitHub
- [ ] Coordinate generalization on all map views

## 9. Revision History

| Date | Version | Author | Change |
|---|---|---|---|
| Sep 30, 2026 | 0.1 | Shashank Chaudhary | Initial draft |
