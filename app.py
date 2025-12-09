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

# Import after path setup
from utils.auth_service import AuthService, AuthUI

# Initialize auth session
AuthService.initialize_session()

# Header with login/logout
col1, col2, col3 = st.columns([4, 1, 1])

with col1:
    st.title("🏠 GitHub Migration Portal")

with col2:
    if AuthService.is_authenticated():
        st.markdown(f"**👤 {AuthService.get_username()}**")

with col3:
    if AuthService.is_authenticated():
        if st.button("🚪 Logout", use_container_width=True, key="logout_home"):
            AuthService.logout()
            st.rerun()
    else:
        # Show login form in expander
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
                    if AuthService.login(username, password):
                        st.session_state.show_login_form = False
                        st.success(f"Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")

            if cancel:
                st.session_state.show_login_form = False
                st.rerun()

        st.markdown("---")

# Show authentication status
if AuthService.is_authenticated():
    st.success(f"✅ Logged in as: **{AuthService.get_username()}**" +
               (f" **(Admin)**" if AuthService.is_admin() else ""))
else:
    st.info("ℹ️ You are browsing as a guest. Click **Login** button above to access protected pages.")

    # Show test credentials
    with st.expander("🔑 Test Credentials", expanded=False):
        st.markdown("""
        **For Testing/Development:**
        
        Admin Users:
        - Username: `admin` / Password: `admin123`
        - Username: `siva` / Password: `password123`
        
        Regular Users:
        - Username: `john.doe` / Password: `john123`
        - Username: `jane.smith` / Password: `jane123`
        
        ⚠️ **Important:** Change these passwords before production use!
        """)

st.markdown("---")

# Welcome section
st.header("Welcome to the GitHub Migration Portal")

st.markdown("""
This portal helps you manage and track GitHub repository migrations.

### 📋 Available Pages

#### 🔓 Public Pages (No Login Required)
- **Home** - This page

#### 🔒 Protected Pages (Login Required)
- **GitHub Migration** - Manage migration data and track progress
  - View and edit migration records
  - Filter and search data
  - Update JIRA status
  - Track changes and save progress

### 🎯 Features

- **Real-time Data Management** - Edit and save migration data
- **JIRA Integration** - Fetch and update JIRA ticket status
- **Advanced Filtering** - Filter by any column
- **Change Tracking** - View and manage pending changes
- **Role-based Access** - Admin and user roles

### 🔐 Authentication

To access protected pages, click on **github_migration** in the sidebar (or click Login button above first), then log in with your credentials.

For security reasons, sessions expire after 60 minutes of inactivity.
""")

# Quick stats section (if user is logged in)
if AuthService.is_authenticated():
    st.markdown("---")
    st.subheader("📊 Quick Access")

    # Get accessible pages for current user
    accessible_pages = AuthService.get_accessible_pages()

    col1, col2, col3 = st.columns(3)

    with col1:
        # Check if user can access github_migration
        if AuthService.can_access_page("github_migration"):
            st.info("**GitHub Migration**\n\n✅ Manage migration data")
            st.markdown("Click **github_migration** in the sidebar →")
        else:
            st.warning("**GitHub Migration**\n\n🚫 Access restricted")
            st.caption("You don't have permission")

    with col2:
        st.info("**Session Info**\n\nView your session")
        session_info = AuthService.get_session_info()
        if session_info:
            st.write(f"Duration: {session_info['session_duration']}")

    with col3:
        st.info("**User Role**\n\nYour permissions")
        if AuthService.is_admin():
            st.write("🔑 Admin")
        else:
            st.write("👤 User")

    # Show accessible pages list
    if accessible_pages:
        st.markdown("---")
        st.markdown("### 🔓 Your Accessible Pages")
        for page in accessible_pages:
            st.markdown(f"- ✅ {page.replace('_', ' ').title()}")
    else:
        st.info("ℹ️ You don't have access to any restricted pages.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>GitHub Migration Portal v2.0 with Authentication</p>
    <p>For support, please contact your administrator</p>
</div>
""", unsafe_allow_html=True)