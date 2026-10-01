"""Security page - summarizes the cybersecurity workstream (Shashank)."""
import streamlit as st

st.title("Security")
st.markdown(
    "This page summarizes the cybersecurity workstream. Full documents live "
    "in `docs/security/`."
)

st.markdown("### Threat model status")
st.markdown(
    "- **Threat model v0.1** (`docs/security/threat_model.md`): assets, threat "
    "actors, STRIDE analysis, OWASP Top 10 relevance, planned controls, and "
    "security testing plan."
)
st.markdown(
    "- **Privacy review v0.1** (`docs/security/privacy_and_data_protection.md`): "
    "data inventory, privacy principles, credential handling, and location-data "
    "handling."
)

st.markdown("### Controls")

controls = [
    ("Password hashing (PBKDF2 prototype, bcrypt/argon2 planned)", "Implemented (skeleton)", True),
    ("Role-based access control (Admin / Analyst / Data Entry)", "Implemented (skeleton)", True),
    ("Add Incident restricted to authorized roles", "Implemented (skeleton)", True),
    ("Parameterized SQL queries", "Planned (Oct 7-12, with database)", False),
    ("Input validation & output encoding (XSS)", "Planned", False),
    ("Audit logging", "Planned (with database)", False),
    ("Session security hardening", "Planned", False),
    ("Dependency scanning (pip-audit)", "Planned (testing phase)", False),
]

for name, status, done in controls:
    icon = ":white_check_mark:" if done else ":construction:"
    st.markdown(f"{icon} **{name}** - {status}")

st.markdown("### Demo credentials (classroom use only)")
st.code(
    "admin  / demo_admin_123      (Administrator)\n"
    "analyst / demo_analyst_123   (Analyst)\n"
    "entry  / demo_entry_123      (Data Entry)",
    language="text",
)
st.warning(
    "Demo passwords are for classroom demonstrations only and must not be "
    "reused anywhere else."
)
