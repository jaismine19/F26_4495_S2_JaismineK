"""Add Incident - restricted to authorized users (prototype)."""
import streamlit as st

from app.utils.auth import (
    authenticate,
    has_permission,
    is_locked_out,
    log_audit,
    record_failed_attempt,
    reset_attempts,
)

st.title("Add Incident")
st.markdown(
    "Prototype incident-entry feature. User-entered records are kept separate "
    "from public historical data and stored with source/audit information."
)

if "user" not in st.session_state:
    st.session_state.user = None


def do_logout() -> None:
    if st.session_state.user is not None:
        log_audit(st.session_state.user["username"], "logout", "web logout")
    st.session_state.user = None
    st.rerun()


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

user = st.session_state.user
st.success(f"Logged in as **{user['username']}** (role: {user['role']})")
if st.button("Log out"):
    do_logout()

if not has_permission(user, "add_incident"):
    st.error("Your role is not allowed to add incidents.")
    st.stop()

st.markdown("### New incident form")
st.text_input("Crime type", disabled=True)
st.date_input("Incident date", disabled=True)
