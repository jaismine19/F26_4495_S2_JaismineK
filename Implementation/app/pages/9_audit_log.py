"""Audit Log - Administrator-only page.

Shows the append-only audit log written by the authentication module.
Only users with the view_audit permission (Administrator role) can read it.
"""
import pandas as pd
import streamlit as st

from app.utils.auth import authenticate, has_permission, read_audit_log

st.title("Audit Log")
st.markdown(
    "Append-only record of security-relevant events (logins, record changes). "
    "Only Administrators can view this page."
)

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.markdown("### Login")
    with st.form("audit_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
    if submitted:
        user = authenticate(username, password)
        if user is None:
            st.error("Invalid username or password.")
        else:
            st.session_state.user = user
            st.rerun()
    st.stop()

user = st.session_state.user
st.success(f"Logged in as **{user['username']}** (role: {user['role']})")

if not has_permission(user, "view_audit"):
    st.error("Only Administrators can view the audit log.")
    st.stop()

entries = read_audit_log()
if st.button("Refresh"):
    st.rerun()

if not entries:
    st.info(
        "No audit entries yet. Log in or out on the Add Incident page and "
        "then come back here."
    )
else:
    st.caption(f"{len(entries)} entries (newest last)")
    df = pd.DataFrame(entries)
    st.dataframe(
        df[["timestamp_utc", "user_id", "event", "detail"]],
        use_container_width=True,
        hide_index=True,
    )
