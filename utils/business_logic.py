"""
Business Logic Module
Handles all business logic operations for GitHub migration with Database
"""
import time
from utils.data_manager import DataManager
from utils.api_service import fetch_jira_status
from config.config import SAVE_DELAY, REFRESH_DELAY


class MigrationService:
    """Business logic for migration operations"""

    @staticmethod
    def refresh_data():
        """
        Refresh data from database
        
        Returns:
            tuple: (success, data, error_message)
        """
        try:
            time.sleep(REFRESH_DELAY)
            data = DataManager.load_data_from_db()
            return True, data, None
        except Exception as e:
            return False, None, str(e)

    @staticmethod
    def save_changes(data, changed_indices):
        """
        Save changes to database
        
        Args:
            data: DataFrame to save
            changed_indices: List of indices that have changed
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            time.sleep(SAVE_DELAY)
            success_count, errors = DataManager.save_data_to_db(data, changed_indices)
            
            if errors:
                error_msg = f"Saved {success_count} rows. Errors: " + "; ".join(errors)
                return False, error_msg
            
            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def fetch_jira_statuses(data, selected_indices):
        """
        Fetch JIRA statuses for selected rows

        Args:
            data: DataFrame containing the data
            selected_indices: List of row indices to update

        Returns:
            tuple: (success, updated_data, error_message)
        """
        try:
            # Filter out rows without valid JIRA tickets upfront
            status_map = {}

            for idx in selected_indices:
                jira_ticket = data.at[idx, 'jira_ticket']
                if jira_ticket and str(jira_ticket).strip() not in ('', 'None', 'nan'):
                    new_status = fetch_jira_status(jira_ticket)
                    status_map[idx] = new_status

            if not status_map:
                return True, data, None

            # Update data - avoid unnecessary copy if no changes
            updated_data = DataManager.update_jira_status(
                data.copy(),
                list(status_map.keys()),
                status_map
            )

            # Note: JIRA status updates would need to be saved separately
            # since jira_status is not in EDITABLE_DB_COLUMNS

            return True, updated_data, None
        except Exception as e:
            return False, data, str(e)

    @staticmethod
    def detect_changes(original_data, current_data):
        """
        Detect changes between original and current data
        
        Args:
            original_data: Original DataFrame
            current_data: Current DataFrame
            
        Returns:
            tuple: (changed_dataframe, list of changed indices)
        """
        return DataManager.get_changed_rows(original_data, current_data)

    @staticmethod
    def discard_row_changes(current_data, original_data, idx):
        """
        Discard changes for a specific row
        
        Args:
            current_data: Current DataFrame
            original_data: Original DataFrame
            idx: Row index to discard
            
        Returns:
            DataFrame: Updated data with row restored
        """
        return DataManager.reset_row(current_data, original_data, idx)

    @staticmethod
    def validate_data(data):
        """
        Validate data before saving
        
        Args:
            data: DataFrame to validate
            
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # Add validation rules if needed
        # For example, check date ranges, required fields for editable columns, etc.
        
        return len(errors) == 0, errors


class SessionManager:
    """Manages session state for the application"""

    @staticmethod
    def initialize(st_session_state):
        """
        Initialize session state
        
        Args:
            st_session_state: Streamlit session state object
        """
        if 'data' not in st_session_state:
            st_session_state.data = None
            st_session_state.original_data = None
            st_session_state.refreshing = False
            st_session_state.fetching_status = False
            st_session_state.selected_rows = []
            st_session_state.saving = False

    @staticmethod
    def reset_operation_flags(st_session_state):
        """Reset all operation flags"""
        st_session_state.refreshing = False
        st_session_state.fetching_status = False
        st_session_state.saving = False

    @staticmethod
    def set_refreshing(st_session_state, value=True):
        """Set refreshing flag"""
        st_session_state.refreshing = value

    @staticmethod
    def set_saving(st_session_state, value=True):
        """Set saving flag"""
        st_session_state.saving = value

    @staticmethod
    def set_fetching_status(st_session_state, value=True):
        """Set fetching status flag"""
        st_session_state.fetching_status = value

    @staticmethod
    def update_data(st_session_state, data):
        """Update data in session"""
        st_session_state.data = data

    @staticmethod
    def update_original_data(st_session_state, data):
        """Update original data in session"""
        st_session_state.original_data = data

    @staticmethod
    def reset_to_original(st_session_state):
        """Reset data to original"""
        st_session_state.data = st_session_state.original_data.copy()
        st_session_state.selected_rows = []


class EventHandler:
    """Handles user events and actions"""

    @staticmethod
    def handle_refresh(st_session_state, st):
        """Handle refresh button click"""
        SessionManager.set_refreshing(st_session_state)
        st.rerun()

    @staticmethod
    def handle_save(st_session_state, st):
        """Handle save button click"""
        SessionManager.set_saving(st_session_state)
        st.rerun()

    @staticmethod
    def handle_cancel(st_session_state, st):
        """Handle cancel button click"""
        SessionManager.reset_to_original(st_session_state)
        st.rerun()

    @staticmethod
    def handle_fetch_status(st_session_state, st):
        """Handle fetch JIRA status button click"""
        SessionManager.set_fetching_status(st_session_state)
        st.rerun()

    @staticmethod
    def handle_discard_row(st_session_state, st, idx):
        """Handle discard row button click"""
        st_session_state.data = MigrationService.discard_row_changes(
            st_session_state.data,
            st_session_state.original_data,
            idx
        )
        st.rerun()