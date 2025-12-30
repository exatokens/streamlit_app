"""
Data Manager - Handles all data loading, saving, and manipulation with Database
"""
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from utils.dataobject import DataObject
from config.config import DB_CONFIG, COLUMN_DEFINITIONS, EDITABLE_DB_COLUMNS


class DataManager:
    """Manages data operations for the application"""

    @staticmethod
    def _convert_db_to_pandas(value, column_type):
        """
        Convert database value to pandas-friendly value

        Args:
            value: Value from database
            column_type: Column type from COLUMN_DEFINITIONS

        Returns:
            Converted value suitable for pandas DataFrame
        """
        # Handle NULL/None values
        if value is None or value == 'NULL' or (isinstance(value, str) and value.strip() == ''):
            if column_type == 'date':
                return pd.NaT
            elif column_type == 'number':
                return pd.NA
            else:
                return pd.NA

        # Handle date conversions
        if column_type == 'date':
            if isinstance(value, (datetime, date)):
                return pd.Timestamp(value)
            elif isinstance(value, str):
                try:
                    return pd.to_datetime(value)
                except:
                    return pd.NaT

        # Handle enum/selectbox - convert to string
        if column_type == 'selectbox':
            return str(value).strip() if value else pd.NA

        # Return as-is for other types
        return value

    @staticmethod
    def _convert_pandas_to_db(value, column_type):
        # Handle pandas NA, None, NaT, empty string
        if pd.isna(value) or value is None or value == '' or value == pd.NaT:
            return None

        # Handle date conversions
        if column_type == 'date':
            if isinstance(value, pd.Timestamp):
                return value.strftime('%Y-%m-%d')
            if isinstance(value, (datetime, date)):
                return pd.to_datetime(value).strftime('%Y-%m-%d')
            if isinstance(value, str):
                try:
                    dt = pd.to_datetime(value)
                    return dt.strftime('%Y-%m-%d')
                except:
                    return None

        # Handle selectbox - ensure string
        if column_type == 'selectbox':
            return str(value).strip() if value else None

        # Handle text - ensure string, convert NA/None/'' to None
        if column_type == 'text':
            if pd.isna(value) or value is None or value == '':
                return None
            return str(value).strip() if value else None

        # Return as-is for numbers
        return value

    @staticmethod
    def load_data_from_db():
        """
        Load data from MySQL database

        Returns:
            pd.DataFrame: Loaded dataframe with proper type conversions
        """
        db = None
        try:
            # Connect to database
            db = DataObject(database=DB_CONFIG['database'])
            db.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                port=DB_CONFIG['port']
            )

            # Load migration metadata
            records = db.load_migration_metadata()

            if not records:
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(records)

            # Pre-compute column type mapping for efficiency
            col_type_map = {col: COLUMN_DEFINITIONS[col].get('type', 'text')
                           for col in df.columns if col in COLUMN_DEFINITIONS}

            # Apply type conversions using vectorized operations where possible
            for col, col_type in col_type_map.items():
                if col_type == 'date':
                    # Vectorized date conversion
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                elif col_type in ('selectbox', 'text'):
                    # Vectorized string conversion
                    df[col] = df[col].astype(str).replace({'None': pd.NA, 'nan': pd.NA, '': pd.NA})
                elif col_type == 'number':
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Ensure all configured columns exist
            configured_columns = [col for col in COLUMN_DEFINITIONS.keys() if col != 'select']
            missing_cols = set(configured_columns) - set(df.columns)

            for col in missing_cols:
                col_type = COLUMN_DEFINITIONS[col].get('type', 'text')
                if col_type == 'date':
                    df[col] = pd.NaT
                elif col_type == 'number':
                    df[col] = pd.NA
                else:
                    df[col] = pd.NA

            # Reorder columns according to COLUMN_DEFINITIONS
            column_order = [col for col in COLUMN_DEFINITIONS.keys() if col in df.columns and col != 'select']
            df = df[column_order]

            # Reset index
            df.reset_index(drop=True, inplace=True)

            return df

        except Exception as e:
            raise Exception(f"Error loading data from database: {str(e)}")
        finally:
            if db:
                db.disconnect()

    @staticmethod
    def save_data_to_db(df, changed_indices):
        """
        Save updated data back to database
        Only updates rows that have changed and only the editable columns

        Args:
            df: DataFrame with updated data
            changed_indices: List of row indices that have changed

        Returns:
            tuple: (success_count, error_list)
        """
        db = None
        success_count = 0
        errors = []

        try:
            # Connect to database
            db = DataObject(database=DB_CONFIG['database'])
            db.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                port=DB_CONFIG['port']
            )

            # Process each changed row
            for idx in changed_indices:
                try:
                    row = df.iloc[idx]
                    row_id = int(row['id'])

                    # Build updates dictionary for editable columns only
                    updates = {}
                    for col in EDITABLE_DB_COLUMNS:
                        if col in df.columns:
                            col_type = COLUMN_DEFINITIONS[col].get('type', 'text')
                            db_value = DataManager._convert_pandas_to_db(row[col], col_type)
                            updates[col] = db_value

                    # Update database
                    if updates:
                        db.update_migration_metadata(row_id, updates)
                        success_count += 1

                except Exception as e:
                    errors.append(f"Row {idx} (ID: {row_id}): {str(e)}")

            return success_count, errors

        except Exception as e:
            raise Exception(f"Error saving data to database: {str(e)}")
        finally:
            if db:
                db.disconnect()

    @staticmethod
    def get_changed_rows(original_df, edited_df):
        """
        Compare two dataframes and return changed rows
        Only considers editable columns for change detection

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
        original_clean = original_df.drop(columns=['select'], errors='ignore')

        # Get editable columns that exist in both dataframes
        editable_cols = [col for col in EDITABLE_DB_COLUMNS if col in edited_clean.columns]

        if not editable_cols:
            return pd.DataFrame(), []

        # Vectorized comparison for better performance
        # Create a boolean mask for changed rows
        changed_mask = pd.Series([False] * len(edited_clean), index=edited_clean.index)

        for col in editable_cols:
            # Compare values, handling NA/None properly
            orig_series = original_clean[col]
            edit_series = edited_clean[col]

            # XOR logic: changed if one is NA and other isn't, or values differ
            col_changed = (orig_series.isna() != edit_series.isna()) | (
                (~orig_series.isna()) & (~edit_series.isna()) & (orig_series != edit_series)
            )
            changed_mask |= col_changed

        changed_indices = changed_mask[changed_mask].index.tolist()

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
        Add select column at the end if it doesn't exist, or move it to the end.
        """
        if 'select' not in df.columns:
            df['select'] = False  # appends to the end
        else:
            # move existing column to the end
            col = df.pop('select')
            df['select'] = col
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