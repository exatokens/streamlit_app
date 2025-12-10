"""
UI Renderer - Handles all UI rendering logic
"""
import streamlit as st
import pandas as pd
from config.config import COLUMN_CONFIG, TABLE_HEIGHT, COLUMN_DEFINITIONS


class UIRenderer:
    """Handles all UI rendering operations"""

    @staticmethod
    def render_loading_overlay():
        """Render CSS for loading overlay effect"""
        st.markdown("""
        <style>
        div[data-testid="stDataFrame"] {
            opacity: 0.3;
            pointer-events: none;
        }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_header():
        """Render page header with title and refresh button"""
        col_title, col_button = st.columns([6, 1])

        with col_title:
            st.title("Data Table with Refresh")

        with col_button:
            refresh_clicked = st.button("Refresh", width="stretch")

        return refresh_clicked

    @staticmethod
    def render_data_table(df):
        """
        Render the main data table with editor

        Args:
            df: DataFrame to display

        Returns:
            pd.DataFrame: Edited dataframe
        """
        # Build column config for st.data_editor
        editor_column_config = {}

        for col_name in df.columns:
            if col_name in COLUMN_DEFINITIONS:
                col_def = COLUMN_DEFINITIONS[col_name]

                if col_def["type"] == "checkbox":
                    editor_column_config[col_name] = st.column_config.CheckboxColumn(
                        col_def["display_name"],
                        default=False
                    )
                elif col_def["type"] == "selectbox" and "options" in col_def:
                    editor_column_config[col_name] = st.column_config.SelectboxColumn(
                        col_def["display_name"],
                        options=col_def["options"],
                        required=col_def.get("required", False)
                    )
                elif col_def["type"] == "number":
                    editor_column_config[col_name] = st.column_config.NumberColumn(
                        col_def["display_name"]
                    )
                else:  # text
                    editor_column_config[col_name] = st.column_config.TextColumn(
                        col_def["display_name"]
                    )

        # Determine which columns are disabled
        disabled_columns = [
            col for col, def_ in COLUMN_DEFINITIONS.items()
            if not def_.get("editable", True) and col in df.columns
        ]

        edited_data = st.data_editor(
            df,
            width="stretch",
            height=TABLE_HEIGHT,
            hide_index=True,
            num_rows="fixed",
            column_config=editor_column_config,
            disabled=disabled_columns,
            key="main_editor"
        )

        return edited_data

    @staticmethod
    def render_static_table(df):
        """
        Render a static (non-editable) dataframe

        Args:
            df: DataFrame to display
        """
        st.dataframe(
            df,
            width="stretch",
            height=TABLE_HEIGHT,
            hide_index=True
        )

    @staticmethod
    def render_action_buttons(has_changes, num_selected):
        """
        Render action buttons (Save, Cancel, Fetch Status)

        Args:
            has_changes: Boolean indicating if there are unsaved changes
            num_selected: Number of selected rows

        Returns:
            tuple: (save_clicked, cancel_clicked, fetch_clicked)
        """
        save_clicked = False
        cancel_clicked = False
        fetch_clicked = False

        # Save and Cancel buttons
        if has_changes:
            col_empty, col_save, col_cancel = st.columns([4, 1, 1])

            with col_save:
                save_clicked = st.button("Save Changes", width="stretch")

            with col_cancel:
                cancel_clicked = st.button("Cancel", width="stretch")

        # Fetch JIRA Status button
        if num_selected > 0:
            col_info, col_fetch = st.columns([6, 1])

            with col_info:
                st.info(f"Selected {num_selected} row(s)")

            with col_fetch:
                fetch_clicked = st.button(
                    "Fetch JIRA Status",
                    width="stretch"
                )

        return save_clicked, cancel_clicked, fetch_clicked

    @staticmethod
    def render_changed_rows(changed_df, changed_indices):
        """
        Render expandable sections for changed rows

        Args:
            changed_df: DataFrame containing changed rows
            changed_indices: List of indices of changed rows

        Returns:
            list: List of indices where discard was clicked
        """
        st.markdown("### Changed Rows")

        discarded_indices = []

        for idx, row in zip(changed_indices, changed_df.itertuples(index=False)):
            # Get the first visible column value for display
            first_col_value = row[0] if len(row) > 0 else 'N/A'

            with st.expander(
                    f"Row {idx} - {first_col_value}",
                    expanded=True
            ):
                col_display, col_button = st.columns([5, 1])

                with col_display:
                    row_df = pd.DataFrame([row], columns=changed_df.columns)
                    st.dataframe(row_df, width="stretch", hide_index=True)

                with col_button:
                    if st.button("Discard", key=f"discard_{idx}"):
                        discarded_indices.append(idx)

        return discarded_indices

    @staticmethod
    def show_spinner(message):
        """
        Show a spinner with message

        Args:
            message: Message to display

        Returns:
            Context manager for spinner
        """
        return st.spinner(message)

    @staticmethod
    def show_success(message):
        """Show success message"""
        st.success(message)

    @staticmethod
    def show_error(message):
        """Show error message"""
        st.error(message)

    @staticmethod
    def show_info(message):
        """Show info message"""
        st.info(message)