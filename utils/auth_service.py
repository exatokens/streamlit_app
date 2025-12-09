"""
Authentication Service
Handles user authentication and session management
"""
import time

import streamlit as st
from datetime import datetime, timedelta
import hashlib
import json
from streamlit_cookies_controller import CookieController
from config.auth_config import (
    AUTH_ENABLED,
    ALLOWED_USERS,
    ADMIN_USERS,
    SESSION_TIMEOUT_MINUTES,
    AUTH_MESSAGES,
    LDAP_CONFIG,
    AD_CONFIG,
    PAGE_PERMISSIONS,
    BLOCKED_USERS
)


class AuthService:
    """Authentication service for user login and session management"""

    # Cookie controller instance
    _cookie_controller = None

    @staticmethod
    def _get_cookie_controller():
        """Get or create cookie controller instance"""
        if AuthService._cookie_controller is None:
            AuthService._cookie_controller = CookieController()
        return AuthService._cookie_controller

    @staticmethod
    def _create_session_data(username):
        """Create session data dictionary"""
        return {
            'username': username,
            'is_admin': username in ADMIN_USERS,
            'login_time': datetime.now().isoformat(),
            'token': hashlib.sha256(f"{username}{datetime.now().isoformat()}".encode()).hexdigest()[:32]
        }

    @staticmethod
    def initialize_session():
        """Initialize authentication session state"""
        # First time initialization
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.is_admin = False
            st.session_state.login_time = None
            st.session_state.last_activity = None

            # Try to restore from cookie
            try:
                cookies = AuthService._get_cookie_controller()
                session_cookie = cookies.get('auth_session')

                if session_cookie:
                    session_data = json.loads(session_cookie)

                    # Check if session is still valid (within timeout)
                    login_time = datetime.fromisoformat(session_data['login_time'])
                    if datetime.now() - login_time < timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                        # Restore session
                        st.session_state.authenticated = True
                        st.session_state.username = session_data['username']
                        st.session_state.is_admin = session_data['is_admin']
                        st.session_state.login_time = login_time
                        st.session_state.last_activity = datetime.now()
            except Exception:
                # If cookie is invalid or expired, just continue with fresh session
                pass

    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticate user with username and password

        Args:
            username: Username
            password: Password

        Returns:
            bool: True if authentication successful
        """
        # Simple authentication (check against allowed users)
        time.sleep(2)
        if username in ALLOWED_USERS and ALLOWED_USERS[username] == password:
            return True

        # TODO: Add LDAP authentication
        # if LDAP_CONFIG['enabled']:
        #     return AuthService._authenticate_ldap(username, password)

        # TODO: Add AD authentication
        # if AD_CONFIG['enabled']:
        #     return AuthService._authenticate_ad(username, password)

        return False

    @staticmethod
    def _authenticate_ldap(username, password):
        """
        Authenticate user against LDAP server

        Args:
            username: Username
            password: Password

        Returns:
            bool: True if authentication successful
        """
        # TODO: Implement LDAP authentication
        # import ldap3
        # server = ldap3.Server(LDAP_CONFIG['server'])
        # user_dn = LDAP_CONFIG['user_dn_template'].format(username=username)
        # conn = ldap3.Connection(server, user=user_dn, password=password)
        # return conn.bind()
        pass

    @staticmethod
    def _authenticate_ad(username, password):
        """
        Authenticate user against Active Directory

        Args:
            username: Username
            password: Password

        Returns:
            bool: True if authentication successful
        """
        # TODO: Implement AD authentication
        # import ldap3
        # server = ldap3.Server(AD_CONFIG['server'], use_ssl=AD_CONFIG['use_ssl'])
        # user = f"{AD_CONFIG['domain']}\\{username}"
        # conn = ldap3.Connection(server, user=user, password=password)
        # return conn.bind()
        pass

    @staticmethod
    def login(username, password):
        """
        Login user and create session

        Args:
            username: Username
            password: Password

        Returns:
            bool: True if login successful
        """
        if AuthService.authenticate_user(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.is_admin = username in ADMIN_USERS
            st.session_state.login_time = datetime.now()
            st.session_state.last_activity = datetime.now()

            # Save session to cookie
            try:
                session_data = AuthService._create_session_data(username)
                cookies = AuthService._get_cookie_controller()
                # Set cookie to expire in SESSION_TIMEOUT_MINUTES
                cookies.set('auth_session', json.dumps(session_data), max_age=SESSION_TIMEOUT_MINUTES * 60)
            except Exception:
                # If cookie save fails, session will still work for current page load
                pass

            return True
        return False

    @staticmethod
    def logout():
        """Logout user and clear session"""
        # Clear cookie
        try:
            cookies = AuthService._get_cookie_controller()
            cookies.remove('auth_session')
        except Exception:
            pass

        # Clear session state
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.is_admin = False
        st.session_state.login_time = None
        st.session_state.last_activity = None

    @staticmethod
    def is_authenticated():
        """
        Check if user is authenticated and session is valid

        Returns:
            bool: True if authenticated and session valid
        """
        if not AUTH_ENABLED:
            return True

        if not st.session_state.get('authenticated', False):
            return False

        # Check session timeout
        if st.session_state.last_activity:
            elapsed = datetime.now() - st.session_state.last_activity
            if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                AuthService.logout()
                return False

        # Update last activity
        st.session_state.last_activity = datetime.now()
        return True

    @staticmethod
    def is_admin():
        """
        Check if current user is admin

        Returns:
            bool: True if user is admin
        """
        return st.session_state.get('is_admin', False)

    @staticmethod
    def get_username():
        """
        Get current username

        Returns:
            str: Username or None
        """
        return st.session_state.get('username', None)

    @staticmethod
    def get_session_info():
        """
        Get session information

        Returns:
            dict: Session information
        """
        if not AuthService.is_authenticated():
            return None

        login_time = st.session_state.get('login_time')
        last_activity = st.session_state.get('last_activity')

        return {
            'username': st.session_state.username,
            'is_admin': st.session_state.is_admin,
            'login_time': login_time.strftime('%Y-%m-%d %H:%M:%S') if login_time else None,
            'last_activity': last_activity.strftime('%Y-%m-%d %H:%M:%S') if last_activity else None,
            'session_duration': str(datetime.now() - login_time).split('.')[0] if login_time else None
        }

    @staticmethod
    def can_access_page(page_name, username=None):
        """
        Check if user can access a specific page

        Args:
            page_name: Name of the page (e.g., 'github_migration')
            username: Username to check (uses current user if None)

        Returns:
            bool: True if user can access the page
        """
        if not AUTH_ENABLED:
            return True

        if username is None:
            username = AuthService.get_username()

        if not username:
            return False

        # Check if user is blocked from this page
        if page_name in BLOCKED_USERS:
            if username in BLOCKED_USERS[page_name]:
                return False

        # Check if page has specific permissions
        if page_name in PAGE_PERMISSIONS:
            allowed_users = PAGE_PERMISSIONS[page_name]

            # "*" means all authenticated users
            if allowed_users == "*":
                return True

            # Check if user is in the allowed list
            return username in allowed_users

        # If page not in permissions config, allow all authenticated users
        return True

    @staticmethod
    def get_accessible_pages(username=None):
        """
        Get list of pages accessible to a user

        Args:
            username: Username to check (uses current user if None)

        Returns:
            list: List of accessible page names
        """
        if username is None:
            username = AuthService.get_username()

        if not username:
            return []

        accessible_pages = []

        # Check all pages in PAGE_PERMISSIONS
        for page_name in PAGE_PERMISSIONS.keys():
            if AuthService.can_access_page(page_name, username):
                accessible_pages.append(page_name)

        return accessible_pages

    @staticmethod
    def get_access_denied_message(page_name):
        """
        Get access denied message for a specific page

        Args:
            page_name: Name of the page

        Returns:
            str: Access denied message
        """
        username = AuthService.get_username()

        if page_name in BLOCKED_USERS and username in BLOCKED_USERS[page_name]:
            return f"🚫 Access Denied: User '{username}' is not permitted to access this page."

        if page_name in PAGE_PERMISSIONS:
            return f"🚫 Access Denied: User '{username}' does not have permission to access this page."

        return AUTH_MESSAGES['access_denied']


class AuthUI:
    """UI components for authentication"""

    @staticmethod
    def render_login_page():
        """Render login page"""
        st.title(AUTH_MESSAGES['login_title'])
        st.markdown("---")

        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.info(AUTH_MESSAGES['login_prompt'])

            with st.form("login_form"):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                submit = st.form_submit_button("Login", use_container_width=True)

                if submit:
                    if username and password:
                        with st.spinner("Authenticating..."):
                            if AuthService.login(username, password):
                                st.rerun()
                            else:
                                st.error(AUTH_MESSAGES['invalid_credentials'])
                    else:
                        st.warning("Please enter both username and password")

    @staticmethod
    def render_session_info():
        """Render session information in sidebar"""
        if AuthService.is_authenticated():
            session_info = AuthService.get_session_info()

            with st.sidebar:
                st.markdown("---")
                st.markdown("### 👤 Session Info")
                st.markdown(f"**User:** {session_info['username']}")

                if session_info['is_admin']:
                    st.markdown("**Role:** 🔑 Admin")
                else:
                    st.markdown("**Role:** 👤 User")

                st.markdown(f"**Login:** {session_info['login_time']}")
                st.markdown(f"**Duration:** {session_info['session_duration']}")

                if st.button("Logout", use_container_width=True):
                    AuthService.logout()
                    st.success(AUTH_MESSAGES['logout_success'])
                    st.rerun()

    @staticmethod
    def render_logout_button():
        """Render logout button in header"""
        if AuthService.is_authenticated():
            col1, col2 = st.columns([5, 1])
            with col2:
                if st.button("🚪 Logout", use_container_width=True):
                    AuthService.logout()
                    st.rerun()


def require_authentication(func):
    """
    Decorator to require authentication for a function

    Usage:
        @require_authentication
        def my_protected_function():
            # Function code
    """
    def wrapper(*args, **kwargs):
        AuthService.initialize_session()

        if not AuthService.is_authenticated():
            AuthUI.render_login_page()
            st.stop()

        return func(*args, **kwargs)

    return wrapper


def require_admin(func):
    """
    Decorator to require admin role for a function

    Usage:
        @require_admin
        def my_admin_function():
            # Function code
    """
    def wrapper(*args, **kwargs):
        AuthService.initialize_session()

        if not AuthService.is_authenticated():
            AuthUI.render_login_page()
            st.stop()

        if not AuthService.is_admin():
            st.error(AUTH_MESSAGES['access_denied'])
            st.stop()

        return func(*args, **kwargs)

    return wrapper


def require_page_access(page_name):
    """
    Decorator to require specific page access permissions

    Usage:
        @require_page_access("github_migration")
        def main():
            # Function code

    Args:
        page_name: Name of the page (must match key in PAGE_PERMISSIONS)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            AuthService.initialize_session()

            # First check if user is authenticated
            if not AuthService.is_authenticated():
                AuthUI.render_login_page()
                st.stop()

            # Then check if user has access to this specific page
            if not AuthService.can_access_page(page_name):
                st.error(AuthService.get_access_denied_message(page_name))

                # Show which pages they CAN access
                accessible_pages = AuthService.get_accessible_pages()
                if accessible_pages:
                    st.info(f"You have access to: {', '.join(accessible_pages)}")

                # Add a home button
                if st.button("🏠 Go to Home"):
                    st.switch_page("app.py")

                st.stop()

            return func(*args, **kwargs)

        return wrapper
    return decorator