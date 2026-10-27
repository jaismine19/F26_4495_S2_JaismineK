"""Security page - summarizes the cybersecurity workstream."""
import streamlit as st

st.title("Security")
st.markdown(
    "This page summarizes the cybersecurity workstream. Full documents live "
    "in `docs/security/`."
)

st.markdown("### Threat model status")
st.markdown(
    "- **Threat model v0.4** (`docs/security/threat_model.md`): assets, threat "
    "actors, STRIDE analysis, OWASP Top 10 relevance, controls, and "
    "security testing plan."
)
st.markdown(
    "- **Privacy review v0.1** (`docs/security/privacy_and_data_protection.md`): "
    "data inventory, privacy principles, credential handling, and location-data "
    "handling."
)

st.markdown("### Controls")

controls = [
    ("Password hashing (PBKDF2)", "Implemented", True),
    ("Role-based access control (Admin / Analyst / Data Entry)", "Implemented", True),
    ("Add Incident restricted to authorized roles", "Implemented", True),
    ("Login attempt limiting (5 tries, 60s lockout)", "Implemented", True),
    ("Audit logging (append-only)", "Implemented", True),
    ("Input validation & output encoding (XSS)", "Implemented", True),
    ("Parameterized SQL queries (SQLite, user records only)", "Implemented", True),
    ("User records kept separate from public data", "Implemented", True),
    ("Session security hardening", "Planned", False),
    ("Dependency scanning (pip-audit)", "Planned", False),
]

for name, status, done in controls:
    icon = ":white_check_mark:" if done else ":construction:"
    st.markdown(f"{icon} **{name}** - {status}")

st.markdown("### Demo credentials")
st.code(
    "admin  / demo_admin_123      (Administrator)\n"
    "analyst / demo_analyst_123   (Analyst)\n"
    "entry  / demo_entry_123      (Data Entry)",
    language="text",
)
