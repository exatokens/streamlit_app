"""
Configuration file for GitHub Migration application
"""

# File paths
CSV_PATH = '/Users/siva/sandbox/streamlit_app/models/migration_data.csv'

# Column configuration for data editor
COLUMN_CONFIG = {
    "select": {
        "type": "checkbox",
        "label": "Select",
        "default": False
    }
}

# Available JIRA statuses (for simulation)
JIRA_STATUSES = ['open', 'in_progress', 'testing', 'done', 'closed']

# UI Configuration
PAGE_CONFIG = {
    "page_title": "GitHub Migration",
    "layout": "wide",
    "page_icon": "🕸️"
}

# Timing configurations (in seconds)
REFRESH_DELAY = 2
SAVE_DELAY = 1
STATUS_FETCH_DELAY = 1
SUCCESS_MESSAGE_DELAY = 1
ERROR_MESSAGE_DELAY = 2

# Table display settings
TABLE_HEIGHT = 400