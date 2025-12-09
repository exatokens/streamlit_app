"""
Base Page Class
Contains common functionality for all pages
"""
import streamlit as st
from utils.auth_service import AuthService


class BasePage:
    """Base class for all pages with common functionality"""

    # Common page configuration
    PAGE_CONFIG = {
        'layout': 'wide',
        'initial_sidebar_state': 'expanded'
    }

    @staticmethod
    def setup_page(page_title, page_icon="🏠"):
        """
        Setup common page configuration

        Args:
            page_title: Title for the page
            page_icon: Icon for the page
        """
        st.set_page_config(
            page_title=page_title,
            page_icon=page_icon,
            layout=BasePage.PAGE_CONFIG['layout'],
            initial_sidebar_state=BasePage.PAGE_CONFIG['initial_sidebar_state']
        )

        # Hide deploy button
        BasePage._hide_deploy_button()

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
                refresh_clicked = st.button("🔄 Refresh", use_container_width=True)

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
                if st.button("🚪 Logout", use_container_width=True, key="logout_menu"):
                    AuthService.logout()
                    st.rerun()
        else:
            # Show login button
            if st.button("🔐 Login", use_container_width=True, key="show_login"):
                st.session_state.show_login_form = True

    @staticmethod
    def render_footer(text="Foot notes"):
        """
        Render common footer

        Args:
            text: Footer text to display
        """
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>{text}</p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_login_form():
        """Render login form"""
        if not AuthService.is_authenticated() and st.session_state.get('show_login_form', False):
            col_left, col_center, col_right = st.columns([1, 2, 1])

            with col_center:
                st.subheader("🔐 Login")

                with st.form("login_form"):
                    username = st.text_input("Username", key="login_username")
                    password = st.text_input("Password", type="password", key="login_password")

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