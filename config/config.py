"""
Configuration file for GitHub Migration application
"""

# File paths
CSV_PATH = '/Users/siva/sandbox/streamlit_app/models/jira_test_data.csv'
"""
Configuration file for GitHub Migration application
"""

# Column Definitions - Complete control over all columns
COLUMN_DEFINITIONS = {
    "id": {
        "display_name": "ID",
        "type": "number",
        "editable": False,
        "width": "small",
        "visible": True,
        "required": True,
        "comment": "Primary key - should never be edited"
    },
    "prjt_repo": {
        "display_name": "Project Repository",
        "type": "text",
        "editable": True,
        "width": "medium",
        "visible": True,
        "required": True,
        "comment": "Project repository name in format ORG:repo-name"
    },
    "eonid": {
        "display_name": "EON ID",
        "type": "number",
        "editable": True,
        "width": "small",
        "visible": True,
        "required": True,
        "comment": "Employee/Owner Number ID"
    },
    "active": {
        "display_name": "Active",
        "type": "selectbox",
        "options": ['YES', 'NO'],
        "editable": True,
        "width": "small",
        "visible": True,
        "required": True,
        "comment": "Whether the repository is active"
    },
    "archived": {
        "display_name": "Archived",
        "type": "selectbox",
        "options": ['YES', 'NO'],
        "editable": True,
        "width": "small",
        "visible": True,
        "required": True,
        "comment": "Whether the repository is archived"
    },
    "workflow": {
        "display_name": "Workflow",
        "type": "selectbox",
        "options": ['workflow-library', 'workflow-gitflow', 'workflow-trunk'],
        "editable": False,
        "width": "medium",
        "visible": True,
        "required": True,
        "comment": "Workflow type for the repository"
    },
    "phase": {
        "display_name": "Phase",
        "type": "selectbox",
        "options": ['Phase1', 'Phase2', 'Phase3', 'Phase4'],
        "editable": True,
        "width": "small",
        "visible": True,
        "required": True,
        "comment": "Migration phase"
    },
    "test_migration_status": {
        "display_name": "Test Migration Status",
        "type": "text",
        "editable": True,
        "width": "medium",
        "visible": True,
        "required": False,
        "comment": "Status of test migration (can be None)"
    },
    "jira_ticket": {
        "display_name": "JIRA Ticket",
        "type": "text",
        "editable": True,
        "width": "medium",
        "visible": True,
        "required": True,
        "comment": "JIRA ticket ID"
    },
    "jira_status": {
        "display_name": "JIRA Status",
        "type": "selectbox",
        "options": ['Open', 'In Progress', 'Testing', 'Done', 'Closed'],
        "editable": True,
        "width": "medium",
        "visible": True,
        "required": True,
        "comment": "Current JIRA ticket status"
    },
    "meta_project": {
        "display_name": "Meta Project",
        "type": "text",
        "editable": True,
        "width": "medium",
        "visible": True,
        "required": False,
        "comment": "Meta project information (can be None)"
    },
    "migrated_repo": {
        "display_name": "Migrated Repo",
        "type": "selectbox",
        "options": ['YES', 'NO'],
        "editable": True,
        "width": "small",
        "visible": True,
        "required": True,
        "comment": "Whether repository has been migrated"
    },
    "template_repo": {
        "display_name": "Template Repo",
        "type": "selectbox",
        "options": ['YES', 'NO'],
        "editable": True,
        "width": "small",
        "visible": True,
        "required": True,
        "comment": "Whether this is a template repository"
    },
    "migration_status": {
        "display_name": "Migration Status",
        "type": "selectbox",
        "options": ['Pending', 'InProgress', 'Completed', 'Failed', 'On Hold'],
        "editable": True,
        "width": "medium",
        "visible": True,
        "required": True,
        "comment": "Overall migration status"
    },
    "select": {
        "display_name": "Select",
        "type": "checkbox",
        "editable": True,
        "width": "small",
        "visible": True,
        "required": False,
        "comment": "Checkbox for row selection"
    }
}


# Column configuration for data editor (derived from COLUMN_DEFINITIONS)
def get_column_config():
    """Generate Streamlit column config from COLUMN_DEFINITIONS"""
    config = {}

    for col_name, col_def in COLUMN_DEFINITIONS.items():
        if not col_def.get("visible", True):
            continue

        if col_def["type"] == "checkbox":
            config[col_name] = {
                "type": "checkbox",
                "label": col_def["display_name"],
                "default": False
            }
        elif col_def["type"] == "selectbox":
            config[col_name] = {
                "type": "selectbox",
                "options": col_def.get("options", [])
            }
        elif col_def["type"] == "number":
            config[col_name] = {
                "type": "number"
            }

    return config


COLUMN_CONFIG = get_column_config()


# Get list of visible columns in order
def get_visible_columns():
    """Get list of visible column names in order"""
    return [col for col, def_ in COLUMN_DEFINITIONS.items()
            if def_.get("visible", True) and col != "select"]


# Get list of editable columns
def get_editable_columns():
    """Get list of editable column names"""
    return [col for col, def_ in COLUMN_DEFINITIONS.items()
            if def_.get("editable", True)]


# Get list of required columns
def get_required_columns():
    """Get list of required column names"""
    return [col for col, def_ in COLUMN_DEFINITIONS.items()
            if def_.get("required", False)]


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