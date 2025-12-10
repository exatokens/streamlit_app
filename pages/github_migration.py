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
from utils.base_page import BasePage
from utils.data_manager import DataManager
from utils.ui_renderer import UIRenderer
from utils.business_logic import MigrationService, SessionManager, EventHandler
from utils.auth_service import AuthService, require_page_access

# Setup page using BasePage
BasePage.setup_page(
    page_title=PAGE_CONFIG['page_title'],
    page_icon=PAGE_CONFIG['page_icon']
)


@require_page_access("github_migration")
def main():
    """Main application entry point (protected by page-level authentication)"""

    # Initialize session state
    AuthService.initialize_session()
    SessionManager.initialize(st.session_state)

    # Load data on first run
    if st.session_state.data is None:
        with st.spinner("Fetching data..."):
            try:
                # Simulate data loading delay (for DB/large CSV loading)
                import time
                time.sleep(2)

                st.session_state.data = DataManager.load_data_from_csv()
                st.session_state.original_data = st.session_state.data.copy()
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
                st.stop()

    # Always render header first (so it's visible during all operations)
    refresh_clicked = BasePage.render_header(
        title="GitHub Migration Data",
        show_user_menu=True,
        show_refresh=True
    )

    # Handle refresh button click
    if refresh_clicked and not st.session_state.refreshing:
        EventHandler.handle_refresh(st.session_state, st)

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
    # Render the table with reduced opacity
    display_data = DataManager.add_select_column(st.session_state.data.copy())

    # Add CSS to dim the table
    st.markdown("""
    <style>
    div[data-testid="stDataFrame"] {
        opacity: 0.4;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Show the table
    UIRenderer.render_data_table(display_data)

    # Show spinner with message below the table
    with UIRenderer.show_spinner("Refreshing data..."):
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
    # Render the table with reduced opacity
    display_data = DataManager.add_select_column(st.session_state.data.copy())

    # Add CSS to dim the table
    st.markdown("""
    <style>
    div[data-testid="stDataFrame"] {
        opacity: 0.4;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Show the table
    UIRenderer.render_data_table(display_data)

    # Show spinner with message below the table
    with UIRenderer.show_spinner("Saving changes..."):
        # Validate data before saving
        is_valid, errors = MigrationService.validate_data(st.session_state.data)

        if not is_valid:
            SessionManager.set_saving(st.session_state, False)
            UIRenderer.show_error(f"Validation failed: {', '.join(errors)}")
            time.sleep(ERROR_MESSAGE_DELAY)
        else:
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
    # Render the table with reduced opacity
    display_data = DataManager.add_select_column(st.session_state.data.copy())
    for idx in st.session_state.selected_rows:
        display_data.at[idx, 'select'] = True

    # Add CSS to dim the table
    st.markdown("""
    <style>
    div[data-testid="stDataFrame"] {
        opacity: 0.4;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Show the table
    UIRenderer.render_data_table(display_data)

    # Get list of JIRA ticket IDs for selected rows
    jira_tickets = [
        st.session_state.data.at[idx, 'jira_ticket']
        for idx in st.session_state.selected_rows
    ]
    jira_tickets_str = ", ".join(jira_tickets)

    # Show spinner with message below the table
    with UIRenderer.show_spinner(
        f"Fetching JIRA status for: {jira_tickets_str}"
    ):
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

            UIRenderer.show_success(f"Updated JIRA status for: {jira_tickets_str}")
        else:
            UIRenderer.show_error(f"Error fetching JIRA status: {error}")

    SessionManager.set_fetching_status(st.session_state, False)
    st.session_state.selected_rows = []
    time.sleep(SUCCESS_MESSAGE_DELAY)
    st.rerun()


def render_main_view():
    """Render the main application view (header already rendered in main())"""
    # Get current data (no filters applied)
    display_data = DataManager.add_select_column(st.session_state.data.copy())

    # Render data table
    edited_data = UIRenderer.render_data_table(display_data)

    # Update selected rows
    st.session_state.selected_rows = DataManager.get_selected_rows(edited_data)

    # Update data with edits (exclude select column)
    edited_clean = edited_data.drop(columns=['select'], errors='ignore')

    # Track if we made any actual changes
    has_updates = False
    for idx in edited_clean.index:
        for col in edited_clean.columns:
            if col in st.session_state.data.columns:
                old_value = st.session_state.data.at[idx, col]
                new_value = edited_clean.at[idx, col]
                if old_value != new_value:
                    st.session_state.data.at[idx, col] = new_value
                    has_updates = True

    # Get changed rows
    changed_rows, changed_indices = MigrationService.detect_changes(
        st.session_state.original_data,
        st.session_state.data
    )

    # If we made updates, rerun to show changes immediately
    if has_updates:
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

    # Render footer
    st.markdown("---")
    st.caption("GitHub Migration Data Manager")


def render_admin_section():
    """Render admin-only section"""
    with st.expander("🔑 Admin Section", expanded=False):
        st.info("You are admin. Only you can see this text.")


# Call main function (Streamlit pages run directly)
main()