"""
GitHub Migration Portal - Main Entry Point
Run this file to start the application: streamlit run app.py
"""
import streamlit as st
import sys
from pathlib import Path

# Set up path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# This will be the home page
st.set_page_config(
    page_title="GitHub Migration Portal",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide deploy button only
st.markdown("""
<style>
    /* Hide deploy button */
    [data-testid="stToolbar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Import after path setup
from utils.auth_service import AuthService, AuthUI

# Initialize auth session
AuthService.initialize_session()

# Header
col1, col2 = st.columns([10, 1])

with col1:
    st.title("🏠 GitHub Migration Portal")

with col2:
    if AuthService.is_authenticated():
        # Get session info for display
        session_info = AuthService.get_session_info()
        username = AuthService.get_username()

        # Kebab menu with username and settings
        with st.popover(f"👤 {username}"):
            st.markdown(f"### {username}")

            # Show role
            if AuthService.is_admin():
                st.caption("🔑 Administrator")
            else:
                st.caption("👤 User")

            st.markdown("---")

            # Session info
            if session_info:
                st.markdown(f"**Login Time:** {session_info['login_time']}")
                st.markdown(f"**Session Duration:** {session_info['session_duration']}")

            st.markdown("---")

            # Logout button
            if st.button("🚪 Logout", use_container_width=True, key="logout_home"):
                AuthService.logout()
                st.rerun()
    else:
        # Show login button
        if st.button("🔐 Login", use_container_width=True, key="show_login"):
            st.session_state.show_login_form = True

st.markdown("---")

# Show login form if button clicked
if not AuthService.is_authenticated() and st.session_state.get('show_login_form', False):
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        st.subheader("🔐 Login")

        with st.form("login_form_home"):
            username = st.text_input("Username", key="home_login_username")
            password = st.text_input("Password", type="password", key="home_login_password")

            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submit = st.form_submit_button("Login", use_container_width=True)
            with col_cancel:
                cancel = st.form_submit_button("Cancel", use_container_width=True)

            if submit:
                if username and password:
                    with st.spinner("Authenticating..."):
                        if AuthService.login(username, password):
                            st.session_state.show_login_form = False
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")

            if cancel:
                st.session_state.show_login_form = False
                st.rerun()

        st.markdown("---")

# Remove the logged in status message
st.markdown("---")

# Welcome section
st.header("Welcome to the GitHub Migration Portal")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Foot notes</p>
</div>
""", unsafe_allow_html=True)