"""
Security module for APGI Framework
Provides input sanitization and security utilities.
"""

from .input_sanitization import (
    InputSanitizer,
    SecureFileHandler,
    SecurityError,
    sanitize_filename,
    sanitize_path,
    sanitize_text_input,
    validate_file_extension,
)


# Mock classes for testing
class AccessController:
    """Mock access controller for testing purposes."""

    def __init__(self):
        self.access_policies = {}
        self.user_permissions = {}
        self.access_logs = []

    def add_access_policy(self, policy_name, policy_rules):
        """Add an access policy."""
        self.access_policies[policy_name] = policy_rules

    def grant_permission(self, user_id, permissions):
        """Grant permissions to a user."""
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = []
        self.user_permissions[user_id].extend(permissions)

    def check_access(self, user_id, resource, action):
        """Check if a user has access to perform an action on a resource."""
        user_permissions = self.user_permissions.get(user_id, [])
        required_permission = f"{resource}:{action}"

        access_granted = required_permission in user_permissions

        # Log the access attempt
        log_entry = {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "granted": access_granted,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        self.access_logs.append(log_entry)

        return access_granted

    def get_access_logs(self, user_id=None):
        """Get access logs, optionally filtered by user."""
        if user_id:
            return [log for log in self.access_logs if log["user_id"] == user_id]

        return self.access_logs


__all__ = [
    "InputSanitizer",
    "SecureFileHandler",
    "SecurityError",
    "sanitize_filename",
    "sanitize_path",
    "validate_file_extension",
    "sanitize_text_input",
    # Mock classes for testing
    "AccessController",
]
