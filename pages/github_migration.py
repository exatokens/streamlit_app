"""
GitHub Migration - Main Page
Streamlit application for managing GitHub migration data with authentication
"""
import streamlit as st
import time
import sys
from pathlib import Path

# Add parent directory to path to import modules
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from config.config import (
    PAGE_CONFIG,
    SUCCESS_MESSAGE_DELAY,
    ERROR_MESSAGE_DELAY
)
from config.auth_config import AUTH_ENABLED
from utils.data_manager import DataManager
from utils.ui_renderer import UIRenderer
from utils.business_logic import MigrationService, SessionManager, EventHandler
from utils.auth_service import AuthService, AuthUI, require_authentication, require_page_access

# Page configuration
st.set_page_config(**PAGE_CONFIG)

# Hide deploy button only
st.markdown("""
<style>
    /* Hide deploy button */
    [data-testid="stToolbar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


@require_page_access("github_migration")
def main():
    """Main application entry point (protected by page-level authentication)"""

    # Initialize session state
    AuthService.initialize_session()
    SessionManager.initialize(st.session_state)

    # Load data on first run
    if st.session_state.data is None:
        try:
            st.session_state.data = DataManager.load_data_from_csv()
            st.session_state.original_data = st.session_state.data.copy()
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.stop()

    # Process different states
    if st.session_state.refreshing:
        process_refresh()
    elif st.session_state.saving:
        process_save()
    elif st.session_state.fetching_status:
        process_fetch_status()
    else:
        render_main_view()


def process_refresh():
    """Process data refresh operation"""
    UIRenderer.render_loading_overlay()

    with UIRenderer.show_spinner("Refreshing data..."):
        UIRenderer.render_static_table(st.session_state.data)

        # Refresh data
        success, data, error = MigrationService.refresh_data()

        if success:
            SessionManager.update_data(st.session_state, data)
            SessionManager.update_original_data(st.session_state, data)
        else:
            UIRenderer.show_error(f"Error refreshing data: {error}")
            time.sleep(ERROR_MESSAGE_DELAY)

    SessionManager.reset_operation_flags(st.session_state)
    st.session_state.selected_rows = []
    st.rerun()


def process_save():
    """Process save operation"""
    UIRenderer.render_loading_overlay()

    # Display data during save
    display_data = DataManager.add_select_column(st.session_state.data.copy())

    with UIRenderer.show_spinner("Saving changes..."):
        UIRenderer.render_static_table(display_data)

        # Validate data before saving
        is_valid, errors = MigrationService.validate_data(st.session_state.data)

        if not is_valid:
            SessionManager.set_saving(st.session_state, False)
            UIRenderer.show_error(f"Validation failed: {', '.join(errors)}")
            time.sleep(ERROR_MESSAGE_DELAY)
            st.rerun()
            return

        # Save data
        success, error = MigrationService.save_changes(st.session_state.data)

        if success:
            # Update session state
            actual_data = st.session_state.data.drop(columns=['select'], errors='ignore')
            SessionManager.update_original_data(st.session_state, actual_data.copy())
            SessionManager.update_data(st.session_state, actual_data.copy())
            SessionManager.set_saving(st.session_state, False)

            UIRenderer.show_success("Data saved successfully!")
            time.sleep(SUCCESS_MESSAGE_DELAY)
        else:
            SessionManager.set_saving(st.session_state, False)
            UIRenderer.show_error(f"Error saving data: {error}")
            time.sleep(ERROR_MESSAGE_DELAY)

    st.rerun()


def process_fetch_status():
    """Process JIRA status fetch operation"""
    UIRenderer.render_loading_overlay()

    # Display data with selections during fetch
    display_data = DataManager.add_select_column(st.session_state.data.copy())
    for idx in st.session_state.selected_rows:
        display_data.at[idx, 'select'] = True

    with UIRenderer.show_spinner(
        f"Fetching JIRA status for {len(st.session_state.selected_rows)} rows..."
    ):
        UIRenderer.render_static_table(display_data)

        # Fetch JIRA statuses
        success, updated_data, error = MigrationService.fetch_jira_statuses(
            st.session_state.data,
            st.session_state.selected_rows
        )

        if success:
            # Update session state
            actual_data = updated_data.drop(columns=['select'], errors='ignore')
            SessionManager.update_original_data(st.session_state, actual_data.copy())
            SessionManager.update_data(st.session_state, actual_data.copy())

            UIRenderer.show_success("Updated JIRA status for selected rows!")
        else:
            UIRenderer.show_error(f"Error fetching JIRA status: {error}")

    SessionManager.set_fetching_status(st.session_state, False)
    st.session_state.selected_rows = []
    time.sleep(SUCCESS_MESSAGE_DELAY)
    st.rerun()


def render_main_view():
    """Render the main application view"""
    # Render header with kebab menu containing username and settings
    col_title, col_menu, col_refresh = st.columns([8, 1, 1])

    with col_title:
        st.markdown("### GitHub Migration Data")

    with col_menu:
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
            if st.button("🚪 Logout", use_container_width=True, key="logout_main"):
                AuthService.logout()
                st.rerun()

    with col_refresh:
        if st.button("🔄 Refresh", use_container_width=True):
            EventHandler.handle_refresh(st.session_state, st)

    # Render filter row
    data_columns = list(st.session_state.data.columns)
    updated_filters = UIRenderer.render_filter_row(
        data_columns,
        st.session_state.filters
    )

    # Check if filters changed
    filters_changed = updated_filters != st.session_state.filters
    if filters_changed:
        EventHandler.handle_filter_change(st.session_state, st, updated_filters)

    # Apply filters
    filtered_data = MigrationService.apply_filters(
        st.session_state.data,
        st.session_state.filters
    )

    # Add select column
    display_data = DataManager.add_select_column(filtered_data.copy())

    # Render data table
    edited_data = UIRenderer.render_data_table(display_data)

    # Check if data was actually edited (cell changed)
    # Compare edited_data with display_data to detect changes
    edited_clean = edited_data.drop(columns=['select'], errors='ignore')
    display_clean = display_data.drop(columns=['select'], errors='ignore')

    # If data changed, trigger rerun to update the UI
    data_was_edited = False
    try:
        if not edited_clean.equals(display_clean):
            data_was_edited = True
    except:
        # If comparison fails, assume data was edited
        data_was_edited = True

    # Update selected rows
    st.session_state.selected_rows = DataManager.get_selected_rows(edited_data)

    # Update data with edits (exclude select column)
    for idx in edited_clean.index:
        for col in edited_clean.columns:
            if col in st.session_state.data.columns:
                st.session_state.data.at[idx, col] = edited_clean.at[idx, col]

    # Get changed rows
    changed_rows, changed_indices = MigrationService.detect_changes(
        st.session_state.original_data,
        st.session_state.data
    )

    # If data was edited, rerun to show changes immediately
    if data_was_edited:
        st.rerun()

    # Render action buttons
    save_clicked, cancel_clicked, fetch_clicked = UIRenderer.render_action_buttons(
        has_changes=not changed_rows.empty,
        num_selected=len(st.session_state.selected_rows)
    )

    # Handle button clicks
    if save_clicked:
        EventHandler.handle_save(st.session_state, st)
    if cancel_clicked:
        EventHandler.handle_cancel(st.session_state, st)
    if fetch_clicked:
        EventHandler.handle_fetch_status(st.session_state, st)

    # Render changed rows section
    if not changed_rows.empty:
        discarded_indices = UIRenderer.render_changed_rows(
            changed_rows,
            changed_indices
        )

        # Handle discard clicks
        for idx in discarded_indices:
            EventHandler.handle_discard_row(st.session_state, st, idx)

    # Show statistics (for admin users)
    if AuthService.is_admin():
        render_admin_section()


def render_admin_section():
    """Render admin-only section"""
    with st.expander("🔑 Admin Section", expanded=False):
        st.info("You are admin. Only you can see this text.")


# Call main function (Streamlit pages run directly)
main()