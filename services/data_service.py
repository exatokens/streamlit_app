"""
Data service layer for handling all data operations.
This module manages CSV file operations, data loading, and persistence.
Separates data access logic from business logic and UI.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from models.schemas import MigrationRecord
from config.config import Settings


class DataService:
    """
    Service class for managing migration data persistence.

    Handles:
    - Loading data from CSV files
    - Saving updated data back to CSV
    - Converting between different data formats
    - Data validation and error handling

    This abstraction allows easy switching of data sources (CSV -> DB)
    without changing the rest of the application.
    """

    def __init__(self, csv_path: str = None):
        """
        Initialize the DataService with a CSV file path.

        Args:
            csv_path: Path to the CSV file containing migration data.
                     Defaults to the path defined in Settings.
        """
        self.csv_path = csv_path or Settings.DATA_FILE_PATH

    def load_data(self) -> pd.DataFrame:
        """
        Load migration data from CSV file into a DataFrame.

        This method reads the CSV file and returns it as a pandas DataFrame.
        It handles missing files gracefully by returning an empty DataFrame
        with the expected schema.

        Returns:
            DataFrame containing migration records

        Raises:
            FileNotFoundError: If CSV file doesn't exist (handled with empty DF)
        """
        try:
            df = pd.read_csv(self.csv_path)
            # Ensure all expected columns exist
            expected_columns = list(Settings.COLUMN_CONFIG.keys())
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            return df
        except FileNotFoundError:
            # Return empty DataFrame with expected schema if file doesn't exist
            return pd.DataFrame(columns=list(Settings.COLUMN_CONFIG.keys()))

    def save_data(self, df: pd.DataFrame) -> bool:
        """
        Save DataFrame back to CSV file.

        Persists the current state of migration data to the CSV file.
        This is called after users make edits to save their changes.

        Args:
            df: DataFrame containing updated migration records

        Returns:
            True if save was successful, False otherwise
        """
        try:
            df.to_csv(self.csv_path, index=False)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    def get_record_by_repository(self, df: pd.DataFrame, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single record by project repository name.

        Since project_repository is our unique identifier, this method
        allows quick lookup of a specific record for updates or display.

        Args:
            df: DataFrame to search in
            repo_name: Project repository name to find

        Returns:
            Dictionary containing the record data, or None if not found
        """
        records = df[df['project_repository'] == repo_name]
        if len(records) > 0:
            return records.iloc[0].to_dict()
        return None

    def update_record(self, df: pd.DataFrame, repo_name: str, updates: Dict[str, Any]) -> pd.DataFrame:
        """
        Update a specific record identified by repository name.

        This method finds the record and applies the provided updates.
        Used when saving individual row edits from the UI.

        Args:
            df: DataFrame containing all records
            repo_name: Project repository name (unique identifier)
            updates: Dictionary of field names and new values

        Returns:
            Updated DataFrame with the changes applied
        """
        # Find the index of the record to update
        mask = df['project_repository'] == repo_name

        # Apply updates to the matching record
        for field, value in updates.items():
            df.loc[mask, field] = value

        return df

    def get_all_records(self, df: pd.DataFrame) -> List[MigrationRecord]:
        """
        Convert DataFrame to list of typed MigrationRecord objects.

        This provides a typed interface for working with migration data,
        making the code more maintainable and enabling IDE auto-completion.

        Args:
            df: DataFrame containing migration records

        Returns:
            List of MigrationRecord objects
        """
        records = []
        for _, row in df.iterrows():
            records.append(MigrationRecord.from_dict(row.to_dict()))
        return records

    def records_to_dataframe(self, records: List[MigrationRecord]) -> pd.DataFrame:
        """
        Convert list of MigrationRecord objects back to DataFrame.

        Used when we've been working with typed objects and need to
        convert back to DataFrame format for display or storage.

        Args:
            records: List of MigrationRecord objects

        Returns:
            DataFrame representation of the records
        """
        data = [record.to_dict() for record in records]
        return pd.DataFrame(data)