"""
Database Object - Handles MySQL database operations
"""
import inspect
import mysql.connector
from mysql.connector import Error
import pandas as pd
from typing import Optional, List, Dict, Any
import logging


class Logger:
    """Simple logger wrapper"""

    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def get_logger(self):
        return self.logger


class DBConnector:
    """MySQL Database Connector for workflow_db"""

    def __init__(self, database="workflow_db"):
        """
        Initialize database connector

        Args:
            database: Database name (default: workflow_db)
        """
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self, host="localhost", user="root", password="", port=3306):
        """
        Connect to MySQL database

        Args:
            host: Database host
            user: Database user
            password: Database password
            port: Database port
        """
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=self.database,
                port=port
            )
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except Error as e:
            raise Exception(f"Error connecting to MySQL: {e}")

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute(self, query, params=None):
        """Execute a query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor
        except Error as e:
            raise Exception(f"Error executing query: {e}")

    def commit(self):
        """Commit transaction"""
        if self.connection:
            self.connection.commit()

    def rollback(self):
        """Rollback transaction"""
        if self.connection:
            self.connection.rollback()


class DataObject(DBConnector):
    """Data Object for migration metadata operations"""

    def __init__(self, database="workflow_db"):
        super().__init__(database=database)
        self.logger = Logger(name=self.__class__.__name__).get_logger()

    def load_migration_metadata(self) -> List[Dict[str, Any]]:
        """Load all migration metadata from MySQL"""
        try:
            query = """
                SELECT
                    mm.id,
                    CONCAT(m.name, ':', p.name) AS meta_project,
                    mm.eon_id,
                    mm.multiple_eon,
                    mm.active,
                    CASE WHEN p.archived = 1 THEN 'YES' ELSE 'NO' END AS archived,
                    mm.workflow,
                    mm.phase,
                    mm.jira_ticket,
                    mm.jira_status,
                    mm.migrated_by,
                    mm.migration_start_date,
                    mm.migration_end_date,
                    mm.comments,
                    mm.restricted_files,
                    mm.large_files,
                    mm.hsip,
                    mm.ssh
                FROM migration_metadata mm
                INNER JOIN project p ON mm.project_id = p.id
                INNER JOIN meta m ON p.meta_id = m.id
                ORDER BY mm.id ASC
            """

            self.cursor.execute(query)
            records = self.cursor.fetchall()
            return records
        except Exception as e:
            self.logger.error(
                f"Error {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} at line {inspect.currentframe().f_lineno}: {e}"
            )
            raise

    def update_migration_metadata(self, row_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update migration metadata for a specific row

        Args:
            row_id: The ID of the row to update
            updates: Dictionary containing column names and values to update

        Returns:
            bool: Success status
        """
        try:
            # Build UPDATE query dynamically based on provided updates
            allowed_columns = ['migrated_by', 'migration_start_date', 'migration_end_date', 'phase', 'comments']

            # Filter updates to only allowed columns
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_columns}

            if not filtered_updates:
                return True  # No updates needed

            # Build SET clause
            set_clause = ", ".join([f"{col} = %s" for col in filtered_updates.keys()])
            values = list(filtered_updates.values())
            values.append(row_id)  # Add ID for WHERE clause

            query = f"""
                UPDATE migration_metadata
                SET {set_clause}
                WHERE id = %s
            """

            self.cursor.execute(query, values)
            self.commit()
            return True
        except Exception as e:
            self.rollback()
            self.logger.error(
                f"Error updating migration_metadata for ID {row_id}: {e}"
            )
            raise