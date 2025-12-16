"""
Configuration file for GitHub Migration application - Database Edition
"""

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '***',
    'database': 'workflow_db',
    'port': 3306
}

# Column Definitions based on database schema
# Maps database columns to UI configuration
COLUMN_DEFINITIONS = {
    "id": {
        "display_name": "ID",
        "type": "number",
        "editable": False,
        "width": "small",
        "visible": True,
        "required": True,
        "db_column": "id",
        "comment": "Primary key - auto-generated"
    },
    "meta_project": {
        "display_name": "Meta Project",
        "type": "text",
        "editable": False,
        "width": "large",
        "visible": True,
        "required": True,
        "db_column": "meta_project",
        "comment": "Concatenation of meta.name : project.name"
    },
    "eon_id": {
        "display_name": "EON ID",
        "type": "number",
        "editable": False,
        "width": "small",
        "visible": True,
        "required": False,
        "db_column": "eon_id",
        "comment": "Employee Owner Number ID"
    },
    "multiple_eon": {
        "display_name": "Multiple EON",
        "type": "selectbox",
        "options": ['YES', 'NO'],
        "editable": False,
        "width": "small",
        "visible": True,
        "required": False,
        "db_column": "multiple_eon",
        "comment": "Whether project has multiple EONs"
    },
    "active": {
        "display_name": "Active",
        "type": "selectbox",
        "options": ['YES', 'NO'],
        "editable": False,
        "width": "small",
        "visible": True,
        "required": False,
        "db_column": "active",
        "comment": "Whether the project is active"
    },
    "archived": {
        "display_name": "Archived",
        "type": "selectbox",
        "options": ['YES', 'NO'],
        "editable": False,
        "width": "small",
        "visible": True,
        "required": False,
        "db_column": "archived",
        "comment": "Whether the project is archived"
    },
    "workflow": {
        "display_name": "Workflow",
        "type": "text",
        "editable": False,
        "width": "medium",
        "visible": True,
        "required": False,
        "db_column": "workflow",
        "comment": "Workflow type (varchar 255)"
    },
    "phase": {
        "display_name": "Phase",
        "type": "selectbox",
        "options": ['Phase1', 'Phase2', 'Phase3', 'Phase4'],
        "editable": True,
        "width": "small",
        "visible": True,
        "required": False,
        "db_column": "phase",
        "comment": "Migration phase - EDITABLE"
    },
    "jira_ticket": {
        "display_name": "JIRA Ticket",
        "type": "text",
        "editable": False,
        "width": "medium",
        "visible": True,
        "required": False,
        "db_column": "jira_ticket",
        "comment": "JIRA ticket ID"
    },
    "jira_status": {
        "display_name": "JIRA Status",
        "type": "text",
        "editable": False,
        "width": "medium",
        "visible": True,
        "required": False,
        "db_column": "jira_status",
        "comment": "Current JIRA status"
    },
    "migrated_by": {
        "display_name": "Migrated By",
        "type": "text",
        "editable": True,
        "width": "medium",
        "visible": True,
        "required": False,
        "db_column": "migrated_by",
        "comment": "Person who performed migration - EDITABLE"
    },
    "migration_start_date": {
        "display_name": "Migration Start Date",
        "type": "date",
        "editable": True,
        "width": "medium",
        "visible": True,
        "required": False,
        "db_column": "migration_start_date",
        "comment": "Migration start date - EDITABLE"
    },
    "migration_end_date": {
        "display_name": "Migration End Date",
        "type": "date",
        "editable": True,
        "width": "medium",
        "visible": True,
        "required": False,
        "db_column": "migration_end_date",
        "comment": "Migration end date - EDITABLE"
    },
    "comments": {
        "display_name": "Comments",
        "type": "text",
        "editable": True,
        "width": "large",
        "visible": True,
        "required": False,
        "db_column": "comments",
        "comment": "Comments/notes - EDITABLE"
    },
    "restricted_files": {
        "display_name": "Restricted Files",
        "type": "selectbox",
        "options": ['YES', 'NO'],
        "editable": False,
        "width": "small",
        "visible": True,
        "required": False,
        "db_column": "restricted_files",
        "comment": "Whether project has restricted files"
    },
    "large_files": {
        "display_name": "Large Files",
        "type": "selectbox",
        "options": ['YES', 'NO'],
        "editable": False,
        "width": "small",
        "visible": True,
        "required": False,
        "db_column": "large_files",
        "comment": "Whether project has large files"
    },
    "hsip": {
        "display_name": "HSIP",
        "type": "selectbox",
        "options": ['YES', 'NO'],
        "editable": False,
        "width": "small",
        "visible": True,
        "required": False,
        "db_column": "hsip",
        "comment": "HSIP flag"
    },
    "ssh": {
        "display_name": "SSH",
        "type": "selectbox",
        "options": ['YES', 'NO'],
        "editable": False,
        "width": "small",
        "visible": True,
        "required": False,
        "db_column": "ssh",
        "comment": "SSH flag"
    },
    "select": {
        "display_name": "Fetch Update",
        "type": "checkbox",
        "editable": True,
        "width": "small",
        "visible": True,
        "required": False,
        "comment": "Checkbox for row selection"
    }
}

# Editable columns that can be updated in the database
EDITABLE_DB_COLUMNS = ['migrated_by', 'migration_start_date', 'migration_end_date', 'phase', 'comments']

def get_required_columns():
    """Get list of required column names"""
    return [col for col, def_ in COLUMN_DEFINITIONS.items()
            if def_.get("required", False)]

def get_configured_columns():
    """Get list of all configured column names (excluding 'select')"""
    return [col for col in COLUMN_DEFINITIONS.keys() if col != 'select']

def get_editable_columns():
    """Get list of editable column names"""
    return [col for col, def_ in COLUMN_DEFINITIONS.items()
            if def_.get("editable", False) and col != 'select']

# Available JIRA statuses (for simulation/API calls)
JIRA_STATUSES = ['Open', 'In Progress', 'Testing', 'Done', 'Closed']

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