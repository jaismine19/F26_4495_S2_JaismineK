"""Add Incident - end-to-end secure incident entry (prototype).

Login (RBAC + attempt limiting + audit) -> validated form (allow-lists, date
checks, sanitization) -> parameterized SQLite insert -> user-entered records
displayed separately from public VPD data. The audit trail itself is shown on
the administrator-only Audit Log page.
"""
from datetime import date

import streamlit as st

from app.utils import db
from app.utils.auth import (
    authenticate,
    has_permission,
    is_locked_out,
    log_audit,
    record_failed_attempt,
    reset_attempts,
)
from app.utils.validation import (
    ALLOWED_CRIME_TYPES,
    ALLOWED_NEIGHBOURHOODS,
    validate_incident_record,
    validate_notes,
)

st.title("Add Incident")
st.markdown(
    "Prototype incident-entry feature. User-entered records are stored in a "
    "separate database table with `source='user'` and audit information; they "
    "are never mixed into the public VPD dataset."
)

if "user" not in st.session_state:
    st.session_state.user = None


def do_logout() -> None:
    if st.session_state.user is not None:
        log_audit(st.session_state.user["username"], "logout", "web logout")
    st.session_state.user = None
    st.rerun()


# ------------------------------------------------------------------- login
if st.session_state.user is None:
    st.markdown("### Login")
    st.caption("Demo users: `admin` / `analyst` / `entry` (see Security page for demo passwords)")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
    if submitted:
        username = username.strip().lower()
        if is_locked_out(username):
            st.error("Too many failed attempts. Account locked for 60 seconds.")
        else:
            user = authenticate(username, password)
            if user is None:
                log_audit(username or "unknown", "login_failure", "invalid credentials")
                locked = record_failed_attempt(username)
                message = "Invalid username or password."
                if locked:
                    message += " Account locked for 60 seconds."
                st.error(message)
            else:
                reset_attempts(username)
                log_audit(username, "login_success", "web login")
                st.session_state.user = user
                st.rerun()
    st.stop()

# -------------------------------------------------------------- logged in
user = st.session_state.user
st.success(f"Logged in as **{user['username']}** (role: {user['role']})")
if st.button("Log out"):
    do_logout()

if not has_permission(user, "add_incident"):
    st.error("Your role is not allowed to add incidents.")
    st.stop()

if has_permission(user, "view_audit"):
    st.info(
        "Your role (Administrator) can add incidents, see all entered "
        "records, and view the Audit Log page."
    )
elif has_permission(user, "view_all"):
    st.info(
        "Your role (Analyst) can add incidents and see all entered records, "
        "but cannot view the Audit Log."
    )
else:
    st.info(
        "Your role (Data Entry) can add incidents but can only see the "
        "records they entered themselves."
    )

# ------------------------------------------------------------------- form
st.markdown("### New incident form")

crime_type = st.selectbox(
    "Crime type", sorted(ALLOWED_CRIME_TYPES), index=None,
    placeholder="Select a crime type...",
)
incident_date = st.date_input(
    "Incident date",
    min_value=date(2003, 1, 1),
    max_value=date.today(),
)
neighbourhood = st.selectbox(
    "Neighbourhood", sorted(ALLOWED_NEIGHBOURHOODS), index=None,
    placeholder="Select a neighbourhood...",
)
hour = st.selectbox(
    "Hour of day",
    ["Not recorded"] + list(range(24)),
    index=0,
    format_func=lambda h: "Not recorded" if h == "Not recorded" else f"{h:02d}:00",
)
location = st.text_input(
    "Location (hundred block or general area)", max_chars=100,
)
notes = st.text_area("Notes (optional)", max_chars=200)

if st.button("Submit incident"):
    record = {
        "crime_type": crime_type or "",
        "incident_date": incident_date,
        "neighbourhood": neighbourhood or "",
        "hour": None if hour == "Not recorded" else int(hour),
        "location": location or "",
        "notes": notes or "",
    }
    is_valid, errors = validate_incident_record(record)
    if not is_valid:
        for field, message in errors.items():
            st.error(f"{field}: {message}")
    else:
        record["notes"] = validate_notes(record["notes"])
        new_id = db.insert_incident(record, user["username"], user["role"])
        log_audit(
            user["username"],
            "incident_added",
            f"id={new_id} type={record['crime_type']}",
        )
        st.success(f"Incident saved (id {new_id}). It appears below, tagged "
                   "`source='user'` and kept separate from VPD data.")

# ------------------------------------------------- user-entered records list
st.markdown("### Prototype entries (user-entered, separate from VPD data)")
st.metric("Total user-entered incidents", db.count_incidents())
if has_permission(user, "view_all"):
    entries = db.fetch_incidents(limit=20)
    st.caption(
        f"Your role ({user['role']}) can see all entered records from every user."
    )
else:
    entries = db.fetch_incidents(limit=20, created_by=user["username"])
    st.caption(
        f"Your role ({user['role']}) can see only the records you entered."
    )
if not entries:
    st.caption("No prototype entries yet. Submit the form above to create one.")
else:
    st.dataframe(entries, width="stretch", hide_index=True)
    st.caption(
        "These records are fictional/demo data. They are stored in a separate "
        "table and are never shown in the public-data analytics pages."
    )
