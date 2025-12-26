"""
Base Page Class
Contains common functionality for all pages
"""
import streamlit as st
from typing import Literal
from pathlib import Path
import base64
from utils.auth_service import AuthService


class BasePage:
    """Base class for all pages with common functionality"""

    # Common page configuration
    PAGE_CONFIG = {
        'layout': 'wide',
        'initial_sidebar_state': 'expanded'
    }

    @staticmethod
    def _get_logo_base64():
        import os
        """Get base64 encoded logo for CSS injection"""
        logo_path = '/Users/siva/web_developments/streamlit_app/ms_logo.png'
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                data = f.read()
                return base64.b64encode(data).decode()
        return None

    @staticmethod
    def _inject_sidebar_logo():
        """Inject logo at the top of sidebar using CSS"""
        logo_base64 = BasePage._get_logo_base64()

        if logo_base64:
            st.markdown(f"""
                <style>
                    /* Add logo at the very top of sidebar */
                    [data-testid="stSidebar"] {{
                        background-image: url("data:image/png;base64,{logo_base64}");
                        background-repeat: no-repeat;
                        background-position: center 20px;
                        background-size: 180px auto;
                        padding-top: 100px !important;
                    }}
                    
                    /* Adjust sidebar content to accommodate logo */
                    [data-testid="stSidebar"] > div:first-child {{
                        padding-top: 20px;
                    }}
                    
                    /* Ensure navigation starts below logo */
                    section[data-testid="stSidebar"] > div {{
                        padding-top: 0px;
                    }}
                </style>
            """, unsafe_allow_html=True)

    @staticmethod
    def setup_page(page_title: str, page_icon: str = "🏠"):
        """
        Setup common page configuration

        Args:
            page_title: Title for the page
            page_icon: Icon for the page
        """
        st.set_page_config(
            page_title=page_title,
            page_icon=page_icon,
            layout=BasePage.PAGE_CONFIG['layout'],  # type: ignore
            initial_sidebar_state=BasePage.PAGE_CONFIG['initial_sidebar_state']  # type: ignore
        )

        # Hide deploy button
        BasePage._hide_deploy_button()

        # Inject sidebar logo
        BasePage._inject_sidebar_logo()

        # Initialize authentication session
        AuthService.initialize_session()

    @staticmethod
    def _hide_deploy_button():
        """Hide Streamlit deploy button"""
        st.markdown("""
        <style>
            /* Hide deploy button */
            [data-testid="stToolbar"] {
                display: none;
            }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_header(title, show_user_menu=True, show_refresh=False):
        """
        Render common header with title and optional user menu

        Args:
            title: Page title to display
            show_user_menu: Whether to show user menu (default: True)
            show_refresh: Whether to show refresh button (default: False)

        Returns:
            bool: True if refresh button clicked (if shown)
        """
        if show_refresh:
            col_title, col_menu, col_refresh = st.columns([8, 1, 1])
        else:
            col_title, col_menu = st.columns([10, 1])

        with col_title:
            if title.startswith("🏠"):
                st.title(title)
            else:
                st.markdown(f"### {title}")

        refresh_clicked = False

        if show_user_menu:
            with col_menu:
                BasePage._render_user_menu()

        if show_refresh:
            with col_refresh:
                refresh_clicked = st.button("🔄 Refresh", width="stretch")

        return refresh_clicked

    @staticmethod
    def _render_user_menu():
        """Render user menu dropdown"""
        if AuthService.is_authenticated():
            session_info = AuthService.get_session_info()
            username = AuthService.get_username()

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
                if st.button("🚪 Logout", width="stretch", key="logout_menu"):
                    AuthService.logout()
                    st.rerun()
        else:
            # Show login button
            if st.button("🔐 Login", width="stretch", key="show_login"):
                st.session_state.show_login_form = True

    @staticmethod
    def render_footer(text="Foot notes"):
        """
        Render common footer

        Args:
            text: Footer text to display
        """
        st.markdown("---")
        st.caption(text)

    @staticmethod
    def render_login_form():
        """Render login form if user is not authenticated"""
        if not AuthService.is_authenticated():
            with st.container():
                st.info("🔐 Please login to access all features")

                col1, col2, col3 = st.columns([1, 2, 1])

                with col2:
                    with st.form("login_form"):
                        st.markdown("### Login")
                        username = st.text_input("Username")
                        password = st.text_input("Password", type="password")
                        submit = st.form_submit_button("Login", use_container_width=True)

                        if submit:
                            if AuthService.login(username, password):
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Invalid credentials")