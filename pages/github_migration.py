"""
GitHub Migration - Main Page
Streamlit application for managing GitHub migration data with authentication
"""
import streamlit as st
import time
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path to import modules
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from config.config import (
    PAGE_CONFIG,
    SUCCESS_MESSAGE_DELAY,
    ERROR_MESSAGE_DELAY,
    COLUMN_DEFINITIONS,
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
                st.session_state.data = DataManager.load_data_from_db()
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

    # Render column filters in sidebar (widgets must be outside fragments)
    _render_filters_sidebar()

    # Process different states
    if st.session_state.refreshing:
        process_refresh()
    elif st.session_state.saving:
        process_save()
    elif st.session_state.fetching_status:
        process_fetch_status()
    else:
        render_main_view()


def _values_different(old_value, new_value):
    if pd.isna(old_value) and pd.isna(new_value):
        return False
    if pd.isna(old_value) and not pd.isna(new_value):
        return True
    if not pd.isna(old_value) and pd.isna(new_value):
        return True
    return old_value != new_value


def _init_column_filters():
    """Ensure column filters dict exists in session state."""
    if "column_filters" not in st.session_state:
        st.session_state.column_filters = {}


def _render_filters_sidebar():
    """
    Render filters in the sidebar.
    One text input per column (except id and select/fetch update).
    """
    _init_column_filters()

    with st.sidebar.expander("🔍 Filters", expanded=False):
        st.caption("Type to filter rows. Matching is case-insensitive and substring-based.")

        # Build list of columns to filter: all except id and select/fetch-update
        for col in st.session_state.data.columns:
            if col in ("id", "select"):
                continue

            col_def = COLUMN_DEFINITIONS.get(col, {})
            label = col_def.get("display_name", col.replace("_", " ").title())

            key = f"filter_{col}"
            current_value = st.session_state.column_filters.get(col, "")

            value = st.text_input(label, value=current_value, key=key)
            # Persist trimmed value back to filters dict
            st.session_state.column_filters[col] = value.strip()


def _apply_column_filters(df):
    """Return a filtered copy of df based on current column_filters."""
    _init_column_filters()
    filtered = df

    for col, term in st.session_state.column_filters.items():
        if not term:
            continue
        if col not in filtered.columns:
            continue
        # Case-insensitive substring match on stringified values
        filtered = filtered[
            filtered[col]
            .astype(str)
            .str.contains(term, case=False, na=False)
        ]

    return filtered

@st.fragment
def process_refresh():
    """Process data refresh operation"""
    # Render the (filtered) table with reduced opacity
    base_data = _apply_column_filters(st.session_state.data.copy())
    display_data = DataManager.add_select_column(base_data)

    # Add CSS to dim the table
    st.markdown("""
    <style>
    div[data-testid="stDataFrame"] {
        opacity: 0.4;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Show the table (same table position, just visually dimmed)
    UIRenderer.render_data_table(display_data)

    # Show spinner with message
    with UIRenderer.show_spinner("Refreshing data..."):
        # Refresh data
        success, data, error = MigrationService.refresh_data()

        if success:
            fresh = data.copy()
            SessionManager.update_data(st.session_state, fresh.copy())
            SessionManager.update_original_data(st.session_state, fresh.copy())
            st.session_state.selected_rows = []
        else:
            UIRenderer.show_error(f"Error refreshing data: {error}")
            time.sleep(ERROR_MESSAGE_DELAY)

    SessionManager.reset_operation_flags(st.session_state)
    st.session_state.selected_rows = []
    st.rerun()


@st.fragment
def process_save():
    """Process save operation"""
    # Render the (filtered) table with reduced opacity
    base_data = _apply_column_filters(st.session_state.data.copy())
    display_data = DataManager.add_select_column(base_data)

    st.markdown("""
    <style>
    div[data-testid="stDataFrame"] {
        opacity: 0.4;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Show the table (same table position, just visually dimmed)
    UIRenderer.render_data_table(display_data)

    with UIRenderer.show_spinner("Saving changes..."):
        # detect changed rows first
        changed_rows, changed_indices = MigrationService.detect_changes(
            st.session_state.original_data,
            st.session_state.data
        )

        if not changed_indices:
            SessionManager.set_saving(st.session_state, False)
            UIRenderer.show_info("No changes to save.")
            time.sleep(SUCCESS_MESSAGE_DELAY)
            st.rerun()
            return

        # Try to save
        success, error_msg = MigrationService.save_changes(
            st.session_state.data,
            changed_indices
        )

        if success:
            # Update original data to match current
            st.session_state.original_data = st.session_state.data.copy()
            UIRenderer.show_success("✓ Changes saved successfully")
        else:
            UIRenderer.show_error(f"Error saving changes: {error_msg}")

    SessionManager.set_saving(st.session_state, False)
    time.sleep(SUCCESS_MESSAGE_DELAY)
    st.rerun()


@st.fragment
def process_fetch_status():
    """Process JIRA status fetch operation"""
    # Render the (filtered) table with reduced opacity
    base_data = _apply_column_filters(st.session_state.data.copy())
    display_data = DataManager.add_select_column(base_data)

    st.markdown("""
    <style>
    div[data-testid="stDataFrame"] {
        opacity: 0.4;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Show the table (same table position, just visually dimmed)
    UIRenderer.render_data_table(display_data)

    with UIRenderer.show_spinner("Fetching JIRA status..."):
        selected_rows = st.session_state.selected_rows

        if not selected_rows:
            UIRenderer.show_warning("No rows selected")
            SessionManager.set_fetching_status(st.session_state, False)
            time.sleep(ERROR_MESSAGE_DELAY)
            st.rerun()
            return

        # Fetch JIRA status
        success, actual_data, error, jira_tickets_str = MigrationService.fetch_jira_status_for_rows(
            st.session_state.data,
            selected_rows
        )

        if success:
            SessionManager.update_original_data(st.session_state, actual_data.copy())
            SessionManager.update_data(st.session_state, actual_data.copy())

            UIRenderer.show_success(f"Updated JIRA status for: {jira_tickets_str}")
        else:
            UIRenderer.show_error(f"Error fetching JIRA status: {error}")

    SessionManager.set_fetching_status(st.session_state, False)
    st.session_state.selected_rows = []
    time.sleep(SUCCESS_MESSAGE_DELAY)
    st.rerun()


@st.fragment
def render_changed_rows_fragment(changed_rows, changed_indices):
    """Render changed rows with discard actions"""
    if changed_rows.empty:
        return

    discarded_indices = UIRenderer.render_changed_rows(
        changed_rows,
        changed_indices
    )

    for idx in discarded_indices:
        EventHandler.handle_discard_row(st.session_state, st, idx)


@st.fragment
def render_admin_fragment():
    """Render admin-only section"""
    if AuthService.is_admin():
        render_admin_section()


def render_main_view():
    """Render the main application view (header already rendered in main())"""
    # Get current data and apply filters
    base_data = _apply_column_filters(st.session_state.data.copy())
    display_data = DataManager.add_select_column(base_data)
    total_count = len(st.session_state.data) if st.session_state.data is not None else 0
    filtered_count = len(base_data)

    # Render data table
    edited_data = UIRenderer.render_data_table(display_data)

    # Show record counts below the table
    st.caption(f"Showing {filtered_count} of {total_count} record(s)")

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
                if _values_different(old_value, new_value):
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

    # Render changed rows section (fragment)
    render_changed_rows_fragment(changed_rows, changed_indices)

    # Show statistics (for admin users) via fragment
    render_admin_fragment()

    # Render footer
    st.markdown("---")
    st.caption("GitHub Migration Data Manager")


def render_admin_section():
    """Render admin-only section"""
    with st.expander("🔑 Admin Section", expanded=False):
        st.info("You are admin. Only you can see this text.")


# Call main function (Streamlit pages run directly)
main()