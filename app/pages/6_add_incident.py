"""Add Incident - restricted to authorized users (prototype)."""
import streamlit as st

from app.utils.auth import authenticate, has_permission

st.title("Add Incident")
st.markdown(
    "Prototype incident-entry feature. User-entered records are kept separate "
    "from public historical data and stored with source/audit information."
)

if "user" not in st.session_state:
    st.session_state.user = None


def do_logout() -> None:
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
        user = authenticate(username, password)
        if user is None:
            st.error("Invalid username or password.")
        else:
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
st.info("Form fields and database storage arrive in the Oct 29-Nov 9 phase.")
st.text_input("Crime type", disabled=True)
st.date_input("Incident date", disabled=True)
