"""
UI Renderer - Handles all UI rendering logic
"""
import streamlit as st
import pandas as pd
from config.config import COLUMN_CONFIG, TABLE_HEIGHT


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
            refresh_clicked = st.button("Refresh", use_container_width=True)

        return refresh_clicked

    @staticmethod
    def render_filter_row(columns, current_filters):
        """
        Render filter inputs for each column

        Args:
            columns: List of column names
            current_filters: Dictionary of current filter values

        Returns:
            dict: Updated filters dictionary
        """
        filter_cols = st.columns(len(columns) + 1)  # +1 for Select column
        updated_filters = {}

        for i, col in enumerate(columns):
            with filter_cols[i]:
                filter_value = st.text_input(
                    f"filter_{col}",
                    value=current_filters.get(col, ""),
                    placeholder=f"{col}",
                    key=f"filter_{col}",
                    label_visibility="collapsed"
                )
                updated_filters[col] = filter_value

        # Placeholder for Select column filter
        with filter_cols[len(columns)]:
            st.text_input(
                "filter_select",
                value="",
                placeholder="Select",
                disabled=True,
                label_visibility="collapsed"
            )

        return updated_filters

    @staticmethod
    def render_data_table(df):
        """
        Render the main data table with editor

        Args:
            df: DataFrame to display

        Returns:
            pd.DataFrame: Edited dataframe
        """
        edited_data = st.data_editor(
            df,
            use_container_width=True,
            height=TABLE_HEIGHT,
            hide_index=True,
            num_rows="fixed",
            column_config={
                "select": st.column_config.CheckboxColumn(
                    COLUMN_CONFIG["select"]["label"],
                    default=COLUMN_CONFIG["select"]["default"]
                )
            },
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
            use_container_width=True,
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
                save_clicked = st.button("Save Changes", use_container_width=True)

            with col_cancel:
                cancel_clicked = st.button("Cancel", use_container_width=True)

        # Fetch JIRA Status button
        if num_selected > 0:
            col_info, col_fetch = st.columns([6, 1])

            with col_info:
                st.info(f"Selected {num_selected} row(s)")

            with col_fetch:
                fetch_clicked = st.button(
                    "Fetch JIRA Status",
                    use_container_width=True
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
            with st.expander(
                    f"Row {idx} - {row[0] if len(row) > 0 else 'N/A'}",
                    expanded=True
            ):
                col_display, col_button = st.columns([5, 1])

                with col_display:
                    row_df = pd.DataFrame([row], columns=changed_df.columns)
                    st.dataframe(row_df, use_container_width=True, hide_index=True)

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