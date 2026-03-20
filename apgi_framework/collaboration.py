"""
Collaboration module for APGI Framework.

This module provides collaborative workflow capabilities.
"""

# Mock classes for testing
class CollaborationManager:
    """Mock collaboration manager for testing purposes."""

    def __init__(self):
        self.collaborators = []
        self.shared_workspaces = {}

    def add_collaborator(self, collaborator_info):
        """Add a collaborator to the workspace."""
        collaborator_id = f"collab_{hash(str(collaborator_info)) % 10000:04d}"
        collaborator = {
            "collaborator_id": collaborator_id,
            "info": collaborator_info,
            "joined_at": "2024-01-01T00:00:00Z",
            "active": True,
        }
        self.collaborators.append(collaborator)
        return collaborator

    def create_workspace(self, workspace_name):
        """Create a shared workspace."""
        workspace_id = f"ws_{hash(workspace_name) % 10000:04d}"
        workspace = {
            "workspace_id": workspace_id,
            "name": workspace_name,
            "created_at": "2024-01-01T00:00:00Z",
            "collaborators": [],
            "shared_data": {},
        }
        self.shared_workspaces[workspace_id] = workspace
        return workspace

    def share_data(self, workspace_id, data):
        """Share data in a workspace."""
        if workspace_id in self.shared_workspaces:
            data_id = f"data_{hash(str(data)) % 10000:04d}"
            self.shared_workspaces[workspace_id]["shared_data"][data_id] = {
                "data_id": data_id,
                "data": data,
                "shared_at": "2024-01-01T00:00:00Z",
            }
            return data_id
        return None

    def get_workspace(self, workspace_id):
        """Get workspace information."""

        return self.shared_workspaces.get(workspace_id)


__all__ = [
    "CollaborationManager",
]
