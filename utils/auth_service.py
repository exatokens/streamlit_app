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
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.is_admin = False
            st.session_state.login_time = None
            st.session_state.last_activity = None

            try:
                cookies = AuthService._get_cookie_controller()
                session_cookie = cookies.get('auth_session')

                if session_cookie:
                    session_data = json.loads(session_cookie)
                    login_time = datetime.fromisoformat(session_data['login_time'])
                    if datetime.now() - login_time < timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                        st.session_state.authenticated = True
                        st.session_state.username = session_data['username']
                        st.session_state.is_admin = session_data['is_admin']
                        st.session_state.login_time = login_time
                        st.session_state.last_activity = datetime.now()
            except Exception:
                pass

    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user with username and password"""
        if username in ALLOWED_USERS and ALLOWED_USERS[username] == password:
            return True
        return False

    @staticmethod
    def login(username, password):
        """Login user and create session"""
        if AuthService.authenticate_user(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.is_admin = username in ADMIN_USERS
            st.session_state.login_time = datetime.now()
            st.session_state.last_activity = datetime.now()

            try:
                session_data = AuthService._create_session_data(username)
                cookies = AuthService._get_cookie_controller()
                cookies.set('auth_session', json.dumps(session_data), max_age=SESSION_TIMEOUT_MINUTES * 60)
            except Exception:
                pass

            return True
        return False

    @staticmethod
    def logout():
        """Logout user and clear session"""
        try:
            cookies = AuthService._get_cookie_controller()
            cookies.remove('auth_session')
        except Exception:
            pass

        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.is_admin = False
        st.session_state.login_time = None
        st.session_state.last_activity = None

    @staticmethod
    def is_authenticated():
        """Check if user is authenticated and session is valid"""
        if not AUTH_ENABLED:
            return True

        if not st.session_state.get('authenticated', False):
            return False

        if st.session_state.last_activity:
            elapsed = datetime.now() - st.session_state.last_activity
            if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                AuthService.logout()
                return False

        st.session_state.last_activity = datetime.now()
        return True

    @staticmethod
    def is_admin():
        """Check if current user is admin"""
        return st.session_state.get('is_admin', False)

    @staticmethod
    def get_username():
        """Get current username"""
        return st.session_state.get('username', None)

    @staticmethod
    def get_session_info():
        """Get session information"""
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
        """Check if user can access a specific page"""
        if not AUTH_ENABLED:
            return True

        if username is None:
            username = AuthService.get_username()

        if not username:
            return False

        if page_name in BLOCKED_USERS:
            if username in BLOCKED_USERS[page_name]:
                return False

        if page_name in PAGE_PERMISSIONS:
            allowed_users = PAGE_PERMISSIONS[page_name]

            if allowed_users == "*":
                return True

            return username in allowed_users

        return True

    @staticmethod
    def get_accessible_pages(username=None):
        """Get list of pages accessible to a user"""
        if username is None:
            username = AuthService.get_username()

        if not username:
            return []

        accessible_pages = []

        for page_name in PAGE_PERMISSIONS.keys():
            if AuthService.can_access_page(page_name, username):
                accessible_pages.append(page_name)

        return accessible_pages

    @staticmethod
    def get_access_denied_message(page_name):
        """Get access denied message for a specific page"""
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

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.info(AUTH_MESSAGES['login_prompt'])

            with st.form("login_form"):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                submit = st.form_submit_button("Login", width="stretch")

                if submit:
                    if username and password:
                        with st.spinner("Authenticating..."):
                            if AuthService.login(username, password):
                                st.rerun()
                            else:
                                st.error(AUTH_MESSAGES['invalid_credentials'])
                    else:
                        st.warning("Please enter both username and password")


def require_page_access(page_name):
    """Decorator to require specific page access permissions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            AuthService.initialize_session()

            if not AuthService.is_authenticated():
                AuthUI.render_login_page()
                st.stop()

            if not AuthService.can_access_page(page_name):
                st.error(AuthService.get_access_denied_message(page_name))

                accessible_pages = AuthService.get_accessible_pages()
                if accessible_pages:
                    st.info(f"You have access to: {', '.join(accessible_pages)}")

                if st.button("🏠 Go to Home"):
                    st.switch_page("app.py")

                st.stop()

            return func(*args, **kwargs)

        return wrapper
    return decorator