"""
Data Manager - Handles all data loading, saving, and manipulation
"""
import pandas as pd
from config.config import CSV_PATH


class DataManager:
    """Manages data operations for the application"""

    @staticmethod
    def load_data_from_csv():
        """
        Load data from CSV file - only load columns defined in COLUMN_DEFINITIONS

        Returns:
            pd.DataFrame: Loaded dataframe with only configured columns
        """
        try:
            # Get list of columns we want to load from config
            from config.config import COLUMN_DEFINITIONS, get_configured_columns
            configured_columns = get_configured_columns()

            # Read CSV - only load configured columns that exist in the CSV
            df = pd.read_csv(CSV_PATH)

            # Filter to only keep columns that are in our configuration
            available_columns = [col for col in configured_columns if col in df.columns]
            df = df[available_columns]

            # Replace 'None' string with empty string for all columns
            df = df.replace('None', '')

            # Get all text columns from config (not number, selectbox, or checkbox)
            text_columns = [
                col for col, col_def in COLUMN_DEFINITIONS.items()
                if col_def.get('type') == 'text' and col in df.columns
            ]

            # Fill NaN values with empty strings for all text columns
            for col in text_columns:
                df[col] = df[col].fillna('')

            # Drop rows where all values are NaN
            df = df.dropna(how='all')

            # Drop rows where all values are empty strings or whitespace
            df = df[~df.apply(lambda row: row.astype(str).str.strip().eq('').all(), axis=1)]

            # Reset index after dropping rows
            df = df.reset_index(drop=True)

            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found at: {CSV_PATH}")
        except Exception as e:
            raise Exception(f"Error loading CSV: {str(e)}")

    @staticmethod
    def save_data_to_csv(df, include_select=False):
        """
        Save dataframe to CSV file

        Args:
            df: DataFrame to save
            include_select: Whether to include the 'select' column

        Returns:
            bool: Success status
        """
        try:
            # Remove select column if it exists and not requested
            if not include_select and 'select' in df.columns:
                df = df.drop(columns=['select'])

            # Drop rows where all values are NaN
            df = df.dropna(how='all')

            # Drop rows where all values are empty strings or whitespace
            df = df[~df.apply(lambda row: row.astype(str).str.strip().eq('').all(), axis=1)]

            # Reset index before saving
            df = df.reset_index(drop=True)

            df.to_csv(CSV_PATH, index=False)
            return True
        except Exception as e:
            raise Exception(f"Error saving CSV: {str(e)}")

    @staticmethod
    def get_changed_rows(original_df, edited_df):
        """
        Compare two dataframes and return changed rows

        Args:
            original_df: Original dataframe
            edited_df: Edited dataframe

        Returns:
            tuple: (changed_dataframe, list of changed indices)
        """
        if original_df is None or edited_df is None:
            return pd.DataFrame(), []

        # Remove select column for comparison
        edited_clean = edited_df.drop(columns=['select'], errors='ignore')

        changed_indices = []
        for idx in range(min(len(original_df), len(edited_clean))):
            if not original_df.iloc[idx].equals(edited_clean.iloc[idx]):
                changed_indices.append(idx)

        if changed_indices:
            return edited_clean.iloc[changed_indices].copy(), changed_indices

        return pd.DataFrame(), []

    @staticmethod
    def reset_row(df, original_df, idx):
        """
        Reset a specific row to its original values

        Args:
            df: Current dataframe
            original_df: Original dataframe
            idx: Index of row to reset

        Returns:
            pd.DataFrame: Updated dataframe
        """
        for col in original_df.columns:
            df.at[idx, col] = original_df.at[idx, col]
        return df

    @staticmethod
    def update_jira_status(df, row_indices, status_map):
        """
        Update JIRA status for specific rows

        Args:
            df: DataFrame to update
            row_indices: List of row indices to update
            status_map: Dictionary mapping row index to new status

        Returns:
            pd.DataFrame: Updated dataframe
        """
        for idx in row_indices:
            if idx in status_map:
                df.at[idx, 'jira_status'] = status_map[idx]
        return df

    @staticmethod
    def add_select_column(df):
        """
        Add select column if it doesn't exist

        Args:
            df: DataFrame

        Returns:
            pd.DataFrame: DataFrame with select column
        """
        if 'select' not in df.columns:
            df['select'] = False
        return df

    @staticmethod
    def get_selected_rows(df):
        """
        Get indices of selected rows

        Args:
            df: DataFrame with select column

        Returns:
            list: List of selected row indices
        """
        if 'select' in df.columns:
            return df[df['select'] == True].index.tolist()
        return []