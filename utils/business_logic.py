"""
Business Logic Module
Handles all business logic operations for GitHub migration
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
        Refresh data from CSV

        Returns:
            tuple: (success, data, error_message)
        """
        try:
            time.sleep(REFRESH_DELAY)
            data = DataManager.load_data_from_csv()
            return True, data, None
        except Exception as e:
            return False, None, str(e)

    @staticmethod
    def save_changes(data):
        """
        Save changes to CSV

        Args:
            data: DataFrame to save

        Returns:
            tuple: (success, error_message)
        """
        try:
            time.sleep(SAVE_DELAY)
            DataManager.save_data_to_csv(data, include_select=False)
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
            status_map = {}

            for idx in selected_indices:
                jira_id = data.at[idx, 'jira_id']
                new_status = fetch_jira_status(jira_id)
                status_map[idx] = new_status

            # Update data
            updated_data = DataManager.update_jira_status(
                data.copy(),
                selected_indices,
                status_map
            )

            # Save updated data
            DataManager.save_data_to_csv(updated_data, include_select=False)

            return True, updated_data, None
        except Exception as e:
            return False, data, str(e)

    @staticmethod
    def apply_filters(data, filters):
        """
        Apply filters to data

        Args:
            data: DataFrame to filter
            filters: Dictionary of filters

        Returns:
            DataFrame: Filtered data
        """
        return DataManager.apply_filters(data, filters)

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

        # Check required columns
        required_columns = ['jira_id', 'project_name', 'repo_name']
        for col in required_columns:
            if col not in data.columns:
                errors.append(f"Missing required column: {col}")

        # Check for empty required fields
        if 'jira_id' in data.columns:
            empty_jira = data['jira_id'].isna().sum()
            if empty_jira > 0:
                errors.append(f"{empty_jira} rows have empty JIRA ID")

        # Check for duplicate JIRA IDs
        if 'jira_id' in data.columns:
            duplicates = data['jira_id'].duplicated().sum()
            if duplicates > 0:
                errors.append(f"{duplicates} duplicate JIRA IDs found")

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
            st_session_state.filters = {}

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
        st_session_state.filters = {}


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

    @staticmethod
    def handle_filter_change(st_session_state, st, filters):
        """Handle filter change"""
        st_session_state.filters = filters
        st.rerun()