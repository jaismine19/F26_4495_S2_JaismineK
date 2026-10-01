# Work Log - Shashank Chaudhary (300392521)

| Date | Hours | Description of work done |
|---|---|---|
| Sep 18, 2026 | 1.5 | Initial research/project planning |
| Sep 22, 2026 | 2.5 | Cybersecurity research/threat modeling: Identified potential security risks for the crime-data web application, including unauthorized access, SQL injection, XSS, password security, session security, and data exposure |
| Sep 26, 2026 | 2 | GitHub/repository work: Accepted collaborator invitation, cloned the project repository, and set up the local project directory for development |
| Sep 30, 2026 | 1.5 | Project setup: Created folder structure (data/, scripts/, docs/, app/, tests/, worklogs/); added .gitignore; wrote scripts/00_download_data.py for reproducible data acquisition |
| Sep 30, 2026 | 1.5 | Data acquisition: Downloaded VPD crime dataset from GeoDASH open data (all neighbourhoods, all years); wrote scripts/01_inspect_data.py; generated data quality summary (927,794 rows; 34,527 duplicates; missing 2022; 83K zero coordinates) |
| Sep 30, 2026 | 1 | Documentation: Wrote docs/research/dataset_documentation.md covering source, schema, quality findings, and privacy notes |
| Sep 30, 2026 | 1.5 | Threat model: Drafted docs/security/threat_model.md v0.1 - assets, threat actors, STRIDE analysis, OWASP Top 10 relevance, planned controls, and security testing plan |
| Sep 30, 2026 | 1.5 | Data cleaning: Wrote scripts/02_clean_data.py (dedupe, categorical standardization, zero-coordinate flagging, date/day-of-week/season features); cleaned dataset 927,794 to 893,267 rows with documented cleaning log |
| Sep 30, 2026 | 1.5 | Privacy review: Drafted docs/security/privacy_and_data_protection.md v0.1 - data inventory, privacy principles, credential handling, location-data handling, implementation checklist |
| Sep 30, 2026 | 0.5 | Repository maintenance: Updated README progress table and work log; committed and pushed all work to GitHub |
