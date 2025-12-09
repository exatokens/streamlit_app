"""
Authentication Configuration
"""

# Authentication settings
AUTH_ENABLED = True  # Set to False to disable authentication
SESSION_TIMEOUT_MINUTES = 60  # Session timeout in minutes

# Allowed users (username: password)
# TODO: Replace with LDAP/AD authentication
ALLOWED_USERS = {
    "admin": "admin123",
    "siva": "password123",
    "john.doe": "john123",
    "jane.smith": "jane123"
}

# Admin users (have additional privileges)
ADMIN_USERS = ["admin", "siva"]

# Authentication messages
AUTH_MESSAGES = {
    "login_title": "GitHub Migration - Login",
    "login_prompt": "Please enter your credentials to access this page",
    "invalid_credentials": "Invalid username or password",
    "session_expired": "Your session has expired. Please login again.",
    "access_denied": "You do not have permission to access this page",
    "logout_success": "You have been logged out successfully"
}

# LDAP/AD Configuration (for future implementation)
LDAP_CONFIG = {
    "enabled": False,
    "server": "ldap://your-ldap-server.com",
    "base_dn": "dc=example,dc=com",
    "user_dn_template": "uid={username},ou=users,dc=example,dc=com",
    "bind_dn": "",  # Admin DN for binding
    "bind_password": "",  # Admin password
    "search_filter": "(uid={username})",
    "attributes": ["cn", "mail", "memberOf"]
}

# Active Directory Configuration (for future implementation)
AD_CONFIG = {
    "enabled": False,
    "domain": "YOURDOMAIN",
    "server": "ldap://your-ad-server.com",
    "base_dn": "dc=yourdomain,dc=com",
    "use_ssl": True,
    "port": 636
}

PAGE_PERMISSIONS = {
    "github_migration": ["admin", "siva", "jane.smith"],  # Whitelist
}

BLOCKED_USERS = {
    "github_migration": ["john.doe"],  # john.doe is blocked!
}